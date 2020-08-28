import os
import torch as t
import jukebox.utils.dist_adapter as dist

from jukebox.hparams import Hyperparams
from jukebox.data.labels import EmptyLabeller
from jukebox.utils.torch_utils import empty_cache
from jukebox.utils.audio_utils import save_wav, load_audio
from jukebox.make_models import make_model
from jukebox.align import get_alignment
from jukebox.save_html import save_html
from jukebox.utils.sample_utils import split_batch, get_starts
from jukebox.utils.dist_utils import print_once

# Sample a partial window of length<n_ctx with tokens_to_sample new tokens on level=level
def sample_partial_window(zs, labels, sampling_kwargs, level, prior, tokens_to_sample, hps):
    z = zs[level]
    n_ctx = prior.n_ctx
    current_tokens = z.shape[1]
    if current_tokens < n_ctx - tokens_to_sample:
        sampling_kwargs['sample_tokens'] = current_tokens + tokens_to_sample
        start = 0
    else:
        sampling_kwargs['sample_tokens'] = n_ctx
        start = current_tokens - n_ctx + tokens_to_sample

    return sample_single_window(zs, labels, sampling_kwargs, level, prior, start, hps)

# Sample a single window of length=n_ctx at position=start on level=level
def sample_single_window(zs, labels, sampling_kwargs, level, prior, start, hps):
    n_samples = hps.n_samples
    n_ctx = prior.n_ctx
    end = start + n_ctx

    # get z already sampled at current level
    z = zs[level][:,start:end]

    if 'sample_tokens' in sampling_kwargs:
        # Support sampling a window shorter than n_ctx
        sample_tokens = sampling_kwargs['sample_tokens']
    else:
        sample_tokens = (end - start)
    conditioning_tokens, new_tokens = z.shape[1], sample_tokens - z.shape[1]

    print_once(f"Sampling {sample_tokens} tokens for [{start},{start+sample_tokens}]. Conditioning on {conditioning_tokens} tokens")

    if new_tokens <= 0:
        # Nothing new to sample
        return zs

    # get z_conds from level above
    z_conds = prior.get_z_conds(zs, start, end)

    # set y offset, sample_length and lyrics tokens
    y = prior.get_y(labels, start)

    empty_cache()

    max_batch_size = sampling_kwargs['max_batch_size']
    del sampling_kwargs['max_batch_size']

    z_list = split_batch(z, n_samples, max_batch_size)
    z_conds_list = split_batch(z_conds, n_samples, max_batch_size)
    y_list = split_batch(y, n_samples, max_batch_size)
    z_samples = []
    for z_i, z_conds_i, y_i in zip(z_list, z_conds_list, y_list):
        z_samples_i = prior.sample(n_samples=z_i.shape[0], z=z_i, z_conds=z_conds_i, y=y_i, **sampling_kwargs)
        z_samples.append(z_samples_i)
    z = t.cat(z_samples, dim=0)

    sampling_kwargs['max_batch_size'] = max_batch_size

    # Update z with new sample
    z_new = z[:,-new_tokens:]
    zs[level] = t.cat([zs[level], z_new], dim=1)
    return zs

# Sample multiple levels
def _sample(zs, labels, sampling_kwargs, priors, sample_levels, hps):
    alignments = None
    for level in reversed(sample_levels):
        prior = priors[level]
        prior.cuda()
        empty_cache()

        # Set correct total_length, hop_length, labels and sampling_kwargs for level
        assert hps.sample_length % prior.raw_to_tokens == 0, f"Expected sample_length {hps.sample_length} to be multiple of {prior.raw_to_tokens}"
        total_length = hps.sample_length//prior.raw_to_tokens
        hop_length = int(hps.hop_fraction[level]*prior.n_ctx)
        zs = sample_level(zs, labels[level], sampling_kwargs[level], level, prior, total_length, hop_length, hps)

        prior.cpu()
        empty_cache()

        # Decode sample
        x = prior.decode(zs[level:], start_level=level, bs_chunks=zs[level].shape[0])

        if dist.get_world_size() > 1:
            logdir = f"{hps.name}_rank_{dist.get_rank()}/level_{level}"
        else:
            logdir = f"{hps.name}/level_{level}"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        t.save(dict(zs=zs, labels=labels, sampling_kwargs=sampling_kwargs, x=x), f"{logdir}/data.pth.tar")
        save_wav(logdir, x, hps.sr)
        if alignments is None and priors[-1] is not None and priors[-1].n_tokens > 0 and not isinstance(priors[-1].labeller, EmptyLabeller):
            alignments = get_alignment(x, zs, labels[-1], priors[-1], sampling_kwargs[-1]['fp16'], hps)
        save_html(logdir, x, zs, labels[-1], alignments, hps)
    return zs

def upsample(zs, labels, sampling_kwargs, priors, hps):
    sample_levels = list(range(len(priors) - 1))
    zs = _sample(zs, labels, sampling_kwargs, priors, sample_levels, hps)
    return zs

def run(**kwargs):
    from jukebox.utils.dist_utils import setup_dist_from_mpi
    model = "1b_lyrics"
    port = 29500
    rank, local_rank, device = setup_dist_from_mpi(port=port)
    hps = Hyperparams()
    hps.sr = 44100
    hps.n_samples = 1
    hps.name = kwargs["sample_name"]
    chunk_size = 32
    max_batch_size = 16
    hps.levels = 3
    hps.hop_fraction = [.5,.5,.125]

    vqvae, *priors = MODELS[model]
    vqvae = make_vqvae(setup_hparams(vqvae, dict(sample_length = 1048576)), device)
    top_prior = make_prior(setup_hparams(priors[-1], dict()), vqvae, device)

    sample_length_in_seconds = kwargs["sample_length"]
    hps.sample_length = (int(sample_length_in_seconds*hps.sr)//top_prior.raw_to_tokens)*top_prior.raw_to_tokens
    assert hps.sample_length >= top_prior.n_ctx*top_prior.raw_to_tokens, f'Please choose a larger sampling rate'

    metas = [dict(
                artist = kwargs["artist"],
                genre = kwargs["genre"],
                total_length = hps.sample_length,
                offset = 0,
                lyrics = kwargs["lyrics"],
            ),
    ] * hps.n_samples

    labels = [None, None, top_prior.labeller.get_batch_labels(metas, 'cuda')]

    sampling_temperature = .98

    lower_batch_size = 16
    max_batch_size = 16
    lower_level_chunk_size = 32
    chunk_size =  32
    sampling_kwargs = [
        dict(temp=.99, fp16=True, max_batch_size=lower_batch_size,
            chunk_size=lower_level_chunk_size),
        dict(temp=0.99, fp16=True, max_batch_size=lower_batch_size,
            chunk_size=lower_level_chunk_size),
        dict(temp=sampling_temperature, fp16=True, 
            max_batch_size=max_batch_size, chunk_size=chunk_size)
    ]

    zs = [t.zeros(hps.n_samples,0,dtype=t.long, device='cuda') for _ in range(len(priors))]
    zs = _sample(zs, labels, sampling_kwargs, [None, None, top_prior], [2], hps)

    del top_prior
    empty_cache()
    top_prior=None
    upsamplers = [make_prior(setup_hparams(prior, dict()), vqvae, 'cpu') for prior in priors[:-1]]
    labels[:2] = [prior.labeller.get_batch_labels(metas, 'cuda') for prior in upsamplers]

    zs = upsample(zs, labels, sampling_kwargs, [*upsamplers, top_prior], hps)

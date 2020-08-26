try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

def char_check(c):
    return c != "\b" and c != "" and c.isalnum or c == " "
###~~~###~~~###~~~###~~~###~~~###

class PrimerFileExplorer:
    def __init__(self, parent):
        self.button = tk.Button(parent, text="Browse", command=self.browse_files)
        self.button.grid(row=9, column=3)
        self.opened_file = ""

    def browse_files(self):
        self.opened_file = filedialog.askopenfilename(
            initialdir = "../../",
            title = "Select a sound file to prime with",
            filetypes = (("WAV", "*.wav*"), ("MP3", ".mp3"))
        )

###~~~###~~~###~~~###~~~###~~~###

class OutputFilenameField:
    def __init__(self, parent):
        self.input_label = tk.Label(parent, text="Output file name:")
        self.input_ = tk.Entry(parent)
        self.input_label.grid(row=9, column=4)
        self.input_.grid(row=10, column=4)

###~~~###~~~###~~~###~~~###~~~###

class SampleLengthSlider:
    def __init__(self, parent):
        self.slider_value = tk.StringVar()
        self.input_ = tk.Entry(parent, textvariable=self.slider_value, width=3)
        self.slider = tk.Scale(
            parent, from_=1, to=120, variable=self.slider_value, 
            showvalue=0, orient=tk.HORIZONTAL, relief=tk.FLAT)
        self.input_.bind("<Key>", self.check_input)
        self.slider.grid(row=9, column=0, columnspan=2, sticky="E")
        self.input_.grid(row=9, column=2, sticky="W")

    def check_input(self, e):
        if e.char.isnumeric or e.char == "\b":
            input_val = int(self.input_.get())
            if input_val <= 120 or input_val >= 0:
                self.slider.set(input_val)

###~~~###~~~###~~~###~~~###~~~###

class LyricWriter:
    def __init__(self, parent):
        self.input_label = tk.Label(parent, text="Enter lyrics")
        self.state = tk.StringVar()
        self.input_ = ScrolledText(parent, width=20, height=12)

        self.input_label.grid(row=2, column=6)
        self.input_.grid(row=3, column=6, rowspan=5, columnspan=8) 

###~~~###~~~###~~~###~~~###~~~###

class ArtistSelector:
    def __init__(self, parent):
        self.artists = []

        self.lb = tk.Listbox(parent, relief=tk.FLAT)
        self.filter_ = tk.StringVar() 
        self.filter_label = tk.Label(parent, text="Filter artist")
        self.filter_input = tk.Entry(parent, textvariable=self.filter_)
        self.filter_input.bind("<Key>", self.filter_change)

        self.lb.yview()
        self.load_artists()

        self.filter_label.grid(row=2, column=1)
        self.filter_input.grid(row=3, column=1)
        self.lb.grid(row=4, column=1, rowspan=5, columnspan=2)   


    def load_artists(self):
        f = open("./data/ids/v3_artist_ids.txt")
        artists_raw = f.readlines()
        artists_raw.sort()
        i = 0
        for a in artists_raw:
            i += 1
            artist = a.split(";")[0].title()
            self.artists.append(artist)
            self.lb.insert(i, artist)
        f.close()

    def filter_change(self, e):
        current = (self.filter_input.get() + e.char).lower()
        a_len = len(self.artists)
        if char_check(e.char):
            i = 0
            while i < a_len:
                if self.artists[i].lower().startswith(current):
                    break
                i += 1
            self.lb.yview_scroll(i-self.lb.nearest(0), tk.UNITS)

###~~~###~~~###~~~###~~~###~~~###



###~~~###~~~###~~~###~~~###~~~###

class GenreSelector:
    def __init__(self, parent):
        self.genres = []

        self.lb = tk.Listbox(parent, relief=tk.FLAT)
        self.filter_ = tk.StringVar()
        self.filter_label = tk.Label(parent, text="Filter genre")
        self.filter_input = tk.Entry(parent, textvariable=self.filter_)
        self.filter_input.bind("<Key>", self.filter_change)

        self.lb.yview()
        self.load_genres()

        self.filter_label.grid(row=2, column=4)
        self.filter_input.grid(row=3, column=4)
        self.lb.grid(row=4, column=4, rowspan=5, columnspan=2)

    def load_genres(self):
        f = open("./data/ids/v3_genre_ids.txt")
        genres_raw = f.readlines()
        genres_raw.sort()
        i = 0 
        for g in genres_raw:
            i += 1
            genre = g.split(";")[0].title()
            self.genres.append(genre)
            self.lb.insert(i, genre)
        f.close()

    def filter_change(self, e):
        current = (self.filter_input.get() + e.char).lower()
        g_len = len(self.genres)
        if char_check(e.char):
            i = 0
            while i < g_len:
                if self.genres[i].lower().startswith(current):
                    break
                i += 1
            self.lb.yview_scroll(i-self.lb.nearest(0), tk.UNITS)


###~~~###~~~###~~~###~~~###~~~###



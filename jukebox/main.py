try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    import Tkinter as tk
    import ttk

from widgets import *


def main():

    # TODO: Call the run method in sample.py
    def run():
        artist = a_select.selection
        genre = g_select.selection
        lyrics = l_writer.input_.get("1.0", tk.END)
        f_in = f_browse.opened_file
        f_out = f_output.input_.get()
        s_length = int(sl_slider.slider_value.get())
        print(f"artist: {artist}\ngenre: {genre}\nlyrics: {lyrics}\ninput file: {f_in}\noutput file: {f_out}\nsample length: {s_length}")

    def handle_eta_change(event):
        val_ = sl_slider.slider.get()
        eta_display.calc_eta(val_)

    # Application initialization
    app = tk.Tk()
    style = ttk.Style(app)
    style.theme_use("clam")
    app.title("lmariAI")
    top = tk.Frame(app)
    top.pack()

    win = tk.LabelFrame(top,  text="lmariAI", bd=1, relief=tk.FLAT)
    win.grid(padx=50, pady=20)

    # Widget initialization
    a_select = ArtistSelector(
        win, 0, 0, "Choose artist"
    )
    g_select = GenreSelector(
        win, 0, 1, "Choose genre"
    )
    l_writer = LyricWriter(
        win, 1, 0, 2, 10, "Enter lyrics"
    )
    f_browse = PrimerFileExplorer(
        win, 0, 2, "Choose primer sound file"
    )
    f_output = OutputFilenameField(
        win, 1, 2, "Output name:"
    )
    sl_slider = SampleLengthSlider(
        win, 2, 0, "Length of sample:"
    )
    eta_display = EstimatedTimeDisplay(
        win, 2, 1, "Estimated time:"
    )

    sl_slider.slider.bind("<B1-Motion>", handle_eta_change)

    run_button = tk.Button(win, text="Run", command=run)
    run_button.grid(row=10, column=1)

    # Start Tk App
    app.mainloop()


main()

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    import Tkinter as tk
    import ttk

from widgets import *

def run():
    print("I shidded")

def main():

    app = tk.Tk()
    style = ttk.Style(app)
    style.theme_use("clam")
    app.title("lmariAI")

    #X, Y = 1080, 720

    top = tk.Frame(app)
    top.pack()
    title = tk.Label(top, text="lmariAI")

    a_select = ArtistSelector(top)
    g_select = GenreSelector(top)
    f_browse = PrimerFileExplorer(top)
    output_f = OutputFilenameField(top)
    lw = LyricWriter(top)
    sls = SampleLengthSlider(top)

    run_button = tk.Button(top, text="Run", command=run)

    title.grid(padx=20, pady=20, row=0, column=0, rowspan=2, columnspan=10, sticky="NW")

    run_button.grid(row=10, column=1)

    app.mainloop()


main()

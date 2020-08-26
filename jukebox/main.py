try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    import Tkinter as tk
    import ttk

from widgets import *

# TODO: Call the run method in sample.py
def run():
    print("I shidded")

def main():

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

    # Widget initialization
    a_select = ArtistSelector(top)
    g_select = GenreSelector(top)
    f_browse = PrimerFileExplorer(top)
    f_output = OutputFilenameField(top)
    l_writer = LyricWriter(top)
    sl_slider = SampleLengthSlider(top)
    eta_display = EstimatedTimeDisplay(top)

    sl_slider.slider.bind("<B1-Motion>", handle_eta_change)

    title = tk.Label(top, text="lmariAI")
    run_button = tk.Button(top, text="Run", command=run)
    title.grid(padx=20, pady=20, row=0, column=0, rowspan=2, columnspan=10, sticky="NW")
    run_button.grid(row=10, column=1)

    # Start Tk App
    app.mainloop()


main()

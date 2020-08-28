try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    import Tkinter as tk
    import ttk

from widgets import *
import sample


def main():

    def proc_start():
        a = a_select.selection
        g = g_select.selection
        l = l_writer.input_.get("1.0", tk.END)
        in_f = f_browse.opened_file
        s_n = f_output.input_.get()
        s_l = int(sl_slider.slider_value.get())
        print(f"artist: {a}\ngenre: {g}\nlyrics: {l}\ninput file: {in_f}\noutput file: {s_n}\nsample length: {s_l}")

        sample.run(
            artist=a, 
            genre=g, 
            lyrics=l, 
            input_file=in_f, 
            sample_name=s_n, 
            sample_length=s_l
        )

    def handle_slider_input(event):
        handle_eta_change(event)
        sl_slider.check_input(event)

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

    win = tk.LabelFrame(top,  text="lmariAI", bd=5, relief=tk.RIDGE)
    win.grid(padx=20, pady=20)

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
    eta_display.calc_eta(20)

    sl_slider.slider.bind("<B1-Motion>", handle_eta_change)
    sl_slider.input_.bind("<Key>", handle_slider_input)

    run_button = tk.Button(win, text="Run", command=proc_start)
    run_button.grid(row=2, column=2)

    # Start Tk App
    app.mainloop()


main()

try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

import math as m

def char_check(c):
    return c != "\b" and c != "" and c.isalnum or c == " "

###~~~###~~~###~~~###~~~###~~~###

class UIWidget:
    def __init__(self, parent, h=1, w=1, gy=0, gx=0, py=5, px=10, label=""):
        self.frame = tk.LabelFrame(parent, text=label, relief=tk.FLAT)
        self.frame.grid(
                row=gy, column=gx, 
                rowspan=h, columnspan=w,
                pady=py, padx=px
        )

###~~~###~~~###~~~###~~~###~~~###

class PrimerFileExplorer(UIWidget): 
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.button = tk.Button(self.frame, text="Browse", command=self.browse_files)
        self.opened_file = ""
        self.file_parsed = tk.StringVar()
        self.file_label = tk.Label(self.frame, textvariable=self.file_parsed)
        self.button.grid()
        self.file_label.grid()

    def browse_files(self):
        self.opened_file = filedialog.askopenfilename(
            initialdir = "../../",
            title = "Select a sound file to prime with",
            filetypes = (("WAV", "*.wav*"), ("MP3", ".mp3"))
        )
        self.file_parsed.set(self.opened_file.split("/")[-1])

###~~~###~~~###~~~###~~~###~~~###

class EstimatedTimeDisplay(UIWidget):
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.eta = tk.StringVar()
        self.IT_SEC = 13.5
        self.display = tk.Label(self.frame, textvariable=self.eta)
        self.display.grid()

    def calc_eta(self, sample_length):
        sec_  = (sample_length * 5512) / self.IT_SEC
        min_  = m.floor(sec_ / 60)
        hour_ = m.floor(min_ / 60)
        formatted = f"{hour_}h {min_ - (hour_ * 60)}m"
        self.eta.set(formatted)

###~~~###~~~###~~~###~~~###~~~###

class OutputFilenameField(UIWidget):
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.input_ = tk.Entry(self.frame)
        self.input_.grid()

###~~~###~~~###~~~###~~~###~~~###

class SampleLengthSlider(UIWidget):
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.slider_value = tk.StringVar()
        self.input_ = tk.Entry(self.frame, textvariable=self.slider_value, width=3)
        self.slider = tk.Scale(
            self.frame, from_=20, to=200, variable=self.slider_value, 
            showvalue=0, orient=tk.HORIZONTAL, relief=tk.FLAT
        )
        self.s_label = tk.Label(self.frame, text="sec")
        self.slider.grid(row=0)
        self.input_.grid(row=0, column=1)
        self.s_label.grid(row=0, column=2, sticky="W")

    def check_input(self, e):
        if e.char.isnumeric or e.char == "\b":
            input_val = int(self.input_.get())
            if input_val <= 120 or input_val >= 0:
                self.slider.set(input_val)

###~~~###~~~###~~~###~~~###~~~###

class LyricWriter(UIWidget):
    def __init__(self, parent, gy, gx, w, py, label):
        super().__init__(parent, gy=gy, gx=gx, w=w, label=label)
        self.input_ = ScrolledText(self.frame, wrap=tk.WORD, width=20, height=12)
        self.input_.grid() 

###~~~###~~~###~~~###~~~###~~~###

class ArtistSelector(UIWidget):
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.artists = []

        self.lb = tk.Listbox(self.frame, relief=tk.FLAT)
        self.filter_ = tk.StringVar() 
        self.selection = "unknown"
        self.filter_input = tk.Entry(self.frame, textvariable=self.filter_)
        self.lb.bind("<ButtonRelease-1>", self.save_selection)
        self.lb.bind("<FocusOut>", self.display_selection)
        self.filter_input.bind("<Key>", self.filter_change)

        self.lb.yview()
        self.load_artists()

        self.filter_input.grid()
        self.lb.grid() 

    def load_artists(self):
        f = open("./data/ids/v3_artist_ids.txt")
        artists_raw = f.readlines()
        artists_raw.sort()
        i = 0 
        for a in artists_raw:
            artist = a.split(";")[0].title()
            if len(artist) > 1:
                i += 1
                self.artists.append(artist)
                self.lb.insert(i, artist)
        f.close()

    def save_selection(self, e):
        i = self.lb.curselection()
        if i:
            self.selection = self.lb.get(i)

    def display_selection(self, e):
        self.filter_.set(self.selection)

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

class GenreSelector(UIWidget):
    def __init__(self, parent, gy, gx, label):
        super().__init__(parent, gy=gy, gx=gx, label=label)
        self.genres = []

        self.lb = tk.Listbox(self.frame, relief=tk.FLAT)
        self.selection = "unknown"
        self.filter_ = tk.StringVar()
        self.filter_input = tk.Entry(self.frame, textvariable=self.filter_)
        self.lb.bind("<ButtonRelease-1>", self.save_selection)
        self.lb.bind("<FocusOut>", self.display_selection)
        self.filter_input.bind("<Key>", self.filter_change)

        self.lb.yview()
        self.load_genres()

        self.filter_input.grid()
        self.lb.grid()

    def load_genres(self):
        f = open("./data/ids/v3_genre_ids.txt")
        genres_raw = f.readlines()
        genres_raw.sort()
        i = 0 
        for g in genres_raw:
            genre = g.split(";")[0].title()
            if len(genre) > 1:
                i += 1
                self.genres.append(genre)
                self.lb.insert(i, genre)
        f.close()

    def _get(self):
        i = self.lb.curselection()
        if i:
            return self.lb.get(i)

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

    def save_selection(self, e):
        i = self.lb.curselection()
        print(i)
        if i:
            self.selection = self.lb.get(i)

    def display_selection(self, e):
        self.filter_.set(self.selection)

###~~~###~~~###~~~###~~~###~~~###



import tkinter as tk
from tkinter import ttk


class Window(tk.Toplevel):
    def __init__(self, parent, file_content=''):
        super().__init__(parent)

        self.geometry('400x400+100+100')
        self.title('File content')

        self.output_text = tk.Text(self)
        self.output_text.insert('1.0', file_content)
        self.output_text.place(x=5, y=5, height=390, width=390)

import tkinter as tk
from tkinter import ttk

from loans_tab import LoansTab
from repository.database import Database
from library_tab import LibraryTab
from readers_tab import ReadersTab


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library App")
        self.geometry("1000x800")
        self.resizable(True, True)

        # TODO: user & password
        self.db = Database(db_name="library_db", user="postgres", password="123")

        self.notebook = ttk.Notebook()
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.library_management_tab = LibraryTab(self, self.db)
        self.notebook.add(self.library_management_tab.frame, text="Управление библиотекой")

        self.readers_tab = ReadersTab(self, self.db)
        self.notebook.add(self.readers_tab.frame, text="Управление читателями")

        self.loans_tab = LoansTab(self, self.db)
        self.notebook.add(self.loans_tab.frame, text="Управление займами")

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
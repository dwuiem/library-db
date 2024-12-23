import tkinter as tk
from tkinter import ttk

from gui.tabs.loans_tab import LoansTab
from database import Database
from gui.tabs.library_tab import LibraryTab
from gui.tabs.readers_tab import ReadersTab

import dotenv as env
import os


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library App")
        self.geometry("1000x800")
        self.resizable(True, True)

        env.load_dotenv()

        db_name = os.getenv('DB_NAME')

        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')

        db_user = os.getenv('DB_USER_LOGIN')
        db_password = os.getenv('DB_USER_PASSWORD')


        self.db = Database(db_name, user=db_user, password=db_password, host=db_host, port=db_port)

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
import tkinter as tk
from tkinter import messagebox

from repository.database import Database
from entity import Author
from datetime import datetime

DATE_FORMAT = "%d.%m.%Y"

class AddAuthorWindow:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db

        self.window = tk.Toplevel(parent)
        self.window.title("Добавить автора")
        self.window.transient(parent)
        self.window.grab_set()

        tk.Label(self.window, text="ФИО автора:").pack(padx=10, pady=5)
        self.name_entry = tk.Entry(self.window)
        self.name_entry.pack(padx=10, pady=5)

        tk.Label(self.window, text="Дата рождения (необязательно):").pack(padx=10, pady=5)
        self.birth_date_entry = tk.Entry(self.window)
        self.birth_date_entry.pack(padx=10, pady=5)

        confirm_author_button = tk.Button(self.window, text="Подтвердить", command=self.confirm_add_author)
        confirm_author_button.pack(padx=10, pady=10)

    def confirm_add_author(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Ошибка", "ФИО автора обязательно!")
            return

        birth_date = None
        birth_date_str = self.birth_date_entry.get()
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, DATE_FORMAT).date()
            except ValueError:
                messagebox.showwarning("Ошибка", "Укажите дату рождения формата DD.MM.YYYY")
                return
        author = Author(name, birth_date)
        try:
            self.db.author_repository.save(author)
        except ValueError:
            messagebox.showwarning("Ошибка", "Имя автора должно быть уникальным")
            return
        self.window.destroy()
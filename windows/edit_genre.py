import tkinter as tk
from tkinter import messagebox

from repository.database import Database
from entity import Genre

class EditGenreWindow:
    def __init__(self, parent: tk.Tk, db: Database, genre: Genre):
        self.db = db
        self.genre = genre

        self.window = tk.Toplevel(parent)
        self.window.title("Изменить жанр")
        self.window.transient(parent)
        self.window.grab_set()

        tk.Label(self.window, text="Новое имя:").pack(padx=10, pady=5)
        self.name_entry = tk.Entry(self.window)
        self.name_entry.pack(padx=10, pady=5)
        self.name_entry.insert(tk.END, self.genre.name)

        confirm_author_button = tk.Button(self.window, text="Подтвердить изменения", command=self.confirm_edit_genre)
        confirm_author_button.pack(padx=10, pady=10)

    def confirm_edit_genre(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Ошибка", "Имя жанра обязательно")
            return

        self.genre.name = name

        self.db.genre_repository.update(self.genre)
        self.window.destroy()
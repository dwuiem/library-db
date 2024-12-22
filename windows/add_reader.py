import tkinter as tk
from tkinter import messagebox

from repository.database import Database
from entity import Reader

class AddReaderWindow:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db
        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Добавить книгу")
        self.window.transient(parent)
        self.window.grab_set()

        tk.Label(self.window, text="Имя читателя:").pack(padx=10, pady=5)
        self.name_entry = tk.Entry(self.window, width=50)
        self.name_entry.pack(padx=50, pady=5)

        tk.Label(self.window, text="Телефон:").pack(padx=10, pady=5)
        self.phone_entry = tk.Entry(self.window, width=50)
        self.phone_entry.pack(padx=50, pady=5)

        tk.Label(self.window, text="Email (необязательно):").pack(padx=10, pady=5)
        self.email_entry = tk.Entry(self.window, width=50)
        self.email_entry.pack(padx=50, pady=5)

        confirm_button = tk.Button(self.window, text="Подтвердить", command=self.confirm_add_reader)
        confirm_button.pack(padx=10, pady=10)

    def confirm_add_reader(self):
        reader_name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get() if self.email_entry.get() else None

        if not reader_name or not phone:
            messagebox.showerror("Ошибка", "Имя и номер обязательно должны быть указаны")
            return

        reader = Reader(reader_name, email, phone)
        try:
            self.db.reader_repository.save(reader)
        except ValueError:
            messagebox.showwarning("Ошибка", "Имя, email и телефон должны быть уникальными")
            return
        self.window.destroy()
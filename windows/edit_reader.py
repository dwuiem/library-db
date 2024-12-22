import tkinter as tk
from tkinter import messagebox

from database import Database
from entity import Reader
from utils import validate_and_convert, validate_email


class EditReaderWindow:
    def __init__(self, parent: tk.Tk, db: Database, reader: Reader):
        self.db = db
        self.parent = parent
        self.reader = reader

        self.window = tk.Toplevel(parent)
        self.window.title("Изменить читателя")
        self.window.transient(parent)
        self.window.grab_set()

        tk.Label(self.window, text="Имя читателя:").pack(padx=10, pady=5)
        self.name_entry = tk.Entry(self.window, width=50)
        self.name_entry.pack(padx=50, pady=5)
        self.name_entry.insert(tk.END, self.reader.name)

        tk.Label(self.window, text="Телефон:").pack(padx=10, pady=5)
        self.phone_entry = tk.Entry(self.window, width=50)
        self.phone_entry.pack(padx=50, pady=5)
        self.phone_entry.insert(tk.END, self.reader.phone)

        tk.Label(self.window, text="Email (необязательно):").pack(padx=10, pady=5)
        self.email_entry = tk.Entry(self.window, width=50)
        self.email_entry.pack(padx=50, pady=5)
        self.email_entry.insert(tk.END, self.reader.email)

        confirm_button = tk.Button(self.window, text="Подтвердить изменения", command=self.confirm_edit_reader)
        confirm_button.pack(padx=10, pady=10)

    def confirm_edit_reader(self):
        reader_name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get() if self.email_entry.get() else None

        if not reader_name or not phone:
            messagebox.showerror("Ошибка", "Имя и номер обязательно должны быть указаны")
            return

        phone = validate_and_convert(phone_number=phone)
        if not phone:
            messagebox.showerror("Ошибка", "Неверный формат номера телефона")
            return
        if not validate_email(email=email):
            messagebox.showerror("Ошибка", "Неверный формат почты")
            return

        reader = Reader(id=self.reader.id, name=reader_name, email=email, phone=phone)
        try:
            self.db.reader_repository.update(reader)
        except ValueError:
            messagebox.showwarning("Ошибка", "Имя, email и телефон должны быть уникальными")
            return
        self.window.destroy()
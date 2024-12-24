import tkinter as tk
from tkinter import messagebox

from database import Database
from typing import List

from datetime import datetime, timedelta

from utils import DATE_FORMAT


class LendBookWindow:
    def __init__(self, parent: tk.Tk, db: Database, reader_id: int, book_ids: List[int]):
        self.db = db

        self.reader_id = reader_id
        self.book_ids = book_ids

        self.window = tk.Toplevel(parent)
        self.window.title("Забронировать книги")
        self.window.transient(parent)
        self.window.grab_set()

        tk.Label(self.window, text="Когда вы собираетесь вернуть их (дата, не более 7 дней):").pack(padx=10, pady=5)
        self.return_date_entry = tk.Entry(self.window)
        self.return_date_entry.pack(padx=10, pady=5)

        confirm_author_button = tk.Button(self.window, text="Подтвердить", command=self.confirm_loan)
        confirm_author_button.pack(padx=10, pady=10)

    def confirm_loan(self):
        return_date_str = self.return_date_entry.get()
        try:
            return_date = datetime.strptime(return_date_str, DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте формат DD.MM.YYYY.")
            return
        current_date = datetime.now()
        max_return_date = current_date + timedelta(days=14)
        if return_date > max_return_date or return_date <= current_date:
            messagebox.showerror("Ошибка", "Дата возврата не может быть текущей и ранее или позже, чем через 7 дней от текущей.")
            return
        self.db.loan_repository.lend_book(self.reader_id, self.book_ids, return_date)
        self.window.destroy()
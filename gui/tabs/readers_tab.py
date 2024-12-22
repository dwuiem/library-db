import tkinter as tk
from tkinter import ttk, messagebox

from entity import Reader
from database import Database
from gui.windows.add_reader import AddReaderWindow
from gui.windows.edit_reader import EditReaderWindow


class ReadersTab:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db

        self.parent = parent
        self.readers = self.db.reader_repository.get_all()
        self.loans = self.db.loan_repository.get_all()

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = ttk.Frame(self.frame)
        self.top_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.top_frame)
        self.right_panel.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(self.frame, text="Обновить данные", command=self.update_all_info)
        self.refresh_button.pack(padx=10, pady=5, anchor="ne")

        self.readers_treeview = ttk.Treeview(self.right_panel, columns=("ID", "Name", "Email", "Phone"),
                                             show="headings")
        self.readers_treeview.pack(fill=tk.BOTH, expand=True)

        self.readers_treeview.heading("ID", text="ID")
        self.readers_treeview.heading("Name", text="Имя")
        self.readers_treeview.heading("Email", text="Почта")
        self.readers_treeview.heading("Phone", text="Телефон")

        self.readers_treeview.column("ID", width=50, stretch=tk.YES)
        self.readers_treeview.column("Name", width=200, stretch=tk.YES)
        self.readers_treeview.column("Email", width=250, stretch=tk.YES)
        self.readers_treeview.column("Phone", width=150, stretch=tk.YES)

        self.readers_buttons = ttk.Frame(self.right_panel)
        self.readers_buttons.pack(pady=5, fill=tk.X)

        self.add_reader_button = tk.Button(self.readers_buttons, text="Добавить читателя", command=lambda: AddReaderWindow(self.parent, self.db))
        self.add_reader_button.pack(side=tk.LEFT, padx=5)

        self.edit_reader_button = tk.Button(self.readers_buttons, text="Изменить читателя", command=self.edit_reader)
        self.edit_reader_button.pack(side=tk.LEFT, padx=5)

        self.remove_reader_button = tk.Button(self.readers_buttons, text="Удалить читателя/читателей", command=self.remove_readers)
        self.remove_reader_button.pack(side=tk.LEFT, padx=5)

        self.loans_frame = ttk.Frame(self.right_panel)
        self.loans_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10)

        self.loans_treeview = ttk.Treeview(self.loans_frame, columns=("Loan ID", "Reader Name", "Loan Date", "Return Date"),
                                           show="headings")
        self.loans_treeview.pack(fill=tk.BOTH, expand=True)

        self.loans_treeview.heading("Loan ID", text="ID")
        self.loans_treeview.heading("Reader Name", text="Имя Читателя")
        self.loans_treeview.heading("Loan Date", text="Дата займа")
        self.loans_treeview.heading("Return Date", text="Дата возврата")

        self.loans_treeview.column("Loan ID", width=50, stretch=tk.YES)
        self.loans_treeview.column("Reader Name", width=200, stretch=tk.YES)
        self.loans_treeview.column("Loan Date", width=150, stretch=tk.YES)
        self.loans_treeview.column("Return Date", width=150, stretch=tk.YES)

        self.update_all_info()

    def edit_reader(self):
        selection = self.readers_treeview.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror("Ошибка", "Выберите ТОЛЬКО одного читателя")
            return

        values = self.readers_treeview.item(selection[0])['values']

        reader = Reader(id=values[0], name=values[1], email=values[2], phone=values[3])
        EditReaderWindow(self.parent, self.db, reader)

    def remove_readers(self):
        selected_items = self.readers_treeview.selection()
        if selected_items:
            for item in selected_items:
                reader_id = self.readers_treeview.item(item)['values'][0]
                self.db.reader_repository.delete_by_id(reader_id)
                self.readers_treeview.delete(item)


    def update_all_info(self):
        self.update_readers_treeview()
        self.update_loans_treeview()

    def update_readers_treeview(self):
        self.readers = self.db.reader_repository.get_all()
        for item in self.readers_treeview.get_children():
            self.readers_treeview.delete(item)
        for reader in self.readers:
            self.readers_treeview.insert("", tk.END, values=(reader.id, reader.name, reader.email if reader.email else "", reader.phone) )

    def update_loans_treeview(self):
        self.loans = self.db.loan_repository.get_all()
        for item in self.loans_treeview.get_children():
            self.loans_treeview.delete(item)
        for loan in self.loans:
            self.loans_treeview.insert("", tk.END, values=(loan.id, loan.reader.name, loan.loan_date.strftime('%d.%m.%Y'), loan.return_date.strftime('%d.%m.%Y')))


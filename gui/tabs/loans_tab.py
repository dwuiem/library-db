import tkinter as tk
from tkinter import ttk

from database import Database
from tkinter import messagebox

from utils import DATE_FORMAT
from gui.windows.lend_book import LendBookWindow


class LoansTab:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db
        self.parent = parent

        self.reader = None
        self.available_books = []
        self.reserved_books = []

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Top section: Reader name input and search button
        self.top_frame = ttk.Frame(self.frame)
        self.top_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        self.reader_label = ttk.Label(self.top_frame, text="Имя читателя:")
        self.reader_label.pack(side=tk.LEFT, padx=5)

        self.reader_entry = ttk.Entry(self.top_frame, width=30)
        self.reader_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(self.top_frame, text="Отобразить", command=self.display_reader_info)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.top_frame, text="Удалить читателя по имени", command=self.remove_reader)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.reader_info_label = ttk.Label(self.frame, text="Читатель не выбран")
        self.reader_info_label.pack(padx=10, pady=5, anchor="w")

        self.bottom_frame = ttk.Frame(self.frame)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.available_books_frame = ttk.Frame(self.bottom_frame)
        self.available_books_frame.pack(fill=tk.BOTH, expand=True)

        self.available_books_treeview = ttk.Treeview(
            self.available_books_frame,
            columns=("ID", "Title", "Author", "Year", "Genre"),
            show="headings"
        )
        self.available_books_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.available_books_treeview.heading("ID", text="ID")
        self.available_books_treeview.heading("Title", text="Название")
        self.available_books_treeview.heading("Author", text="Автор")
        self.available_books_treeview.heading("Year", text="Год публикации")
        self.available_books_treeview.heading("Genre", text="Жанр")

        self.available_books_treeview.column("ID", width=20, stretch=tk.YES)
        self.available_books_treeview.column("Title", width=160, stretch=tk.YES)
        self.available_books_treeview.column("Author", width=150, stretch=tk.YES)
        self.available_books_treeview.column("Year", width=50, stretch=tk.YES)
        self.available_books_treeview.column("Genre", width=50, stretch=tk.YES)

        self.available_books_button_frame = ttk.Frame(self.available_books_frame)
        self.available_books_button_frame.pack(pady=5, fill=tk.X)

        self.reserve_book_button = tk.Button(
            self.available_books_button_frame, text="Забронировать", command=self.lend_book
        )
        self.reserve_book_button.pack(side=tk.LEFT, padx=5)

        self.reserved_books_frame = ttk.Frame(self.bottom_frame)
        self.reserved_books_frame.pack(fill=tk.BOTH, expand=True)

        self.reserved_books_treeview = ttk.Treeview(
            self.reserved_books_frame,
            columns=("Book ID", "Title", "Loan ID", "Loan date", "Return date"),
            show="headings"
        )
        self.reserved_books_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.reserved_books_treeview.heading("Book ID", text="ID Книги")
        self.reserved_books_treeview.heading("Title", text="Название книги")
        self.reserved_books_treeview.heading("Loan ID", text="ID Займа")
        self.reserved_books_treeview.heading("Loan date", text="Дата займа")
        self.reserved_books_treeview.heading("Return date", text="Дата возврата")

        self.reserved_books_treeview.column("Book ID", width=20, stretch=tk.YES)
        self.reserved_books_treeview.column("Title", width=160, stretch=tk.YES)
        self.reserved_books_treeview.column("Loan ID", width=150, stretch=tk.YES)
        self.reserved_books_treeview.column("Loan date", width=50, stretch=tk.YES)
        self.reserved_books_treeview.column("Return date", width=50, stretch=tk.YES)

        self.reserved_books_button_frame = ttk.Frame(self.reserved_books_frame)
        self.reserved_books_button_frame.pack(pady=5, fill=tk.X)

        self.return_book_button = tk.Button(
            self.reserved_books_button_frame, text="Вернуть", command=self.return_book
        )
        self.return_book_button.pack(side=tk.LEFT, padx=5)

    def display_reader_info(self):
        self.reader = self.db.reader_repository.get_by_name(self.reader_entry.get())
        if not self.reader:
            messagebox.showerror("Ошибка", "Такого читателя не существует")
            return

        self.available_books = self.db.book_repository.get_all_available()
        self.reserved_books = self.db.book_repository.get_all_by_reader_id(reader_id=self.reader.id)
        reader_info = (f"Читатель: {self.reader.name} \n"
                       f"Телефон: {self.reader.phone} \n"
                       f"EMAIL: {self.reader.email}")
        self.reader_info_label.config(text=reader_info)

        for item in self.available_books_treeview.get_children():
            self.available_books_treeview.delete(item)
        for item in self.reserved_books_treeview.get_children():
            self.reserved_books_treeview.delete(item)

        for book in self.available_books:
            id = book.id
            title = book.title
            author_name = book.author.name
            publication_year = book.publication_year if book.publication_year else ""
            genre_name = book.genre.name if book.genre else ""
            self.available_books_treeview.insert("", tk.END, values=(id, title, author_name, publication_year, genre_name))

        for book in self.reserved_books:
            book_id = book.id
            title = book.title
            load_id = book.loan.id
            return_date = book.loan.return_date
            loan_date = book.loan.loan_date
            self.reserved_books_treeview.insert("", tk.END, values=(book_id, title, load_id, loan_date.strftime(DATE_FORMAT), return_date.strftime(DATE_FORMAT)))

    def lend_book(self):
        if not self.reader:
            messagebox.showerror("Ошибка", "Читатель не выбран")
            return
        selected_items = self.available_books_treeview.selection()
        if selected_items:
            if len(selected_items) > 5:
                messagebox.showerror("Ошибка", "Вы можете выбрать не более 5-ти книг")
                return
            book_ids = []
            for item in selected_items:
                values = self.available_books_treeview.item(item)['values']
                book_id = int(values[0])
                book_ids.append(book_id)
            LendBookWindow(self.parent, self.db, self.reader.id, book_ids)

    def remove_reader(self):
        reader_name = self.reader_entry.get()
        if not reader_name:
            messagebox.showerror("Ошибка", "Читатель не выбран")
            return
        self.db.reader_repository.delete_by_name(reader_name)


    def return_book(self):
        selected_items = self.reserved_books_treeview.selection()
        if selected_items:
            for item in selected_items:
                values = self.reserved_books_treeview.item(item)['values']
                book_id = int(values[0])
                self.db.book_repository.return_by_id(book_id)
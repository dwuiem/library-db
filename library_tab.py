import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from entity import Book, Author, Genre
from utils import DATE_FORMAT
from windows.add_author import AddAuthorWindow
from windows.add_book import AddBookWindow
from windows.edit_author import EditAuthorWindow
from windows.edit_book import EditBookWindow
from datetime import datetime

from windows.edit_genre import EditGenreWindow


class LibraryTab:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db

        self.books = self.db.book_repository.get_all()
        self.authors = self.db.author_repository.get_all()
        self.genres = self.db.genre_repository.get_all()

        self.parent = parent

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = ttk.Frame(self.frame)
        self.top_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.top_frame)
        self.right_panel.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(self.frame, text="Обновить данные", command=self.update_all_info)
        self.refresh_button.pack(padx=10, pady=5, anchor="ne")

        self.clear_button = tk.Button(self.frame, text="Очистить ВСЕ данные", command=self.db.clear_all_tables)
        self.clear_button.pack(padx=10, pady=5, anchor="center")

        self.books_treeview = ttk.Treeview(self.right_panel, columns=("ID", "Title", "Author", "Year", "Genre"),
                                           show="headings")
        self.books_treeview.pack(fill=tk.BOTH, expand=True)

        self.books_treeview.heading("ID", text="ID")
        self.books_treeview.heading("Title", text="Название")
        self.books_treeview.heading("Author", text="Автор")
        self.books_treeview.heading("Year", text="Год публикации")
        self.books_treeview.heading("Genre", text="Жанр")

        self.books_treeview.column("ID", width=20, stretch=tk.YES)
        self.books_treeview.column("Title", width=160, stretch=tk.YES)
        self.books_treeview.column("Author", width=180, stretch=tk.YES)
        self.books_treeview.column("Year", width=100, stretch=tk.YES)
        self.books_treeview.column("Genre", width=100, stretch=tk.YES)

        self.books_buttons = ttk.Frame(self.right_panel)
        self.books_buttons.pack(pady=5, fill=tk.X)

        self.add_book_button_right = tk.Button(self.books_buttons, text="Добавить книгу", command=lambda: AddBookWindow(self.parent, self.db))
        self.add_book_button_right.pack(side=tk.LEFT, padx=5)

        self.edit_book_button_right = tk.Button(self.books_buttons, text="Изменить книгу", command=self.edit_book)
        self.edit_book_button_right.pack(side=tk.LEFT, padx=5)

        self.remove_book_button_right = tk.Button(self.books_buttons, text="Удалить книги", command=self.remove_book)
        self.remove_book_button_right.pack(side=tk.LEFT, padx=5)

        self.clear_books_button = tk.Button(self.books_buttons, text="Очистить все книги", command=self.db.book_repository.clear_all)
        self.clear_books_button.pack(side=tk.LEFT, padx=5)

        self.authors_and_genres_frame = ttk.Frame(self.right_panel)
        self.authors_and_genres_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.authors_frame = ttk.Frame(self.authors_and_genres_frame)
        self.authors_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.authors_treeview = ttk.Treeview(self.authors_frame, columns=("ID", "Author", "Birthdate"), show="headings")
        self.authors_treeview.pack(fill=tk.BOTH, expand=True)

        self.authors_treeview.heading("ID", text="ID")
        self.authors_treeview.heading("Author", text="Имя")
        self.authors_treeview.heading("Birthdate", text="Родился")

        self.authors_treeview.column("ID", width=20, stretch=tk.YES)
        self.authors_treeview.column("Author", width=250, stretch=tk.YES)
        self.authors_treeview.column("Birthdate", width=230, stretch=tk.YES)

        self.authors_buttons = ttk.Frame(self.authors_frame)
        self.authors_buttons.pack(pady=5)

        self.edit_author_button = tk.Button(self.authors_buttons, text="Добавить автора", command=lambda: AddAuthorWindow(self.parent, self.db))
        self.edit_author_button.pack(side=tk.LEFT, padx=5)

        self.edit_author_button = tk.Button(self.authors_buttons, text="Изменить автора", command=self.edit_author)
        self.edit_author_button.pack(side=tk.LEFT, padx=5)

        self.remove_author_button = tk.Button(self.authors_buttons, text="Удалить авторов", command=self.remove_author)
        self.remove_author_button.pack(side=tk.LEFT, padx=5)

        self.genres_frame = ttk.Frame(self.authors_and_genres_frame)
        self.genres_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.genres_treeview = ttk.Treeview(self.genres_frame, columns=("ID", "Name"), show="headings")
        self.genres_treeview.pack(fill=tk.BOTH, expand=True)

        self.genres_treeview.heading("ID", text="ID")
        self.genres_treeview.heading("Name", text="Имя")

        self.genres_treeview.column("ID", width=20, stretch=tk.YES)
        self.genres_treeview.column("Name", width=250, stretch=tk.YES)

        self.genres_buttons = ttk.Frame(self.genres_frame)
        self.genres_buttons.pack(pady=5)

        self.edit_genre_button = tk.Button(self.genres_buttons, text="Изменить жанр", command=self.edit_genre)
        self.edit_genre_button.pack(side=tk.LEFT, padx=5)

        self.remove_genre_button = tk.Button(self.genres_buttons, text="Удалить жанры", command=self.remove_genre)
        self.remove_genre_button.pack(side=tk.LEFT, padx=5)

        self.update_all_info()

    def edit_book(self):
        selection = self.books_treeview.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror("Ошибка", "Выберите ТОЛЬКО одну книгу")
            return

        selected_item = selection[0]
        values = self.books_treeview.item(selected_item)['values']

        book_id = values[0]
        title = values[1]
        author = self.db.author_repository.get_by_book_id(book_id)
        publication_year = int(values[3]) if values[3] else None
        genre = self.db.genre_repository.get_by_book_id(book_id)

        book = Book(title, author, publication_year, genre, id=book_id)
        EditBookWindow(self.parent, self.db, book)

    def edit_author(self):
        selection = self.authors_treeview.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror("Ошибка", "Выберите ТОЛЬКО одного автора")
            return
        selected_item = self.authors_treeview.selection()[0]
        values = self.authors_treeview.item(selected_item)['values']

        id = int(values[0])
        name = values[1]
        birth_day = datetime.strptime(values[2], DATE_FORMAT) if values[2] else None

        author = Author(name, birth_day, id)
        EditAuthorWindow(self.parent, self.db, author)

    def edit_genre(self):
        selection = self.genres_treeview.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror("Ошибка", "Выберите ТОЛЬКО один жанр")
            return
        selected_item = selection[0]
        values = self.genres_treeview.item(selected_item)['values']

        id = int(values[0])
        name = values[1]

        genre = Genre(name, id)
        EditGenreWindow(self.parent, self.db, genre)

    def remove_book(self):
        selected_items = self.books_treeview.selection()
        if selected_items:
            for item in selected_items:
                book_id = self.books_treeview.item(item)['values'][0]
                self.db.book_repository.delete_by_id(book_id)
                self.books_treeview.delete(item)

    def remove_author(self):
        selected_items = self.authors_treeview.selection()
        if selected_items:
            action = messagebox.askyesno("Подтверждение", "Все связанные с автором книги будут также удалены")
            if action:
                for item in selected_items:
                    author_id = self.authors_treeview.item(item)['values'][0]
                    self.db.author_repository.delete_by_id(author_id)
                    self.authors_treeview.delete(item)
                self.books_treeview.update()

    def remove_genre(self):
        selected_items = self.genres_treeview.selection()
        if selected_items:
            action = messagebox.askyesno("Подтверждение", "Все связанные с жанром книги будут также удалены")
            if action:
                for item in selected_items:
                    genre_id = self.genres_treeview.item(item)['values'][0]
                    self.db.genre_repository.delete_by_id(genre_id)
                    self.genres_treeview.delete(item)
                self.books_treeview.update()

    def update_all_info(self):
        self.update_books_treeview()
        self.update_authors_treeview()
        self.update_genres_treeview()

    def update_books_treeview(self):
        self.books = self.db.book_repository.get_all()
        for item in self.books_treeview.get_children():
            self.books_treeview.delete(item)

        for book in self.books:
            id = book.id
            title = book.title
            author_name = book.author.name
            publication_year = book.publication_year if book.publication_year else ""
            genre_name = book.genre.name if book.genre else ""
            self.books_treeview.insert("", tk.END, values=(id, title, author_name, publication_year, genre_name))

    def update_authors_treeview(self):
        self.authors = self.db.author_repository.get_all()
        for item in self.authors_treeview.get_children():
            self.authors_treeview.delete(item)

        for author in self.authors:
            id = author.id
            name = author.name
            birth_date = author.birth_date.strftime(DATE_FORMAT) if author.birth_date else ""
            self.authors_treeview.insert("", tk.END, values=(id, name, birth_date))

    def update_genres_treeview(self):
        self.genres = self.db.genre_repository.get_all()
        for item in self.genres_treeview.get_children():
            self.genres_treeview.delete(item)

        for genre in self.genres:
            id = genre.id
            name = genre.name
            self.genres_treeview.insert("", tk.END, values=(id, name))
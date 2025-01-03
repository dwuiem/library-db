import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from entity import Book, Genre

class AddBookWindow:
    def __init__(self, parent: tk.Tk, db: Database):
        self.db = db
        self.parent = parent

        self.authors = self.db.author_repository.get_all()
        self.genres = self.db.genre_repository.get_all()

        self.authors_map = {
            author.name + (" | " + str(author.birth_date) if author.birth_date else ""): author
            for author in self.authors
        }

        self.genres_map = {
            genre.name: genre
            for genre in self.genres
        }

        self.window = tk.Toplevel(parent)
        self.window.title("Добавить книгу")
        self.window.transient(parent)
        self.window.grab_set()

        # Элементы интерфейса
        tk.Label(self.window, text="Название книги:").pack(padx=10, pady=5)
        self.title_entry = tk.Entry(self.window, width=50)
        self.title_entry.pack(padx=50, pady=5)

        tk.Label(self.window, text="Год издания:").pack(padx=10, pady=5)
        self.year_entry = tk.Entry(self.window, width=10)
        self.year_entry.pack(padx=50, pady=5)

        tk.Label(self.window, text="Автор:").pack(padx=10, pady=5)

        self.authors_combobox = ttk.Combobox(self.window, state="readonly", width=50)
        self.authors_combobox.pack(padx=50, pady=5)

        # Обновляем список авторов
        self.authors_combobox['values'] = list(self.authors_map.keys())

        # Жанр
        tk.Label(self.window, text="Жанр:").pack(padx=10, pady=5)
        self.genres_combobox = ttk.Combobox(self.window)
        self.genres_combobox.pack(padx=10, pady=5)

        self.genres_combobox['values'] = list(self.genres_map.keys())

        # Кнопка подтверждения
        confirm_button = tk.Button(self.window, text="Подтвердить", command=self.confirm_add_book)
        confirm_button.pack(padx=10, pady=10)

    def confirm_add_book(self):
        if not self.authors_combobox.get():
            messagebox.showerror("Ошибка", "Автор должен быть указан")
            return
        if not self.title_entry.get():
            messagebox.showerror("Ошибка", "Название книги должно быть непустым")
            return

        title = self.title_entry.get()
        publication_year = self.year_entry.get() if self.year_entry.get() else None

        if publication_year and not publication_year.isdigit():
            messagebox.showerror("Ошибка", "Год издания книги должен быть числом")
            return

        author = self.authors_map[self.authors_combobox.get()]

        genre = None
        genre_name = self.genres_combobox.get()
        if genre_name in self.genres_map:
            genre = self.genres_map[genre_name]
        elif genre_name:
            genre = Genre(genre_name)
            genre.id = self.db.genre_repository.save(genre)

        book = Book(title, author, publication_year, genre)
        try:
            self.db.book_repository.save(book)
        except ValueError:
            messagebox.showwarning("Ошибка", "Имя автора должно быть уникальным")
            return

        self.window.destroy()
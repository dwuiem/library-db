from typing import Optional, List

from psycopg2.extensions import connection as connection_type
from entity import Book, Genre, Author, Loan


class BookRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def clear_all(self):
        try:
            self.cursor.callproc('clear_books')
            self.connection.commit()

            print(f"All books were cleared")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while clearing all books {e}")

    def save(self, book: Book) -> int:
        try:
            self.cursor.callproc('save_book', (book.title, book.author.id, book.genre.id if book.genre else None, book.publication_year))
            book.id = self.cursor.fetchone()[0]

            self.connection.commit()
            print(f"Book '{book.title}' by author '{book.author.name}' saved with ID: {book.id}")

            return book.id
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving book: {e}")

    def get_all_available(self) -> Optional[List[Book]]:
        try:
            self.cursor.callproc('get_all_available_books')
            rows = self.cursor.fetchall()

            books_list = []
            for row in rows:
                author = Author(name=row[3], birth_date=row[4])
                genre = Genre(name=row[5]) if row[5] else None
                books_list.append(Book(id=row[0], title=row[1], publication_year=row[2], author=author, genre=genre))

            return books_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")

    def get_all(self) -> Optional[List[Book]]:
        try:
            self.cursor.callproc('get_all_books')
            rows = self.cursor.fetchall()

            books_list = []
            for row in rows:
                author = Author(name=row[3], birth_date=row[4])
                genre = Genre(name=row[5]) if row[5] else None
                books_list.append(Book(id=row[0], title=row[1], publication_year=row[2], author=author, genre=genre))

            return books_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")

    def update(self, book: Book):
        try:
            self.cursor.callproc('update_book', (book.id, book.title, book.author.id, book.genre.id if book.genre else None, book.publication_year))
            self.connection.commit()

            print(f"Book with ID {book.id} successfully updated")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating book with ID {book.id}: {e}")

    def return_by_id(self, book_id: int):
        try:
            self.cursor.callproc('return_book_by_id', (book_id,))
            self.connection.commit()

            print(f"Book with ID {book_id} returned back to library")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while returning book with ID {book_id}: {e}")

    def get_all_by_reader_id(self, reader_id: int) -> Optional[List[Book]]:
        try:
            self.cursor.callproc('get_books_by_reader_id', (reader_id,))
            data = self.cursor.fetchall()

            book_list = []
            for row in data:
                author = Author(name=row[2])
                genre = Genre(name=row[4]) if row[4] else None
                loan = Loan(id=row[5], return_date=row[6], loan_date=row[7], reader=None)
                book_list.append(Book(title=row[1], author=author, genre=genre, loan=loan, id=row[0]))

            return book_list

        except Exception as e:
            print(f"Error retrieving loaned books for reader {reader_id}: {e}")
            return None

    def delete_by_id(self, book_id: int):
        try:
            self.cursor.callproc('delete_book_by_id', (book_id,))
            self.connection.commit()
            print(f"Book with ID {book_id} successfully deleted")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting book with ID {book_id}: {e}")
            return False
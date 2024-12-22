from typing import Optional, List

from psycopg2.extensions import connection as connection_type
from entity import Book, Genre, Author, Loan


class BookRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def save(self, book: Book) -> int:
        try:
            insert_query = """
                INSERT INTO books (title, author_id, genre_id, publication_year) 
                VALUES (%s, %s, %s, %s) RETURNING id;
            """
            self.cursor.execute(insert_query, (book.title, book.author.id, book.genre.id if book.genre else None, book.publication_year))
            book_id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Book '{book.title}' by author '{book.author.name}' saved")
            return book_id
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving book: {e}")

    def get_all_available(self) -> Optional[List[Book]]:
        try:
            self.cursor.execute("""
                SELECT b.id, b.title, b.publication_year, a.name AS author_name, a.birth_date AS author_birth_date, g.name AS genre_name
                FROM books b
                JOIN authors a ON b.author_id = a.id
                LEFT OUTER JOIN genres g ON b.genre_id = g.id
                WHERE b.loan_id IS NULL;
            """)
            data = self.cursor.fetchall()

            books_list = []
            for row in data:
                author = Author(name=row[3], birth_date=row[4])
                genre = Genre(name=row[5]) if row[5] else None
                books_list.append(Book(id=row[0], title=row[1], publication_year=row[2], author=author, genre=genre))

            return books_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")

    def get_all(self) -> Optional[List[Book]]:
        try:
            self.cursor.execute("""
                SELECT b.id, b.title, b.publication_year, a.name AS author_name, a.birth_date AS author_birth_date, g.name
                FROM books b
                JOIN authors a ON b.author_id = a.id
                LEFT OUTER JOIN genres g ON b.genre_id = g.id;
            """)
            data = self.cursor.fetchall()

            books_list = []
            for row in data:
                author = Author(name=row[3], birth_date=row[4])
                genre = Genre(name=row[5]) if row[5] else None
                books_list.append(Book(id=row[0], title=row[1], publication_year=row[2], author=author, genre=genre))

            return books_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")

    def update(self, book: Book):
        try:
            update_query = """
                UPDATE books
                SET
                    title = %s,
                    author_id = %s,
                    genre_id = %s,
                    publication_year = %s
                WHERE id = %s;
            """
            self.cursor.execute(update_query, (book.title, book.author.id, book.genre.id if book.genre else None, book.publication_year, book.id))
            self.connection.commit()

            print(f"Book with ID {book.id} successfully updated")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating book with ID {book.id}: {e}")

    def return_by_id(self, book_id: int):
        try:
            update_query = """
                UPDATE books SET loan_id = NULL WHERE id = %s
            """

            self.cursor.execute(update_query, (book_id,))
            self.connection.commit()

            print(f"Book with ID {book_id} returned back to library")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while returning book with ID {book_id}: {e}")

    def get_all_by_reader_id(self, reader_id: int) -> Optional[List[Book]]:
        try:
            query = """
                    SELECT b.id, b.title, a.name, a.birth_date, g.name, l.id, l.return_date, l.loan_date
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    LEFT OUTER JOIN genres g ON b.genre_id = g.id
                    JOIN loans l ON b.loan_id = l.id
                    WHERE l.reader_id = %s
            """
            self.cursor.execute(query, (reader_id,))
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
            delete_query = "DELETE FROM books WHERE id = %s;"
            self.cursor.execute(delete_query, (book_id,))
            self.connection.commit()
            print(f"Book with ID {book_id} successfully deleted")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting book with ID {book_id}: {e}")
            return False
import datetime
from typing import Optional, List

import psycopg2
from psycopg2.extensions import connection as connection_type
from entity import Author

class AuthorRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def save(self, author: Author) -> int:
        try:
            self.cursor.callproc('save_author', (author.name, author.birth_date))
            author.id = self.cursor.fetchone()[0]

            self.connection.commit()

            print(f"Author '{author.name}' saved with ID {author.id}")
            return author.id
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving author: {e}")

    def get_by_name(self, name: str) -> Optional[Author]:
        try:
            self.cursor.callproc('get_author_by_name', (name,))
            author_row = self.cursor.fetchone()

            if author_row:
                return Author(id=author_row[0], name=author_row[1], birth_date=author_row[2])
            else:
                print(f"Author '{name}' not found")
                return None
        except Exception as e:
            print(f"Error while retrieving author: {e}")
            return None

    def get_all(self) -> Optional[List[Author]]:
        try:
            self.cursor.callproc('get_all_authors')
            authors = self.cursor.fetchall()

            if not authors:
                return []

            return [
                Author(id=author[0], name=author[1],
                       birth_date=author[2] if author[2] else None)
                for author in authors
            ]
        except Exception as e:
            print(f"Error while retrieving authors: {e}")
            return None

    def update(self, author: Author):
        try:
            self.cursor.callproc('update_author', (author.id, author.name, author.birth_date))
            self.connection.commit()

            print(f"Author with ID {author.id} successfully updated")
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating author with ID {author.id}: {e}")

    def delete_by_id(self, author_id: int):
        try:
            self.cursor.callproc('delete_author_by_id', (author_id,))
            self.connection.commit()
            print(f"Author with ID {author_id} successfully deleted")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting author with ID {author_id}: {e}")
            return False
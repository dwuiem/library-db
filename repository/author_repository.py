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
            if author.birth_date:
                birth_date = author.birth_date
            else:
                birth_date = None

            insert_query = """
                INSERT INTO authors (name, birth_date) 
                VALUES (%s, %s) RETURNING id;
            """
            self.cursor.execute(insert_query, (author.name, birth_date))
            author.id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Author '{author.name}' saved")
            return author.id
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving author: {e}")

    def get_by_name(self, name: str) -> Optional[Author]:
        try:
            self.cursor.execute("SELECT id, name, birth_date FROM authors WHERE name = %s;", (name,))
            author = self.cursor.fetchone()

            if author:
                return Author(id=author[0], name=author[1], birth_date=author[2])
            else:
                print(f"Author '{name}' not found")
                return None
        except Exception as e:
            print(f"Error while retrieving author: {e}")
            return None

    def get_all(self) -> Optional[List[Author]]:
        try:
            self.cursor.execute("SELECT id, name, birth_date FROM authors;")
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
            update_query = """
                UPDATE authors
                SET
                    name = %s,
                    birth_date = %s
                WHERE id = %s;
            """
            self.cursor.execute(update_query, (author.name, author.birth_date, author.id))
            self.connection.commit()

            print(f"Author with ID {author.id} successfully updated")
            return True
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating author with ID {author.id}: {e}")
            return False

    def delete_by_id(self, author_id: int):
        try:
            delete_query = "DELETE FROM authors WHERE id = %s;"
            self.cursor.execute(delete_query, (author_id,))
            self.connection.commit()
            print(f"Author with ID {author_id} successfully deleted")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting author with ID {author_id}: {e}")
            return False
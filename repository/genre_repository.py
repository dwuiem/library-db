from typing import Optional, List

import psycopg2
from psycopg2.extensions import connection as connection_type
from entity import Genre

class GenreRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def save(self, genre: Genre) -> int:
        try:
            insert_query = """
                INSERT INTO genres (name) 
                VALUES (%s) RETURNING id;
            """
            self.cursor.execute(insert_query, (genre.name,))
            genre.id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Genre '{genre.name}' saved with ID {genre.id}")
            return genre.id
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving genre: {e}")

    def get_by_name(self, name: str) -> Optional[Genre]:
        try:
            self.cursor.execute("SELECT id, name FROM genres WHERE name = %s;", (name,))
            genre = self.cursor.fetchone()

            if genre:
                return Genre(id=genre[0], name=genre[1])
            else:
                print(f"Genre '{name}' not found")
                return None
        except Exception as e:
            print(f"Error while retrieving genre: {e}")
            return None

    def get_all(self) -> Optional[List[Genre]]:
        try:
            self.cursor.execute("SELECT id, name FROM genres;")
            genres = self.cursor.fetchall()

            if not genres:
                return []

            return [Genre(id=genre[0], name=genre[1]) for genre in genres]
        except Exception as e:
            print(f"Error while retrieving genres: {e}")
            return None

    def update(self, genre: Genre):
        try:
            update_query = """
                UPDATE genres
                SET
                    name = %s
                WHERE id = %s;
            """
            self.cursor.execute(update_query, (genre.name, genre.id))
            self.connection.commit()

            print(f"Genre with ID {genre.id} successfully updated")
            return True
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating genre with ID {genre.id}: {e}")
            return False

    def delete_by_id(self, genre_id: int):
        try:
            delete_query = "DELETE FROM genres WHERE id = %s;"
            self.cursor.execute(delete_query, (genre_id,))
            self.connection.commit()
            print(f"Genre with ID {genre_id} successfully deleted")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting genre with ID {genre_id}: {e}")
            return False
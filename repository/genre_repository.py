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
            self.cursor.callproc('save_genre', (genre.name,))
            genre.id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Genre '{genre.name}' saved with ID {genre.id}")
            return genre.id
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving genre: {e}")

    def get_by_book_id(self, book_id: int) -> Optional[Genre]:
        try:
            self.cursor.callproc('get_genre_by_book_id', (book_id,))
            genre = self.cursor.fetchone()

            if genre:
                return Genre(id=genre[0], name=genre[1])
            else:
                return None
        except Exception as e:
            print(f"Error while retrieving genre by book id: {e}")
            return None

    def get_all(self) -> Optional[List[Genre]]:
        try:
            self.cursor.callproc('get_all_genres')
            genres = self.cursor.fetchall()

            if not genres:
                return []

            return [Genre(id=genre[0], name=genre[1]) for genre in genres]
        except Exception as e:
            print(f"Error while retrieving genres: {e}")
            return None

    def update(self, genre: Genre):
        try:
            self.cursor.callproc('update_genre', (genre.id, genre.name))
            self.connection.commit()

            print(f"Genre with ID {genre.id} successfully updated")
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating genre with ID {genre.id}: {e}")

    def delete_by_id(self, genre_id: int):
        try:
            self.cursor.callproc('delete_genre_by_id', (genre_id,))
            self.connection.commit()

            print(f"Genre with ID {genre_id} successfully deleted")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while deleting genre with ID {genre_id}: {e}")
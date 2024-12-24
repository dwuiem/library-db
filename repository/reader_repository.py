from typing import Optional, List

import psycopg2
from psycopg2.extensions import connection as connection_type
from entity import Reader


class ReaderRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def save(self, reader: Reader) -> int:
        try:
            self.cursor.callproc('save_reader', (reader.name, reader.email if reader.email else None, reader.phone))
            reader_id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Reader {reader.name} was saved")
            return reader_id
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while saving reader: {e}")

    def get_by_name(self, name: str) -> Optional[Reader]:
        try:
            self.cursor.callproc('get_reader_by_name', (name,))
            reader_row = self.cursor.fetchone()
            if reader_row:
                return Reader(reader_row[1], reader_row[2], reader_row[3], reader_row[0])
            else:
                return None
        except Exception as e:
            print(f"Error while retrieving readers: {e}")

    def get_all(self) -> Optional[List[Reader]]:
        try:
            self.cursor.callproc('get_all_readers')
            rows = self.cursor.fetchall()

            readers_list = []
            for row in rows:
                readers_list.append(Reader(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    phone=row[3]
                ))
            return readers_list
        except Exception as e:
            print(f"Error while retrieving readers: {e}")

    def update(self, reader: Reader):
        try:
            self.cursor.callproc('update_reader', (reader.id, reader.name, reader.email, reader.phone))
            self.connection.commit()

            print(f"Reader {reader.name} was updated")
        except psycopg2.IntegrityError:
            raise ValueError
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating reader with ID {reader.id}: {e}")

    def delete_by_id(self, reader_id: int):
        try:
            self.cursor.callproc('delete_reader_by_id', (reader_id,))
            self.connection.commit()

            print(f"Reader with ID {reader_id} was removed")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating reader with ID {reader_id}: {e}")

    def delete_by_name(self, reader_name: str):
        try:
            self.cursor.callproc('delete_reader_by_name', (reader_name,))
            self.connection.commit()

            print(f"Reader with Name {reader_name} was removed")
        except Exception as e:
            self.connection.rollback()
            print(f"Error while updating reader with Name {reader_name}: {e}")
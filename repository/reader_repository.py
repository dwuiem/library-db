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
            insert_query = """
                INSERT INTO readers (name, email, phone)
                VALUES (%s, %s, %s) RETURNING id;
            """

            self.cursor.execute(insert_query, (reader.name, reader.email if reader.email else None, reader.phone))
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
            self.cursor.execute("""
                SELECT id, name, email, phone FROM readers WHERE name = %s
            """, (name,))
            reader_row = self.cursor.fetchone()
            if reader_row:
                return Reader(reader_row[1], reader_row[2], reader_row[3], reader_row[0])
            else:
                return None
        except Exception as e:
            print(f"Error while retrieving readers: {e}")

    def get_all(self) -> Optional[List[Reader]]:
        try:
            self.cursor.execute("""
                SELECT id, name, email, phone FROM readers
            """)
            data = self.cursor.fetchall()

            readers_list = []
            for row in data:
                readers_list.append(Reader(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    phone=row[3],
                ))
            return readers_list
        except Exception as e:
            print(f"Error while retrieving readers: {e}")
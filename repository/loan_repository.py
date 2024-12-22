from psycopg2.extensions import connection as connection_type
from datetime import datetime, date

from typing import List, Optional

from entity import Loan, Reader, Book


class LoanRepository:
    def __init__(self, connection: connection_type):
        self.connection = connection
        self.cursor = connection.cursor()

    def get_all(self) -> List[Loan]:
        try:
            self.cursor.execute("""
                SELECT l.id, r.id, r.name, r.email, r.phone, l.return_date, l.loan_date
                FROM loans l
                JOIN readers r ON r.id = l.reader_id
            """)
            data = self.cursor.fetchall()

            loans_list = []
            for row in data:
                reader = Reader(row[2], row[3], row[4], row[1])
                loans_list.append(Loan(reader, row[5], row[6], row[0]))
            return loans_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")


    def lend_book(self, reader_id: int, book_ids: List[int], return_date: date) -> int:
        try:
            self.cursor.execute(
                """
                INSERT INTO loans (reader_id, return_date)
                VALUES (%s, %s)
                RETURNING id;
                """, (reader_id, return_date)
            )
            loan_id = self.cursor.fetchone()[0]

            for book_id in book_ids:
                self.cursor.execute(
                    """
                    UPDATE books SET loan_id = %s
                    WHERE id = %s;
                    """, (loan_id, book_id)
                )
            self.connection.commit()
            return loan_id
        except Exception as e:
            self.connection.rollback()
            print(f"Error while lending books: {e}")
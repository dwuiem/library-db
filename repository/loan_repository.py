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
            self.cursor.callproc('get_all_loans')
            rows = self.cursor.fetchall()

            loans_list = []
            for row in rows:
                reader = Reader(row[2], row[3], row[4], row[1])
                loans_list.append(Loan(reader, row[5], row[6], row[0]))
            return loans_list
        except Exception as e:
            print(f"Error while retrieving books: {e}")


    def lend_book(self, reader_id: int, book_ids: List[int], return_date: date) -> int:
        try:
            self.cursor.callproc('lend_books', (reader_id, book_ids, return_date))
            loan_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return loan_id
        except Exception as e:
            self.connection.rollback()
            print(f"Error while lending books: {e}")
from typing import Optional
from datetime import date, datetime

from utils import DATE_FORMAT


class Genre:
    def __init__(self, name: str, id: Optional[int] = None):
        self.id = id
        self.name = name

class Author:
    def __init__(self, name: str, birth_date: Optional[date] = None, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.birth_date = birth_date

    def get_info(self):
        return self.name + (" | " + str(self.birth_date.strftime(DATE_FORMAT)) if self.birth_date else "")

class Reader:
    def __init__(self, name: str, email: Optional[str], phone: str, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

class Loan:
    def __init__(self, reader: Optional[Reader], return_date: Optional[datetime], loan_date: Optional[datetime] = datetime.now(), id: Optional[int] = None):
        self.id = id
        self.reader = reader
        self.return_date = return_date
        self.loan_date = loan_date

class Book:
    def __init__(self, title: str, author: Author, publication_year: Optional[int] = None, genre: Optional[Genre] = None, loan: Optional[Loan] = None, id: Optional[int] = None):
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.genre = genre
        self.loan = loan
        self.id = id
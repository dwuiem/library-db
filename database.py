import psycopg2
from psycopg2 import sql

from repository.author_repository import AuthorRepository
from repository.book_repository import BookRepository
from repository.genre_repository import GenreRepository
from repository.loan_repository import LoanRepository
from repository.reader_repository import ReaderRepository

class Database:
    def __init__(self, db_name: str, user: str, password: str, host: str, port: str):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        try:
            connection = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                [self.db_name]
            )

            if cursor.fetchone() is None:
                # Если базы данных нет, создаем её
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(self.db_name),
                        sql.Identifier(self.user)
                    )
                )
                print(f"Database '{self.db_name}' created successfully.")
            else:
                print(f"Database '{self.db_name}' already exists.")
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Error creating db: {e}")
        try:
            self.connection = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to the database {db_name}")
        except Exception as e:
            print(f"Error connection to db: {e}")
            return

        self.book_repository = BookRepository(self.connection)
        self.author_repository = AuthorRepository(self.connection)
        self.reader_repository = ReaderRepository(self.connection)
        self.genre_repository = GenreRepository(self.connection)
        self.loan_repository = LoanRepository(self.connection)

        self.init_database()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def init_database(self):
        try:
            with open("sql_scripts/init_db.sql", "r") as file:
                script = file.read()
                file.close()
            self.cursor.execute(script)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error while database initialization: {e}")
        print("Database initialized")

    def clear_all_tables(self):
        try:
            self.cursor.callproc('clear_all_tables')
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error while clearing all tables: {e}")
        print("All tables were cleared")
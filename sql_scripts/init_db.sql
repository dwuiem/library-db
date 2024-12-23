-- Создание таблиц

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birth_date DATE
);

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS readers (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    phone TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    reader_id INT NOT NULL,
    loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    return_date TIMESTAMP NOT NULL,
    book_count INT,
    FOREIGN KEY (reader_id) REFERENCES readers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INT NOT NULL,
    genre_id INT,
    publication_year INT,
    loan_id INT DEFAULT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans (id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE CASCADE
);

-- Очистка всех таблиц

CREATE OR REPLACE FUNCTION clear_all_tables()
RETURNS VOID AS
$$
BEGIN
    DELETE FROM loans;
    DELETE FROM books;
    DELETE FROM readers;
    DELETE FROM genres;
    DELETE FROM authors;
END;
$$ LANGUAGE plpgsql;

-- Очистка всех книг

CREATE OR REPLACE FUNCTION clear_books()
RETURNS VOID AS
$$
BEGIN
    DELETE FROM books;
END;
$$ LANGUAGE plpgsql;

-- Индекс для ускорения запроса поиска по имени

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_readers_name'
    ) THEN
        CREATE INDEX idx_readers_name ON readers(name);
    END IF;
END $$;

-- Если займ будет удалён, то остальные книги останутся незанятыми

CREATE OR REPLACE FUNCTION update_books_on_loan_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE books
    SET loan_id = NULL
    WHERE loan_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_books_on_loan_delete
AFTER DELETE ON loans
FOR EACH ROW
EXECUTE FUNCTION update_books_on_loan_delete();

-- Создание функции триггера

CREATE OR REPLACE FUNCTION update_book_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновление поля book_count при добавлении книги в займ
    IF (TG_OP = 'UPDATE') THEN
        UPDATE loans
        SET book_count = (SELECT COUNT(*) FROM books WHERE loan_id = NEW.loan_id)
        WHERE id = NEW.loan_id;
    -- Обновление поля book_count при удалении книги из займа
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE loans
        SET book_count = (SELECT COUNT(*) FROM books WHERE loan_id = OLD.loan_id)
        WHERE id = OLD.loan_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера для таблицы books
CREATE OR REPLACE TRIGGER book_count_trigger
AFTER UPDATE OR DELETE ON books
FOR EACH ROW
EXECUTE FUNCTION update_book_count();

-- Удалять займы в которых не осталось книг, которые не вернули

CREATE OR REPLACE FUNCTION delete_unused_loans()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM books
        WHERE loan_id = OLD.loan_id
    ) THEN
        DELETE FROM loans WHERE id = OLD.loan_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER check_and_delete_loans
AFTER UPDATE OF loan_id OR DELETE
ON books
FOR EACH ROW
EXECUTE FUNCTION delete_unused_loans();

-- ----------------
-- Author functions
-- ----------------

CREATE OR REPLACE FUNCTION save_author(author_name TEXT, author_birth_date DATE)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO authors (name, birth_date)
    VALUES (author_name, author_birth_date)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_author_by_book_id(book_id INT)
RETURNS TABLE(id INT, name TEXT, birth_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT authors.id, authors.name, authors.birth_date
    FROM books
    JOIN authors ON books.author_id = authors.id
    WHERE books.id = book_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_authors()
RETURNS TABLE(id INT, name TEXT, birth_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT authors.id, authors.name, authors.birth_date
    FROM authors;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_author(author_id INT, author_name TEXT, author_birth_date DATE)
RETURNS VOID AS $$
BEGIN
    UPDATE authors
    SET name = author_name, birth_date = author_birth_date
    WHERE authors.id = author_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_author_by_id(author_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM authors WHERE authors.id = author_id;
END;
$$ LANGUAGE plpgsql;

-- --------------
-- Book functions
-- --------------

CREATE OR REPLACE FUNCTION save_book(book_title TEXT, book_author_id INT, book_genre_id INT, book_publication_year INT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO books (title, author_id, genre_id, publication_year)
    VALUES (book_title, book_author_id, book_genre_id, book_publication_year)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_available_books()
RETURNS TABLE(id INT, title TEXT, publication_year INT, author_name TEXT, author_birth_date DATE, genre_name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT b.id, b.title, b.publication_year, a.name, a.birth_date, g.name
    FROM books b
    JOIN authors a ON b.author_id = a.id
    LEFT OUTER JOIN genres g ON b.genre_id = g.id
    WHERE b.loan_id IS NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_books()
RETURNS TABLE(id INT, title TEXT, publication_year INT, author_name TEXT, author_birth_date DATE, genre_name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT b.id, b.title, b.publication_year, a.name, a.birth_date, g.name
    FROM books b
    JOIN authors a ON b.author_id = a.id
    LEFT OUTER JOIN genres g ON b.genre_id = g.id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_book(book_id INT, book_title TEXT, book_author_id INT, book_genre_id INT, book_publication_year INT)
RETURNS VOID AS $$
BEGIN
    UPDATE books
    SET title = book_title, author_id = book_author_id, genre_id = book_genre_id, publication_year = book_publication_year
    WHERE books.id = book_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION return_book_by_id(book_id INT)
RETURNS VOID AS $$
BEGIN
    UPDATE books
    SET loan_id = NULL
    WHERE books.id = book_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_books_by_reader_id(target_reader_id INT)
RETURNS TABLE (
    book_id INT,
    book_title TEXT,
    author_name TEXT,
    author_birth_date DATE,
    genre_name TEXT,
    loan_id INT,
    loan_return_date TIMESTAMP,
    loan_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.id,
        b.title,
        a.name,
        a.birth_date,
        g.name,
        l.id,
        l.return_date,
        l.loan_date
    FROM books b
    JOIN authors a ON b.author_id = a.id
    LEFT OUTER JOIN genres g ON b.genre_id = g.id
    JOIN loans l ON b.loan_id = l.id
    WHERE l.reader_id = target_reader_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_book_by_id(book_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM books WHERE books.id = book_id;
END;
$$ LANGUAGE plpgsql;

-- ---------------
-- Genre functions
-- ---------------

CREATE OR REPLACE FUNCTION save_genre(genre_name TEXT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO genres (name)
    VALUES (genre_name)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_genre_by_book_id(book_id INT)
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT genres.id, genres.name
    FROM books
    JOIN genres ON books.genre_id = genres.id
    WHERE books.id = book_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_genres()
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT genres.id, genres.name
    FROM genres;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_genre(genre_id INT, genre_name TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE genres
    SET name = genre_name
    WHERE genres.id = genre_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_genre_by_id(genre_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM genres WHERE genres.id = genre_id;
END;
$$ LANGUAGE plpgsql;

-- ----------------
-- Reader functions
-- ----------------

CREATE OR REPLACE FUNCTION save_reader(reader_name TEXT, reader_email TEXT, reader_phone TEXT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO readers (name, email, phone)
    VALUES (reader_name, reader_email, reader_phone)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_reader_by_name(reader_name TEXT)
RETURNS TABLE(id INT, name TEXT, email TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT readers.id, readers.name, readers.email, readers.phone
    FROM readers
    WHERE readers.name = reader_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_readers()
RETURNS TABLE(id INT, name TEXT, email TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT readers.id, readers.name, readers.email, readers.phone
    FROM readers;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_reader(reader_id INT, reader_name TEXT, reader_email TEXT, reader_phone TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE readers
    SET name = reader_name, email = reader_email, phone = reader_phone
    WHERE readers.id = reader_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_reader_by_id(reader_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM readers WHERE id = reader_id;
END;
$$ LANGUAGE plpgsql;

-- --------------
-- Loan functions
-- --------------

CREATE OR REPLACE FUNCTION get_all_loans()
RETURNS TABLE (
    loan_id INT,
    reader_id INT,
    reader_name TEXT,
    reader_email TEXT,
    reader_phone TEXT,
    return_date TIMESTAMP,
    loan_date TIMESTAMP,
    book_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id, r.id, r.name, r.email, r.phone, l.return_date, l.loan_date, l.book_count
    FROM loans l
    JOIN readers r ON r.id = l.reader_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION lend_books(loan_reader_id INT, book_ids INT[], loan_return_date TIMESTAMP)
RETURNS INT AS $$
DECLARE
    new_loan_id INT;
BEGIN
    INSERT INTO loans (reader_id, return_date)
    VALUES (loan_reader_id, loan_return_date)
    RETURNING id INTO new_loan_id;

    UPDATE books
    SET loan_id = new_loan_id
    WHERE books.id = ANY(book_ids);

    RETURN new_loan_id;
END;
$$ LANGUAGE plpgsql;

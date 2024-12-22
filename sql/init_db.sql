CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birth_date DATE
);
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
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
    FOREIGN KEY (reader_id) REFERENCES readers(id) ON DELETE CASCADE
);

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


-- Author table
CREATE OR REPLACE FUNCTION save_author(name TEXT, birth_date DATE)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO authors (name, birth_date)
    VALUES (name, birth_date)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_author_by_name(author_name TEXT)
RETURNS TABLE(id INT, name TEXT, birth_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, birth_date
    FROM authors
    WHERE name = author_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_authors()
RETURNS TABLE(id INT, name TEXT, birth_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, birth_date
    FROM authors;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_author(id INT, name TEXT, birth_date DATE)
RETURNS VOID AS $$
BEGIN
    UPDATE authors
    SET name = name, birth_date = birth_date
    WHERE id = id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_author_by_id(author_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM authors WHERE id = author_id;
END;
$$ LANGUAGE plpgsql;

-- Book functions

CREATE OR REPLACE FUNCTION save_book(title TEXT, author_id INT, genre_id INT, publication_year INT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO books (title, author_id, genre_id, publication_year)
    VALUES (title, author_id, genre_id, publication_year)
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

CREATE OR REPLACE FUNCTION update_book(id INT, title TEXT, author_id INT, genre_id INT, publication_year INT)
RETURNS VOID AS $$
BEGIN
    UPDATE books
    SET title = title, author_id = author_id, genre_id = genre_id, publication_year = publication_year
    WHERE id = id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_book_by_id(book_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM books WHERE id = book_id;
END;
$$ LANGUAGE plpgsql;

-- Genre functions

CREATE OR REPLACE FUNCTION save_genre(name TEXT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO genres (name)
    VALUES (name)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_genre_by_name(name TEXT)
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name
    FROM genres
    WHERE name = name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_genres()
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name
    FROM genres;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_genre(id INT, name TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE genres
    SET name = name
    WHERE id = id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_genre_by_id(genre_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM genres WHERE id = genre_id;
END;
$$ LANGUAGE plpgsql;

-- Reader functions

CREATE OR REPLACE FUNCTION save_reader(name TEXT)
RETURNS INT AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO readers (name)
    VALUES (name)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_reader_by_name(name TEXT)
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name
    FROM readers
    WHERE name = name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_readers()
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name
    FROM readers;
END;
$$ LANGUAGE plpgsql;

-- ДОРАБОТАТЬ ПАРАМЕТРЫ
--CREATE OR REPLACE FUNCTION update_reader(id INT, name TEXT)
--RETURNS VOID AS $$
--BEGIN
--    UPDATE readers
--    SET name = name
--    WHERE id = id;
--END;
--$$ LANGUAGE plpgsql;

--CREATE OR REPLACE FUNCTION delete_reader_by_id(reader_id INT)
--RETURNS VOID AS $$
--BEGIN
--    DELETE FROM readers WHERE id = reader_id;
--END;
--$$ LANGUAGE plpgsql;

-- Loan functions

CREATE OR REPLACE FUNCTION get_all_loans()
RETURNS TABLE (
    loan_id INT,
    reader_id INT,
    reader_name TEXT,
    reader_email TEXT,
    reader_phone TEXT,
    return_date DATE,
    loan_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id, r.id, r.name, r.email, r.phone, l.return_date, l.loan_date
    FROM loans l
    JOIN readers r ON r.id = l.reader_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION lend_books(reader_id INT, book_ids INT[], return_date DATE)
RETURNS INT AS $$
DECLARE
    loan_id INT;
BEGIN
    INSERT INTO loans (reader_id, return_date)
    VALUES (reader_id, return_date)
    RETURNING id INTO loan_id;

    UPDATE books
    SET loan_id = loan_id
    WHERE id = ANY(book_ids);

    RETURN loan_id;
END;
$$ LANGUAGE plpgsql;

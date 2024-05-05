import psycopg

user = """
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    joined_date DATE NOT NULL
);
"""

books = """
CREATE TABLE books (
    book_id VARCHAR(13) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    publication_date VARCHAR(255),
    description TEXT,
    cover_image_url VARCHAR(255)
);
"""

read = """
CREATE TABLE readList (
    read_list_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    book_id VARCHAR NOT NULL REFERENCES Books(book_id),
    read_date DATE NOT NULL
);
"""

toRead = """
CREATE TABLE toReadList (
    to_read_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    book_id VARCHAR NOT NULL REFERENCES Books(book_id),
    added_date DATE NOT NULL
);
"""

reviews = """
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    book_id VARCHAR NOT NULL REFERENCES Books(book_id),
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL,
    review_date DATE NOT NULL
);
"""

def get_connection():
    return psycopg.connect(
        dbname="Books",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

def create_tables(connection):
    try:
        with connection.cursor() as crsr:
            crsr.execute(user)
            crsr.execute(books)
            crsr.execute(read)
            crsr.execute(toRead)
            crsr.execute(reviews)
        connection.commit()
        print("created tables")
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

def drop_tables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS toReadList CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS readList CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS reviews CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS books CASCADE;")
        connection.commit()
        print("dropped tables")
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()


def main():
    conn = get_connection()

    #drop_tables(conn)
    create_tables(conn)
    conn.close()


if __name__ == "__main__":
    main()
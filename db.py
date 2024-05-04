import psycopg
import requests

def create_tables(conn):
    with conn.cursor() as cur:
        # Create the users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL
            );
        """)

        # Create the books_read table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books_read (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publish_date TEXT,
                genre TEXT[]
            );
        """)
        conn.commit()

def get_or_create_user(conn, username):
    with conn.cursor() as cur:
        # Check if the user exists
        cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()

        if user:
            user_id = user[0]
        else:
            # Insert a new user
            cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id;", (username,))
            user_id = cur.fetchone()[0]
            conn.commit()

    return user_id

def add_book(conn, user_id, title, author, publish_date, genres):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO books_read (user_id, title, author, publish_date, genre)
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, title, author, publish_date, genres))
        conn.commit()
    print(f"Book '{title}' added to your reading list.")

def get_book_details(book_name):
    api_key = "AIzaSyCkpmRc2m9bY_zOWtTRgNho-KTBDVx9fIs"
    url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["totalItems"] > 0:
            book_info = data["items"][0]["volumeInfo"]
            author = ", ".join(book_info.get("authors", ["Unknown Author"]))
            publish_date = book_info.get("publishedDate", "Unknown")
            categories = book_info.get("categories", ["Unknown"])
            return author, publish_date, categories
        else:
            return None, None, None
    else:
        print(f"Error: {response.status_code}")
        return None, None, None

def search_books(query):
    api_key = "AIzaSyCkpmRc2m9bY_zOWtTRgNho-KTBDVx9fIs"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        books = []
        for item in data["items"]:
            book_info = item["volumeInfo"]
            title = book_info.get("title", "Unknown Title")
            authors = ", ".join(book_info.get("authors", ["Unknown Author"]))
            books.append(f"{title} by {authors}")
        return books
    else:
        print(f"Error: {response.status_code}")
        return []

conn = psycopg.connect(
        dbname="Books",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

create_tables(conn)

username = input("Enter your username: ")

user_id = get_or_create_user(conn, username)

while True:
    user_input = input("Enter the book name (or 'q' to quit): ")
    if user_input.lower() == 'q':
        break

    book_results = search_books(user_input)

    if book_results:
        print("Select the book you want from the following options:")
        for i, book in enumerate(book_results, start=1):
            print(f"{i}. {book}")

        choice = int(input("Enter the number of your choice: "))
        if 1 <= choice <= len(book_results):
            selected_book = book_results[choice - 1].split(" by ")[0]
            author, publish_date, genres = get_book_details(selected_book)
            if author and publish_date and genres:
                add_book(conn, user_id, selected_book, author, publish_date, genres)
            else:
                print("No book details found.")
        else:
            print("Invalid choice.")
    else:
        print("No books found.")

conn.close()
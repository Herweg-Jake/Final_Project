import requests
import psycopg
from datetime import date

def get_connection():
    return psycopg.connect(
        dbname="Books",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

def get_or_create_user(conn, username):
    with conn.cursor() as crsr:
        crsr.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
        user = crsr.fetchone()
        if user:
            user_id = user[0]
        else:
            crsr.execute("INSERT INTO users (username, joined_date) VALUES (%s, CURRENT_DATE) RETURNING user_id;", (username,))
            user_id = crsr.fetchone()[0]
            conn.commit()
    return user_id

def add_book_to_read_list(conn, user_id, book_info):
    title = book_info["volumeInfo"]["title"]
    author = ", ".join(book_info["volumeInfo"].get("authors", ["Unknown Author"]))
    publish_date = book_info["volumeInfo"].get("publishedDate", "Unknown")
    genres = book_info["volumeInfo"].get("categories", ["Unknown"])
    isbn_13 = book_info["volumeInfo"].get("industryIdentifiers", [{"type": "ISBN_13", "identifier": ""}])[0].get("identifier", "")

    with conn.cursor() as crsr:
        crsr.execute("SELECT book_id FROM books WHERE book_id = %s;", (isbn_13,))
        book = crsr.fetchone()
        if book:
            book_id = book[0]
        else:
            crsr.execute("INSERT INTO books (book_id, title, author, publication_date, description) VALUES (%s, %s, %s, %s, %s);", (isbn_13, title, author, publish_date, ", ".join(genres)))
            conn.commit()

        crsr.execute("INSERT INTO readList (user_id, book_id, read_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, isbn_13))
        conn.commit()
        print(f"Book '{title}' added to your reading list.")

def add_book_to_to_read_list(conn, user_id, book_info):
    title = book_info["volumeInfo"]["title"]
    author = ", ".join(book_info["volumeInfo"].get("authors", ["Unknown Author"]))
    publish_date = book_info["volumeInfo"].get("publishedDate", "Unknown")
    genres = book_info["volumeInfo"].get("categories", ["Unknown"])
    isbn_13 = book_info["volumeInfo"].get("industryIdentifiers", [{"type": "ISBN_13", "identifier": ""}])[0].get("identifier", "")

    with conn.cursor() as crsr:
        crsr.execute("SELECT book_id FROM books WHERE book_id = %s;", (isbn_13,))
        book = crsr.fetchone()
        if book:
            book_id = book[0]
        else:
            crsr.execute("INSERT INTO books (book_id, title, author, publication_date, description) VALUES (%s, %s, %s, %s, %s);", (isbn_13, title, author, publish_date, ", ".join(genres)))
            conn.commit()

        crsr.execute("INSERT INTO toReadList (user_id, book_id, added_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, isbn_13))
        conn.commit()
        print(f"Book '{title}' added to your to-read list.")

def get_book_details(book_name):
    api_key = "AIzaSyCkpmRc2m9bY_zOWtTRgNho-KTBDVx9fIs"
    url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["totalItems"] > 0:
            book_info = data["items"][0]
            return book_info
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

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
            books.append({"title": title, "authors": authors, "info": item})
        return books
    else:
        print(f"Error: {response.status_code}")
        return []

def return_book_details():
    book_name = input("Enter the book name: ")
    book_results = search_books(book_name)

    if book_results:
        print("Select the book you want from the following options:")
        for i, book in enumerate(book_results, start=1):
            print(f"{i}. {book['title']} by {book['authors']}")

        choice = int(input("Enter the number of your choice: "))
        if 1 <= choice <= len(book_results):
            selected_book = book_results[choice - 1]["info"]
            title = selected_book["volumeInfo"]["title"]
            author = ", ".join(selected_book["volumeInfo"].get("authors", ["Unknown Author"]))
            publish_date = selected_book["volumeInfo"].get("publishedDate", "Unknown")
            genres = selected_book["volumeInfo"].get("categories", ["Unknown"])
            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Published Date: {publish_date}")
            print(f"Genres: {', '.join(genres)}")
        else:
            print("Invalid choice.")
    else:
        print("No book details found.")

def view_book_list():
    choice = input("Enter a number of list to view:\n1. Read List\n2. To Read List\n3. Personal Book Reviews")
    
    if choice == '1':
        pass
    elif choice == '2':
        pass
    else:
        print("invalid option")

def user_add_book(conn, user_id):
    book_name = input("Enter the book name: ")
    book_results = search_books(book_name)

    if book_results:
        print("Select the book you want from the following options:")
        for i, book in enumerate(book_results, start=1):
            print(f"{i}. {book['title']} by {book['authors']}")

        choice = int(input("Enter the number of your choice: "))
        if 1 <= choice <= len(book_results):
            selected_book = book_results[choice - 1]["info"]
            list_choice = input("Enter 'r' to add to read list or 't' to add to to-read list: ")
            if list_choice.lower() == 'r':
                add_book_to_read_list(conn, user_id, selected_book)
            elif list_choice.lower() == 't':
                add_book_to_to_read_list(conn, user_id, selected_book)
            else:
                print("Invalid choice.")
        else:
            print("Invalid choice.")
    else:
        print("No books found.")

def main():
    conn = get_connection()
    print("Welcome to your digital bookshelf!!")
    username = input("Enter your username: ")
    user_id = get_or_create_user(conn, username)

    while True:
        print("What wouild you like to do?")
        choice = input("1. Add a book to a list\2. View a List\n3. Delete a book from a list\n4. Get book details\n5. Quit")

        if choice == '1':
            user_add_book(conn, user_id)
        elif choice == '2':
            pass
        elif choice == '3':
            pass     
        elif choice == '4':
            return_book_details()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

    conn.close()

if __name__ == "__main__":
    main()
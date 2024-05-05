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
    
def remove_book_from_list(conn, user_id): #make less repetitive
    list_choice = input("Enter the list number you would like to remove a book from:\n1. Finished Books\n2. Books To Read\n")

    if list_choice == '1':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, r.added_date
                FROM readList r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.user_id = %s
                ORDER BY r.added_date DESC;
            """, (user_id,))
            read_books = crsr.fetchall()

            if read_books:
                print("Finished Books:")
                for i, book in enumerate(read_books, start=1):
                    title, author, added_date = book
                    print(f"{i}. {title} by {author} (Read on {added_date})")

                choice = int(input("Enter the number of the book you want to remove: "))
                if 1 <= choice <= len(read_books):
                    selected_book = read_books[choice - 1]
                    title, author, added_date = selected_book
                    book_id = get_book_id(conn, title, author)

                    if book_id:
                        crsr.execute("DELETE FROM readList WHERE user_id = %s AND book_id = %s;", (user_id, book_id))
                        conn.commit()
                        print(f"Book '{title}' removed from your read list.")
                    else:
                        print("Book not found.")
                else:
                    print("Invalid choice.")
            else:
                print("Your read list is empty.")

    elif list_choice == '2':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, r.added_date
                FROM toReadList r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.user_id = %s
                ORDER BY r.added_date DESC;
            """, (user_id,))
            to_read_books = crsr.fetchall()

            if to_read_books:
                print("Books in your to-read list:")
                for i, book in enumerate(to_read_books, start=1):
                    title, author, added_date = book
                    print(f"{i}. {title} by {author} (Added on {added_date})")

                choice = int(input("Enter the number of the book you want to remove: "))
                if 1 <= choice <= len(to_read_books):
                    selected_book = to_read_books[choice - 1]
                    title, author, added_date = selected_book
                    book_id = get_book_id(conn, title, author)

                    if book_id:
                        crsr.execute("DELETE FROM toReadList WHERE user_id = %s AND book_id = %s;", (user_id, book_id))
                        conn.commit()
                        print(f"Book '{title}' removed from your to-read list.")
                    else:
                        print("Book not found.")
                else:
                    print("Invalid choice.")
            else:
                print("Your to-read list is empty.")
    else:
        print("Invalid choice.")

def get_book_id(conn, title, author):
    with conn.cursor() as crsr:
        crsr.execute("SELECT book_id FROM books WHERE title = %s AND author = %s;", (title, author))
        book = crsr.fetchone()
        if book:
            return book[0]
        else:
            return None
        
def add_book_review(conn, user_id): #fix duplicate review for exisiting books
    with conn.cursor() as crsr:
        crsr.execute("""
            SELECT b.title, b.author, r.added_date
            FROM readList r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = %s
            ORDER BY r.added_date DESC;
        """, (user_id,))
        read_books = crsr.fetchall()

        if read_books:
            print("Select the book you want to review from your read list:")
            for i, book in enumerate(read_books, start=1):
                title, author, read_date = book
                print(f"{i}. {title} by {author} (Read on {read_date})")

            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(read_books):
                selected_book = read_books[choice - 1]
                title, author, _ = selected_book
                book_id = get_book_id(conn, title, author)

                if book_id:
                    review_text = input(f"Enter your review for '{title}' (max 200 words): ")
                    if len(review_text) > 200:
                        print("Exceeded 200 word limit.")
                    else:
                        rating = float(input(f"Enter your rating for '{title}' (0-5): "))
                        if 0 <= rating <= 5:
                            crsr.execute("""
                                SELECT review_id FROM reviews 
                                WHERE user_id = %s AND book_id = %s;
                            """, (user_id, book_id))
                            review = crsr.fetchone()

                            if review:
                                crsr.execute("""
                                    UPDATE reviews SET review_text = %s, rating = %s, review_date = CURRENT_DATE
                                    WHERE user_id = %s AND book_id = %s;
                                """, (review_text, rating, user_id, book_id))
                            else:
                                crsr.execute("""
                                    INSERT INTO reviews (user_id, book_id, review_text, rating, review_date)
                                    VALUES (%s, %s, %s, %s, CURRENT_DATE);
                                """, (user_id, book_id, review_text, rating))
                            
                            conn.commit()
                            print("Review added successfully.")
                        else:
                            print("Please enter a value between 0 and 5.")
                else:
                    print("Book not found.")
            else:
                print("Invalid choice.")
        else:
            print("You have no finished books.")
            
def view_list(conn, user_id): #make less repetitive
    choice = input("What list would you like to view?\n1. Finished Books\n2. Books to Read\n3. Book Reviews\n")
    if choice == '1':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, b.publication_date, r.added_date
                FROM readList r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.user_id = %s
                ORDER BY r.added_date DESC;
            """, (user_id,))
            read_books = crsr.fetchall()

            if read_books:
                print("Finished Books:")
                print("-" * 20)
                for book in read_books:
                    title, author, publication_date, added_date = book
                    print(f"Title: {title}")
                    print(f"Author: {author}")
                    print(f"Published Date: {publication_date}")
                    print(f"Added Date: {added_date}")
                    print("-" * 20)
            else:
                print("You have no finished books.")
    elif choice == '2':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, b.publication_date, r.added_date
                FROM toReadList r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.user_id = %s
                ORDER BY r.added_date DESC;
            """, (user_id,))
            read_books = crsr.fetchall()

            if read_books:
                print("Books in your to-read list:")
                print("-" * 20)
                for book in read_books:
                    title, author, publication_date, added_date = book
                    print(f"Title: {title}")
                    print(f"Author: {author}")
                    print(f"Published Date: {publication_date}")
                    print(f"Added Date: {added_date}")
                    print("-" * 20)
            else:
                print("Your to-read list is empty.")
    elif choice == '3':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, r.review_text, r.rating, r.review_date
                FROM reviews r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.user_id = %s
                ORDER BY r.review_date DESC;
            """, (user_id,))
            reviews = crsr.fetchall()

            if reviews:
                print("Your Book Reviews:")
                print("-" * 20)
                for review in reviews:
                    title, author, review_text, rating, review_date = review
                    print(f"Title: {title}, Author: {author}, Rating: {rating}, Review Date: {review_date}")
                    print(f"Review: {review_text}")
                    print("*" * 20)
            else:
                print("You have no reviews.")
    else:
        print("Invalid option.")
    
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

def add_book_to_list(conn, user_id, book_info):
    title = book_info["volumeInfo"]["title"]
    author = ", ".join(book_info["volumeInfo"].get("authors", ["Unknown Author"]))
    publish_date = book_info["volumeInfo"].get("publishedDate", "Unknown")
    genres = ", ".join(book_info["volumeInfo"].get("categories", ["Unknown"]))
    isbn_13 = book_info["volumeInfo"].get("industryIdentifiers", [{"type": "ISBN_13", "identifier": ""}])[0].get("identifier", "")
    page_count = book_info["volumeInfo"].get("pageCount", 0)
    average_rating = book_info["volumeInfo"].get("averageRating", 0.0)
    description = book_info["volumeInfo"].get("description", "No description available.")
    cover_image_url = book_info["volumeInfo"].get("imageLinks", {}).get("thumbnail", "")
    buy_link = book_info["saleInfo"].get("buyLink", "")
    price = book_info["saleInfo"].get("listPrice", {}).get("amount", 0.0)

    with conn.cursor() as crsr:
        crsr.execute("SELECT book_id FROM books WHERE book_id = %s;", (isbn_13,))
        book = crsr.fetchone()
        if book:
            book_id = book[0]
        else:
            crsr.execute("""
                INSERT INTO books (book_id, title, author, publication_date, description, cover_image_url, page_count, average_rating, buy_link, price, genres)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING book_id;
            """, (isbn_13, title, author, publish_date, description, cover_image_url, page_count, average_rating, buy_link, price, genres))
            book_id = crsr.fetchone()[0]
            conn.commit()

        list_choice = input(f"Which list would you like to add '{title}' to?\n1. Finished Books\n2. Books To Read\n")
        if list_choice == '1':
            crsr.execute("INSERT INTO readList (user_id, book_id, added_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, book_id))
            conn.commit()
            print(f"Book '{title}' added to your reading list.")
        elif list_choice == '2':
            crsr.execute("INSERT INTO toReadList (user_id, book_id, added_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, book_id))
            conn.commit()
            print(f"Book '{title}' added to your to-read list.")
        else:
            print("Invalid choice.")
            
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
            print("-" * 20)
            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Published Date: {publish_date}")
            print(f"Genres: {', '.join(genres)}")
            print("-" * 20)
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
            add_book_to_list(conn, user_id, selected_book)
        else:
            print("Invalid choice.")
    else:
        print("No books found.")

def main():
    conn = get_connection()
    print("*" * 20)
    print("Welcome to your digital bookshelf!!")
    print("*" * 20)
    username = input("Enter your username: ")
    user_id = get_or_create_user(conn, username)

    while True:
        print("What wouild you like to do?")
        choice = input("1. Add a book to a list\n2. View a List\n3. Delete a book from a list\n4. Get book details\n5. Review a Finished Book\n6. Quit\n")

        if choice == '1':
            user_add_book(conn, user_id)
        elif choice == '2':
            view_list(conn, user_id)
        elif choice == '3':
            remove_book_from_list(conn, user_id)     
        elif choice == '4':
            return_book_details()
        elif choice == '5':
            add_book_review(conn, user_id)
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

    conn.close()

if __name__ == "__main__":
    main()
import requests
import psycopg

def get_connection():
    return psycopg.connect(
        dbname="Books",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    
def remove_book_from_list(conn, user_id):
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
                        log_user_activity(conn, user_id, "Delete Book", f"Deleted book ID {book_id} from list.")
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
        
def add_book_review(conn, user_id):
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
            print("-" * 20)
            for i, book in enumerate(read_books, start=1):
                title, author, read_date = book
                print(f"{i}. {title} by {author} (Added on {read_date})")
            print("-" * 20)
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(read_books):
                selected_book = read_books[choice - 1]
                title, author, _ = selected_book
                book_id = get_book_id(conn, title, author)

                if book_id:
                    review_text = input(f"Enter your review for '{title}' (max 200 words): ")
                    if len(review_text) > 200:
                        print("Exceeded 200 word limit")
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
                            print("Review added successfully")
                            log_user_activity(conn, user_id, "Add Review", f"Added review for book ID {book_id}.")
                        else:
                            print("Enter a value 0-5")
                else:
                    print("Book not found")
            else:
                print("Invalid choice")
        else:
            print("You have no finished books")
            
def view_list(conn, user_id):
    choice = input("What list would you like to view?\n1. Finished Books\n2. Books to Read\n3. Book Reviews\n4. User log\n")
    if choice == '1':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, b.publication_date, r.added_date, b.page_count
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
                    title, author, publication_date, added_date, page_count = book
                    print(f"Title: {title}")
                    print(f"Author: {author}")
                    print(f"Published Date: {publication_date}")
                    print(f"Added Date: {added_date}")
                    print(f"Page count: {page_count}")
                    print("-" * 20)
            else:
                print("You have no finished books.")
    elif choice == '2':
        with conn.cursor() as crsr:
            crsr.execute("""
                SELECT b.title, b.author, b.publication_date, r.added_date, b.page_count, b.average_rating, b.price
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
                    title, author, publication_date, added_date, page_count, average_rating, price  = book
                    print(f"Title: {title}")
                    print(f"Author: {author}")
                    print(f"Published Date: {publication_date}")
                    print(f"Added Date: {added_date}")
                    print(f"Page count: {page_count}")
                    print(f"Average Rating: {average_rating}")
                    print(f"Price: ${price}")
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
                    print(f"Title: {title}, Author: {author}, Review Date: {review_date}")
                    print(f"Rating: {rating}")
                    print(f"Review: {review_text}")
                    print("-" * 20)
            else:
                print("You have no reviews.")
    elif choice == '4':
        get_user_logs(conn, user_id)
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

def add_book_to_list(conn, user_id):
    book_info = get_book_details()
    title = book_info["volumeInfo"]["title"]
    author = ", ".join(book_info["volumeInfo"].get("authors", ["Unknown Author"]))
    publish_date = book_info["volumeInfo"].get("publishedDate", "Unknown")
    genres = ", ".join(book_info["volumeInfo"].get("categories", ["Unknown"]))
    isbn_13 = book_info["volumeInfo"].get("industryIdentifiers", [{"type": "ISBN_13", "identifier": ""}])[0].get("identifier", "")
    page_count = book_info["volumeInfo"].get("pageCount", 0)
    average_rating = book_info["volumeInfo"].get("averageRating", 0.0)
    description = book_info["volumeInfo"].get("description", "No description available.")
    price = book_info["saleInfo"].get("listPrice", {}).get("amount", 0.0)

    with conn.cursor() as crsr:
        crsr.execute("SELECT book_id FROM books WHERE book_id = %s;", (isbn_13,))
        book = crsr.fetchone()
        if book:
            book_id = book[0]
        else:
            crsr.execute("""
                INSERT INTO books (book_id, title, author, publication_date, description, page_count, average_rating, price, genres)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING book_id;
            """, (isbn_13, title, author, publish_date, description, page_count, average_rating, price, genres))
            book_id = crsr.fetchone()[0]
            conn.commit()

        list_choice = input(f"Which list would you like to add '{title}' to?\n1. Finished Books\n2. Books To Read\n")
        if list_choice == '1':
            crsr.execute("INSERT INTO readList (user_id, book_id, added_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, book_id))
            conn.commit()
            print(f"Book '{title}' added to your reading list.")
            log_user_activity(conn, user_id, "Add Book", f"Added {title} to list.")
        elif list_choice == '2':
            crsr.execute("INSERT INTO toReadList (user_id, book_id, added_date) VALUES (%s, %s, CURRENT_DATE);", (user_id, book_id))
            conn.commit()
            print(f"Book '{title}' added to your to-read list.")
            log_user_activity(conn, user_id, "Add Book", f"Added {title} to list.")
        else:
            print("Invalid choice.")
            
def get_book_details():
    api_key = "AIzaSyCkpmRc2m9bY_zOWtTRgNho-KTBDVx9fIs"
    book_name = input("Enter the book name: ")
    url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}&maxResults=10&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["totalItems"] > 0:
            books = []
            for item in data["items"]:
                book_info = item["volumeInfo"]
                title = book_info.get("title", "Unknown Title")
                authors = ", ".join(book_info.get("authors", ["Unknown Author"]))
                books.append({"title": title, "authors": authors, "info": item})
            
            print("Select the book you want from the following options:")
            print("-" * 20)
            for i, book in enumerate(books, start=1):
                print(f"{i}. {book['title']} by {book['authors']}")
            print("-" * 20)
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(books):
                selected_book = books[choice - 1]["info"]
                return selected_book
            else:
                print("Invalid choice.")
                return None
        else:
            print("No book details found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

def return_book_details():
    book_details = get_book_details()
    if book_details:
        volume_info = book_details.get("volumeInfo", {})
        sale_info = book_details.get("saleInfo", {})

        title = volume_info.get("title", "Unknown Title")
        authors = ", ".join(volume_info.get("authors", ["Unknown Author"]))
        publish_date = volume_info.get("publishedDate", "Unknown")
        genres = ", ".join(volume_info.get("categories", ["Unknown"]))
        page_count = volume_info.get("pageCount", "Unknown")
        average_rating = volume_info.get("averageRating", "Not Rated")
        description = volume_info.get("description", "No description available.")
        price = sale_info.get("listPrice", {}).get("amount", "Not for sale")

        print("-" * 20)
        print(f"Title: {title}")
        print(f"Author: {authors}")
        print(f"Published Date: {publish_date}")
        print(f"Genres: {genres}")
        print(f"Page Count: {page_count}")
        print(f"Average rating: {average_rating}")
        print(f"Price: ${price}")
        print(f"Description: {description}")
        print("-" * 20)
    else:
        print("No book details found.")

def log_user_activity(conn, user_id, operation, details):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO user_logs (user_id, operation, details)
            VALUES (%s, %s, %s);
        """, (user_id, operation, details))
        conn.commit()

def get_user_logs(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT operation, details, log_date FROM user_logs
            WHERE user_id = %s ORDER BY log_date DESC;
        """, (user_id,))
        logs = cursor.fetchall()
        for log in logs:
            operation, details, log_date = log
            print(f"{log_date}: {operation} - {details}")

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
            add_book_to_list(conn, user_id)
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
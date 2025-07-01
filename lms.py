#bobok,member
#add book ,register members,borrow books,return books,view available books
#search books by title or author
#limit the no. of books a member can borrow(max 3)
#handles fines for late returns
#track borrow date and calculate files on return
import csv
import os
from datetime import datetime, timedelta

# File paths
BOOKS_FILE = "books.csv"
MEMBERS_FILE = "members.csv"
BORROW_FILE = "borrowed.csv"
MAX_BORROW = 3
FINE_PER_DAY = 5


class Library:
    def __init__(self):
        self.init_files()

    def init_files(self):
        if not os.path.exists(BOOKS_FILE):
            with open(BOOKS_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["ID", "Title", "Author", "Available"])
        if not os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["MemberID", "Name"])
        if not os.path.exists(BORROW_FILE):
            with open(BORROW_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["MemberID", "BookID", "BorrowDate"])

    def view_available_books(self):
        with open(BOOKS_FILE, "r") as f:
            reader = csv.DictReader(f)
            print("Available Books:")
            for row in reader:
                if row['Available'] == 'Yes':
                    print(f'{row["ID"]} - {row["Title"]} by {row["Author"]}')

    def search_books(self, keyword):
        with open(BOOKS_FILE, "r") as f:
            reader = csv.DictReader(f)
            found = False
            for row in reader:
                if keyword.lower() in row["Title"].lower() or keyword.lower() in row["Author"].lower():
                    print(f'{row["ID"]} - {row["Title"]} by {row["Author"]} - Available: {row["Available"]}')
                    found = True
            if not found:
                print("No matching books found.")


class Book(Library):
    def add_book(self, book_id, title, author):
        with open(BOOKS_FILE, "a", newline="") as f:
            csv.writer(f).writerow([book_id, title, author, "Yes"])
        print("Book added successfully.")


class Member(Book):
    def register_member(self, member_id, name):
        with open(MEMBERS_FILE, "a", newline="") as f:
            csv.writer(f).writerow([member_id, name])
        print("Member registered successfully.")

    def borrow_book(self, member_id, book_id):
        with open(BORROW_FILE, "r") as f:
            borrow_count = sum(1 for row in csv.DictReader(f) if row["MemberID"] == member_id)
        if borrow_count >= MAX_BORROW:
            print("Borrow limit reached (max 3 books).")
            return

        updated = False
        books = []
        with open(BOOKS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID"] == book_id and row["Available"] == "Yes":
                    row["Available"] = "No"
                    updated = True
                books.append(row)

        if updated:
            with open(BOOKS_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ID", "Title", "Author", "Available"])
                writer.writeheader()
                writer.writerows(books)

            with open(BORROW_FILE, "a", newline="") as f:
                csv.writer(f).writerow([member_id, book_id, datetime.now().strftime("%Y-%m-%d")])
            print("Book borrowed successfully.")
        else:
            print("Book not available or already borrowed.")

    def return_book(self, member_id, book_id):
        rows, returned = [], False
        fine = 0
        with open(BORROW_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["MemberID"] == member_id and row["BookID"] == book_id:
                    borrow_date = datetime.strptime(row["BorrowDate"], "%Y-%m-%d")
                    days_late = (datetime.now() - borrow_date).days - 14
                    fine = max(0, days_late * FINE_PER_DAY)
                    returned = True
                    continue
                rows.append(row)
 
        if returned:
            with open(BORROW_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["MemberID", "BookID", "BorrowDate"])
                writer.writeheader()
                writer.writerows(rows)

            books = []
            with open(BOOKS_FILE, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["ID"] == book_id:
                        row["Available"] = "Yes"
                    books.append(row)

            with open(BOOKS_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ID", "Title", "Author", "Available"])
                writer.writeheader()
                writer.writerows(books)

            print("Book returned successfully.")
            if fine > 0:
                print(f"You have a fine of ₹{fine}")
        else:
            print("No such borrow record found.")

# Example menu to use the system
def main():
    system = Member()
    while True:
        print("\n1. View available books")
        print("2. Register member")
        print("3. Add book")
        print("4. Borrow book")
        print("5. Return book")
        print("6. Search books")
        print("0. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            system.view_available_books()
        elif choice == "2":
            mid = input("Enter Member ID: ")
            name = input("Enter Member Name: ")
            system.register_member(mid, name)
        elif choice == "3":
            bid = input("Enter Book ID: ")
            title = input("Enter Book Title: ")
            author = input("Enter Author: ")
            system.add_book(bid, title, author)
        elif choice == "4":
            mid = input("Enter Member ID: ")
            bid = input("Enter Book ID: ")
            system.borrow_book(mid, bid)
        elif choice == "5":
            mid = input("Enter Member ID: ")
            bid = input("Enter Book ID: ")
            system.return_book(mid, bid)
        elif choice == "6":
            keyword = input("Enter book title or author: ")
            system.search_books(keyword)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()

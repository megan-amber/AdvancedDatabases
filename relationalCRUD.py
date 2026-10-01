"""
Name: Megan Gerth
Date: 10/1/2026
Assignment Name: 5.6 Performance Assessment
Purpose of the Program: This application creates and interacts with an SQLite database 
                        named EN_ReviewData using CRUD operations. It builds tables for 
                        Reviewers, Categories, Products, and Reviews, seeds them from 
                        a JSON file named dataset_en_dev.json, and provides an interactive 
                        menu allowing users to perform queries, inserts, conditional 
                        displays, and deletions.
"""

import json
import sqlite3

# Define database name and JSON file path
DB_NAME = "EN_ReviewData.db"
JSON_FILE = "dataset_en_dev.json"


def get_connection():
    """Returns a connection to the SQLite database with Foreign Keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    # Enable foreign key constraint support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Create a new database named EN_ReviewData
def initialize_database():
    """Initializes the database connection and creates required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create a new table in the database named Reviewers
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Reviewers (
            reviewer_id TEXT PRIMARY KEY
        );
    """
    )

    # Create a new table in the database named Categories
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Categories (
            product_category TEXT PRIMARY KEY
        );
    """
    )

    # Create a new table in the database named Products
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            product_id TEXT PRIMARY KEY,
            product_category TEXT,
            FOREIGN KEY (product_category) REFERENCES Categories(product_category)
        );
    """
    )

    # Create a new table in the database named Reviews
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT,
            reviewer_id TEXT,
            stars INTEGER,
            review_body TEXT,
            review_title TEXT,
            FOREIGN KEY (product_id) REFERENCES Products(product_id),
            FOREIGN KEY (reviewer_id) REFERENCES Reviewers(reviewer_id)
        );
    """
    )

    conn.commit()
    conn.close()


# Insert data from the JSON file into the tables
def load_json_data():
    """Reads data from dataset_en_dev.json and inserts it into tables."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)

                # Insert into Reviewers table (ignore if duplicate)
                cursor.execute(
                    "INSERT OR IGNORE INTO Reviewers (reviewer_id) VALUES (?);",
                    (record["reviewer_id"],),
                )

                # Insert into Categories table (ignore if duplicate)
                cursor.execute(
                    "INSERT OR IGNORE INTO Categories (product_category) VALUES (?);",
                    (record["product_category"],),
                )

                # Insert into Products table (ignore if duplicate)
                cursor.execute(
                    "INSERT OR IGNORE INTO Products (product_id, product_category) VALUES (?, ?);",
                    (record["product_id"], record["product_category"]),
                )

                # Insert into Reviews table (ignore if duplicate)
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Reviews 
                    (review_id, product_id, reviewer_id, stars, review_body, review_title) 
                    VALUES (?, ?, ?, ?, ?, ?);
                """,
                    (
                        record["review_id"],
                        record["product_id"],
                        record["reviewer_id"],
                        int(record["stars"]),
                        record["review_body"],
                        record["review_title"],
                    ),
                )

        conn.commit()
        print(f"Data successfully loaded from '{JSON_FILE}'.")

    except FileNotFoundError:
        print(f"Error: The file '{JSON_FILE}' was not found in the working directory.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data from '{JSON_FILE}': {e}")
    finally:
        conn.close()


# Allow the user to insert a row into any table
def insert_new_record():
    """Prompts user to select a table and insert a new row."""
    print("\n--- Insert a New Record ---")
    print("1. Reviewers")
    print("2. Categories")
    print("3. Products")
    print("4. Reviews")

    choice = input("Select a table to insert into (1-4): ").strip()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if choice == "1":
            r_id = input("Enter Reviewer ID: ").strip()
            cursor.execute(
                "INSERT INTO Reviewers (reviewer_id) VALUES (?);", (r_id,)
            )

        elif choice == "2":
            cat = input("Enter Product Category: ").strip()
            cursor.execute(
                "INSERT INTO Categories (product_category) VALUES (?);", (cat,)
            )

        elif choice == "3":
            p_id = input("Enter Product ID: ").strip()
            cat = input("Enter Product Category: ").strip()
            cursor.execute(
                "INSERT INTO Products (product_id, product_category) VALUES (?, ?);",
                (p_id, cat),
            )

        elif choice == "4":
            rev_id = input("Enter Review ID: ").strip()
            p_id = input("Enter Product ID: ").strip()
            r_id = input("Enter Reviewer ID: ").strip()
            stars = int(input("Enter Stars (1-5): ").strip())
            title = input("Enter Review Title: ").strip()
            body = input("Enter Review Body: ").strip()

            cursor.execute(
                """
                INSERT INTO Reviews (review_id, product_id, reviewer_id, stars, review_body, review_title)
                VALUES (?, ?, ?, ?, ?, ?);
            """,
                (rev_id, p_id, r_id, stars, body, title),
            )
        else:
            print("Invalid table selection.")
            conn.close()
            return

        conn.commit()
        print("Record inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting record: {e}")
    finally:
        conn.close()


# Display the categories that have at least a certain number of products determined by a user-entered value
def display_product_count_per_category():
    """Displays categories having at least a user-specified threshold of products."""
    try:
        min_count = int(
            input("\nEnter minimum number of products per category: ").strip()
        )
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT product_category, COUNT(product_id) as product_count
        FROM Products
        GROUP BY product_category
        HAVING COUNT(product_id) >= ?;
    """

    cursor.execute(query, (min_count,))
    results = cursor.fetchall()
    conn.close()

    print(f"\n--- Categories with at least {min_count} product(s) ---")
    if not results:
        print("No categories meet the criteria.")
    else:
        for cat, count in results:
            print(f"Category: {cat} | Product Count: {count}")


# Allow the user to type in and execute SQL SELECT statements
def enter_custom_query():
    """Allows user to enter and run custom SQL SELECT queries."""
    query = input("\nEnter your SQL SELECT statement: ").strip()

    if not query.upper().startswith("SELECT"):
        print("Only SELECT queries are permitted in this section.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        print("\n--- Query Results ---")
        print(" | ".join(columns))
        print("-" * 40)
        for row in results:
            print(" | ".join(str(item) for item in row))
        if not results:
            print("Query returned 0 rows.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# Delete all records in the Reviews table for a user-entered product_category
def delete_reviews_from_category():
    """Deletes all review records associated with a specific product category."""
    category = input(
        "\nEnter the product category to delete reviews for: "
    ).strip()

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        DELETE FROM Reviews
        WHERE product_id IN (
            SELECT product_id FROM Products WHERE product_category = ?
        );
    """

    try:
        cursor.execute(query, (category,))
        deleted_count = cursor.rowcount
        conn.commit()
        print(
            f"Successfully deleted {deleted_count} review(s) for category '{category}'."
        )
    except sqlite3.Error as e:
        print(f"Error deleting reviews: {e}")
    finally:
        conn.close()


# Allow the user to delete all tables in the database
def delete_all_tables():
    """Drops all tables from the database."""
    confirm = (
        input(
            "\nAre you sure you want to delete ALL tables? (yes/no): "
        )
        .strip()
        .lower()
    )
    if confirm != "yes":
        print("Action cancelled.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Drop child tables first to respect foreign key constraints
    tables = ["Reviews", "Products", "Categories", "Reviewers"]

    try:
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()
        print("All tables have been successfully deleted.")
    except sqlite3.Error as e:
        print(f"Error deleting tables: {e}")
    finally:
        conn.close()


def main():
    # Execute required setup before showing the menu
    initialize_database()
    load_json_data()

    while True:
        print("\n================ MENU ================")
        print("1. Insert a new record")
        print("2. Display a product count per category")
        print("3. Enter a query")
        print("4. Delete reviews from a category")
        print("5. Delete all tables")
        print("6. Exit the program")
        print("======================================")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            insert_new_record()
        elif choice == "2":
            display_product_count_per_category()
        elif choice == "3":
            enter_custom_query()
        elif choice == "4":
            delete_reviews_from_category()
        elif choice == "5":
            delete_all_tables()
        elif choice == "6":
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 6.")


if __name__ == "__main__":
    main()

'''
    Name: Megan Gerth
    Date: 9/17/2026
    Assignment: 3.5 Performance Assessment
    Purpose: Perform CRUD operations on a Cassandra Column Family Database
    with a menu for the user to manipulate
'''

import json
from cassandra.cluster import Cluster

def display_menu():
    print("\n----- Amazon Database Menu -----")
    print("1. Display all distinct product categories")
    print("2. Display the count of all 4+ star reviews in a category")
    print("3. Display the count of all 1 star reviews in a category")
    print("4. Execute custom query")
    print("5. Add or remove columns from designated tables")
    print("6. Delete Reviews and ProductCategories tables")
    print("7. Delete Amazon keyspace")
    print("8. Exit")
    print("-----------------------------------")

def connect_database(session):
    #Create keyspace named Amazon
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS Amazon WITH replication =
        {'class':'SimpleStrategy', 'replication_factor':1};
        """)
    session.execute("USE Amazon;")

    #Create table named Reviews
    session.execute("""
        CREATE TABLE IF NOT EXISTS Reviews(
            review_id text PRIMARY KEY,
            product_id text,
            reviewer_id text,
            stars int,
            review_body text,
            review_title text,
            product_category text);
        """)

    #Create table named ProductCategories
    session.execute("""
        CREATE TABLE IF NOT EXISTS ProductCategories(
            product_id text,
            stars int,
            language text,
            product_category text,
            PRIMARY KEY((product_category), stars, product_id));
        """)
    print("Keyspace 'Amazon' and tables 'Reviews' and 'ProductCategories' created successfully!")
    

    #Insert data from JSON file into tables
    print("Importing data from file...")
    try:
        for line in open('dataset_en_dev.json', 'r'):
            dataSet = json.loads(line)

            insert_reviews = """
                INSERT INTO Reviews (review_id, product_id, reviewer_id, stars, review_body, review_title, product_category)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
            session.execute(insert_reviews, [
                dataSet.get("review_id"),
                dataSet.get("product_id"),
                dataSet.get("reviewer_id"),
                int(dataSet.get("stars", 0)),
                dataSet.get("review_body"),
                dataSet.get("review_title"),
                dataSet.get("product_category")
            ])

            insert_categories = """
                INSERT INTO ProductCategories (product_id, stars, language, product_category)
                VALUES (%s, %s, %s, %s);
                """
            session.execute(insert_categories, [
                dataSet.get("product_id"),
                int(dataSet.get("stars", 0)),
                dataSet.get("language"),
                dataSet.get("product_category")
            ])
        print("Data imported successfully into both tables!")
    except FileNotFoundError:
        print("Error: file not found.")

def display_distinct_categories(session):
    #Display all distinct product categories from the ProductCategories table
    session.execute("USE Amazon;")
    try:
        query = 'SELECT DISTINCT product_category FROM ProductCategories;'
        results = session.execute(query)
        print("\n--- Distinct Product Categories ---")
        for row in results:
            print(row.product_category)
    except Exception as e:
        print(f"Error: {e}")

def display_high_rating_reviews(session):
    #Display the count of 4-star and higher reviews for a user-entered product category
    session.execute("USE Amazon;")
    cat = input("Enter product category: ").strip()
    try:
        query = "SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s AND stars >= 4 ALLOW FILTERING;"
        result = session.execute(query, [cat])
        count = result.one().count
        print(f"\nNumber of 4-star and higher reviews for category '{cat}': {count}")
    except Exception as e:
        print(f"Error: {e}")

def display_one_star_reviews(session):
    #Display the count of 1-star reviews for a user-entered product category
    session.execute("USE Amazon;")
    cat = input("Enter product category: ").strip()
    try:
        query = "SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s AND stars = 1 ALLOW FILTERING;"
        result = session.execute(query, [cat])
        count = result.one().count
        print(f"\nNumber of 1-star reviews for category '{cat}': {count}")
    except Exception as e:
        print(f"Error: {e}")

def execute_custom_cql(session):
    #Allow the user to type in and execute CQL SELECT statements
    session.execute("USE Amazon;")
    cql = input("Enter your CQL SELECT statement: ").strip()
    if not cql.lower().startswith("select"):
        print("Only SELECT statements are permitted here.")
    else:
        try:
            results = session.execute(cql)
            print("\n--- Query Results ---")
            for row in results:
                print(row)
        except Exception as e:
            print(f"Error executing statement: {e}")

def alter_table_columns(session):
    #Allow the user to add and remove columns from the Reviews and ProductCategories tables
    session.execute("USE Amazon;")
    table_choice = input("Select table (1: Reviews, 2: ProductCategories): ").strip()
    action = input("Choose action (1: Add column, 2: Remove column): ").strip()
    
    table_name = "Reviews" if table_choice == '1' else "ProductCategories" if table_choice == '2' else None
    if not table_name:
        print("Invalid table choice.")
        return
    
    if action == '1':
        col_name = input("Enter new column name: ").strip()
        col_type = input("Enter data type (e.g., text, int): ").strip()
        try:
            session.execute(f"ALTER TABLE {table_name} ADD {col_name} {col_type};")
            print(f"Column '{col_name}' added to {table_name} successfully.")
        except Exception as e:
            print(f"Error: {e}")
    elif action == '2':
        col_name = input("Enter column name to remove: ").strip()
        try:
            session.execute(f"ALTER TABLE {table_name} DROP {col_name};")
            print(f"Column '{col_name}' removed from {table_name} successfully.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid action choice.")

def delete_tables(session):
    #Allow the user to delete the Reviews and ProductCategories tables
    session.execute("USE Amazon;")
    confirm = input("Are you sure you want to delete both tables? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            session.execute("DROP TABLE IF EXISTS Reviews;")
            session.execute("DROP TABLE IF EXISTS ProductCategories;")
            print("Tables 'Reviews' and 'ProductCategories' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")

def delete_keyspace(session):
    #Allow the user to delete the Amazon keyspace
    confirm = input("Are you sure you want to delete the 'Amazon' keyspace? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            session.execute("DROP KEYSPACE IF EXISTS Amazon;")
            print("Keyspace 'Amazon' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("Connecting to local Cassandra database...")
    cluster = Cluster()
    session = cluster.connect()

    # Automatically run keyspace/table creation and data insertion before entering the menu loop
    connect_database(session)

    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':
            display_distinct_categories(session)
        elif choice == '2':
            display_high_rating_reviews(session)
        elif choice == '3':
            display_one_star_reviews(session)
        elif choice == '4':
            execute_custom_cql(session)
        elif choice == '5':
            alter_table_columns(session)
        elif choice == '6':
            delete_tables(session)
        elif choice == '7':
            delete_keyspace(session)
        elif choice == '8':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main()
        

"""
Name: Megan Gerth
Date: September 13, 2026
Assignment Name: MongoDB CRUD Operations Application
Purpose: Python CLI application providing CRUD (Create, Read, Update, Delete)
         functionality on an Amazon MongoDB database (`ReviewData` collection)
         using PyMongo with interactive nested menus.
"""

import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Database and Collection configuration for local MongoDB Compass connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "Amazon"
COLLECTION_NAME = "ReviewData"


def connect_database():
    """Establish connection to MongoDB client and return database and collection references."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verify active connection to MongoDB server
        client.admin.command("ping")
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"Successfully connected to MongoDB ({DB_NAME}.{COLLECTION_NAME}).")
        return client, db, collection
    except PyMongoError as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Make sure your local MongoDB service is running.")
        sys.exit(1)


# Utility display helper function
def display_document(doc):
    """Formats and prints MongoDB document key-value pairs cleanly."""
    for key, val in doc.items():
        if key != "_id":
            print(f"  {key}: {val}")


#Query Functions for Nested Menu
            
#Retrieve documents from the ReviewData collection using the .find_one() function
def query_by_review_id(collection):
    """Sub-menu Option 1: Retrieve document using find_one()."""
    print("\n--- Query by reviewID ---")
    review_id = input("Enter reviewID (review_id) to search for: ").strip()

    try:
        document = collection.find_one({"review_id": review_id})
        if document:
            print("\nDocument Found:")
            display_document(document)
        else:
            print(f"No document found with reviewID: '{review_id}'")
    except PyMongoError as e:
        print(f"An error occurred while querying database: {e}")


#Retrieve documents using .find() filtering for greater than or equal to stars
def filter_stars_gte(collection):
    """Sub-menu Option 2: Retrieve documents with stars >= entered value."""
    print("\n--- Filter for a number of stars and greater (>=) ---")
    stars_input = input("Enter minimum number of stars: ").strip()

    if not stars_input.isdigit():
        print("Invalid input! Please enter a valid number.")
        return

    stars_num = int(stars_input)
    # Checks for both integer and string representations stored in MongoDB
    query = {
        "$or": [
            {"stars": {"$gte": stars_num}},
            {"stars": {"$gte": str(stars_num)}},
        ]
    }

    execute_find_query(collection, query)


#Retrieve documents using .find() filtering for less than a number of stars
def filter_stars_lt(collection):
    """Sub-menu Option 3: Retrieve documents with stars < entered value."""
    print("\n--- Filter for less than a number of stars (<) ---")
    stars_input = input("Enter maximum number of stars: ").strip()

    if not stars_input.isdigit():
        print("Invalid input! Please enter a valid number.")
        return

    stars_num = int(stars_input)
    # Checks for both integer and string representations stored in MongoDB
    query = {
        "$or": [
            {"stars": {"$lt": stars_num}},
            {"stars": {"$lt": str(stars_num)}},
        ]
    }

    execute_find_query(collection, query)


# * Retrieve documents using .find() filtering for a word within review_title
def filter_by_title_word(collection):
    """Sub-menu Option 4: Substring search in review_title using regex."""
    print("\n--- Filter for a word in the title ---")
    term = input("Enter word to search in review title: ").strip()

    if not term:
        print("Search term cannot be empty.")
        return

    query = {"review_title": {"$regex": term, "$options": "i"}}
    execute_find_query(collection, query)


#Retrieve documents using .find() filtering for a word within review_body
def filter_by_body_word(collection):
    """Sub-menu Option 5: Substring search in review_body using regex."""
    print("\n--- Filter for a word in the review body content ---")
    term = input("Enter word to search in review body: ").strip()

    if not term:
        print("Search term cannot be empty.")
        return

    query = {"review_body": {"$regex": term, "$options": "i"}}
    execute_find_query(collection, query)


def execute_find_query(collection, query):
    """Helper function to execute find() cursors and print results."""
    try:
        cursor = collection.find(query)
        results = list(cursor)

        if results:
            print(f"\nFound {len(results)} matching document(s):")
            for i, doc in enumerate(results, start=1):
                print(f"\n--- Result #{i} ---")
                display_document(doc)
        else:
            print("No matching documents found.")
    except PyMongoError as e:
        print(f"An error occurred during query execution: {e}")


def query_documents_submenu(collection):
    """Sub-Menu for Main Menu Option 1: Query for documents."""
    while True:
        print("\n--- QUERY DOCUMENTS SUB-MENU --- ")
        print("1. Query by reviewID")
        print("2. Filter for a number of stars and greater")
        print("3. Filter for less than a number of stars")
        print("4. Filter for a word in the title")
        print("5. Filter for a word in the review body content")
        print("6. Go back to main menu")

        sub_choice = input("Select an option (1-6): ").strip()

        if sub_choice == "1":
            query_by_review_id(collection)
        elif sub_choice == "2":
            filter_stars_gte(collection)
        elif sub_choice == "3":
            filter_stars_lt(collection)
        elif sub_choice == "4":
            filter_by_title_word(collection)
        elif sub_choice == "5":
            filter_by_body_word(collection)
        elif sub_choice == "6":
            print("Returning to Main Menu...")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")

#Main Menu Functions

#Create a new document in the Amazon database in the ReviewData collection
def add_new_document(collection):
    """Main Menu Option 2: Add a new document."""
    print("\n--- Add a New Document ---")
    review_id = input("Enter Review ID (e.g., en_0999999): ").strip()
    product_id = input("Enter Product ID (e.g., product_en_0999999): ").strip()
    reviewer_id = input(
        "Enter Reviewer ID (e.g., reviewer_en_0999999): "
    ).strip()

    while True:
        stars_input = input("Enter Stars rating (1-5): ").strip()
        if stars_input.isdigit() and 1 <= int(stars_input) <= 5:
            stars = int(stars_input)
            break
        print("Invalid input! Please enter an integer between 1 and 5.")

    review_title = input("Enter Review Title: ").strip()
    review_body = input("Enter Review Body: ").strip()
    language = input("Enter Language (default 'en'): ").strip() or "en"
    product_category = input("Enter Product Category: ").strip()

    document = {
        "review_id": review_id,
        "product_id": product_id,
        "reviewer_id": reviewer_id,
        "stars": stars,
        "review_title": review_title,
        "review_body": review_body,
        "language": language,
        "product_category": product_category,
    }

    try:
        result = collection.insert_one(document)
        print(f"Success! Inserted review document with _id: {result.inserted_id}")
    except PyMongoError as e:
        print(f"An error occurred while inserting document: {e}")


# Allow the user to enter a field and update the value within the document
def update_document_fields(collection):
    """Main Menu Option 3: Update fields of a document."""
    print("\n--- Update Fields of a Document ---")
    review_id = input(
        "Enter review_id of the document you want to update: "
    ).strip()

    # Search for document to confirm it exists before updating
    document = collection.find_one({"review_id": review_id})
    if not document:
        print(f"Document with review_id '{review_id}' not found.")
        return

    print("\nTarget Document Found:")
    display_document(document)

    field_name = input(
        "\nEnter field name to update (e.g., stars, review_title, review_body, product_category): "
    ).strip()
    new_value = input(f"Enter new value for field '{field_name}': ").strip()

    # Handle numeric conversion if stars field is updated
    if field_name == "stars" and new_value.isdigit():
        new_value = int(new_value)

    try:
        result = collection.update_one(
            {"review_id": review_id}, {"$set": {field_name: new_value}}
        )

        if result.modified_count > 0:
            print("Success! Document updated successfully.")
        else:
            print(
                "No changes made (the new value might be identical to the existing value)."
            )
    except PyMongoError as e:
        print(f"An error occurred during update execution: {e}")


#Allow the user to enter a document ID and delete a specific document
def delete_single_document(collection):
    """Main Menu Option 4: Delete a document."""
    print("\n--- Delete a Document ---")
    review_id = input(
        "Enter review_id of document to delete (e.g., en_0968227): "
    ).strip()

    try:
        result = collection.delete_one({"review_id": review_id})
        if result.deleted_count > 0:
            print(
                f"Success! Document with review_id '{review_id}' was deleted."
            )
        else:
            print(f"No document found with review_id: '{review_id}'")
    except PyMongoError as e:
        print(f"An error occurred during deletion: {e}")


#Menu option to remove all documents in a collection
def delete_all_documents(collection):
    """Main Menu Option 5: Delete all documents from the collection."""
    print("\n--- Delete All Documents from Collection ---")
    confirm = input(
        f"Are you sure you want to delete ALL documents from '{COLLECTION_NAME}'? (yes/no): "
    ).strip().lower()

    if confirm == "yes":
        try:
            result = collection.delete_many({})
            print(
                f"Success! Removed {result.deleted_count} document(s) from '{COLLECTION_NAME}'."
            )
        except PyMongoError as e:
            print(f"An error occurred while clearing collection: {e}")
    else:
        print("Operation cancelled.")


#Menu option to delete the collection from the Amazon database
def delete_entire_collection(db):
    """Main Menu Option 6: Delete a collection."""
    print(f"\n--- Delete Collection '{COLLECTION_NAME}' ---")
    confirm = input(
        f"WARNING: Are you sure you want to DROP collection '{COLLECTION_NAME}' from database '{DB_NAME}'? (yes/no): "
    ).strip().lower()

    if confirm == "yes":
        try:
            db.drop_collection(COLLECTION_NAME)
            print(
                f"Success! Collection '{COLLECTION_NAME}' has been deleted."
            )
        except PyMongoError as e:
            print(f"An error occurred while dropping collection: {e}")
    else:
        print("Operation cancelled.")


#Main application function with menu

def main():
    """Main application loop carrying the top-level menu options."""
    client, db, collection = connect_database()

    while True:
        print("\n" + "=" * 45)
        print("         MAIN MENU - AMAZON REVIEWS")
        print("=" * 45)
        print("1. Query for documents")
        print("2. Add a new document")
        print("3. Update fields of a document")
        print("4. Delete a document")
        print("5. Delete all documents from the collection")
        print("6. Delete a collection")
        print("7. Exit the Program")
        print("=" * 45)

        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            # Opens the nested sub-menu for query operations
            query_documents_submenu(collection)
        elif choice == "2":
            add_new_document(collection)
        elif choice == "3":
            update_document_fields(collection)
        elif choice == "4":
            delete_single_document(collection)
        elif choice == "5":
            delete_all_documents(collection)
        elif choice == "6":
            delete_entire_collection(db)
        elif choice == "7":
            print("\nExiting program. Goodbye!")
            client.close()
            break
        else:
            print("Invalid menu option! Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()

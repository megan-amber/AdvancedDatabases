"""
    Name: Megan Gerth
    Date: 9/28/2026
    Assignment: 4.5 Performance Assessment
    Purpose: Import Amazon review dataset into Neo4j graph database to model
         relationships between Categories, Products, Reviews, and Reviewers.
         Provides an interactive CLI menu allowing users to perform CRUD operations 
         (Create, Read, Update, Delete) on nodes and relationships.
"""

import json
from neo4j import GraphDatabase

# Connection information for local Neo4j database
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password1")

print("Connecting to local Neo4j database...")
driver = GraphDatabase.driver(URI, auth=AUTH)


# Helper function to clear previous driver sessions gracefully
def run_query(query, parameters=None):
    with driver.session() as session:
        return list(session.run(query, parameters or {}))


def import_json_data(file_path="dataset_en_dev.json"):
    """
    Reads the JSON dataset and populates the Graph Database with:
    - Category nodes
    - Product nodes
    - Review nodes
    - Reviewer nodes
    - Relationships: (Reviewer)-[:WROTE]->(Review),
                     (Product)-[:CLASSIFIED_AS]->(Category),
                     (Product)-[:HAS_REVIEW]->(Review)
    """
    print("\nImporting data from file and creating nodes/relationships...")

    # Data structures to keep track of unique entries
    categories = set()
    products = set()
    reviewers = set()
    reviews = []  # List of dicts with review details
    product_category_map = []  # List of tuples: (product_id, category_name)

    # Read and parse JSON file line by line
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            cat_name = data.get("product_category")
            prod_id = data.get("product_id")
            reviewer_id = data.get("reviewer_id")
            review_id = data.get("review_id")
            title = data.get("review_title", "")
            content = data.get("review_body", "")
            stars = data.get("stars", 0)

            if cat_name:
                categories.add(cat_name)
            if prod_id:
                products.add(prod_id)
            if reviewer_id:
                reviewers.add(reviewer_id)

            if prod_id and cat_name:
                product_category_map.append((prod_id, cat_name))

            if review_id:
                reviews.append(
                    {
                        "review_id": review_id,
                        "title": title,
                        "content": content,
                        "stars": stars,
                        "reviewer_id": reviewer_id,
                        "product_id": prod_id,
                    }
                )

    # Create Category labeled nodes from imported JSON data
    print("Creating Category nodes...")
    for category in categories:
        run_query(
            "MERGE (:Category {name: $name})",
            {"name": category},
        )

    # Create Product labeled nodes from imported JSON data
    print("Creating Product nodes...")
    for product in products:
        run_query(
            "MERGE (:Product {name: $name})",
            {"name": product},
        )

    # 3. Create Review labeled nodes from imported JSON data
    print("Creating Review nodes...")
    # 4. Create Reviewer labeled nodes from imported JSON data
    print("Creating Reviewer nodes...")
    for rev in reviews:
        # Create Review node
        run_query(
            """
            MERGE (r:Review {review_id: $review_id})
            SET r.title = $title, r.content = $content, r.stars = $stars
            """,
            {
                "review_id": rev["review_id"],
                "title": rev["title"],
                "content": rev["content"],
                "stars": rev["stars"],
            },
        )

        # Create Reviewer node if present
        if rev["reviewer_id"]:
            run_query(
                "MERGE (:Reviewer {name: $name})",
                {"name": rev["reviewer_id"]},
            )

    # Create a relationship between Reviewer nodes and Review nodes
    print("Connecting Reviewers to Reviews...")
    for rev in reviews:
        if rev["reviewer_id"] and rev["review_id"]:
            run_query(
                """
                MATCH (rr:Reviewer {name: $reviewer_id})
                MATCH (r:Review {review_id: $review_id})
                MERGE (rr)-[:WROTE]->(r)
                """,
                {
                    "reviewer_id": rev["reviewer_id"],
                    "review_id": rev["review_id"],
                },
            )

    # Create a relationship between Product nodes and Category nodes
    print("Connecting Products to Categories...")
    for prod_id, cat_name in product_category_map:
        run_query(
            """
            MATCH (p:Product {name: $prod_id})
            MATCH (c:Category {name: $cat_name})
            MERGE (p)-[:CLASSIFIED_AS]->(c)
            """,
            {"prod_id": prod_id, "cat_name": cat_name},
        )

    # Create a relationship between Product nodes and Review nodes
    print("Connecting Products to Reviews...")
    for rev in reviews:
        if rev["product_id"] and rev["review_id"]:
            run_query(
                """
                MATCH (p:Product {name: $prod_id})
                MATCH (r:Review {review_id: $review_id})
                MERGE (p)-[:HAS_REVIEW]->(r)
                """,
                {"prod_id": rev["product_id"], "review_id": rev["review_id"]},
            )

    print("Data import complete!\n")


def display_menu():
    """Displays the CLI menu options."""
    print("=" * 55)
    print("          NEO4J GRAPH DATABASE MANAGEMENT")
    print("=" * 55)
    print("1.  Import/Load initial JSON dataset into graph database")
    print("2.  Create custom Node (Category, Product, Review, Reviewer)")
    print(
        "3.  Create custom Relationship (Product->Category or Product->Review)"
    )
    print("4.  Get count of Products in a Category")
    print("5.  Get count of Reviews written by a Reviewer")
    print("6.  Delete a Category node by name")
    print("7.  Delete ALL relationships in the graph")
    print("8.  Delete ALL nodes in the graph")
    print("9.  Exit")
    print("=" * 55)


# Allow the user to create their own node with a Category, Product, Review, or Reviewer label
def user_create_node():
    print("\n--- Create Node ---")
    print("Labels: 1. Category  2. Product  3. Review  4. Reviewer")
    choice = input("Select label (1-4): ").strip()

    if choice == "1":
        name = input("Enter Category Name: ").strip()
        run_query("CREATE (:Category {name: $name})", {"name": name})
        print(f"Category node '{name}' created successfully.")

    elif choice == "2":
        name = input("Enter Product ID/Name: ").strip()
        run_query("CREATE (:Product {name: $name})", {"name": name})
        print(f"Product node '{name}' created successfully.")

    elif choice == "3":
        rev_id = input("Enter Review ID: ").strip()
        title = input("Enter Review Title: ").strip()
        content = input("Enter Review Content: ").strip()
        stars = input("Enter Stars (1-5): ").strip()

        try:
            stars = int(stars)
        except ValueError:
            stars = 0

        run_query(
            """
            CREATE (:Review {
                review_id: $rev_id, 
                title: $title, 
                content: $content, 
                stars: $stars
            })
            """,
            {
                "rev_id": rev_id,
                "title": title,
                "content": content,
                "stars": stars,
            },
        )
        print(f"Review node '{rev_id}' created successfully.")

    elif choice == "4":
        name = input("Enter Reviewer Name/ID: ").strip()
        run_query("CREATE (:Reviewer {name: $name})", {"name": name})
        print(f"Reviewer node '{name}' created successfully.")

    else:
        print("Invalid choice.")


# Allow the user to create their own relationship between Product and Category nodes, or Product and Review nodes
def user_create_relationship():
    print("\n--- Create Relationship ---")
    print("1. Product -> CLASSIFIED_AS -> Category")
    print("2. Product -> HAS_REVIEW -> Review")
    choice = input("Select relationship type (1-2): ").strip()

    if choice == "1":
        prod_name = input("Enter Product Name/ID: ").strip()
        cat_name = input("Enter Category Name: ").strip()

        query = """
        MATCH (p:Product {name: $prod_name})
        MATCH (c:Category {name: $cat_name})
        MERGE (p)-[r:CLASSIFIED_AS]->(c)
        RETURN r
        """
        res = run_query(query, {"prod_name": prod_name, "cat_name": cat_name})
        if res:
            print(
                f"Relationship Created: ({prod_name}) -[:CLASSIFIED_AS]-> ({cat_name})"
            )
        else:
            print("Error: Ensure both Product and Category nodes exist.")

    elif choice == "2":
        prod_name = input("Enter Product Name/ID: ").strip()
        rev_id = input("Enter Review ID: ").strip()

        query = """
        MATCH (p:Product {name: $prod_name})
        MATCH (r:Review {review_id: $rev_id})
        MERGE (p)-[rel:HAS_REVIEW]->(r)
        RETURN rel
        """
        res = run_query(query, {"prod_name": prod_name, "rev_id": rev_id})
        if res:
            print(
                f"Relationship Created: ({prod_name}) -[:HAS_REVIEW]-> ({rev_id})"
            )
        else:
            print("Error: Ensure both Product and Review nodes exist.")

    else:
        print("Invalid choice.")


# Allow the user to enter a category name and see the count of Product nodes related to it
def user_count_products_in_category():
    print("\n--- Count Products in Category ---")
    category_name = input("Enter Category Name: ").strip()

    query = """
    MATCH (p:Product)-[:CLASSIFIED_AS]->(c:Category {name: $cat_name})
    RETURN COUNT(p) AS product_count
    """
    res = run_query(query, {"cat_name": category_name})
    count = res[0]["product_count"] if res else 0
    print(
        f"Category '{category_name}' has {count} associated Product node(s)."
    )


# Allow the user to enter a reviewer name (reviewer_id) and see the count of Review nodes related to it
def user_count_reviews_by_reviewer():
    print("\n--- Count Reviews by Reviewer ---")
    reviewer_name = input("Enter Reviewer Name/ID: ").strip()

    query = """
    MATCH (rr:Reviewer {name: $reviewer_name})-[:WROTE]->(r:Review)
    RETURN COUNT(r) AS review_count
    """
    res = run_query(query, {"reviewer_name": reviewer_name})
    count = res[0]["review_count"] if res else 0
    print(
        f"Reviewer '{reviewer_name}' has created {count} associated Review node(s)."
    )


# Allow the user to enter a category name and delete the associated Category node
def user_delete_category():
    print("\n--- Delete Category Node ---")
    cat_name = input("Enter Category Name to delete: ").strip()

    # Using DETACH DELETE to drop node along with any connected relationships
    query = """
    MATCH (c:Category {name: $cat_name})
    DETACH DELETE c
    """
    run_query(query, {"cat_name": cat_name})
    print(
        f"Category node '{cat_name}' and its immediate relationships removed."
    )


# Delete all relationships in the graph
def user_delete_all_relationships():
    print("\n--- Delete All Relationships ---")
    confirm = input(
        "Are you sure you want to delete ALL relationships? (y/n): "
    ).lower()
    if confirm == "y":
        query = "MATCH ()-[r]->() DELETE r"
        run_query(query)
        print("All relationships successfully deleted from the graph.")


# Delete all nodes in the graph
def user_delete_all_nodes():
    print("\n--- Delete All Nodes ---")
    confirm = input(
        "Are you sure you want to delete ALL nodes (and relationships)? (y/n): "
    ).lower()
    if confirm == "y":
        query = "MATCH (n) DETACH DELETE n"
        run_query(query)
        print("All nodes and relationships successfully deleted from the graph.")


# Main application menu loop
def main():
    while True:
        display_menu()
        choice = input("Enter selection (1-9): ").strip()

        if choice == "1":
            import_json_data()
        elif choice == "2":
            user_create_node()
        elif choice == "3":
            user_create_relationship()
        elif choice == "4":
            user_count_products_in_category()
        elif choice == "5":
            user_count_reviews_by_reviewer()
        elif choice == "6":
            user_delete_category()
        elif choice == "7":
            user_delete_all_relationships()
        elif choice == "8":
            user_delete_all_nodes()
        elif choice == "9":
            print("\nClosing connection to database. Goodbye!")
            driver.close()
            break
        else:
            print("Invalid selection. Please enter a number between 1 and 9.")


if __name__ == "__main__":
    main()

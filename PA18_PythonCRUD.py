# Megan Gerth, September 7th, 2026
# Performance Assessment 1.8 - Accessing a Key-Value Database with Python

import sys
import redis


#Connect to the server
def connect_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        return r
    except redis.ConnectionError:
        print("Error: Could not connect to Redis server. Ensure Redis is running.")
        sys.exit(1)

#Function to create a new set
def create_set(r):
    #prompt for set key and members, then create set
    set_name = input("Enter the desired key for the set: ").strip()
    if not set_name:
        print("Set name cannot be empty.")
        return
    
    members_og = input("Enter members seperated by commas: ")
    members = [m.strip() for m in members_og.split(',') if m.strip()]
    if not members:
        print("No valid members provided.")
        return
    member_count = r.sadd(set_name, *members)
    print(f"Success! Created/updated set '{set_name}' with {member_count} new member(s).")

#Function to read members from a specific set
def read_set(r):
    set_name = input("Enter the key of the set to retrieve: ").strip()
    if not r.exists(set_name):
        print(f"Error: Key '{set_name}' does not exist in the database.")
        return

    #utilize smembers to retrieve all members of a set
    members = r.smembers(set_name)
    print(f"\n--- Members of Set '{set_name}' ---")
    for idx, member in enumerate(members, 1):
        print(f"{idx}. {member}")
    print("------------------------------------")

#Function to update the members of a specified set
def update_set(r):
    set_name = input("Enter the key of the set to update: ").strip()
    if not r.exists(set_name):
        print(f"Error: Key '{set_name}' does not exist.")
        return

    print("\nUpdate Options:")
    print("1. Add new members to this set")
    print("2. Remove specific members from this set")
    choice = input("Select an option (1-2): ").strip()

    if choice == '1':
        members_og = input("Enter new members to add seperated by commas: ")
        members = [m.strip() for m in members_og.split(',') if m.strip()]
        if members:
            member_count = r.sadd(set_name, *members)
            print(f"Added {member_count} new member(s) to '{set_name}'.")
        else:
            print("No members added.")
    elif choice == '2':
        members_og = input("Enter members to remove seperated by commas: ")
        members = [m.strip() for m in members_og.split(',') if m.strip()]
        if members:
            rem_count = r.srem(set_name, *members)
            print(f"Removed {rem_count} member(s) from '{set_name}'.")
        else:
            print("No members removed.")
    else:
        print("Invalid choice.")

#Delete a specifed set from the database
def delete_set(r):
    set_name = input("Enter the key of the set to delete: ").strip()

    if not r.exists(set_name):
        print(f"Error: Key '{set_name}' does not exist.")
        return

    confirm = input(f"Are you sure you want to delete set '{set_name}'? (y/n): ").strip()
    if confirm == 'y':
        r.delete(set_name)
        print("Successfully deleted.")
    else:
        print("Operation cancelled.")

#Delete all data from database
def delete_all_data(r):
    confirm = input("WARNING: This will erase ALL data in the database. Continue? (yes/no): ").strip().lower()
    if confirm == 'yes':
        r.flushdb()
        print("All records successfully deleted.")
    else:
        print("Operation cancelled.")

#Combine functions together with menu in main function
def main():
    r = connect_redis()

    while True:
        print("--- REDIS SET MANAGEMENT MENU ---")
        print("1. Create a new set")
        print("2. Retrieve members from a set")
        print("3. Update members of a set")
        print("4. Delete a specific set")
        print("5. Delete ALL data from database")
        print("6. Exit")
        print("----------------------------------")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            create_set(r)
        elif choice == '2':
            read_set(r)
        elif choice == '3':
            update_set(r)
        elif choice == '4':
            delete_set(r)
        elif choice == '5':
            delete_all_data(r)
        elif choice == '6':
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

if __name__ == '__main__':
    main()
            
              
    


                

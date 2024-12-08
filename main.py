from datetime import datetime
import mysql.connector
from mydb import get_db_connection

# Current user ID
current_user_id = None


# Function to register a new user
def register_user():
    connection = get_db_connection()
    cursor = connection.cursor()

    username = input("Enter a username: ")
    password = input("Enter a password (min 5 characters): ")
    if len(password) < 5:
        print("Error: Password must be at least 5 characters.")
        return

    try:
        query = "INSERT INTO user_info (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        connection.commit()
        print("User registered successfully!")
    except mysql.connector.IntegrityError:
        print("Error: Username already exists.")
    finally:
        cursor.close()
        connection.close()

# Function to log in an existing user
def login_user():
    global current_user_id
    connection = get_db_connection()
    cursor = connection.cursor()

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    query = "SELECT user_id, password FROM user_info WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result:
        user_id, stored_password = result
        if password == stored_password:
            current_user_id = user_id
            print("Login successful!")
        else:
            print("Error: Incorrect password.")
    else:
        print("Error: Username not found.")

    cursor.close()
    connection.close()

# Function to add an expense 
def add_expense(amount, category, description, current_user_id):
    
    connection = get_db_connection()
    cursor = connection.cursor()
    expense = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "category": category,
        "description": description
    }
    print(current_user_id)
    # Insert the expense record into the database
    query = "INSERT INTO expense_data (user_id, amount, category, description, date) VALUES (%s, %s, %s, %s, %s)"
    values = (current_user_id, amount, category, description, expense["date"])
    cursor.execute(query, values)
    connection.commit()

    print("Expense recorded successfully!")
    cursor.close()
    connection.close()

# Function to validate input
def validate_input(prompt, input_type=float):
    while True:
        try:
            value = input_type(input(prompt))
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Invalid input. Please enter a positive numeric value.")

# Function to set the monthly budget for the logged-in user
def set_monthly_budget(amount):
    if current_user_id is None:
        print("Error: You must be logged in to set a budget.")
        return

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if the user already has a budget
    query = "SELECT monthly_budget FROM user_budget WHERE user_id = %s"
    cursor.execute(query, (current_user_id,))
    result = cursor.fetchone()

    if result:
        # Update the existing budget
        query = "UPDATE user_budget SET monthly_budget = %s WHERE user_id = %s"
        cursor.execute(query, (amount, current_user_id))
    else:
        # Insert a new budget record
        query = "INSERT INTO user_budget (user_id, monthly_budget) VALUES (%s, %s)"
        cursor.execute(query, (current_user_id, amount))

    connection.commit()
    print(f"Monthly budget set to Rs.{amount}")
    cursor.close()
    connection.close()

# Function to display remaining budget
def display_remaining_budget():
    if current_user_id is None:
        print("Error: You must be logged in to view the budget.")
        return

    connection = get_db_connection()
    cursor = connection.cursor()

    # Get the user's monthly budget
    query = "SELECT monthly_budget FROM user_budget WHERE user_id = %s"
    cursor.execute(query, (current_user_id,))
    result = cursor.fetchone()

    if result:
        monthly_budget = result[0]
    else:
        print("Error: Monthly budget not set.")
        return

    # Calculate total expenses for the logged-in users
    query = "SELECT SUM(amount) FROM expense_data WHERE user_id = %s"
    cursor.execute(query, (current_user_id,))
    result = cursor.fetchone()
    total_spent = result[0] if result[0] is not None else 0

    remaining_budget = monthly_budget - total_spent
    print(f"Total spent so far: Rs.{total_spent}")
    print(f"Remaining budget: Rs.{remaining_budget}")

    cursor.close()
    connection.close()

# Main function 
def main():
    print("Welcome to Budget Buddy!")

    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Set Monthly Budget")
        print("4. Add an Expense")
        print("5. Display Remaining Budget")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            if current_user_id is not None:
                amount = validate_input("Enter your monthly budget: ")
                set_monthly_budget(amount)
            else:
                print("Error: You must be logged in to set a budget.")
        elif choice == '4':
            if current_user_id is not None:
                amount = validate_input("Enter expense amount: ")
                category = input("Enter category (Food, Lecture materials & stationery, Transportation, Miscellaneous): ")
                description = input("Enter a brief description: ")
                add_expense(amount, category, description)
            else:
                print("Error: You must be logged in to add expenses.")
        elif choice == '5':
            if current_user_id is not None:
                display_remaining_budget()
            else:
                print("Error: You must be logged in to view the budget.")
        elif choice == '6':
            print("Exiting Budget Buddy. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

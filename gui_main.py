import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# Assuming these functions are imported from main.py
from main import add_expense
from mydb import get_db_connection

current_user_id = None


# Register User GUI
def register_user_gui():
    def submit_registration():
        username = username_entry.get()
        password = password_entry.get()

        if len(password) < 5:
            messagebox.showerror("Error", "Password must be at least 5 characters long.")
            return
        
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = "INSERT INTO user_info (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            connection.commit()
            messagebox.showinfo("Success", "User registered successfully.")
            registration_window.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            cursor.close()
            connection.close()

    registration_window = tk.Toplevel(root)
    registration_window.title("Register")

    tk.Label(registration_window, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(registration_window, text="Password").grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(registration_window)
    password_entry = tk.Entry(registration_window, show="*")

    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    submit_button = tk.Button(registration_window, text="Register", command=submit_registration)
    submit_button.grid(row=2, columnspan=2, pady=10)

# Login User GUI
def login_user_gui():
    def submit_login():
        global current_user_id
        username = username_entry.get()
        password = password_entry.get()

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT user_id, password FROM user_info WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            user_id, stored_password = result
            print(user_id)
            if password == stored_password:
                current_user_id = user_id
                messagebox.showinfo("Success", "Login successful!")
                login_window.destroy()
                show_main_menu()  # Load main menu on successful login
            else:
                messagebox.showerror("Error", "Incorrect password.")
        else:
            messagebox.showerror("Error", "Username not found.")
        
        cursor.close()
        connection.close()

    login_window = tk.Toplevel(root)
    login_window.title("Login")
    
    tk.Label(login_window, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(login_window, text="Password").grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(login_window)
    password_entry = tk.Entry(login_window, show="*")

    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    submit_button = tk.Button(login_window, text="Login", command=submit_login)
    submit_button.grid(row=2, columnspan=2, pady=10)

# Add Expense GUI
def add_expense_gui():
    print(current_user_id)
    if current_user_id == 0:
        messagebox.showerror("Error", "You must be logged in to add expenses.")
        return

    def submit_expense():
        amount = float(amount_entry.get())
        category = category_entry.get()
        description = description_entry.get()
        add_expense(amount, category, description, current_user_id)
        messagebox.showinfo("Success", "Expense added successfully!")
        expense_window.destroy()

    expense_window = tk.Toplevel(root)
    expense_window.title("Add Expense")

    tk.Label(expense_window, text="Amount").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(expense_window, text="Category").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(expense_window, text="Description").grid(row=2, column=0, padx=10, pady=5)

    amount_entry = tk.Entry(expense_window)
    category_entry = tk.Entry(expense_window)
    description_entry = tk.Entry(expense_window)

    amount_entry.grid(row=0, column=1, padx=10, pady=5)
    category_entry.grid(row=1, column=1, padx=10, pady=5)
    description_entry.grid(row=2, column=1, padx=10, pady=5)

    submit_button = tk.Button(expense_window, text="Add Expense", command=submit_expense)
    submit_button.grid(row=3, columnspan=2, pady=10)

# Display Remaining Budget GUI
def display_remaining_budget_gui():
    if current_user_id is None:
        messagebox.showerror("Error", "You must be logged in to view the budget.")
        return

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT monthly_budget FROM user_budget WHERE user_id = %s"
    cursor.execute(query, (current_user_id,))
    result = cursor.fetchone()

    if result:
        monthly_budget = result[0]
    else:
        messagebox.showerror("Error", "Monthly budget not set.")
        return

    query = "SELECT SUM(amount) FROM expense_data WHERE user_id = %s"
    cursor.execute(query, (current_user_id,))
    result = cursor.fetchone()
    total_spent = result[0] if result[0] is not None else 0

    remaining_budget = monthly_budget - total_spent
    messagebox.showinfo("Remaining Budget", f"Total spent so far: Rs.{total_spent}\nRemaining budget: Rs.{remaining_budget}")

    cursor.close()
    connection.close()

# Set Monthly Budget GUI
def set_monthly_budget_gui():
    if current_user_id is None:
        messagebox.showerror("Error", "You must be logged in to set the budget.")
        return

    def submit_budget():
        try:
            monthly_budget = float(budget_entry.get())
            if monthly_budget <= 0:
                messagebox.error("Error", "Please enter a positive budget amount")
                return
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "INSERT INTO user_budget (user_id, monthly_budget) VALUES (%s, %s) ON DUPLICATE KEY UPDATE monthly_budget = %s"
            cursor.execute(query, (current_user_id, monthly_budget, monthly_budget))
            connection.commit()
            messagebox.showinfo("Success", "Monthly budget set successfully!")
            budget_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget value.")

    budget_window = tk.Toplevel(root)
    budget_window.title("Set Monthly Budget")

    tk.Label(budget_window, text="Monthly Budget").grid(row=0, column=0, padx=10, pady=5)
    
    budget_entry = tk.Entry(budget_window)
    budget_entry.grid(row=0, column=1, padx=10, pady=5)

    submit_button = tk.Button(budget_window, text="Set Budget", command=submit_budget)
    submit_button.grid(row=1, columnspan=2, pady=10)

# Main Menu
def show_main_menu():
    main_menu = tk.Toplevel(root)
    main_menu.title("Budget Buddy - Main Menu")

    tk.Button(main_menu, text="Add Expense", command=add_expense_gui).pack(pady=10)
    tk.Button(main_menu, text="Set Monthly Budget", command=set_monthly_budget_gui).pack(pady=10)
    tk.Button(main_menu, text="View Remaining Budget", command=display_remaining_budget_gui).pack(pady=10)

# Main Root Window
root = tk.Tk()
root.title("Budget Buddy")

# Add a welcome message
welcome_label = tk.Label(root, text="Welcome to Budget Buddy!", font=("Arial", 16, "bold"))
welcome_label.pack(pady=20)

# Add main buttons for registration and login
tk.Button(root, text="Register", command=register_user_gui).pack(pady=10)
tk.Button(root, text="Login", command=login_user_gui).pack(pady=10)

root.mainloop()

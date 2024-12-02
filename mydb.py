import mysql.connector

# Database connection function
def get_db_connection():
    connection =  mysql.connector.connect(
        host="localhost",
        user="root",
        password="hi12345",
        database="budget_buddy_db"
    )
    cursor=connection.cursor()

    #Creating the database for budget buddy
    cursor.execute("CREATE DATABASE IF NOT EXISTS budget_db ")
    print("Database created successfully")



    #Creating a table to store user data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_info( 
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        Password VARCHAR(5)NOT NULL

    )
    """)
    print("user info table created successfully.")



    #Creating a table to store expenses
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS expense_data(
        expense_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        amount DECIMAL(10,2) NOT NULL,
        category VARCHAR(50),
        description VARCHAR(100),
        date DATE NOT NULL,
        FOREIGN KEY(user_id)REFERENCES user_info(user_id)
            
    
    )                  
    """)

    print("Expense table created successfully.")

    # Creating a table to store user monthly budget
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS user_budget(
        budget_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        monthly_budget DECIMAL(10,2) NOT NULL,
        FOREIGN KEY(user_id) REFERENCES user_info(user_id)
      )
    """)
    print("User budget table created successfully.")


    cursor.close()
    return connection








    
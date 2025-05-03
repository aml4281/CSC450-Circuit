import sqlite3
import os

# Run this script to create the database and tables (For development only)
# In the final version, the database will be hosted alongside the source files

def create_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db'))

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create the projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Project (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL
        )
    ''')

    # Create the project_users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Project_User (
            project_id INTEGER,
            user_id INTEGER,
            role TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES Project (project_id),
            FOREIGN KEY (user_id) REFERENCES User (user_id),
            PRIMARY KEY (project_id, user_id)
        )
    ''')

    # Create the tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Task (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_title TEXT NOT NULL,
            task_description TEXT,
            task_status TEXT NOT NULL,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES Project (project_id)
        )
    ''')

    # Create the task_users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Task_User (
            task_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES Task (task_id),
            FOREIGN KEY (user_id) REFERENCES User (user_id),
            PRIMARY KEY (task_id, user_id)
        )
    ''')

    # Create the messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Message (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender_id INTEGER,
            project_id INTEGER,
            FOREIGN KEY (sender_id) REFERENCES User (user_id),
            FOREIGN KEY (project_id) REFERENCES Project (project_id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
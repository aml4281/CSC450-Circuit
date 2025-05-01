import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import models

# Define various functions to interact with the database

def register_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('''
            INSERT INTO User (username, password)
            VALUES (?, ?)
        ''', (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT password, user_id FROM User WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()

    if result and check_password_hash(result[0], password):
        return models.User(result[1], username) # Return user object
    else:
        return False
    
def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT username FROM User WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return models.User(user_id, result[0])  # Return user object
    else:
        return None
    
def get_user_projects(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Project.project_id, project_name FROM Project
        JOIN Project_User ON Project.project_id = Project_User.project_id
        WHERE Project_User.user_id = ?
    ''', (user_id,))
    projects = cursor.fetchall()
    conn.close()

    return [models.Project(project[0], project[1]) for project in projects]  # Return list of project objects

def get_project_users(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_id, username FROM User
        JOIN Project_User ON User.user_id = Project_User.user_id
        WHERE Project_User.project_id = ?
    ''', (project_id,))
    users = cursor.fetchall()
    conn.close()

    return [models.User(user[0], user[1]) for user in users]  # Return list of user objects

def get_project_tasks(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT task_id, task_title, task_description, task_status FROM Task
        WHERE project_id = ?
    ''', (project_id,))
    tasks = cursor.fetchall()
    conn.close()

    return [models.Task(task[0], task[1], task[2], task[3]) for task in tasks]  # Return list of task objects

def add_project(project_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Project (project_name)
        VALUES (?)
    ''', (project_name,))
    conn.commit()
    conn.close()

def add_task(task_title, task_description, task_status, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Task (task_title, task_description, task_status, project_id)
        VALUES (?, ?, ?, ?)
    ''', (task_title, task_description, task_status, project_id))
    conn.commit()
    conn.close()

def add_message(content, user_id, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Message (content, user_id, project_id)
        VALUES (?, ?, ?)
    ''', (content, user_id, project_id))
    conn.commit()
    conn.close()


    

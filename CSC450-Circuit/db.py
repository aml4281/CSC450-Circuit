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
    
def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_id FROM User WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return models.User(result[0], username)  # Return user object
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

def get_project_name(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT project_name FROM Project WHERE project_id = ?
    ''', (project_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Return project name
    else:
        return None

def get_project_users(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT User.user_id, username FROM User
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

def get_project_messages(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT message_id, content, sender_id, timestamp FROM Message
        WHERE project_id = ?
    ''', (project_id,))
    messages = cursor.fetchall()
    conn.close()

    return [models.Message(message[0], message[1], message[2], project_id, message[3]) for message in messages]  # Return list of message objects

def add_project(project_name, user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Project (project_name)
        VALUES (?)
    ''', (project_name,))

    new_id = cursor.lastrowid  # Get the ID of the new project
    cursor.execute('''
        INSERT INTO Project_User (project_id, user_id, role)
        VALUES (?, ?, ?)
    ''', (new_id, user_id, 'admin'))
    conn.commit()
    conn.close()

    return new_id  # Return the project ID of the new project

def add_task(task_title, task_description, task_status, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Task (task_title, task_description, task_status, project_id)
        VALUES (?, ?, ?, ?)
    ''', (task_title, task_description, task_status, project_id))
    conn.commit()
    conn.close()

    return cursor.lastrowid  # Return the task ID of the new task

def get_task(task_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT task_title, task_description, task_status FROM Task WHERE task_id = ?
    ''', (task_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return models.Task(task_id, result[0], result[1], result[2])  # Return task object
    else:
        return None

def assign_task_to_user(task_id, user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Task_User (task_id, user_id)
        VALUES (?, ?)
    ''', (task_id, user_id))
    conn.commit()
    conn.close()

def get_task_assignees(task_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT User.user_id, username FROM User
        JOIN Task_User ON User.user_id = Task_User.user_id
        WHERE Task_User.task_id = ?
    ''', (task_id,))
    users = cursor.fetchall()
    conn.close()

    return [user[1] for user in users]  # Return list of username strings

def add_message(content, user_id, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Message (content, sender_id, project_id)
        VALUES (?, ?, ?)
    ''', (content, user_id, project_id))
    conn.commit()
    conn.close()

def get_messages(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT message_id, content, sender_id, timestamp FROM Message
        WHERE project_id = ?
    ''', (project_id,))
    messages = cursor.fetchall()
    conn.close()

    return [models.Message(message[0], message[1], message[2], project_id, message[3]) for message in messages]  # Return list of message objects

def is_admin(user_id, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT role FROM Project_User WHERE user_id = ? AND project_id = ?
    ''', (user_id, project_id))
    result = cursor.fetchone()
    conn.close()

    return result and result[0] == 'admin'  # Return True if user is admin, False otherwise

def add_member_to_project(project_id, user_id, role):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Project_User (project_id, user_id, role)
        VALUES (?, ?, ?)
    ''', (project_id, user_id, role))
    conn.commit()
    conn.close()

def is_member(user_id, project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Project_User WHERE user_id = ? AND project_id = ?
    ''', (user_id, project_id))
    result = cursor.fetchone()
    conn.close()

    return result is not None  # Return True if user is a member, False otherwise

def remove_member_from_project(project_id, user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Delete all task assignments for the user in the project
    cursor.execute('''
        DELETE FROM Task_User WHERE user_id = ? AND task_id IN (SELECT task_id FROM Task WHERE project_id = ?)
    ''', (user_id, project_id))

    # Delete the user from the project
    cursor.execute('''
        DELETE FROM Project_User WHERE project_id = ? AND user_id = ?
    ''', (project_id, user_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Delete all associations with tasks and users
    cursor.execute('''
        DELETE FROM Task_User WHERE task_id IN (SELECT task_id FROM Task WHERE project_id = ?)
    ''', (project_id,))

    # Delete all tasks associated with the project
    cursor.execute('''
        DELETE FROM Task WHERE project_id = ?
    ''', (project_id,))

    # Delete all messages associated with the project
    cursor.execute('''
        DELETE FROM Message WHERE project_id = ?
    ''', (project_id,))

    # Delete all associations with users
    cursor.execute('''
        DELETE FROM Project_User WHERE project_id = ?
    ''', (project_id,))

    cursor.execute('''
        DELETE FROM Project WHERE project_id = ?
    ''', (project_id,))

    conn.commit()
    conn.close()

    

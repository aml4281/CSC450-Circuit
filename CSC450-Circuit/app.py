from flask import Flask, render_template, request, session, redirect
import db
from dotenv import load_dotenv
import os

# Main Flask application with routing and session management

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    '''Landing page with login and registration options.'''
    return render_template('login.html')

@app.route('/go_to_register')
def go_to_register(error=False):
    '''Redirect to the registration page.'''
    return render_template('register.html', error=error)

@app.route('/register', methods=['POST'])
def register():
    '''Handle user registration.'''
    username = request.form['username']
    password = request.form['password']
    
    # Call the register_user function from db.py
    register = db.register_user(username, password)

    if not register:
        return go_to_register(True)
    else:
        return redirect('/')
    
@app.route('/login', methods=['POST'])
def login():
    '''Handle user login.'''
    username = request.form['username']
    password = request.form['password']
    
    # Call the login_user function from db.py
    user = db.login_user(username, password)

    if not user:
        return render_template('login.html', error=True)
    else:
        session['user_id'] = user.user_id # Store user object in session
        return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    '''Display the user's dashboard with their projects.'''
    if not session.get('user_id'):
        return redirect('/')
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/')
    
    # Fetch user projects
    projects = db.get_user_projects(user.user_id)
    
    return render_template('dashboard.html', username=user.username, projects=projects)

@app.route('/project/<int:project_id>')
def project(project_id):
    '''Display the project page with tasks and messages.'''
    if not session.get('user_id'):
        return redirect('/')
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/')
    
    # Fetch user projects
    projects = db.get_user_projects(user.user_id)

    # Fetch project name
    project = db.get_project_name(project_id)
    if not project:
        return redirect('/dashboard')
    
    # Fetch tasks for the project
    tasks = db.get_project_tasks(project_id)

    tasks = [task.to_dict() for task in tasks]
    for task in tasks:
        task["assigned_members"] = db.get_task_assignees(task['task_id'])

    # Fetch project users
    users = db.get_project_users(project_id)

    if user.username not in [member.username for member in users]:
        return redirect('/dashboard')

    # Fetch messages
    messages = db.get_project_messages(project_id)
    messages.sort(key=lambda x: x.date_time)
    messages = [i.to_dict() for i in messages]
    for message in messages:
        message['sender_name'] = db.get_user(message['user_id']).username
    
    return render_template('project.html', isAdmin=db.is_admin(user.user_id, project_id), username=user.username, projects=projects, project_id=project_id, project_name=project, tasks=tasks, members=[member.username for member in users], messages=messages)

@app.route('/create_project', methods=['POST'])
def create_project():
    '''Handle project creation.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_name = request.form['project_name']
    
    new_id = int(db.add_project(project_name, session.get('user_id')))

    if not new_id:
        return redirect('/dashboard')
    else:
        return redirect(f'/project/{new_id}')

@app.route('/project/add_project_member', methods=['POST'])
def add_member():
    '''Handle adding a member to a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    user_to_add = request.form['username']
    role = request.form['role']
    
    if not db.is_admin(session.get('user_id'), project_id):
        return redirect('/dashboard')
    

    user_to_add = db.get_user_by_username(user_to_add)
    if not user_to_add:
        return redirect(f'/project/{project_id}')

    # Check if user is already a member of the project
    if db.is_member(user_to_add.user_id, project_id):
        return redirect(f'/project/{project_id}')

    db.add_member_to_project(project_id, user_to_add.user_id, role)

    return redirect(f'/project/{project_id}')

@app.route('/project/remove_project_member', methods=['POST'])
def remove_member():
    '''Handle removing a member from a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    user_to_remove = request.form['username']
    
    if not db.is_admin(session.get('user_id'), project_id):
        return redirect('/dashboard')
    
    # Admin cannot remove a user if they don't exist, are not a member of the project, or are the admin themselves
    user_to_remove = db.get_user_by_username(user_to_remove)
    if not (user_to_remove and db.is_member(user_to_remove.user_id, project_id)) or user_to_remove.user_id == session.get('user_id'):
        return redirect(f'/project/{project_id}')

    db.remove_member_from_project(project_id, user_to_remove.user_id)

    return redirect(f'/project/{project_id}')

@app.route('/project/leave_project', methods=['POST'])
def leave_project():
    '''Handle a user leaving a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    
    if db.is_admin(user.user_id, project_id):
        return redirect('/dashboard')

    db.remove_member_from_project(project_id, user.user_id)

    return redirect('/dashboard')

@app.route('/project/delete_project', methods=['POST'])
def delete_project():
    '''Handle project deletion.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    if not db.is_admin(user.user_id, project_id):
        return redirect('/dashboard')

    db.delete_project(project_id)

    return redirect('/dashboard')

@app.route('/project/send_message', methods=['POST'])
def send_message():
    '''Handle sending a message in a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    content = request.form['message']
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    if not db.is_member(user.user_id, project_id):
        return redirect('/dashboard')

    db.add_message(content, user.user_id, project_id)

    return redirect(f'/project/{project_id}#messages')

@app.route('/project/add_task', methods=['POST'])
def add_task():
    '''Handle adding a task to a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    task_title = request.form['task_title']
    task_description = request.form['task_description']
    task_members = request.form.getlist('assigned_members')
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    
    if not db.is_member(user.user_id, project_id):
        return redirect('/dashboard')

    task_id = db.add_task(task_title, task_description, 'todo', project_id)
    
    # Assign task to selected members
    for member in task_members:
        member = db.get_user_by_username(member)
        if member:
            db.assign_task_to_user(task_id, member.user_id)

    return redirect(f'/project/{project_id}')

@app.route('/project/change_status', methods=['POST'])
def change_status():
    '''Handle changing the status of a task.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    task_id = request.form['task_id']
    status = request.form['task_status']

    print(project_id, task_id, status)
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    
    if not db.is_member(user.user_id, project_id):
        return redirect('/dashboard')

    db.change_task_status(task_id, status)

    return redirect(f'/project/{project_id}')

@app.route('/project/delete_task', methods=['POST'])
def delete_task():
    '''Handle deleting a task from a project.'''
    if not session.get('user_id'):
        return redirect('/')
    
    project_id = request.form['project_id']
    task_id = request.form['task_id']
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/dashboard')
    
    if not db.is_member(user.user_id, project_id):
        return redirect('/dashboard')

    db.delete_task(task_id)

    return redirect(f'/project/{project_id}')

@app.route('/logout')
def logout():
    '''Handle user logout.'''
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, session, redirect
import db
from dotenv import load_dotenv
from os import getenv

load_dotenv('.env')

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/go_to_register')
def go_to_register(error=False):
    return render_template('register.html', error=error)

@app.route('/register', methods=['POST'])
def register():
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
    if not session.get('user_id'):
        return redirect('/')
    
    user = db.get_user(session.get('user_id'))
    if not user:
        return redirect('/')
    
    # Fetch project details
    project = db.get_project(project_id)
    if not project:
        return redirect('/dashboard')
    
    # Fetch tasks for the project
    tasks = db.get_project_tasks(project_id)
    
    return render_template('project.html', username=user.username, project=project, tasks=tasks)

@app.route('/create_project', methods=['POST'])
def create_project():
    pass


@app.route('/logout')
def logout():
    pass


if __name__ == '__main__':
    app.run(debug=True)
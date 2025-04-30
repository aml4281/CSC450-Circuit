# Import the Flask library and SQLite
import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for

# Create a Flask application instance
app = Flask(__name__)

# --- Database Setup ---
DB_PATH = 'circuit.db'

# SQL statements to create the database tables
# (Full definitions needed here)
all_create_table_statements = [
    """CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY NOT NULL,
        email TEXT UNIQUE
    );""",
    """CREATE TABLE IF NOT EXISTS servers (
        server_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner_username TEXT NOT NULL,
        FOREIGN KEY (owner_username) REFERENCES users (username)
            ON UPDATE CASCADE ON DELETE CASCADE
    );""",
    """CREATE TABLE IF NOT EXISTS task_boards (
        board_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        server_id INTEGER NOT NULL,
        FOREIGN KEY (server_id) REFERENCES servers (server_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );""",
    """CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        progress TEXT DEFAULT 'To Do',
        board_id INTEGER NOT NULL,
        FOREIGN KEY (board_id) REFERENCES task_boards (board_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    );""",
    """CREATE TABLE IF NOT EXISTS server_members (
        server_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        PRIMARY KEY (server_id, username),
        FOREIGN KEY (server_id) REFERENCES servers (server_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES users (username)
            ON UPDATE CASCADE ON DELETE CASCADE
    );""",
    """CREATE TABLE IF NOT EXISTS task_assignments (
        task_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        PRIMARY KEY (task_id, username),
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES users (username)
            ON UPDATE CASCADE ON DELETE CASCADE
    );"""
]

def initialize_database(db_path=DB_PATH):
    """Connects/creates DB & tables."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Connected to database at {db_path}")
        cursor.execute("PRAGMA foreign_keys = ON;") # Enable foreign key enforcement
        for statement in all_create_table_statements:
            cursor.execute(statement)
        conn.commit()
        print("Database tables checked/created successfully.")
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close(); print("Database connection closed after init.")

# --- CSS Style Definition (Dark Mode) ---
dark_mode_css = """
<style>
    body {
        background-color: #121212; /* Very dark grey */
        color: #e0e0e0; /* Light grey text */
        font-family: sans-serif;
        margin: 20px;
        padding: 10px; /* Add some padding around the body content */
    }

    h2, h3 {
        color: #bb86fc; /* A purple accent color */
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
        margin-top: 20px; /* Add space above headings */
    }

    h2:first-of-type, h3:first-of-type {
         margin-top: 0; /* Remove top margin from the very first heading */
    }


    a {
        color: #03dac6; /* A teal accent color for links */
        text-decoration: none; /* Remove underline from links */
    }

    a:hover {
        color: #ffffff;
        text-decoration: underline; /* Add underline on hover */
    }

    ul {
        list-style: none;
        padding: 0;
    }

    li {
        background-color: #1e1e1e; /* Slightly lighter dark background for items */
        border: 1px solid #333;
        margin-bottom: 10px;
        padding: 15px; /* Increase padding inside list items */
        border-radius: 4px;
    }

    /* Style specifically for server links in the dashboard */
    .server-list li a { /* Use a class for more specific targeting if needed */
        font-weight: bold;
        display: block; /* Make the whole list item area clickable potentially */
    }

    form {
        background-color: #1e1e1e;
        padding: 20px; /* Increase padding inside forms */
        border-radius: 4px;
        border: 1px solid #333;
        margin-top: 15px;
    }

    /* Add labels for better accessibility and structure */
    label {
        display: block; /* Make labels appear on their own line */
        margin-bottom: 5px;
        color: #aaa; /* Slightly lighter label text */
        font-size: 0.9em;
    }

    input[type="text"], textarea, select {
        background-color: #333;
        color: #e0e0e0;
        border: 1px solid #555;
        padding: 10px; /* Increase padding */
        margin-bottom: 15px; /* Increase spacing below inputs */
        border-radius: 4px;
        width: 100%; /* Make inputs take full width of container */
        box-sizing: border-box; /* Include padding and border in the element's total width */
    }

    textarea {
        height: 80px; /* Slightly taller textarea */
        resize: vertical; /* Allow vertical resizing */
    }

    select[multiple] {
         height: 120px; /* Taller multi-select */
    }

    /* Remove <br> tags visually if using labels, rely on block display and margins */
    form br {
       display: none;
    }

    input[type="submit"] {
        background-color: #bb86fc;
        color: #121212;
        border: none;
        padding: 12px 20px; /* Larger button padding */
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        margin-top: 10px; /* Add space above submit button */
        transition: background-color 0.2s ease; /* Smooth hover effect */
    }

    input[type="submit"]:hover {
        background-color: #9e6fda;
    }

    hr {
        border: none;
        border-top: 1px solid #333;
        margin-top: 25px; /* Increase spacing around hr */
        margin-bottom: 25px;
    }

    /* Simple class for messages/alerts */
    .alert {
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid transparent;
        border-radius: 4px;
        color: #e0e0e0;
        background-color: #333;
    }
    .alert-error {
         border-color: #cf6679; /* Error color */
         background-color: rgba(207, 102, 121, 0.2); /* Slight red background */
    }

</style>
"""

# --- HTML Templates (Regular Strings) ---
# Using {{ css | safe }} to inject the CSS string.
login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Circuit</title>
    {{ css | safe }}
</head>
<body>
    <h2>Login / Register</h2>
    <form method="post" action="{{ url_for('login') }}">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <input type="submit" value="Login / Register">
    </form>
    </body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Circuit</title>
    {{ css | safe }}
</head>
<body>
    <h2>Circuit Dashboard</h2>
    <p>Welcome, {{ username }}!</p>
    <hr>
    <h3>Your Servers:</h3>
    <ul class="server-list">
        {% for server_id, server_info in user_servers.items() %}
            {# Create a link to the specific server page, passing username #}
            <li><a href="{{ url_for('view_server', server_id=server_id, username=username) }}">{{ server_info.name }}</a> (ID: {{ server_id }})</li>
        {% else %}
            <li>No servers joined or created yet.</li>
        {% endfor %}
    </ul>

    <h3>Create New Server:</h3>
    {# Pass username in the action URL #}
    <form method="post" action="{{ url_for('create_server', username=username) }}">
        <label for="server_name">Server Name:</label>
        <input type="text" id="server_name" name="server_name" required>
        <input type="submit" value="Create Server">
    </form>
    <hr>
    <p><a href="{{ url_for('home') }}">Logout</a></p>
</body>
</html>
"""

server_page_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Server: {{ server.name }} - Circuit</title>
    {{ css | safe }}
</head>
<body>
    <h2>Server: {{ server.name }} (ID: {{ server_id }})</h2>
    <p>Owner: {{ server.owner_username }}</p>
    {# Link back to dashboard, passing username #}
    <p><a href="{{ url_for('dashboard', username=username) }}">Back to Dashboard</a></p>
    <hr>

    <h3>Tasks (on Board: {{ board.name }})</h3>
     {# Check if board exists before trying to list tasks #}
    {% if board and board.board_id %}
        <ul>
            {% for task_id, task_info in board_tasks.items() %}
                <li>
                    <strong>{{ task_info.name }}</strong> (ID: {{ task_id }})<br>
                    Description: {{ task_info.description or 'N/A' }}<br>
                    Assigned: {{ task_info.assigned_users | join(', ') if task_info.assigned_users else 'None' }}<br>
                    Status: {{ task_info.progress }}
                </li>
            {% else %}
                <li>No tasks yet on this board.</li>
            {% endfor %}
        </ul>
        <hr>
        <h3>Create New Task</h3>
        {# *** CORRECTED board_id access in url_for *** #}
        <form method="post" action="{{ url_for('create_task', server_id=server_id, board_id=board.board_id, username=username) }}">
            <label for="task_name">Task Name:</label>
            <input type="text" id="task_name" name="task_name" required>

            <label for="task_description">Description:</label>
            <textarea id="task_description" name="task_description"></textarea>

            <label for="assigned_users">Assign Users:</label>
            <select id="assigned_users" name="assigned_users" multiple>
                {% for user in all_users %}
                    <option value="{{ user }}">{{ user }}</option>
                {% else %}
                     <option value="" disabled>No users found</option>
                {% endfor %}
            </select>

            <input type="submit" value="Create Task">
        </form>
    {% else %}
        {# Display message if no board exists for this server #}
        <p class="alert">No task board found or configured for this server.</p>
    {% endif %}


    <hr>
    <p><a href="{{ url_for('home') }}">Logout</a></p>
    {# Display error message if passed from route #}
    {% if error %}
        <p class='alert alert-error'>{{ error }}</p>
    {% endif %}
</body>
</html>
"""

# --- Helper Function for DB Connection ---
def get_db_conn():
    """Establishes a database connection, enables foreign keys, and sets row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

# --- Routes ---

@app.route('/', methods=['GET'])
def home():
    """Displays the login page."""
    return render_template_string(login_html, css=dark_mode_css)

@app.route('/login', methods=['POST'])
def login():
    """Handles user login/registration using the database."""
    username = request.form.get('username')
    error_message = None
    conn = None
    if not username or not username.strip(): error_message = "Username cannot be empty."
    else:
        username = username.strip(); dummy_email = f'{username}@example.com'
        try:
            conn = get_db_conn(); cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                try:
                    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, dummy_email)); conn.commit()
                    print(f"User '{username}' registered in DB.")
                except sqlite3.IntegrityError as e: print(f"DB Integrity Error: {e}"); error_message = "Username might be taken."; conn.rollback()
            else: print(f"User '{username}' found in DB.")
        except sqlite3.Error as e: print(f"DB Error: {e}"); error_message = "DB error during login."; conn.rollback()
        finally:
            if conn: conn.close()
    if error_message:
        template_with_error = login_html.replace('', f"<p class='alert alert-error'>{error_message}</p>")
        return render_template_string(template_with_error, css=dark_mode_css), 400
    else: return redirect(url_for('dashboard', username=username))


@app.route('/dashboard/<username>', methods=['GET'])
def dashboard(username):
    """Displays the user's dashboard using data from the database."""
    conn = None; user_servers_info = {}
    try:
        conn = get_db_conn(); cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if not cursor.fetchone(): return redirect(url_for('home'))
        cursor.execute("""SELECT s.server_id, s.name FROM servers s JOIN server_members sm ON s.server_id = sm.server_id WHERE sm.username = ? ORDER BY s.name COLLATE NOCASE""", (username,))
        user_servers = cursor.fetchall()
        user_servers_info = {row['server_id']: {'name': row['name']} for row in user_servers}
    except sqlite3.Error as e: print(f"DB Error fetching dashboard: {e}")
    finally:
        if conn: conn.close()
    return render_template_string(dashboard_html, username=username, user_servers=user_servers_info, css=dark_mode_css)

@app.route('/create_server/<username>', methods=['POST'])
def create_server(username):
    """Creates a new server, default board, and adds owner as member in the database."""
    server_name = request.form.get('server_name'); conn = None
    if not server_name or not server_name.strip(): return "Server name required.", 400
    server_name = server_name.strip()
    try:
        conn = get_db_conn(); cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if not cursor.fetchone(): return "User not found.", 400
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO servers (name, owner_username) VALUES (?, ?)", (server_name, username))
        new_server_id = cursor.lastrowid; assert new_server_id
        default_board_name = f"{server_name} Board"
        cursor.execute("INSERT INTO task_boards (name, server_id) VALUES (?, ?)", (default_board_name, new_server_id))
        new_board_id = cursor.lastrowid; assert new_board_id
        cursor.execute("INSERT INTO server_members (server_id, username) VALUES (?, ?)", (new_server_id, username))
        conn.commit(); print(f"Server '{server_name}' (ID: {new_server_id}) created.")
    except sqlite3.Error as e: print(f"DB Error creating server: {e}"); conn.rollback(); return f"DB error: {e}", 500
    finally:
        if conn: conn.close()
    return redirect(url_for('dashboard', username=username))


@app.route('/server/<int:server_id>/<username>', methods=['GET'])
def view_server(server_id, username):
    """Displays server page with details and tasks fetched from the database."""
    conn = None; server_info = None; board_info = None
    board_tasks_info = {}; all_user_list = []; error_message = None
    try:
        conn = get_db_conn(); cursor = conn.cursor()
        # Check user exists
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if not cursor.fetchone(): return redirect(url_for('home'))
        # Check membership
        cursor.execute("SELECT 1 FROM server_members WHERE server_id = ? AND username = ?", (server_id, username))
        if not cursor.fetchone(): return "Access Denied: Not a member.", 403
        # Fetch server details
        cursor.execute("SELECT server_id, name, owner_username FROM servers WHERE server_id = ?", (server_id,))
        server_info = cursor.fetchone()
        if not server_info: return "Server not found.", 404
        # Fetch board details (assuming first board)
        cursor.execute("SELECT board_id, name FROM task_boards WHERE server_id = ? LIMIT 1", (server_id,))
        board_info = cursor.fetchone() # Will be None if no board found

        if board_info:
            # Fetch tasks for this board
            cursor.execute("SELECT task_id, name, description, progress FROM tasks WHERE board_id = ?", (board_info['board_id'],))
            tasks_cursor = cursor.fetchall()
            task_ids = [row['task_id'] for row in tasks_cursor]
             # Use dict comprehension to create task info, converting Row to dict and adding empty list
            board_tasks_info = { row['task_id']: dict(row, assigned_users=[]) for row in tasks_cursor }

            # Fetch assignments for these tasks
            if task_ids:
                placeholders = ','.join('?' * len(task_ids))
                sql_assignments = f"SELECT task_id, username FROM task_assignments WHERE task_id IN ({placeholders})"
                cursor.execute(sql_assignments, task_ids)
                assignments = cursor.fetchall()
                for assignment in assignments:
                    # Use .get() for safer access in case task_id somehow not in dict (though it should be)
                    task_dict = board_tasks_info.get(assignment['task_id'])
                    if task_dict:
                        task_dict['assigned_users'].append(assignment['username'])
        # else: board_info remains None if no board found

        # Fetch all users for dropdown
        cursor.execute("SELECT username FROM users ORDER BY username COLLATE NOCASE")
        all_users = cursor.fetchall()
        all_user_list = [row['username'] for row in all_users]

    except sqlite3.Error as e:
         print(f"DB error viewing server {server_id}: {e}"); error_message = "DB error loading server page."
         # Provide defaults if essential info is missing to prevent further errors
         server_info = server_info or {} # If None, make it empty dict
         board_info = board_info # Keep it None or the Row object
         board_tasks_info = board_tasks_info or {}
         all_user_list = all_user_list or []
    finally:
        if conn: conn.close()

    # *** CORRECTED Fallback logic: Assign placeholder dict if board_info is still None ***
    if board_info is None:
         board_info = {'board_id': None, 'name': '[No Board Found]'}
         # Optionally set error message if not already set by DB error
         # error_message = error_message or "No task board found for this server."

    # Check if server fetch failed critically
    if not server_info and not error_message:
        error_message = "Server data could not be loaded."

    return render_template_string(server_page_html,
                                  username=username, server_id=server_id, server=server_info,
                                  board=board_info, board_tasks=board_tasks_info,
                                  all_users=all_user_list, css=dark_mode_css, error=error_message)


@app.route('/server/<int:server_id>/board/<int:board_id>/create_task/<username>', methods=['POST'])
def create_task(server_id, board_id, username):
    """Creates a new task and assignments in the database."""
    task_name = request.form.get('task_name'); task_description = request.form.get('task_description', '').strip()
    assigned_users_list = request.form.getlist('assigned_users'); conn = None
    if not task_name or not task_name.strip(): return "Task name required.", 400
    task_name = task_name.strip()

    # Handle case where board_id might be None if no board exists
    if board_id is None or board_id == 0: # Check for None or potentially 0 if template logic changes
        return "Cannot create task: No valid board selected.", 400

    try:
        conn = get_db_conn(); cursor = conn.cursor()
        # Authorization checks
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if not cursor.fetchone(): return redirect(url_for('home'))
        cursor.execute("SELECT server_id FROM task_boards WHERE board_id = ?", (board_id,))
        board_check = cursor.fetchone()
        if not board_check or board_check['server_id'] != server_id: return "Invalid board/server.", 400
        cursor.execute("SELECT 1 FROM server_members WHERE server_id = ? AND username = ?", (server_id, username))
        if not cursor.fetchone(): return "Access Denied.", 403
        # Validate assigned users
        valid_assigned_users = []
        if assigned_users_list:
            placeholders = ','.join('?' * len(assigned_users_list))
            sql_check_users = f"SELECT username FROM users WHERE username IN ({placeholders})"
            cursor.execute(sql_check_users, assigned_users_list)
            valid_assigned_users = [row['username'] for row in cursor.fetchall()]

        # Insert task and assignments
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO tasks (name, description, progress, board_id) VALUES (?, ?, ?, ?)", (task_name, task_description, 'To Do', board_id))
        new_task_id = cursor.lastrowid; assert new_task_id
        if valid_assigned_users:
            assignment_data = [(new_task_id, user) for user in valid_assigned_users]
            cursor.executemany("INSERT INTO task_assignments (task_id, username) VALUES (?, ?)", assignment_data)
        conn.commit()
        print(f"Task '{task_name}' (ID: {new_task_id}) created. Assigned to: {valid_assigned_users}")
    except sqlite3.Error as e:
        print(f"DB error creating task: {e}"); conn.rollback(); return f"DB error: {e}", 500
    finally:
        if conn: conn.close()
    return redirect(url_for('view_server', server_id=server_id, username=username))


# --- Run the App ---
if __name__ == '__main__':
    initialize_database() # Initialize DB connection and create tables if needed
    app.run(host='127.0.0.1', port=5000, debug=True) # Use 127.0.0.1 for local access only
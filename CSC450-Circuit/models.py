

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.projects = []

class Project:
    def __init__(self, project_id, project_name):
        self.project_id = project_id
        self.project_name = project_name
        self.tasks = []
        self.users = []

class Task:
    def __init__(self, task_id, task_title, task_description, task_status):
        self.task_id = task_id
        self.task_title = task_title
        self.task_description = task_description
        self.task_status = task_status
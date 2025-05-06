from datetime import datetime
from pytz import timezone, utc

# Defines the class models used throughout the application
# All classes have a to_dict method, allowing them to be easily serialized to JSON for the javascript frontend

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.projects = []

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "projects": [project.to_dict() for project in self.projects]
        }


class Project:
    def __init__(self, project_id, project_name):
        self.project_id = project_id
        self.project_name = project_name
        self.tasks = []
        self.users = []

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "tasks": [task.to_dict() for task in self.tasks],
            "users": [user.to_dict() for user in self.users]
        }


class Task:
    def __init__(self, task_id, task_title, task_description, task_status):
        self.task_id = task_id
        self.task_title = task_title
        self.task_description = task_description
        self.task_status = task_status

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "task_description": self.task_description,
            "task_status": self.task_status
        }
    
class Message:
    def __init__(self, message_id, content, user_id, project_id, date_time):
        self.message_id = message_id
        self.content = content
        self.user_id = user_id
        self.project_id = project_id
        self.date_time = date_time

        # Convert UTC to Eastern Time
        dt_object = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        dt_object = dt_object.replace(tzinfo=utc)
        local_dt = dt_object.astimezone(timezone('America/New_York'))
        
        self.date = local_dt.strftime("%m/%d")
        self.time = local_dt.strftime("%I:%M %p")

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "content": self.content,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "date_time": self.date_time,
            "date": self.date,
            "time": self.time
        }
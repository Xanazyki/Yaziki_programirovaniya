from .storage import TaskStorage

class TaskCommands:
    def __init__(self):
        self.storage = TaskStorage()
        self.tasks = self.storage.load_tasks()

    def add_task(self, title, description='', priority='medium'):
        pass

    def list_tasks(self, status=None, priority=None):
        pass

    def complete_task(self, task_id):
        pass

    def delete_task(self, task_id):
        pass
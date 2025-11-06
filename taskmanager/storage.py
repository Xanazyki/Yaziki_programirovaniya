import json
import os
from .models import Task

class TaskStorage:
    def __init__(self, filename='tasks.json'):
        self.filename = filename

    def save_tasks(self, tasks):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in tasks], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f'Ошибка сохранения: {e}')
            return False
        
    def load_tasks(self):
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except Exception as e:
            print(f'Ошибка загрузки: {e}')
            return []
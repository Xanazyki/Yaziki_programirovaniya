from .storage import TaskStorage
from .models import Task
from datetime import datetime

class TaskCommands:
    def __init__(self):
        self.storage = TaskStorage()
        self.tasks = self.storage.load_tasks()

    def _save(self):
        return self.storage.save_tasks(self.tasks)
    
    def _get_next_id(self):
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def add_task(self, title, description='', priority='medium'):
        try:
            new_task = Task(
                id=self._get_next_id(),
                title=title,
                description=description,
                priority=priority
            )

            self.tasks.append(new_task)
            if self._save():
                print(f'Задача добавлена (ID: {new_task.id})')
                return True
            else:
                return False
        except Exception as e:
            print(f'Ошибка при добавлении задачи: {e}')
            return False

    def list_tasks(self, status=None, priority=None):
        filtered_tasks = self.tasks

        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority]

        if not filtered_tasks:
            print('Задачи не найдены')
            return True
        
        total = len(filtered_tasks)
        completed = len([t for t in filtered_tasks if t.status == 'completed'])

        print(f'\nСписок задач ({completed}/{total} выполнено):')
        print('-' * 50)

        for task in filtered_tasks:
            print(task.detailed_str())
            print('-' * 50)

        return True

    def complete_task(self, task_id):
        task = next((t for t in self.tasks if t.id == task_id), None)

        if not task:
            print(f'Задача с ID {task_id} не найдена')
            return False
        
        if task.status == 'completed':
            print(f'Задача {task_id} уже выполнена')
            return True
        
        task.mark_completed()
        if self._save():
            print(f'Задача {task_id} отмечена как выполнена')
            return True
        else:
            print('Ошибка сохранения')
            return False

    def delete_task(self, task_id):
        task = next((t for t in self.tasks if t.id == task_id), None)

        if not task:
            print(f'Задача с ID {task_id} не найдена')
            return False
        
        self.tasks = [t for t in self.tasks if t.id != task_id]

        if self._save():
            print(f'Задача {task_id} удалена')
            return True
        else:
            print('Ошибка сохранения изменений')
            self.tasks.append(task)
            return False
        
    def get_task_stats(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == 'completed'])
        pending = total - completed

        priority_stats = {
            'high': len([t for t in self.tasks if t.priority == 'hight']),
            'medium': len([t for t in self.tasks if t.priority == 'medium']),
            'low': len([t for t in self.tasks if t.priority == 'low'])
        }

        print(f'\nСтатистика задач:')
        print(f'   Всего задач: {total}')
        print(f'   Выполнено: {completed}')
        print(f'   Ожидает: {pending}')
        print(f'   Высокий приоритет: {priority_stats['high']}')
        print(f'   Средний приоритет: {priority_stats['medium']}')
        print(f'   Низкий приоритет: {priority_stats['low']}')

        return True
class Task:
    def __init__(self, id, title, description='', status='pending', priority='medium'):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
    
    def __str__(self):
        stat_text = '[V]' if self.status == 'completed' else '[ ]'
        return f'{self.id:2d}. {stat_text} {self.title} (Важность: {self.priority})'

tasks = []
current_id = 1

def add(title, descriptin='', priority='medium'):
    "Добавление задачи"
    global current_id
    task = Task(current_id, title, descriptin, 'pending', priority)
    tasks.append(task)
    current_id += 1
    print(f'Задача добавлена: {task}')
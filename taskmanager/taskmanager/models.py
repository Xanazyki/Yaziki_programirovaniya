from datetime import datetime

class Task:
    def __init__(self, id, title, description='', status='pending', priority='medium', created_date=None, completed_date=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_date = created_date or datetime.now().isoformat()
        self.completed_date = completed_date

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_date': self.created_date,
            'completed_date': self.completed_date
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            created_date=data.get('created_date'),
            completed_date=data.get('completed_date')
        )
    
    def mark_completed(self):
        self.status = 'completed'
        self.completed_date = datetime.now().isoformat()
    
    def __str__(self):
        status_display = '[X]' if self.status == 'completed' else '[ ]'
        return f'{self.id:3d}. {status_display} {self.title} ({self.priority})'

    def detailed_str(self):
        status_display = 'выполнена' if self.status == 'completed' else 'не выполнена'

        created = datetime.fromisoformat(self.created_date).strftime('%d.%m.%Y %H:%M')
        completed = ''
        if self.completed_date:
            completed = f'\n Завершена: {datetime.fromisoformat(self.completed_date).strftime('%d.%m.%Y %H:%M')}'

        return f"""{self.id:3d}. {self.title}
    Описание: {self.description or 'нет'}
    Статус: {status_display}
    Приоритет: {self.priority}
    Создана: {created}{completed}"""
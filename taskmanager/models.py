class Task:
    def __init__(self, id, title, description='', status='pending', priority='medium', created_date=None, completed_date=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_date = created_date
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
    
    def __str__(self):
        return f'{self.id}. {self.title} [{self.status}]'
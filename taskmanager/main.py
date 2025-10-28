class Task:
    def __init__(self, id, title, description, status, priority):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
    
    def __str__(self):
        stat_text = '[V]' if self.status == 'completed' else '[ ]'
        return f'{self.id:2d}. {stat_text} {self.title} (Важность: {self.priority})'
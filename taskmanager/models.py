"""
Модуль моделей данных для менеджера задач.

Содержит класс Task для представления задачи и связанную логику.
"""

from datetime import datetime
from typing import Optional


class Task:
    """Класс, представляющий задачу в системе.
    
    Attributes:
        id (int): Уникальный идентификатор задачи
        title (str): Заголовок задачи
        description (str): Описание задачи
        status (str): Статус задачи ('pending', 'completed')
        priority (str): Приоритет задачи ('low', 'medium', 'high')
        created_at (datetime): Дата создания
        due_date (date): Срок выполнения
        completed_at (datetime): Дата завершения
    """
    
    def __init__(self, title: str, description: str = "", 
                 status: str = "pending", priority: str = "medium",
                 due_date: Optional[datetime] = None, 
                 created_at: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None,
                 task_id: Optional[int] = None):
        """Инициализирует объект задачи.
        
        Args:
            title: Заголовок задачи (обязательный)
            description: Описание задачи
            status: Статус задачи ('pending' или 'completed')
            priority: Приоритет задачи ('low', 'medium', 'high')
            due_date: Срок выполнения задачи
            created_at: Дата создания задачи
            completed_at: Дата завершения задачи
            task_id: ID задачи в базе данных
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at or datetime.now()
        self.due_date = due_date
        self.completed_at = completed_at
    
    def __str__(self) -> str:
        """Возвращает читаемое строковое представление задачи.
        
        Returns:
            str: Форматированная строка с данными задачи
        """
        due_date_str = self.due_date.strftime("%d.%m.%Y") if self.due_date else "Нет"
        status_icon = "✅" if self.status == "completed" else "⏳"
        priority_icon = {"low": "🔵", "medium": "🟡", "high": "🔴"}.get(self.priority, "⚪")
        
        return (f"{status_icon} ID: {self.id} | {self.title}\n"
                f"   📝 {self.description}\n"
                f"   {priority_icon} Приоритет: {self.priority} | 📅 Срок: {due_date_str}")
    
    def mark_completed(self):
        """Отмечает задачу как выполненную и устанавливает время завершения."""
        self.status = "completed"
        self.completed_at = datetime.now()
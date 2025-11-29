"""
Модуль моделей данных для менеджера задач.

Содержит классы Task, TaskStatus и Priority для представления задач.
"""

import json
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Перечисление статусов задачи."""
    PENDING = "pending"
    COMPLETED = "completed"


class Priority(Enum):
    """Перечисление приоритетов задачи."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task:
    """Класс, представляющий задачу в менеджере задач.
    
    Attributes:
        id (int): Уникальный идентификатор задачи.
        title (str): Название задачи.
        description (str): Подробное описание задачи.
        status (TaskStatus): Текущий статус задачи.
        priority (Priority): Приоритет выполнения задачи.
        created_at (str): Дата и время создания задачи.
        due_date (str): Срок выполнения задачи.
        completed_at (str): Дата и время завершения задачи.
    """
    
    def __init__(self, title, description="", priority=Priority.MEDIUM, due_date=None):
        """Инициализирует новую задачу.
        
        Args:
            title (str): Название задачи.
            description (str, optional): Описание задачи. По умолчанию "".
            priority (Priority, optional): Приоритет задачи. По умолчанию Priority.MEDIUM.
            due_date (str, optional): Срок выполнения в формате ГГГГ-ММ-ДД. По умолчанию None.
        """
        self.id = None
        self.title = title
        self.description = description
        self.status = TaskStatus.PENDING
        self.priority = priority
        self.created_at = datetime.now().isoformat()
        self.due_date = due_date
        self.completed_at = None

    def to_dict(self):
        """Преобразует объект задачи в словарь для сериализации.
        
        Returns:
            dict: Словарь с данными задачи.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "due_date": self.due_date,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект задачи из словаря.
        
        Args:
            data (dict): Словарь с данными задачи.
            
        Returns:
            Task: Объект задачи.
        """
        task = cls(data["title"], data.get("description", ""))
        task.id = data["id"]
        task.description = data.get("description", "")
        task.status = TaskStatus(data["status"])
        task.priority = Priority(data["priority"])
        task.created_at = data["created_at"]
        task.due_date = data.get("due_date")
        task.completed_at = data.get("completed_at")
        return task

    def mark_completed(self):
        """Отмечает задачу как выполненную."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()

    def __str__(self):
        """Возвращает строковое представление задачи.
        
        Returns:
            str: Строковое представление задачи.
        """
        status_icon = "✓" if self.status == TaskStatus.COMPLETED else "○"
        priority_icon = {
            Priority.LOW: "⬇",
            Priority.MEDIUM: "●",
            Priority.HIGH: "⬆"
        }
        return f"{status_icon} [{priority_icon[self.priority]}] {self.title} (ID: {self.id})"
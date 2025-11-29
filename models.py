import json
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task:
    def __init__(self, title, description="", priority=Priority.MEDIUM, due_date=None):
        self.id = None
        self.title = title
        self.description = description
        self.status = TaskStatus.PENDING
        self.priority = priority
        self.created_at = datetime.now().isoformat()
        self.due_date = due_date
        self.completed_at = None

    def to_dict(self):
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
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()

    def __str__(self):
        status_icon = "✓" if self.status == TaskStatus.COMPLETED else "○"
        priority_icon = {
            Priority.LOW: "⬇",
            Priority.MEDIUM: "●",
            Priority.HIGH: "⬆"
        }
        return f"{status_icon} [{priority_icon[self.priority]}] {self.title} (ID: {self.id})"
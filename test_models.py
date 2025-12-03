"""
Тесты для модуля models.py
"""

import unittest
from datetime import datetime
from models import Task, TaskStatus, Priority


class TestTaskStatusEnum(unittest.TestCase):
    """Тесты для перечисления статусов задач."""
    
    def test_enum_values(self):
        """Проверка значений перечисления."""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")


class TestPriorityEnum(unittest.TestCase):
    """Тесты для перечисления приоритетов."""
    
    def test_enum_values(self):
        """Проверка значений перечисления."""
        self.assertEqual(Priority.LOW.value, "low")
        self.assertEqual(Priority.MEDIUM.value, "medium")
        self.assertEqual(Priority.HIGH.value, "high")


class TestTaskClass(unittest.TestCase):
    """Тесты для класса Task."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.task_title = "Test Task"
        self.task_description = "Test Description"
        self.task = Task(self.task_title, self.task_description, Priority.HIGH, "2024-12-31")
    
    def test_task_initialization(self):
        """Тест инициализации задачи."""
        self.assertEqual(self.task.title, self.task_title)
        self.assertEqual(self.task.description, self.task_description)
        self.assertEqual(self.task.priority, Priority.HIGH)
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertEqual(self.task.due_date, "2024-12-31")
        self.assertIsNone(self.task.id)
        self.assertIsNone(self.task.completed_at)
    
    def test_task_initialization_defaults(self):
        """Тест инициализации задачи со значениями по умолчанию."""
        task = Task("Simple Task")
        self.assertEqual(task.title, "Simple Task")
        self.assertEqual(task.description, "")
        self.assertEqual(task.priority, Priority.MEDIUM)
        self.assertIsNone(task.due_date)
    
    def test_to_dict_method(self):
        """Тест метода преобразования в словарь."""
        task_dict = self.task.to_dict()
        
        self.assertIsNone(task_dict["id"])
        self.assertEqual(task_dict["title"], self.task_title)
        self.assertEqual(task_dict["description"], self.task_description)
        self.assertEqual(task_dict["status"], TaskStatus.PENDING.value)
        self.assertEqual(task_dict["priority"], Priority.HIGH.value)
        self.assertEqual(task_dict["due_date"], "2024-12-31")
        self.assertIsNone(task_dict["completed_at"])
        self.assertIsNotNone(task_dict["created_at"])
    
    def test_from_dict_method(self):
        """Тест создания задачи из словаря."""
        task_data = {
            "id": 1,
            "title": "Task from dict",
            "description": "Description from dict",
            "status": "completed",
            "priority": "low",
            "created_at": "2024-01-01T10:00:00",
            "due_date": "2024-12-31",
            "completed_at": "2024-01-02T10:00:00"
        }
        
        task = Task.from_dict(task_data)
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Task from dict")
        self.assertEqual(task.description, "Description from dict")
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.priority, Priority.LOW)
        self.assertEqual(task.created_at, "2024-01-01T10:00:00")
        self.assertEqual(task.due_date, "2024-12-31")
        self.assertEqual(task.completed_at, "2024-01-02T10:00:00")
    
    def test_from_dict_method_missing_fields(self):
        """Тест создания задачи из словаря с отсутствующими полями."""
        task_data = {
            "id": 1,
            "title": "Minimal task",
            "status": "pending",
            "priority": "medium",
            "created_at": "2024-01-01T10:00:00"
        }
        
        task = Task.from_dict(task_data)
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Minimal task")
        self.assertEqual(task.description, "")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.priority, Priority.MEDIUM)
        self.assertIsNone(task.due_date)
        self.assertIsNone(task.completed_at)
    
    def test_mark_completed_method(self):
        """Тест отметки задачи как выполненной."""
        self.task.mark_completed()
        
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(self.task.completed_at)
    
    def test_str_representation(self):
        """Тест строкового представления задачи."""
        task_str = str(self.task)
        
        self.assertIn("○", task_str)  # символ незавершенной задачи
        self.assertIn("⬆", task_str)  # символ высокого приоритета
        self.assertIn(self.task_title, task_str)
        
        # Проверка для завершенной задачи
        self.task.mark_completed()
        completed_str = str(self.task)
        self.assertIn("✓", completed_str)  # символ завершенной задачи
    
    def test_invalid_priority_enum_conversion(self):
        """Тест обработки неверного значения приоритета при создании из словаря."""
        task_data = {
            "id": 1,
            "title": "Invalid priority task",
            "status": "pending",
            "priority": "invalid_priority",
            "created_at": "2024-01-01T10:00:00"
        }
        
        with self.assertRaises(ValueError):
            Task.from_dict(task_data)
    
    def test_invalid_status_enum_conversion(self):
        """Тест обработки неверного значения статуса при создании из словаря."""
        task_data = {
            "id": 1,
            "title": "Invalid status task",
            "status": "invalid_status",
            "priority": "medium",
            "created_at": "2024-01-01T10:00:00"
        }
        
        with self.assertRaises(ValueError):
            Task.from_dict(task_data)


if __name__ == '__main__':
    unittest.main()
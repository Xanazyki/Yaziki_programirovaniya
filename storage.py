"""
Модуль хранения данных для менеджера задач.

Обеспечивает сохранение, загрузку и управление задачами в JSON-файле.
"""

import json
import os
from typing import List, Optional
from models import Task, TaskStatus, Priority


class TaskStorage:
    """Класс для работы с хранилищем задач в JSON-файле.
    
    Attributes:
        filename (str): Имя файла для хранения задач.
    """
    
    def __init__(self, filename="tasks.json"):
        """Инициализирует хранилище задач.
        
        Args:
            filename (str, optional): Имя файла для хранения. По умолчанию "tasks.json".
        """
        self.filename = filename
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Создает файл хранилища, если он не существует."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_tasks(self) -> List[dict]:
        """Читает задачи из файла.
        
        Returns:
            List[dict]: Список словарей с данными задач.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_tasks(self, tasks_data: List[dict]):
        """Записывает задачи в файл.
        
        Args:
            tasks_data (List[dict]): Список словарей с данными задач.
        """
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False)

    def save_task(self, task: Task) -> Task:
        """Сохраняет задачу (создает новую или обновляет существующую).
        
        Args:
            task (Task): Объект задачи для сохранения.
            
        Returns:
            Task: Сохраненная задача с присвоенным ID.
        """
        tasks_data = self._read_tasks()
        
        if task.id is None:
            if tasks_data:
                task.id = max(t["id"] for t in tasks_data) + 1
            else:
                task.id = 1
            tasks_data.append(task.to_dict())
        else:
            for i, t in enumerate(tasks_data):
                if t["id"] == task.id:
                    tasks_data[i] = task.to_dict()
                    break
        
        self._write_tasks(tasks_data)
        return task

    def get_all_tasks(self) -> List[Task]:
        """Возвращает все задачи из хранилища.
        
        Returns:
            List[Task]: Список всех задач.
        """
        tasks_data = self._read_tasks()
        return [Task.from_dict(t) for t in tasks_data]

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Находит задачу по ID.
        
        Args:
            task_id (int): ID искомой задачи.
            
        Returns:
            Optional[Task]: Найденная задача или None.
        """
        tasks_data = self._read_tasks()
        for task_data in tasks_data:
            if task_data["id"] == task_id:
                return Task.from_dict(task_data)
        return None

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID.
        
        Args:
            task_id (int): ID задачи для удаления.
            
        Returns:
            bool: True если задача удалена, False если не найдена.
        """
        tasks_data = self._read_tasks()
        initial_length = len(tasks_data)
        
        tasks_data = [t for t in tasks_data if t["id"] != task_id]
        
        if len(tasks_data) < initial_length:
            self._write_tasks(tasks_data)
            return True
        return False

    def filter_tasks(self, status: str = None, priority: str = None, 
                    due_date: str = None) -> List[Task]:
        """Фильтрует задачи по различным критериям.
        
        Args:
            status (str, optional): Статус для фильтрации. По умолчанию None.
            priority (str, optional): Приоритет для фильтрации. По умолчанию None.
            due_date (str, optional): Дата для фильтрации. По умолчанию None.
            
        Returns:
            List[Task]: Отфильтрованный список задач.
        """
        tasks = self.get_all_tasks()
        
        if status:
            status_enum = TaskStatus(status.lower())
            tasks = [t for t in tasks if t.status == status_enum]
        
        if priority:
            priority_enum = Priority(priority.lower())
            tasks = [t for t in tasks if t.priority == priority_enum]
        
        if due_date:
            tasks = [t for t in tasks if t.due_date == due_date]
        
        return tasks
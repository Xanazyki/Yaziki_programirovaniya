"""
Модуль обработки команд для менеджера задач.

Содержит класс для обработки аргументов командной строки и выполнения команд.
"""

import argparse
from typing import List
from storage import TaskStorage
from models import Task, TaskStatus, Priority


class TaskCommands:
    """Класс для обработки команд менеджера задач.
    
    Attributes:
        storage (TaskStorage): Объект для работы с хранилищем задач.
    """
    
    def __init__(self, storage: TaskStorage):
        """Инициализирует обработчик команд.
        
        Args:
            storage (TaskStorage): Объект хранилища задач.
        """
        self.storage = storage

    def add_task(self, title: str, description: str = "", 
                priority: str = "medium", due_date: str = None) -> str:
        """Добавляет новую задачу.
        
        Args:
            title (str): Название задачи.
            description (str, optional): Описание задачи. По умолчанию "".
            priority (str, optional): Приоритет задачи. По умолчанию "medium".
            due_date (str, optional): Срок выполнения. По умолчанию None.
            
        Returns:
            str: Сообщение о результате операции.
        """
        try:
            priority_enum = Priority(priority.lower())
        except ValueError:
            return f"Ошибка: Неверный приоритет. Допустимые значения: low, medium, high"
        
        task = Task(title, description, priority_enum, due_date)
        saved_task = self.storage.save_task(task)
        return f"Задача добавлена (ID: {saved_task.id})"

    def list_tasks(self, status: str = None, priority: str = None, 
                  due_date: str = None, show_all: bool = False) -> str:
        """Показывает список задач с фильтрацией.
        
        Args:
            status (str, optional): Фильтр по статусу. По умолчанию None.
            priority (str, optional): Фильтр по приоритету. По умолчанию None.
            due_date (str, optional): Фильтр по сроку. По умолчанию None.
            show_all (bool, optional): Показать все задачи. По умолчанию False.
            
        Returns:
            str: Отформатированный список задач.
        """
        if show_all:
            tasks = self.storage.get_all_tasks()
        else:
            tasks = self.storage.filter_tasks(status, priority, due_date)
        
        if not tasks:
            return "Задачи не найдены"
        
        result = []
        for task in tasks:
            task_str = str(task)
            if task.description:
                task_str += f"\n   Описание: {task.description}"
            if task.due_date:
                task_str += f"\n   Срок: {task.due_date}"
            if task.status == TaskStatus.COMPLETED and task.completed_at:
                task_str += f"\n   Завершена: {task.completed_at[:10]}"
            result.append(task_str)
        
        return "\n\n".join(result)

    def complete_task(self, task_id: int) -> str:
        """Отмечает задачу как выполненную.
        
        Args:
            task_id (int): ID задачи для завершения.
            
        Returns:
            str: Сообщение о результате операции.
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return f"Ошибка: Задача с ID {task_id} не найдена"
        
        if task.status == TaskStatus.COMPLETED:
            return f"Задача {task_id} уже была завершена"
        
        task.mark_completed()
        self.storage.save_task(task)
        return f"Задача {task_id} отмечена как выполненная"

    def delete_task(self, task_id: int) -> str:
        """Удаляет задачу.
        
        Args:
            task_id (int): ID задачи для удаления.
            
        Returns:
            str: Сообщение о результате операции.
        """
        if self.storage.delete_task(task_id):
            return f"Задача {task_id} удалена"
        else:
            return f"Ошибка: Задача с ID {task_id} не найдена"

    def setup_argparse(self):
        """Настраивает парсер аргументов командной строки.
        
        Returns:
            argparse.ArgumentParser: Настроенный парсер аргументов.
        """
        parser = argparse.ArgumentParser(description='Консольный менеджер задач')
        subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

        add_parser = subparsers.add_parser('add', help='Добавить новую задачу')
        add_parser.add_argument('--title', required=True, help='Название задачи')
        add_parser.add_argument('--description', help='Описание задачи')
        add_parser.add_argument('--priority', choices=['low', 'medium', 'high'], 
                               default='medium', help='Приоритет задачи')
        add_parser.add_argument('--due-date', help='Срок выполнения (ГГГГ-ММ-ДД)')

        list_parser = subparsers.add_parser('list', help='Показать список задач')
        list_parser.add_argument('--status', choices=['pending', 'completed'], 
                                help='Фильтр по статусу')
        list_parser.add_argument('--priority', choices=['low', 'medium', 'high'], 
                                help='Фильтр по приоритету')
        list_parser.add_argument('--due-date', help='Фильтр по сроку (ГГГГ-ММ-ДД)')
        list_parser.add_argument('--all', action='store_true', 
                                help='Показать все задачи без фильтров')

        done_parser = subparsers.add_parser('done', help='Отметить задачу как выполненную')
        done_parser.add_argument('task_id', type=int, help='ID задачи')

        delete_parser = subparsers.add_parser('delete', help='Удалить задачу')
        delete_parser.add_argument('task_id', type=int, help='ID задачи')

        return parser

    def execute_command(self, args):
        """Выполняет команду на основе аргументов.
        
        Args:
            args: Аргументы командной строки.
            
        Returns:
            str: Результат выполнения команды.
        """
        if args.command == 'add':
            return self.add_task(
                title=args.title,
                description=args.description or "",
                priority=args.priority,
                due_date=args.due_date
            )
        elif args.command == 'list':
            return self.list_tasks(
                status=args.status,
                priority=args.priority,
                due_date=args.due_date,
                show_all=args.all
            )
        elif args.command == 'done':
            return self.complete_task(args.task_id)
        elif args.command == 'delete':
            return self.delete_task(args.task_id)
        else:
            return "Используйте --help для просмотра доступных команд"
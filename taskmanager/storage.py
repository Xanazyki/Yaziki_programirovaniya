"""
Модуль для работы с хранилищем данных PostgreSQL.

Содержит класс DatabaseManager для выполнения CRUD операций с задачами.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from datetime import datetime
from .models import Task


class DatabaseManager:
    """Менеджер для работы с базой данных PostgreSQL.
    
    Обеспечивает подключение к БД и выполнение операций с задачами.
    """
    
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: int = 5432):
        """Инициализирует подключение к базе данных.
        
        Args:
            dbname: Имя базы данных
            user: Имя пользователя PostgreSQL
            password: Пароль пользователя
            host: Хост базы данных (по умолчанию localhost)
            port: Порт базы данных (по умолчанию 5432)
            
        Raises:
            ConnectionError: Если не удается подключиться к БД
        """
        try:
            self.connection = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            print("✅ Успешное подключение к PostgreSQL")
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"❌ Не удалось подключиться к PostgreSQL: {e}")
    
    def create_tables(self):
        """Создает таблицы в базе данных, если они не существуют."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    priority VARCHAR(50) DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date DATE,
                    completed_at TIMESTAMP
                )
            """)
            self.connection.commit()
        print("✅ Таблицы созданы/проверены")
    
    def add_task(self, task: Task) -> int:
        """Добавляет новую задачу в базу данных.
        
        Args:
            task: Объект Task для добавления
            
        Returns:
            int: ID созданной задачи в базе данных
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tasks (title, description, status, priority, due_date)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (task.title, task.description, task.status, task.priority, task.due_date))
            task_id = cursor.fetchone()[0]
            self.connection.commit()
            return task_id
    
    def get_all_tasks(self) -> List[Task]:
        """Получает все задачи из базы данных.
        
        Returns:
            List[Task]: Список всех задач, отсортированных по дате создания (новые first)
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            tasks_data = cursor.fetchall()
            tasks = []
            for task_data in tasks_data:
                task = Task(
                    task_id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    priority=task_data['priority'],
                    due_date=task_data['due_date'],
                    created_at=task_data['created_at'],
                    completed_at=task_data['completed_at']
                )
                tasks.append(task)
            return tasks
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Получает задачу по её ID.
        
        Args:
            task_id: ID задачи для поиска
            
        Returns:
            Optional[Task]: Найденная задача или None если не найдена
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task_data = cursor.fetchone()
            if task_data:
                return Task(
                    task_id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    priority=task_data['priority'],
                    due_date=task_data['due_date'],
                    created_at=task_data['created_at'],
                    completed_at=task_data['completed_at']
                )
            return None
    
    def update_task(self, task: Task) -> bool:
        """Обновляет задачу в базе данных.
        
        Args:
            task: Объект Task с обновленными данными
            
        Returns:
            bool: True если обновление успешно, False если задача не найдена
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE tasks 
                SET title = %s, description = %s, status = %s, 
                    priority = %s, due_date = %s, completed_at = %s
                WHERE id = %s
            """, (task.title, task.description, task.status, task.priority, 
                  task.due_date, task.completed_at, task.id))
            self.connection.commit()
            return cursor.rowcount > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу из базы данных.
        
        Args:
            task_id: ID задачи для удаления
            
        Returns:
            bool: True если удаление успешно, False если задача не найдена
        """
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            self.connection.commit()
            return cursor.rowcount > 0
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Фильтрует задачи по статусу.
        
        Args:
            status: Статус для фильтрации ('pending' или 'completed')
            
        Returns:
            List[Task]: Список задач с указанным статусом
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM tasks WHERE status = %s ORDER BY created_at DESC", (status,))
            tasks_data = cursor.fetchall()
            tasks = []
            for task_data in tasks_data:
                task = Task(
                    task_id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    priority=task_data['priority'],
                    due_date=task_data['due_date'],
                    created_at=task_data['created_at'],
                    completed_at=task_data['completed_at']
                )
                tasks.append(task)
            return tasks
    
    def close(self):
        """Закрывает подключение к базе данных."""
        if self.connection:
            self.connection.close()
            print("✅ Подключение к БД закрыто")
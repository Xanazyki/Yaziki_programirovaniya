"""
Модуль хранения данных для менеджера задач с использованием PostgreSQL.

Обеспечивает сохранение, загрузку и управление задачами в базе данных PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import os

from models import Task, TaskStatus, Priority
from config import Config


class DatabaseConnection:
    """Класс для управления подключением к PostgreSQL."""
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Контекстный менеджер для получения соединения с БД."""
        conn = None
        try:
            conn = psycopg2.connect(**Config.get_connection_params())
            yield conn
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    @contextmanager
    def get_cursor():
        """Контекстный менеджер для получения курсора."""
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
                conn.commit()


class TaskStorage:
    """Класс для работы с хранилищем задач в PostgreSQL."""
    
    def __init__(self):
        """Инициализирует хранилище задач и создает таблицу если необходимо."""
        self._init_database()
    
    def _init_database(self):
        """Инициализирует базу данных, создает таблицы если их нет."""
        try:
            # Сначала проверяем/создаем базу данных
            self._create_database_if_not_exists()
            
            # Создаем таблицу tasks
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date DATE,
                        completed_at TIMESTAMP,
                        CONSTRAINT valid_status CHECK (status IN ('pending', 'completed')),
                        CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high'))
                    )
                """)
                
                # Создаем индексы для оптимизации запросов
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_status 
                    ON tasks(status)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_priority 
                    ON tasks(priority)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_due_date 
                    ON tasks(due_date)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
                    ON tasks(created_at DESC)
                """)
                
                print("База данных инициализирована успешно")
                
        except Exception as e:
            print(f"Ошибка при инициализации БД: {e}")
            raise
    
    def _create_database_if_not_exists(self):
        """Создает базу данных, если она не существует."""
        # Подключаемся к системной базе данных postgres
        conn_params = Config.get_connection_params()
        db_name = conn_params.pop('dbname')  # Убираем имя БД из параметров
        
        # Подключаемся к postgres чтобы создать БД если нужно
        try:
            conn = psycopg2.connect(**{**conn_params, 'dbname': 'postgres'})
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Проверяем существование базы данных
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"База данных '{db_name}' создана")
            
            cursor.close()
            conn.close()
            
        except psycopg2.ProgrammingError:
            # Если база данных уже существует, игнорируем ошибку
            pass
    
    def save_task(self, task: Task) -> Task:
        """Сохраняет задачу (создает новую или обновляет существующую).
        
        Args:
            task (Task): Объект задачи для сохранения.
            
        Returns:
            Task: Сохраненная задача с присвоенным ID.
        """
        with DatabaseConnection.get_cursor() as cursor:
            if task.id is None:
                # Вставка новой задачи
                cursor.execute("""
                    INSERT INTO tasks (title, description, status, priority, due_date, completed_at, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.due_date,
                    task.completed_at,
                    task.created_at
                ))
                
                result = cursor.fetchone()
                task.id = result['id']
                # Если created_at не был передан, используем значение из БД
                if not task.created_at:
                    task.created_at = result['created_at'].isoformat()
                    
            else:
                # Обновление существующей задачи
                cursor.execute("""
                    UPDATE tasks 
                    SET title = %s, description = %s, status = %s, 
                        priority = %s, due_date = %s, completed_at = %s
                    WHERE id = %s
                """, (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.due_date,
                    task.completed_at,
                    task.id
                ))
        
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Возвращает все задачи из хранилища.
        
        Returns:
            List[Task]: Список всех задач.
        """
        with DatabaseConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, status, priority, 
                       created_at, due_date, completed_at
                FROM tasks 
                ORDER BY 
                    CASE WHEN status = 'pending' THEN 1 ELSE 2 END,
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    created_at DESC
            """)
            
            tasks_data = cursor.fetchall()
        
        tasks = []
        for data in tasks_data:
            # Конвертируем данные из БД в словарь
            task_dict = {
                'id': data['id'],
                'title': data['title'],
                'description': data['description'],
                'status': data['status'],
                'priority': data['priority'],
                'created_at': data['created_at'].isoformat() if data['created_at'] else None,
                'due_date': str(data['due_date']) if data['due_date'] else None,
                'completed_at': data['completed_at'].isoformat() if data['completed_at'] else None
            }
            tasks.append(Task.from_dict(task_dict))
        
        return tasks
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Находит задачу по ID.
        
        Args:
            task_id (int): ID искомой задачи.
            
        Returns:
            Optional[Task]: Найденная задача или None.
        """
        with DatabaseConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, status, priority, 
                       created_at, due_date, completed_at
                FROM tasks 
                WHERE id = %s
            """, (task_id,))
            
            data = cursor.fetchone()
        
        if data:
            task_dict = {
                'id': data['id'],
                'title': data['title'],
                'description': data['description'],
                'status': data['status'],
                'priority': data['priority'],
                'created_at': data['created_at'].isoformat() if data['created_at'] else None,
                'due_date': str(data['due_date']) if data['due_date'] else None,
                'completed_at': data['completed_at'].isoformat() if data['completed_at'] else None
            }
            return Task.from_dict(task_dict)
        
        return None
    
    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID.
        
        Args:
            task_id (int): ID задачи для удаления.
            
        Returns:
            bool: True если задача удалена, False если не найдена.
        """
        with DatabaseConnection.get_cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cursor.rowcount > 0
    
    def filter_tasks(self, status: str = None, priority: str = None, 
                    due_date: str = None) -> List[Task]:
        """Фильтрует задачи по различным критериям.
        
        Args:
            status (str, optional): Статус для фильтрации.
            priority (str, optional): Приоритет для фильтрации.
            due_date (str, optional): Дата для фильтрации.
            
        Returns:
            List[Task]: Отфильтрованный список задач.
        """
        query = """
            SELECT id, title, description, status, priority, 
                   created_at, due_date, completed_at
            FROM tasks 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        
        if due_date:
            query += " AND due_date = %s"
            params.append(due_date)
        
        query += " ORDER BY created_at DESC"
        
        with DatabaseConnection.get_cursor() as cursor:
            cursor.execute(query, params)
            tasks_data = cursor.fetchall()
        
        tasks = []
        for data in tasks_data:
            task_dict = {
                'id': data['id'],
                'title': data['title'],
                'description': data['description'],
                'status': data['status'],
                'priority': data['priority'],
                'created_at': data['created_at'].isoformat() if data['created_at'] else None,
                'due_date': str(data['due_date']) if data['due_date'] else None,
                'completed_at': data['completed_at'].isoformat() if data['completed_at'] else None
            }
            tasks.append(Task.from_dict(task_dict))
        
        return tasks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику по задачам.
        
        Returns:
            Dict[str, Any]: Словарь со статистикой.
        """
        with DatabaseConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
                    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority,
                    SUM(CASE WHEN priority = 'medium' THEN 1 ELSE 0 END) as medium_priority,
                    SUM(CASE WHEN priority = 'low' THEN 1 ELSE 0 END) as low_priority,
                    SUM(CASE WHEN due_date < CURRENT_DATE AND status = 'pending' THEN 1 ELSE 0 END) as overdue_tasks
                FROM tasks
            """)
            
            result = cursor.fetchone()
            
            # Добавляем вычисляемые поля
            stats = dict(result)
            if stats['total_tasks'] > 0:
                stats['completion_rate'] = round((stats['completed_tasks'] / stats['total_tasks']) * 100, 2)
            else:
                stats['completion_rate'] = 0
            
            return stats
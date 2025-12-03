"""
Тесты для модуля storage.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from storage import TaskStorage, DatabaseConnection
from models import Task, TaskStatus, Priority
from config import Config
import psycopg2.extras


class TestDatabaseConnection(unittest.TestCase):
    """Тесты для класса DatabaseConnection."""
    
    @patch('storage.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Тест успешного получения соединения."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        with DatabaseConnection.get_connection() as conn:
            self.assertEqual(conn, mock_conn)
        
        mock_connect.assert_called_once_with(**Config.get_connection_params())
        mock_conn.close.assert_called_once()
    
    @patch('storage.psycopg2.connect')
    def test_get_connection_error(self, mock_connect):
        """Тест ошибки при получении соединения."""
        mock_connect.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            with DatabaseConnection.get_connection():
                pass
    
    @patch('storage.DatabaseConnection.get_connection')
    def test_get_cursor(self, mock_get_connection):
        """Тест получения курсора."""
        # Создаем мок для соединения
        mock_conn = MagicMock()
        
        # Создаем мок для курсора с контекстным менеджером
        mock_cursor_instance = MagicMock()
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor_instance
        mock_cursor_context.__exit__.return_value = None
        
        # Настраиваем цепочку вызовов
        mock_conn.cursor.return_value = mock_cursor_context
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        
        with DatabaseConnection.get_cursor() as cursor:
            # Проверяем, что получен правильный курсор
            self.assertEqual(cursor, mock_cursor_instance)
        
        # Проверяем, что был создан курсор с правильными параметрами
        mock_conn.cursor.assert_called_once_with(cursor_factory=psycopg2.extras.RealDictCursor)
        mock_conn.commit.assert_called_once()


class TestTaskStorage(unittest.TestCase):
    """Тесты для класса TaskStorage."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        # Создаем мок для курсора
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchone = Mock()
        self.mock_cursor.fetchall = Mock()
        self.mock_cursor.execute = Mock()
        self.mock_cursor.rowcount = 0
        
        # Создаем контекстный менеджер для курсора
        self.mock_cursor_context = MagicMock()
        self.mock_cursor_context.__enter__.return_value = self.mock_cursor
        self.mock_cursor_context.__exit__.return_value = None
        
        # Мокаем DatabaseConnection.get_cursor
        self.patcher = patch('storage.DatabaseConnection.get_cursor')
        self.mock_get_cursor = self.patcher.start()
        self.mock_get_cursor.return_value = self.mock_cursor_context
        
        # Мокаем инициализацию БД
        self.patcher_init = patch.object(TaskStorage, '_init_database')
        self.mock_init = self.patcher_init.start()
        
        # Создаем экземпляр хранилища
        self.storage = TaskStorage()
    
    def tearDown(self):
        """Очистка тестового окружения."""
        self.patcher.stop()
        self.patcher_init.stop()
    
    def test_save_task_insert(self):
        """Тест сохранения новой задачи."""
        # Мокаем результат запроса
        self.mock_cursor.fetchone.return_value = {
            'id': 1,
            'created_at': '2024-01-01T10:00:00'
        }
        
        task = Task("New Task", "New Description", Priority.HIGH, "2024-12-31")
        
        saved_task = self.storage.save_task(task)
        
        self.assertEqual(saved_task.id, 1)
        
        # Проверяем, что был вызван SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
        
        # Получаем аргументы вызова
        call_args = self.mock_cursor.execute.call_args[0]
        sql_query = call_args[0]
        
        # Проверяем, что это INSERT запрос
        self.assertIn("INSERT INTO tasks", sql_query)
    
    def test_save_task_update(self):
        """Тест обновления существующей задачи."""
        task = Task("Updated Task", "Updated Description", Priority.LOW, "2024-12-31")
        task.id = 1
        
        self.storage.save_task(task)
        
        # Проверяем, что был вызван SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
        
        # Получаем аргументы вызова
        call_args = self.mock_cursor.execute.call_args[0]
        sql_query = call_args[0]
        
        # Проверяем, что это UPDATE запрос
        self.assertIn("UPDATE tasks", sql_query)
    
    def test_get_all_tasks(self):
        """Тест получения всех задач."""
        # Мокаем данные из БД
        self.mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'title': 'Task 1',
                'description': 'Description 1',
                'status': 'pending',
                'priority': 'high',
                'created_at': '2024-01-01T10:00:00',
                'due_date': None,
                'completed_at': None
            },
            {
                'id': 2,
                'title': 'Task 2',
                'description': 'Description 2',
                'status': 'completed',
                'priority': 'low',
                'created_at': '2024-01-02T10:00:00',
                'due_date': '2024-12-31',
                'completed_at': '2024-01-03T10:00:00'
            }
        ]
        
        tasks = self.storage.get_all_tasks()
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, 1)
        self.assertEqual(tasks[0].title, 'Task 1')
        self.assertEqual(tasks[0].status, TaskStatus.PENDING)
        self.assertEqual(tasks[0].priority, Priority.HIGH)
        
        self.assertEqual(tasks[1].id, 2)
        self.assertEqual(tasks[1].status, TaskStatus.COMPLETED)
        self.assertEqual(tasks[1].priority, Priority.LOW)
        
        # Исправляем проверку даты - учитываем формат хранения
        # В БД дата хранится как datetime, при конвертации в строку получается другой формат
        self.assertEqual(tasks[1].due_date, "2024-12-31 00:00:00")
        
        # Проверяем, что был вызван SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
    
    def test_get_all_tasks_empty(self):
        """Тест получения всех задач из пустой БД."""
        # Мокаем пустой результат
        self.mock_cursor.fetchall.return_value = []
        
        tasks = self.storage.get_all_tasks()
        
        self.assertEqual(len(tasks), 0)
        self.assertTrue(self.mock_cursor.execute.called)
    
    def test_get_task_by_id_found(self):
        """Тест поиска задачи по ID (найдена)."""
        # Мокаем данные из БД
        self.mock_cursor.fetchone.return_value = {
            'id': 1,
            'title': 'Found Task',
            'description': 'Found Description',
            'status': 'pending',
            'priority': 'medium',
            'created_at': '2024-01-01T10:00:00',
            'due_date': None,
            'completed_at': None
        }
        
        task = self.storage.get_task_by_id(1)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, 'Found Task')
        
        # Проверяем SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
        call_args = self.mock_cursor.execute.call_args[0]
        self.assertIn("WHERE id = %s", call_args[0])
        self.assertEqual(call_args[1][0], 1)
    
    def test_get_task_by_id_not_found(self):
        """Тест поиска задачи по ID (не найдена)."""
        self.mock_cursor.fetchone.return_value = None
        
        task = self.storage.get_task_by_id(999)
        
        self.assertIsNone(task)
        self.assertTrue(self.mock_cursor.execute.called)
    
    def test_delete_task_success(self):
        """Тест успешного удаления задачи."""
        self.mock_cursor.rowcount = 1
        
        result = self.storage.delete_task(1)
        
        self.assertTrue(result)
        self.assertTrue(self.mock_cursor.execute.called)
        
        call_args = self.mock_cursor.execute.call_args[0]
        self.assertIn("DELETE FROM tasks", call_args[0])
        self.assertEqual(call_args[1][0], 1)
    
    def test_delete_task_not_found(self):
        """Тест удаления несуществующей задачи."""
        self.mock_cursor.rowcount = 0
        
        result = self.storage.delete_task(999)
        
        self.assertFalse(result)
        self.assertTrue(self.mock_cursor.execute.called)
    
    def test_filter_tasks(self):
        """Тест фильтрации задач."""
        self.mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'title': 'Pending High Task',
                'description': 'Description',
                'status': 'pending',
                'priority': 'high',
                'created_at': '2024-01-01T10:00:00',
                'due_date': '2024-12-31',
                'completed_at': None
            }
        ]
        
        tasks = self.storage.filter_tasks(
            status='pending',
            priority='high',
            due_date='2024-12-31'
        )
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].status, TaskStatus.PENDING)
        self.assertEqual(tasks[0].priority, Priority.HIGH)
        
        # Проверяем SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
        call_args = self.mock_cursor.execute.call_args
        
        sql_query = call_args[0][0]
        params = call_args[0][1]
        
        self.assertIn("AND status = %s", sql_query)
        self.assertIn("AND priority = %s", sql_query)
        self.assertIn("AND due_date = %s", sql_query)
        
        self.assertEqual(params[0], 'pending')
        self.assertEqual(params[1], 'high')
        self.assertEqual(params[2], '2024-12-31')
    
    def test_filter_tasks_no_filters(self):
        """Тест фильтрации задач без фильтров."""
        self.mock_cursor.fetchall.return_value = []
        
        tasks = self.storage.filter_tasks()
        
        # Проверяем SQL запрос
        self.assertTrue(self.mock_cursor.execute.called)
        sql_query = self.mock_cursor.execute.call_args[0][0]
        
        self.assertIn("SELECT", sql_query)
        self.assertNotIn("AND status = %s", sql_query)
        self.assertNotIn("AND priority = %s", sql_query)
        self.assertNotIn("AND due_date = %s", sql_query)
    
    def test_get_statistics(self):
        """Тест получения статистики."""
        self.mock_cursor.fetchone.return_value = {
            'total_tasks': 10,
            'completed_tasks': 6,
            'pending_tasks': 4,
            'high_priority': 2,
            'medium_priority': 5,
            'low_priority': 3,
            'overdue_tasks': 1
        }
        
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats['total_tasks'], 10)
        self.assertEqual(stats['completed_tasks'], 6)
        self.assertEqual(stats['pending_tasks'], 4)
        self.assertEqual(stats['completion_rate'], 60.0)
        self.assertEqual(stats['high_priority'], 2)
        self.assertEqual(stats['medium_priority'], 5)
        self.assertEqual(stats['low_priority'], 3)
        self.assertEqual(stats['overdue_tasks'], 1)
    
    def test_get_statistics_empty(self):
        """Тест получения статистики для пустой базы."""
        self.mock_cursor.fetchone.return_value = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'pending_tasks': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0,
            'overdue_tasks': 0
        }
        
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats['total_tasks'], 0)
        self.assertEqual(stats['completion_rate'], 0)
    
    def test_init_database(self):
        """Тест инициализации базы данных."""
        # Создаем отдельный мок для проверки SQL запросов
        mock_cursor = MagicMock()
        mock_cursor.execute = Mock()
        
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        mock_cursor_context.__exit__.return_value = None
        
        with patch('storage.DatabaseConnection.get_cursor', return_value=mock_cursor_context):
            with patch.object(self.storage, '_create_database_if_not_exists'):
                # Вызываем метод инициализации
                self.storage._init_database()
                
                # Проверяем, что были вызваны SQL запросы
                self.assertGreater(mock_cursor.execute.call_count, 0)
                
                # Проверяем наличие ключевых SQL запросов
                calls = mock_cursor.execute.call_args_list
                sql_queries = [str(call[0][0]) for call in calls]
                
                # Проверяем основные SQL запросы
                has_create_table = any('CREATE TABLE IF NOT EXISTS tasks' in query for query in sql_queries)
                has_create_index = any('CREATE INDEX IF NOT EXISTS' in query for query in sql_queries)
                
                self.assertTrue(has_create_table, "Должен быть запрос создания таблицы")
                self.assertTrue(has_create_index, "Должны быть запросы создания индексов")
    
    def test_assert_raises_exception(self):
        """Тест с использованием assertRaises."""
        # Мокаем исключение при выполнении запроса
        self.mock_cursor.execute.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception):
            self.storage.get_all_tasks()
    
    def test_assert_raises_with_context(self):
        """Тест с использованием assertRaises как контекстного менеджера."""
        # Мокаем исключение при подключении к БД
        with patch('storage.DatabaseConnection.get_cursor') as mock_get_cursor:
            mock_get_cursor.side_effect = Exception("Connection failed")
            
            with self.assertRaises(Exception) as context:
                self.storage.get_all_tasks()
            
            # Проверяем сообщение об ошибке
            self.assertIn("Connection failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
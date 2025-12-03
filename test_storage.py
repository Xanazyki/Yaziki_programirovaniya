"""
Тесты для модуля storage.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from storage import TaskStorage, DatabaseConnection
from models import Task, TaskStatus, Priority
from config import Config


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
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        
        with DatabaseConnection.get_cursor() as cursor:
            self.assertEqual(cursor, mock_cursor)
        
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestTaskStorage(unittest.TestCase):
    """Тесты для класса TaskStorage."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.patcher_connection = patch('storage.DatabaseConnection.get_cursor')
        self.mock_get_cursor = self.patcher_connection.start()
        self.mock_cursor = Mock()
        self.mock_get_cursor.return_value.__enter__.return_value = self.mock_cursor
        
        self.patcher_init = patch.object(TaskStorage, '_init_database')
        self.mock_init = self.patcher_init.start()
        
        self.storage = TaskStorage()
    
    def tearDown(self):
        """Очистка тестового окружения."""
        self.patcher_connection.stop()
        self.patcher_init.stop()
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_save_task_insert(self, mock_get_cursor):
        """Тест сохранения новой задачи."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'id': 1, 'created_at': datetime(2024, 1, 1, 10, 0, 0)}
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        task = Task("New Task", "New Description", Priority.HIGH, "2024-12-31")
        
        saved_task = self.storage.save_task(task)
        
        self.assertEqual(saved_task.id, 1)
        self.assertEqual(saved_task.created_at, datetime(2024, 1, 1, 10, 0, 0).isoformat())
        
        # Проверка SQL запроса для вставки
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("INSERT INTO tasks", call_args[0])
        self.assertEqual(call_args[1][0], "New Task")  # title
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_save_task_update(self, mock_get_cursor):
        """Тест обновления существующей задачи."""
        mock_cursor = Mock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        task = Task("Updated Task", "Updated Description", Priority.LOW, "2024-12-31")
        task.id = 1
        task.created_at = "2024-01-01T10:00:00"
        
        saved_task = self.storage.save_task(task)
        
        self.assertEqual(saved_task.id, 1)
        
        # Проверка SQL запроса для обновления
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("UPDATE tasks", call_args[0])
        self.assertEqual(call_args[1][-1], 1)  # id
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_get_all_tasks(self, mock_get_cursor):
        """Тест получения всех задач."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'title': 'Task 1',
                'description': 'Description 1',
                'status': 'pending',
                'priority': 'high',
                'created_at': datetime(2024, 1, 1, 10, 0, 0),
                'due_date': None,
                'completed_at': None
            },
            {
                'id': 2,
                'title': 'Task 2',
                'description': 'Description 2',
                'status': 'completed',
                'priority': 'low',
                'created_at': datetime(2024, 1, 2, 10, 0, 0),
                'due_date': datetime(2024, 12, 31),
                'completed_at': datetime(2024, 1, 3, 10, 0, 0)
            }
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        tasks = self.storage.get_all_tasks()
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, 1)
        self.assertEqual(tasks[0].title, 'Task 1')
        self.assertEqual(tasks[0].status, TaskStatus.PENDING)
        self.assertEqual(tasks[0].priority, Priority.HIGH)
        
        self.assertEqual(tasks[1].id, 2)
        self.assertEqual(tasks[1].status, TaskStatus.COMPLETED)
        self.assertEqual(tasks[1].priority, Priority.LOW)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_get_task_by_id_found(self, mock_get_cursor):
        """Тест поиска задачи по ID (найдена)."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'title': 'Found Task',
            'description': 'Found Description',
            'status': 'pending',
            'priority': 'medium',
            'created_at': datetime(2024, 1, 1, 10, 0, 0),
            'due_date': None,
            'completed_at': None
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        task = self.storage.get_task_by_id(1)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, 'Found Task')
        
        # Проверка SQL запроса
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("WHERE id = %s", call_args[0])
        self.assertEqual(call_args[1][0], 1)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_get_task_by_id_not_found(self, mock_get_cursor):
        """Тест поиска задачи по ID (не найдена)."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        task = self.storage.get_task_by_id(999)
        
        self.assertIsNone(task)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_delete_task_success(self, mock_get_cursor):
        """Тест успешного удаления задачи."""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.storage.delete_task(1)
        
        self.assertTrue(result)
        
        # Проверка SQL запроса
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("DELETE FROM tasks WHERE id = %s", call_args[0])
        self.assertEqual(call_args[1][0], 1)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_delete_task_not_found(self, mock_get_cursor):
        """Тест удаления несуществующей задачи."""
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.storage.delete_task(999)
        
        self.assertFalse(result)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_filter_tasks(self, mock_get_cursor):
        """Тест фильтрации задач."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'title': 'Pending High Task',
                'description': 'Description',
                'status': 'pending',
                'priority': 'high',
                'created_at': datetime(2024, 1, 1, 10, 0, 0),
                'due_date': datetime(2024, 12, 31),
                'completed_at': None
            }
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        tasks = self.storage.filter_tasks(
            status='pending',
            priority='high',
            due_date='2024-12-31'
        )
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].status, TaskStatus.PENDING)
        self.assertEqual(tasks[0].priority, Priority.HIGH)
        
        # Проверка SQL запроса с параметрами
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        
        sql_query = call_args[0][0]
        params = call_args[0][1]
        
        self.assertIn("AND status = %s", sql_query)
        self.assertIn("AND priority = %s", sql_query)
        self.assertIn("AND due_date = %s", sql_query)
        
        self.assertEqual(params[0], 'pending')
        self.assertEqual(params[1], 'high')
        self.assertEqual(params[2], '2024-12-31')
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_filter_tasks_no_filters(self, mock_get_cursor):
        """Тест фильтрации задач без фильтров."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        tasks = self.storage.filter_tasks()
        
        # Проверка SQL запроса без фильтров
        mock_cursor.execute.assert_called_once()
        sql_query = mock_cursor.execute.call_args[0][0]
        
        self.assertNotIn("AND status = %s", sql_query)
        self.assertNotIn("AND priority = %s", sql_query)
        self.assertNotIn("AND due_date = %s", sql_query)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_get_statistics(self, mock_get_cursor):
        """Тест получения статистики."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'total_tasks': 10,
            'completed_tasks': 6,
            'pending_tasks': 4,
            'high_priority': 2,
            'medium_priority': 5,
            'low_priority': 3,
            'overdue_tasks': 1
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats['total_tasks'], 10)
        self.assertEqual(stats['completed_tasks'], 6)
        self.assertEqual(stats['pending_tasks'], 4)
        self.assertEqual(stats['completion_rate'], 60.0)
        self.assertEqual(stats['high_priority'], 2)
        self.assertEqual(stats['medium_priority'], 5)
        self.assertEqual(stats['low_priority'], 3)
        self.assertEqual(stats['overdue_tasks'], 1)
    
    @patch('storage.DatabaseConnection.get_cursor')
    def test_get_statistics_empty(self, mock_get_cursor):
        """Тест получения статистики для пустой базы."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'pending_tasks': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0,
            'overdue_tasks': 0
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats['total_tasks'], 0)
        self.assertEqual(stats['completion_rate'], 0)


if __name__ == '__main__':
    unittest.main()
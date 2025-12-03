"""
Тесты для модуля commands.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from commands import TaskCommands
from models import Task, TaskStatus, Priority


class TestTaskCommands(unittest.TestCase):
    """Тесты для класса TaskCommands."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.mock_storage = Mock()
        self.commands = TaskCommands(self.mock_storage)
    
    def test_add_task_success(self):
        """Тест успешного добавления задачи."""
        mock_task = Mock()
        mock_task.id = 1
        self.mock_storage.save_task.return_value = mock_task
        
        result = self.commands.add_task(
            title="Test Task",
            description="Test Description",
            priority="high",
            due_date="2024-12-31"
        )
        
        self.assertIn("✅ Задача добавлена (ID: 1)", result)
        self.mock_storage.save_task.assert_called_once()
    
    def test_add_task_invalid_priority(self):
        """Тест добавления задачи с неверным приоритетом."""
        result = self.commands.add_task(
            title="Test Task",
            priority="invalid_priority"
        )
        
        self.assertIn("Ошибка: Неверный приоритет", result)
        self.mock_storage.save_task.assert_not_called()
    
    def test_list_tasks_empty(self):
        """Тест отображения пустого списка задач."""
        self.mock_storage.filter_tasks.return_value = []
        
        result = self.commands.list_tasks()
        
        self.assertEqual(result, "📭 Задачи не найдены")
    
    def test_list_tasks_with_filter(self):
        """Тест отображения списка задач с фильтрацией."""
        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.description = "Test Description"
        mock_task.status = TaskStatus.PENDING
        mock_task.priority = Priority.HIGH
        mock_task.due_date = "2024-12-31"
        mock_task.completed_at = None
        mock_task.__str__ = Mock(return_value="○ [⬆] Test Task (ID: 1)")
        
        self.mock_storage.filter_tasks.return_value = [mock_task]
        
        result = self.commands.list_tasks(
            status="pending",
            priority="high",
            due_date="2024-12-31"
        )
        
        self.assertIn("Test Task", result)
        self.assertIn("Test Description", result)
        self.assertIn("2024-12-31", result)
        self.mock_storage.filter_tasks.assert_called_once_with(
            status="pending",
            priority="high",
            due_date="2024-12-31"
        )
    
    def test_list_tasks_show_all(self):
        """Тест отображения всех задач со статистикой."""
        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.description = ""
        mock_task.status = TaskStatus.COMPLETED
        mock_task.priority = Priority.MEDIUM
        mock_task.due_date = None
        mock_task.completed_at = "2024-01-01T10:00:00"
        mock_task.__str__ = Mock(return_value="✓ [●] Test Task (ID: 1)")
        
        self.mock_storage.get_all_tasks.return_value = [mock_task]
        self.mock_storage.get_statistics.return_value = {
            'total_tasks': 5,
            'completed_tasks': 3,
            'pending_tasks': 2,
            'completion_rate': 60.0
        }
        
        result = self.commands.list_tasks(show_all=True)
        
        self.assertIn("📊 Статистика", result)
        self.assertIn("Всего 5 задач", result)
        self.assertIn("Выполнено: 3 (60.0%)", result)
        self.assertIn("Test Task", result)
    
    def test_complete_task_success(self):
        """Тест успешного завершения задачи."""
        mock_task = Mock()
        mock_task.status = TaskStatus.PENDING
        mock_task.mark_completed = Mock()
        
        self.mock_storage.get_task_by_id.return_value = mock_task
        
        result = self.commands.complete_task(1)
        
        self.assertIn("✅ Задача 1 отмечена как выполненная", result)
        mock_task.mark_completed.assert_called_once()
        self.mock_storage.save_task.assert_called_once_with(mock_task)
    
    def test_complete_task_not_found(self):
        """Тест завершения несуществующей задачи."""
        self.mock_storage.get_task_by_id.return_value = None
        
        result = self.commands.complete_task(999)
        
        self.assertIn("❌ Ошибка: Задача с ID 999 не найдена", result)
    
    def test_complete_task_already_completed(self):
        """Тест повторного завершения уже выполненной задачи."""
        mock_task = Mock()
        mock_task.status = TaskStatus.COMPLETED
        
        self.mock_storage.get_task_by_id.return_value = mock_task
        
        result = self.commands.complete_task(1)
        
        self.assertIn("ℹ️ Задача 1 уже была завершена", result)
        self.mock_storage.save_task.assert_not_called()
    
    def test_delete_task_success(self):
        """Тест успешного удаления задачи."""
        self.mock_storage.delete_task.return_value = True
        
        result = self.commands.delete_task(1)
        
        self.assertIn("🗑️ Задача 1 удалена", result)
    
    def test_delete_task_not_found(self):
        """Тест удаления несуществующей задачи."""
        self.mock_storage.delete_task.return_value = False
        
        result = self.commands.delete_task(999)
        
        self.assertIn("❌ Ошибка: Задача с ID 999 не найдена", result)
    
    def test_show_stats(self):
        """Тест отображения статистики."""
        stats_data = {
            'total_tasks': 10,
            'completed_tasks': 6,
            'pending_tasks': 4,
            'completion_rate': 60.0,
            'high_priority': 2,
            'medium_priority': 5,
            'low_priority': 3,
            'overdue_tasks': 1
        }
        
        self.mock_storage.get_statistics.return_value = stats_data
        
        result = self.commands.show_stats()
        
        self.assertIn("📊 СТАТИСТИКА ЗАДАЧ", result)
        self.assertIn("Всего задач: 10", result)
        self.assertIn("Выполнено: 6", result)
        self.assertIn("В ожидании: 4", result)
        self.assertIn("Процент выполнения: 60.0%", result)
        self.assertIn("Высокий: 2", result)
        self.assertIn("Средний: 5", result)
        self.assertIn("Низкий: 3", result)
        self.assertIn("Просрочено: 1", result)
    
    def test_execute_command_add(self):
        """Тест выполнения команды добавления."""
        mock_args = Mock()
        mock_args.command = 'add'
        mock_args.title = 'Test Task'
        mock_args.description = 'Test Description'
        mock_args.priority = 'high'
        mock_args.due_date = '2024-12-31'
        
        with patch.object(self.commands, 'add_task') as mock_add_task:
            mock_add_task.return_value = "Task added successfully"
            result = self.commands.execute_command(mock_args)
            
            self.assertEqual(result, "Task added successfully")
            mock_add_task.assert_called_once_with(
                title='Test Task',
                description='Test Description',
                priority='high',
                due_date='2024-12-31'
            )
    
    def test_execute_command_invalid(self):
        """Тест выполнения неверной команды."""
        mock_args = Mock()
        mock_args.command = None
        
        result = self.commands.execute_command(mock_args)
        
        self.assertEqual(result, "Используйте --help для просмотра доступных команд")
    
    def test_argparse_setup(self):
        """Тест настройки парсера аргументов."""
        parser = self.commands.setup_argparse()
        
        # Проверка наличия подпарсеров
        self.assertIn('add', parser._subparsers._group_actions[0].choices)
        self.assertIn('list', parser._subparsers._group_actions[0].choices)
        self.assertIn('done', parser._subparsers._group_actions[0].choices)
        self.assertIn('delete', parser._subparsers._group_actions[0].choices)
        self.assertIn('stats', parser._subparsers._group_actions[0].choices)


if __name__ == '__main__':
    unittest.main()
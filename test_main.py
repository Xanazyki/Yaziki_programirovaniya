"""
Тесты для главного модуля main.py
"""

import unittest
import sys
from unittest.mock import patch, Mock
from io import StringIO


class TestMainModule(unittest.TestCase):
    """Тесты для главного модуля."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.patcher_storage = patch('main.TaskStorage')
        self.mock_storage = self.patcher_storage.start()
        
        self.patcher_commands = patch('main.TaskCommands')
        self.mock_commands = self.patcher_commands.start()
        
        self.mock_commands_instance = Mock()
        self.mock_commands.return_value = self.mock_commands_instance
    
    def tearDown(self):
        """Очистка тестового окружения."""
        self.patcher_storage.stop()
        self.patcher_commands.stop()
    
    @patch('main.sys.argv', ['main.py', '--help'])
    @patch('main.TaskCommands.setup_argparse')
    def test_main_no_arguments(self, mock_setup_argparse):
        """Тест запуска без аргументов (показ справки)."""
        mock_parser = Mock()
        mock_setup_argparse.return_value = mock_parser
        
        from main import main
        
        # Перехватываем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            main()
            
            # Парсер должен был показать справку
            mock_parser.print_help.assert_called_once()
    
    @patch('main.sys.argv', ['main.py', 'add', '--title', 'Test Task'])
    @patch('main.TaskCommands.setup_argparse')
    def test_main_with_arguments(self, mock_setup_argparse):
        """Тест запуска с аргументами."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.command = 'add'
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparse.return_value = mock_parser
        
        self.mock_commands_instance.execute_command.return_value = "Task added successfully"
        
        from main import main
        
        # Перехватываем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            main()
            
            # Проверяем выполнение команды
            self.mock_commands_instance.execute_command.assert_called_once_with(mock_args)
            
            output = fake_output.getvalue()
            self.assertIn("Task added successfully", output)
    
    @patch('main.sys.argv', ['main.py', 'add'])
    @patch('main.TaskCommands.setup_argparse')
    def test_main_keyboard_interrupt(self, mock_setup_argparse):
        """Тест обработки прерывания пользователем."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.command = 'add'
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparse.return_value = mock_parser
        
        self.mock_commands_instance.execute_command.side_effect = KeyboardInterrupt()
        
        from main import main
        
        # Перехватываем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            main()
            
            output = fake_output.getvalue()
            self.assertIn("Операция прервана пользователем", output)
    
    @patch('main.sys.argv', ['main.py', 'add'])
    @patch('main.TaskCommands.setup_argparse')
    def test_main_general_exception(self, mock_setup_argparse):
        """Тест обработки общего исключения."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.command = 'add'
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparse.return_value = mock_parser
        
        self.mock_commands_instance.execute_command.side_effect = Exception("Test error")
        
        from main import main
        
        # Перехватываем вывод
        with patch('sys.stdout', new=StringIO()) as fake_output:
            with self.assertRaises(SystemExit):
                main()
            
            output = fake_output.getvalue()
            self.assertIn("❌ Ошибка: Test error", output)
            self.assertIn("Убедитесь, что:", output)


if __name__ == '__main__':
    unittest.main()
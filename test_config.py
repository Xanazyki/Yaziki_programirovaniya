"""
Тесты для модуля config.py
"""

import unittest
from config import Config


class TestConfig(unittest.TestCase):
    """Тесты для класса Config."""
    
    def test_config_values(self):
        """Проверка значений конфигурации."""
        self.assertEqual(Config.DB_NAME, "task_manager")
        self.assertEqual(Config.DB_USER, "postgres")
        self.assertEqual(Config.DB_PASSWORD, "12")
        self.assertEqual(Config.DB_HOST, "localhost")
        self.assertEqual(Config.DB_PORT, "5432")
    
    def test_get_connection_params(self):
        """Тест метода получения параметров подключения."""
        params = Config.get_connection_params()
        
        expected_params = {
            "dbname": "task_manager",
            "user": "postgres",
            "password": "12",
            "host": "localhost",
            "port": "5432"
        }
        
        self.assertEqual(params, expected_params)
    
    def test_class_method(self):
        """Проверка, что метод является классовым методом."""
        # Метод должен работать без создания экземпляра класса
        params = Config.get_connection_params()
        self.assertIsInstance(params, dict)


if __name__ == '__main__':
    unittest.main()
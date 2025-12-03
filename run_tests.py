"""
Скрипт для запуска всех тестов проекта.
"""

import unittest
import sys


def run_all_tests():
    """Запускает все тесты проекта."""
    # Находим все тестовые модули
    test_modules = [
        'test_config',
        'test_models',
        'test_storage',
        'test_commands',
        'test_main'
    ]
    
    # Загружаем тесты из каждого модуля
    loader = unittest.TestLoader()
    suites = []
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite = loader.loadTestsFromModule(module)
            suites.append(suite)
        except ImportError as e:
            print(f"Ошибка при загрузке модуля {module_name}: {e}")
    
    # Объединяем все тестовые наборы
    all_tests = unittest.TestSuite(suites)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)
    
    # Возвращаем код выхода (0 - успешно, 1 - неуспешно)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
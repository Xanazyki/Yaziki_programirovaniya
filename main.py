"""
Главный модуль консольного менеджера задач с PostgreSQL.

Точка входа приложения, обрабатывает аргументы командной строки
и запускает соответствующие команды.
"""

import sys
from commands import TaskCommands
from storage import TaskStorage


def main():
    """Основная функция приложения."""
    # Создаем хранилище с PostgreSQL
    storage = TaskStorage()
    commands = TaskCommands(storage)
    
    parser = commands.setup_argparse()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    try:
        result = commands.execute_command(args)
        print(result)
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nУбедитесь, что:")
        print("1. PostgreSQL установлен и запущен")
        print("2. Пароль в файле .env правильный")
        print("3. Порт 5432 доступен")
        sys.exit(1)


if __name__ == "__main__":
    main()
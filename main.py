"""
Главный модуль приложения менеджера задач.

Точка входа для запуска приложения с обработкой аргументов командной строки.
Координирует работу всех компонентов приложения.
"""

import sys
from taskmanager.storage import DatabaseManager
from taskmanager.commands import setup_parser, add_task, list_tasks, complete_task, delete_task


def main():
    """Основная функция запуска приложения.
    
    Returns:
        int: Код завершения (0 - успех, 1 - ошибка)
    """
    db_config = {
        "dbname": "taskmanager",
        "user": "postgres", 
        "password": "password", 
        "host": "localhost",
        "port": 5432
    }
    
    try:
        db = DatabaseManager(**db_config)
        db.create_tables()
    except Exception as e:
        print(f"❌ Не удалось подключиться к базе данных: {e}")
        print("\n🔧 Убедитесь, что:")
        print("   1. PostgreSQL установлен и запущен")
        print("   2. База данных 'taskmanager' создана")
        print("   3. Пароль в db_config правильный")
        print("   4. Сервер БД доступен по localhost:5432")
        return 1
    
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        db.close()
        return 1
    
    try:
        if args.command == "add":
            add_task(args, db)
        elif args.command == "list":
            list_tasks(args, db)
        elif args.command == "done":
            complete_task(args, db)
        elif args.command == "delete":
            delete_task(args, db)
    except Exception as e:
        print(f"❌ Ошибка при выполнении команды '{args.command}': {e}")
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
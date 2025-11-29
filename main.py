"""
Главный модуль консольного менеджера задач.

Точка входа приложения, обрабатывает аргументы командной строки
и запускает соответствующие команды.
"""

import sys
import os
from commands import TaskCommands
from storage import TaskStorage


def main():
    """Основная функция приложения."""
    storage = TaskStorage()
    commands = TaskCommands(storage)
    
    parser = commands.setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        result = commands.execute_command(args)
        print(result)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
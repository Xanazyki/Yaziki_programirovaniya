"""
Модуль обработчиков команд для командной строки.

Содержит функции для обработки аргументов командной строки и выполнения команд.
"""

import argparse
from typing import List
from datetime import datetime
from .models import Task
from .storage import DatabaseManager


def add_task(args, db: DatabaseManager):
    """Добавляет новую задачу в базу данных.
    
    Args:
        args: Аргументы командной строки с данными задачи
        db: Менеджер базы данных для выполнения операции
    """
    task = Task(
        title=args.title,
        description=args.description or "",
        priority=args.priority,
        due_date=args.due_date
    )
    task_id = db.add_task(task)
    print(f"✅ Задача '{args.title}' добавлена с ID: {task_id}")


def list_tasks(args, db: DatabaseManager):
    """Выводит список задач с возможностью фильтрации по статусу.
    
    Args:
        args: Аргументы командной строки (может содержать статус для фильтрации)
        db: Менеджер базы данных для получения задач
    """
    if args.status:
        tasks = db.get_tasks_by_status(args.status)
        status_text = "выполненные" if args.status == "completed" else "невыполненные"
        print(f"\n📋 {status_text.title()} задачи:")
    else:
        tasks = db.get_all_tasks()
        print("\n📋 Все задачи:")
    
    if not tasks:
        print("   ✨ Нет задач")
        return
    
    for task in tasks:
        print(f"   {task}\n")


def complete_task(args, db: DatabaseManager):
    """Отмечает задачу как выполненную.
    
    Args:
        args: Аргументы командной строки с ID задачи
        db: Менеджер базы данных для обновления задачи
    """
    task = db.get_task_by_id(args.id)
    if not task:
        print(f"❌ Задача с ID {args.id} не найдена")
        return
    
    if task.status == "completed":
        print(f"⚠️ Задача '{task.title}' уже выполнена")
        return
    
    task.mark_completed()
    
    if db.update_task(task):
        print(f"✅ Задача '{task.title}' отмечена как выполненная")
    else:
        print(f"❌ Ошибка при обновлении задачи {args.id}")


def delete_task(args, db: DatabaseManager):
    """Удаляет задачу из базы данных.
    
    Args:
        args: Аргументы командной строки с ID задачи
        db: Менеджер базы данных для удаления задачи
    """
    task = db.get_task_by_id(args.id)
    if not task:
        print(f"❌ Задача с ID {args.id} не найдена")
        return
    
    if db.delete_task(args.id):
        print(f"✅ Задача '{task.title}' удалена")
    else:
        print(f"❌ Ошибка при удалении задачи {args.id}")


def setup_parser() -> argparse.ArgumentParser:
    """Настраивает парсер аргументов командной строки.
    
    Returns:
        argparse.ArgumentParser: Настроенный парсер с командами add, list, done, delete
    """
    parser = argparse.ArgumentParser(
        description="🎯 Менеджер задач - управляйте вашими задачами из командной строки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py add --title "Изучить Python" --description "Прочитать документацию" --priority high
  python main.py list
  python main.py list --status pending
  python main.py done --id 1
  python main.py delete --id 1
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    add_parser = subparsers.add_parser("add", help="Добавить новую задачу")
    add_parser.add_argument("--title", required=True, help="Заголовок задачи (обязательно)")
    add_parser.add_argument("--description", help="Описание задачи")
    add_parser.add_argument("--priority", choices=["low", "medium", "high"], 
                          default="medium", help="Приоритет задачи (по умолчанию: medium)")
    add_parser.add_argument("--due-date", type=lambda s: datetime.strptime(s, "%d.%m.%Y").date(),
                          help="Срок выполнения в формате ДД.ММ.ГГГГ")
    
    list_parser = subparsers.add_parser("list", help="Показать список задач")
    list_parser.add_argument("--status", choices=["pending", "completed"],
                           help="Фильтр по статусу (pending или completed)")
    
    done_parser = subparsers.add_parser("done", help="Отметить задачу как выполненную")
    done_parser.add_argument("--id", type=int, required=True, help="ID задачи для завершения")
    
    delete_parser = subparsers.add_parser("delete", help="Удалить задачу")
    delete_parser.add_argument("--id", type=int, required=True, help="ID задачи для удаления")
    
    return parser
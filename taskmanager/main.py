import argparse
from .commands import TaskCommands

def main():
    parser = argparse.ArgumentParser(description="Консольный менеджер задач")
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    add_parser = subparsers.add_parser('add', help='Добавить новую задачу')
    add_parser.add_argument('title', help='Название задачи')
    add_parser.add_argument('--description', help='Описание задачи', default="")
    add_parser.add_argument('--priority', choices=['low', 'medium', 'high'], 
                          default='medium', help='Приоритет задачи')
    
    list_parser = subparsers.add_parser('list', help='Показать список задач')
    list_parser.add_argument('--status', choices=['pending', 'completed'], 
                           help='Фильтр по статусу')
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high'], 
                           help='Фильтр по приоритету')
    
    done_parser = subparsers.add_parser('done', help='Отметить задачу как выполненную')
    done_parser.add_argument('task_id', type=int, help='ID задачи')
    
    delete_parser = subparsers.add_parser('delete', help='Удалить задачу')
    delete_parser.add_argument('task_id', type=int, help='ID задачи')
    
    stats_parser = subparsers.add_parser('stats', help='Показать статистику задач')
    
    args = parser.parse_args()
    commands = TaskCommands()
    
    if args.command == 'add':
        commands.add_task(args.title, args.description, args.priority)
    elif args.command == 'list':
        commands.list_tasks(args.status, args.priority)
    elif args.command == 'done':
        commands.complete_task(args.task_id)
    elif args.command == 'delete':
        commands.delete_task(args.task_id)
    elif args.command == 'stats':
        commands.get_task_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
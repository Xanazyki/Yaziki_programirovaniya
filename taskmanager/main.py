import argparse
from .commands import TaskCommands

def main():
    parser = argparse.ArgumentParser(description='Менеджер задач')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    add_parser = subparsers.add_parser('add', help='Добавить новую задачу')
    add_parser.add_argument('title', help='Название задачи')
    add_parser.add_argument('--description', help='Описание задачи', default='')
    add_parser.add_argument('--priority', choices=['low', 'medium', 'high'],
                            default='medium', help='Приоритет задачи')
    
    list_parser = subparsers.add_parser('list', help='Показать список задач')
    list_parser.add_argument('--status', choices=['pending', 'completed'],
                             help='Фильтр по статусу')
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high'],
                             help='Фильтр по приоритету')
    
    done_parser = subparsers.add_parser('done', help='Отметить задачу как выполненную')
    done_parser.add_argument('task_id', type=int, help='ID задачи')

    args = parser.parse_args()
    commands = TaskCommands()

    if args.command == 'add':
        commands.add_task(args.title, args.description, args.priority)
    elif args.command == 'list':
        commands.add_task(args.status, args.priority)
    elif args.command == 'done':
        commands.add_task(args.task_id)
    elif args.command == 'delete':
        commands.delete_task(args.task_id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
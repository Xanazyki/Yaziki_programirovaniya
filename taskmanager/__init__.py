"""
Пакет менеджера задач.

Модули:
    models - класс Task и модели данных
    storage - работа с PostgreSQL
    commands - обработчики команд CLI
"""

__version__ = '1.0.0'
__author__ = 'Шматко Михаил'

from .models import Task
from .storage import DatabaseManager
from .commands import setup_parser

__all__ = ['Task', 'DatabaseManager', 'setup_parser']
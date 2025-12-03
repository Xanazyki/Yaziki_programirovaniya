"""
Конфигурация подключения к PostgreSQL.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Конфигурация подключения к PostgreSQL."""
    
    DB_NAME = os.getenv("DB_NAME", "task_manager")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    @classmethod
    def get_connection_string(cls):
        """Возвращает строку подключения."""
        return f"dbname='{cls.DB_NAME}' user='{cls.DB_USER}' password='{cls.DB_PASSWORD}' host='{cls.DB_HOST}' port='{cls.DB_PORT}'"
    
    @classmethod
    def get_connection_params(cls):
        """Возвращает параметры подключения."""
        return {
            "dbname": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "host": cls.DB_HOST,
            "port": cls.DB_PORT
        }
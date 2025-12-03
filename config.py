class Config:
    """Конфигурация подключения к PostgreSQL."""
    
    DB_NAME = "task_manager"
    DB_USER = "postgres"
    DB_PASSWORD = "12" 
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
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
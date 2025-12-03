"""
Скрипт для первоначальной настройки базы данных.
"""

from storage import TaskStorage

def setup_database():
    """Инициализирует базу данных и создает таблицы."""
    print("🔄 Настройка базы данных PostgreSQL...")
    
    try:
        storage = TaskStorage()
        print("✅ База данных готова к работе!")
        print("\nДля теста можете создать первую задачу:")
        print("python main.py add --title 'Первая задача' --priority high")
        
    except Exception as e:
        print(f"❌ Ошибка при настройке БД: {e}")
        print("\nУбедитесь, что:")
        print("1. PostgreSQL установлен и запущен")
        print("2. Вы ввели правильный пароль в файле .env")
        print("3. Порт 5432 не занят другим приложением")
        
        # Попробуем подключиться к PostgreSQL для диагностики
        import psycopg2
        from config import Config
        
        print("\n🔧 Диагностика подключения...")
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                host=Config.DB_HOST,
                port=Config.DB_PORT
            )
            print("✅ Подключение к PostgreSQL успешно!")
            conn.close()
        except Exception as conn_error:
            print(f"❌ Не удалось подключиться к PostgreSQL: {conn_error}")

if __name__ == "__main__":
    setup_database()
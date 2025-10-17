import functools

def require_role(allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.get('role') in allowed_roles:
                return func(user, *args, **kwargs)
            else:
                print(f"Доступ запрещён пользователю {user.get('name')}")
                return None
        return wrapper
    return decorator


users = [
    {"name": "Михаил", "role": "admin"},
    {"name": "Андрей", "role": "moderator"},
    {"name": "Александр", "role": "editor"},
    {"name": "Ольга", "role": "user"},
    {"name": "Петр", "role": "guest"}
]


@require_role(["admin"])
def delete_database(user):
    print(f"База данных удалена пользователем {user['name']}")

@require_role(["admin", "moderator"])
def kick_user(user, username):
    print(f"Пользователь {username} выгнал администратором {user['name']}")

@require_role(["admin", "moderator", "editor"])
def edit_article(user, article_title):
    print(f"Статья '{article_title}' отредактирована пользователем {user['name']}")

@require_role(["admin", "moderator", "editor", "user", "guest"])
def view_content(user, content):
    print(f"Пользователь {user['name']} просматривает: {content}")


for user in users:
    print(f"🧑 Пользователь: {user['name']} (роль: {user['role']})")
    
    print("Просмотр контента:")
    view_content(user, "главная страница")
    
    print("Редактирование статьи:")
    edit_article(user, "Новости Python")
    
    print("Блокировка пользователя:")
    kick_user(user, "нарушитель")
    
    print("Удаление базы данных:")
    delete_database(user)
    
    print("\n" + "=" * 50 + "\n")
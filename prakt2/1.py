import functools

def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызов функции {func.__name__} с аргументами {args} и {kwargs}")
        result = func(*args, **kwargs)
        print(f"Функция {func.__name__} вернула {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

@logger
def divide(a, b):
    if b != 0:
        return a/b
    return "На ноль делить нельзя"

@logger
def greet(name):
    return f"Привет, {name}!"

r1 = add(12, 9)
print(f"Add: {r1}")

r2 = divide(100, 10)
print(f"divide: {r2}")

r3 = divide(100, 0)
print(f"divide: {r3}")

r4 = greet('Михаил')
print(f'greet: {r4}')
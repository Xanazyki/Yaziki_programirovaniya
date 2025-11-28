"""
Скрипт установки пакета taskmanager.

Позволяет установить пакет в систему и использовать как модуль.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="taskmanager",
    version="1.0.0",
    description="Консольный менеджер задач с PostgreSQL",
    author="Ваше Имя",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "taskmanager=main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
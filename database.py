import sqlite3
from pathlib import Path
from typing import Optional

from models import Task


class Database:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.create_table()

    def connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    minutes INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def add_task(self, task: Task) -> Task:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (name, category, completed, minutes)
                VALUES (?, ?, ?, ?)
                """,
                (task.name, task.category, int(task.completed), task.minutes),
            )
            task.id = cursor.lastrowid
        return task

    def get_tasks(self, category: Optional[str] = None) -> list[Task]:
        query = "SELECT id, name, category, completed, minutes FROM tasks"
        parameters = ()

        if category and category != "All":
            query += " WHERE category = ?"
            parameters = (category,)

        query += " ORDER BY completed ASC, id DESC"

        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()

        return [
            Task(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                completed=bool(row["completed"]),
                minutes=row["minutes"],
            )
            for row in rows
        ]

    def get_categories(self) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT category FROM tasks ORDER BY category COLLATE NOCASE"
            ).fetchall()
        return [row["category"] for row in rows]

    def update_task(self, task: Task):
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET name = ?, category = ?, completed = ?, minutes = ?
                WHERE id = ?
                """,
                (task.name, task.category, int(task.completed), task.minutes, task.id),
            )

    def delete_task(self, task_id: int):
        with self.connect() as connection:
            connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

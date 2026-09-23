from database import Database
from models import Task


class TaskService:
    def __init__(self, database: Database):
        self.database = database

    def add_task(self, name: str, category: str) -> Task:
        clean_name = name.strip()
        clean_category = category.strip()

        if not clean_name:
            raise ValueError("Task name cannot be empty.")
        if not clean_category:
            raise ValueError("Category cannot be empty.")

        return self.database.add_task(Task(clean_name, clean_category))

    def get_tasks(self, category: str = "All") -> list[Task]:
        return self.database.get_tasks(category)

    def get_categories(self) -> list[str]:
        return self.database.get_categories()

    def update_task(self, task: Task, name: str, category: str):
        clean_name = name.strip()
        clean_category = category.strip()

        if not clean_name or not clean_category:
            raise ValueError("Task name and category are required.")

        task.name = clean_name
        task.category = clean_category
        self.database.update_task(task)

    def toggle_complete(self, task: Task):
        if task.completed:
            task.mark_incomplete()
        else:
            task.mark_complete()
        self.database.update_task(task)

    def add_minutes(self, task: Task, minutes: int):
        if minutes < 0:
            raise ValueError("Minutes cannot be negative.")
        task.minutes += minutes
        self.database.update_task(task)

    def delete_task(self, task: Task):
        if task.id is not None:
            self.database.delete_task(task.id)

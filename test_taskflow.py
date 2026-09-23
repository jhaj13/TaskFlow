import tempfile
import unittest
from pathlib import Path

from database import Database
from models import Task
from task_service import TaskService


class TaskFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test.db"
        self.database = Database(database_path)
        self.service = TaskService(self.database)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_add_and_load_task(self):
        created = self.service.add_task("Study Python", "School")
        loaded = self.service.get_tasks()
        self.assertIsNotNone(created.id)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "Study Python")

    def test_empty_task_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.add_task("   ", "School")

    def test_complete_edit_and_delete_task(self):
        task = self.service.add_task("Homework", "School")
        self.service.toggle_complete(task)
        self.assertTrue(self.service.get_tasks()[0].completed)

        self.service.update_task(task, "CICS homework", "University")
        self.assertEqual(self.service.get_tasks()[0].name, "CICS homework")

        self.service.delete_task(task)
        self.assertEqual(self.service.get_tasks(), [])

    def test_category_filter(self):
        self.service.add_task("Homework", "School")
        self.service.add_task("Workout", "Health")
        school_tasks = self.service.get_tasks("School")
        self.assertEqual(len(school_tasks), 1)
        self.assertEqual(school_tasks[0].category, "School")

    def test_add_minutes(self):
        task = self.database.add_task(Task("Read", "School"))
        self.service.add_minutes(task, 25)
        self.assertEqual(self.service.get_tasks()[0].minutes, 25)


if __name__ == "__main__":
    unittest.main()

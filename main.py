from database import Database
from task_service import TaskService
from ui import TaskFlowApp


def main():
    database = Database("taskflow.db")
    service = TaskService(database)
    app = TaskFlowApp(service)
    app.mainloop()


if __name__ == "__main__":
    main()

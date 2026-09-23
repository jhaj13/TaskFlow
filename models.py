from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    name: str
    category: str
    completed: bool = False
    minutes: int = 0
    id: Optional[int] = None

    def mark_complete(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False

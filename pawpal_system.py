from enum import Enum
from datetime import datetime, date
from typing import Optional


class TaskType(Enum):
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"


class Task:
    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        description: str,
        scheduled_time: datetime,
        duration: int,
        priority: int,
        is_recurring: bool = False,
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.scheduled_time = scheduled_time
        self.duration = duration
        self.is_completed = False
        self.priority = priority
        self.is_recurring = is_recurring
        self.pet = None

    def complete(self) -> None:
        pass

    def reschedule(self, new_time: datetime) -> None:
        pass

    def is_overdue(self) -> bool:
        return False

    def get_priority(self) -> int:
        return 0


class Pet:
    def __init__(
        self,
        pet_id: str,
        name: str,
        species: str,
        breed: str,
        birthdate: date,
        weight: float,
        medical_notes: str = "",
    ):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.birthdate = birthdate
        self.weight = weight
        self.medical_notes = medical_notes
        self.owner = None
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        return []

    def get_age(self) -> int:
        return 0

    def update_weight(self, weight: float) -> None:
        pass


class Owner:
    def __init__(self, owner_id: str, name: str, email: str, phone: str):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        return []

    def get_task_summary(self) -> str:
        return ""


class Scheduler:
    def __init__(self, overdue_threshold: int = 30):
        self.tasks: list[Task] = []
        self.priority_weights: dict[TaskType, int] = {
            TaskType.MEDICATION: 4,
            TaskType.APPOINTMENT: 3,
            TaskType.FEEDING: 2,
            TaskType.WALK: 1,
        }
        self.overdue_threshold = overdue_threshold

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def prioritize_tasks(self) -> list[Task]:
        return []

    def get_overdue_tasks(self) -> list[Task]:
        return []

    def schedule_next(self, pet: Pet) -> Optional[Task]:
        return None

    def check_conflicts(self) -> list[Task]:
        return []

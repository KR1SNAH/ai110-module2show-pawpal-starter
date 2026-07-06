from __future__ import annotations

import uuid
from enum import Enum
from datetime import datetime, date, timedelta
from typing import Optional


class TaskType(Enum):
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"


class Task:
    def __init__(
        self,
        task_type: TaskType,
        description: str,
        scheduled_time: datetime,
        duration: int,
        priority: int,
        is_recurring: bool = False,
        task_id: Optional[str] = None,
    ):
        """Create a care task, auto-generating a task_id if none is given."""
        self.task_id = task_id or uuid.uuid4().hex
        self.task_type = task_type
        self.description = description
        self.scheduled_time = scheduled_time
        self.duration = duration
        self.is_completed = False
        self.priority = priority
        self.is_recurring = is_recurring
        self.pet: Optional[Pet] = None
        self.completed_at: Optional[datetime] = None

    def mark_complete(self) -> None:
        """Mark the task done; recurring tasks immediately roll forward to their next daily occurrence."""
        self.is_completed = True
        self.completed_at = datetime.now()
        if self.is_recurring:
            # Recurring tasks roll forward to their next daily occurrence
            # instead of a new Task instance being created for it.
            self.scheduled_time = self.scheduled_time + timedelta(days=1)
            self.is_completed = False

    def reschedule(self, new_time: datetime) -> None:
        """Change the task's scheduled time."""
        self.scheduled_time = new_time

    def is_overdue(self, threshold_minutes: int = 0) -> bool:
        """Return True if the task is incomplete and past its scheduled end time plus threshold_minutes."""
        # threshold_minutes comes from Scheduler.overdue_threshold so
        # "overdue" has one definition instead of being decided in two places.
        if self.is_completed:
            return False
        due_by = self.scheduled_time + timedelta(minutes=self.duration + threshold_minutes)
        return datetime.now() > due_by

    def get_priority(self) -> int:
        """Return the task's priority score, boosted if it's currently overdue."""
        score = self.priority
        if self.is_overdue():
            score += 10
        return score


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        breed: str,
        birthdate: date,
        weight: float,
        medical_notes: str = "",
        pet_id: Optional[str] = None,
    ):
        """Create a pet profile, auto-generating a pet_id if none is given."""
        self.pet_id = pet_id or uuid.uuid4().hex
        self.name = name
        self.species = species
        self.breed = breed
        self.birthdate = birthdate
        self.weight = weight
        self.medical_notes = medical_notes
        self.owner: Optional[Owner] = None
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and link the task back to it."""
        # Pet.tasks is the single source of truth for a pet's tasks;
        # Scheduler reads from here rather than keeping its own copy.
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks

    def get_age(self) -> int:
        """Return the pet's age in whole years based on its birthdate."""
        today = date.today()
        had_birthday_this_year = (today.month, today.day) >= (
            self.birthdate.month,
            self.birthdate.day,
        )
        return today.year - self.birthdate.year - (0 if had_birthday_this_year else 1)

    def update_weight(self, weight: float) -> None:
        """Update the pet's weight, rejecting non-positive values."""
        if weight <= 0:
            raise ValueError("Weight must be positive")
        self.weight = weight


class Owner:
    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        owner_id: Optional[str] = None,
    ):
        """Create an owner profile, auto-generating an owner_id if none is given."""
        self.owner_id = owner_id or uuid.uuid4().hex
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and link the pet back to its owner."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given ID from this owner's pet list."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_task_summary(self) -> str:
        """Return a human-readable summary of completed, pending, and overdue tasks across all pets."""
        all_tasks = [task for pet in self.pets for task in pet.tasks]
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.is_completed)
        overdue = sum(1 for t in all_tasks if not t.is_completed and t.is_overdue())
        pending = total - completed
        return (
            f"{self.name} has {total} task(s) across {len(self.pets)} pet(s): "
            f"{completed} completed, {pending} pending, {overdue} overdue."
        )


class Scheduler:
    """Manages scheduling for a single Owner's pets.

    `tasks` is read live from `owner.pets` on every access instead of being
    stored as a separate list, so Pet.tasks stays the single source of
    truth and can never drift out of sync with what the Scheduler sees.
    Conflict checks are therefore automatically scoped to one owner's pets.
    """

    def __init__(self, owner: Owner, overdue_threshold: int = 30):
        """Create a scheduler bound to one owner, with default per-type priority weights."""
        self.owner = owner
        self.priority_weights: dict[TaskType, int] = {
            TaskType.MEDICATION: 4,
            TaskType.APPOINTMENT: 3,
            TaskType.FEEDING: 2,
            TaskType.WALK: 1,
        }
        self.overdue_threshold = overdue_threshold

    @property
    def tasks(self) -> list[Task]:
        """Return all tasks across the owner's pets, computed live rather than cached."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def _score(self, task: Task) -> int:
        """Compute a task's ranking score from its priority, task-type weight, and overdue status."""
        type_weight = self.priority_weights.get(task.task_type, 0)
        overdue_bonus = 100 if task.is_overdue(self.overdue_threshold) else 0
        return task.priority * 10 + type_weight * 5 + overdue_bonus

    def prioritize_tasks(self) -> list[Task]:
        """Return incomplete tasks ranked by score, soonest-scheduled first among ties."""
        pending = [t for t in self.tasks if not t.is_completed]
        return sorted(pending, key=lambda t: (-self._score(t), t.scheduled_time))

    def get_overdue_tasks(self) -> list[Task]:
        """Return incomplete tasks that are overdue using this scheduler's configured threshold."""
        return [
            t for t in self.tasks
            if not t.is_completed and t.is_overdue(self.overdue_threshold)
        ]

    def schedule_next(self, pet: Pet) -> Optional[Task]:
        """Return the highest-priority incomplete task for the given pet, or None if it has none."""
        pending = [t for t in pet.tasks if not t.is_completed]
        if not pending:
            return None
        return sorted(pending, key=lambda t: (-self._score(t), t.scheduled_time))[0]

    def check_conflicts(self) -> list[Task]:
        """Return tasks whose scheduled time windows overlap another task for this owner."""
        # Conflicts are scoped to this owner's tasks across all their pets,
        # since one owner cannot physically be in two places at once.
        conflicting: set[Task] = set()
        ordered = sorted(self.tasks, key=lambda t: t.scheduled_time)
        for i, task_a in enumerate(ordered):
            end_a = task_a.scheduled_time + timedelta(minutes=task_a.duration)
            for task_b in ordered[i + 1:]:
                if task_b.scheduled_time >= end_a:
                    break
                conflicting.add(task_a)
                conflicting.add(task_b)
        return sorted(conflicting, key=lambda t: t.scheduled_time)

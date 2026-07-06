from datetime import date, datetime

from pawpal_system import Pet, Task, TaskType


def test_task_completion_changes_status():
    task = Task(TaskType.WALK, "Evening walk", datetime.now(), 20, priority=2)

    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog", "Shiba Inu", date(2021, 7, 6), 18.5)
    task = Task(TaskType.FEEDING, "Dinner", datetime.now(), 15, priority=1)

    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1

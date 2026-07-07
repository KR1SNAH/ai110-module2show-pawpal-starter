from datetime import date, datetime, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task, TaskFrequency, TaskType


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


def make_owner_with_pet(pet_name="Mochi"):
    owner = Owner("Alex", "alex@example.com", "555-1234")
    pet = Pet(pet_name, "dog", "Shiba Inu", date(2021, 7, 6), 18.5)
    owner.add_pet(pet)
    return owner, pet


# ---------------------------------------------------------------------------
# Recurring tasks (Task.mark_complete)
# ---------------------------------------------------------------------------


def test_mark_complete_non_recurring_returns_none():
    task = Task(TaskType.WALK, "Walk", datetime.now(), 20, priority=1)

    assert task.mark_complete() is None


def test_mark_complete_daily_creates_next_occurrence_from_original_time():
    original_time = datetime(2026, 1, 1, 9, 0)
    task = Task(
        TaskType.FEEDING, "Breakfast", original_time, 15, priority=1,
        frequency=TaskFrequency.DAILY,
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.scheduled_time == original_time + timedelta(days=1)
    assert next_task.is_completed is False
    assert next_task.frequency == TaskFrequency.DAILY


def test_mark_complete_late_still_schedules_from_original_time_not_now():
    # Next occurrence is anchored to the missed task's original schedule, not
    # to when it was actually completed -- so completing several days late
    # produces a next occurrence that is already overdue on arrival.
    original_time = datetime.now() - timedelta(days=5)
    task = Task(
        TaskType.MEDICATION, "Pill", original_time, 5, priority=3,
        frequency=TaskFrequency.DAILY,
    )

    next_task = task.mark_complete()

    assert next_task.scheduled_time == original_time + timedelta(days=1)
    assert next_task.is_overdue() is True


def test_mark_complete_attaches_next_occurrence_to_same_pet():
    owner, pet = make_owner_with_pet()
    task = Task(
        TaskType.WALK, "Walk", datetime.now(), 20, priority=1,
        frequency=TaskFrequency.WEEKLY,
    )
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task.pet is pet
    assert next_task in pet.get_tasks()
    assert len(pet.get_tasks()) == 2


def test_mark_complete_with_no_pet_creates_orphaned_next_task():
    task = Task(
        TaskType.WALK, "Walk", datetime.now(), 20, priority=1,
        frequency=TaskFrequency.DAILY,
    )

    next_task = task.mark_complete()

    # The next occurrence is returned but never attached anywhere since the
    # completed task had no pet to add it to.
    assert next_task is not None
    assert next_task.pet is None


def test_mark_complete_called_twice_spawns_duplicate_next_occurrences():
    # Documents current behavior: nothing guards against re-completing an
    # already-completed recurring task, so each call spawns another
    # occurrence.
    owner, pet = make_owner_with_pet()
    task = Task(
        TaskType.FEEDING, "Dinner", datetime.now(), 15, priority=1,
        frequency=TaskFrequency.DAILY,
    )
    pet.add_task(task)

    first_next = task.mark_complete()
    second_next = task.mark_complete()

    assert first_next is not second_next
    assert len(pet.get_tasks()) == 3


def test_mark_complete_sets_completed_at():
    task = Task(TaskType.WALK, "Walk", datetime.now(), 20, priority=1)

    assert task.completed_at is None

    task.mark_complete()

    assert task.completed_at is not None


# ---------------------------------------------------------------------------
# Overdue / priority
# ---------------------------------------------------------------------------


def test_is_overdue_false_just_before_due_boundary():
    # A couple of seconds of buffer keeps this from flaking against the real
    # clock ticking forward between task creation and the assertion.
    scheduled_time = datetime.now() - timedelta(minutes=10) + timedelta(seconds=5)
    task = Task(TaskType.WALK, "Walk", scheduled_time, duration=10, priority=1)

    assert task.is_overdue() is False


def test_is_overdue_true_just_past_boundary():
    scheduled_time = datetime.now() - timedelta(minutes=11)
    task = Task(TaskType.WALK, "Walk", scheduled_time, duration=10, priority=1)

    assert task.is_overdue() is True


def test_is_overdue_always_false_when_completed():
    scheduled_time = datetime.now() - timedelta(days=1)
    task = Task(TaskType.WALK, "Walk", scheduled_time, duration=10, priority=1)
    task.mark_complete()

    assert task.is_overdue() is False


def test_get_priority_boosts_overdue_tasks():
    scheduled_time = datetime.now() - timedelta(hours=1)
    task = Task(TaskType.WALK, "Walk", scheduled_time, duration=10, priority=5)

    assert task.get_priority() == 15


def test_get_priority_and_scheduler_score_can_disagree_on_overdue():
    # Task.get_priority() always uses a 0-minute overdue threshold, while
    # Scheduler.get_score() uses the scheduler's configured threshold
    # (default 30 minutes) -- so a task can be "overdue" by one definition
    # and not the other.
    owner, pet = make_owner_with_pet()
    scheduled_time = datetime.now() - timedelta(minutes=10)
    task = Task(TaskType.WALK, "Walk", scheduled_time, duration=0, priority=1)
    pet.add_task(task)
    scheduler = Scheduler(owner)  # default overdue_threshold=30

    assert task.is_overdue() is True  # threshold=0
    assert task.is_overdue(scheduler.overdue_threshold) is False  # threshold=30


# ---------------------------------------------------------------------------
# Sorting / prioritization
# ---------------------------------------------------------------------------


def test_prioritize_tasks_breaks_ties_by_soonest_scheduled_time():
    owner, pet = make_owner_with_pet()
    now = datetime.now() + timedelta(days=1)
    later_task = Task(TaskType.WALK, "Later", now + timedelta(hours=2), 10, priority=1)
    sooner_task = Task(TaskType.WALK, "Sooner", now, 10, priority=1)
    pet.add_task(later_task)
    pet.add_task(sooner_task)
    scheduler = Scheduler(owner)

    ranked = scheduler.prioritize_tasks()

    assert ranked == [sooner_task, later_task]


def test_prioritize_tasks_excludes_completed_tasks():
    owner, pet = make_owner_with_pet()
    done = Task(TaskType.WALK, "Done", datetime.now(), 10, priority=5)
    done.mark_complete()
    pending = Task(TaskType.WALK, "Pending", datetime.now(), 10, priority=1)
    pet.add_task(done)
    pet.add_task(pending)
    scheduler = Scheduler(owner)

    assert scheduler.prioritize_tasks() == [pending]


def test_prioritize_tasks_empty_when_no_tasks():
    owner, _pet = make_owner_with_pet()
    scheduler = Scheduler(owner)

    assert scheduler.prioritize_tasks() == []
    assert scheduler.get_overdue_tasks() == []
    assert scheduler.sort_by_time() == []


def test_schedule_next_returns_none_when_pet_has_no_pending_tasks():
    _owner, pet = make_owner_with_pet()
    scheduler = Scheduler(_owner)

    assert scheduler.schedule_next(pet) is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------


def test_back_to_back_tasks_are_not_a_conflict():
    owner, pet = make_owner_with_pet()
    start = datetime(2026, 1, 1, 9, 0)
    task_a = Task(TaskType.WALK, "A", start, duration=10, priority=1)
    task_b = Task(TaskType.WALK, "B", start + timedelta(minutes=10), duration=10, priority=1)
    pet.add_task(task_a)
    pet.add_task(task_b)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts() == []


def test_overlapping_by_one_minute_is_a_conflict():
    owner, pet = make_owner_with_pet()
    start = datetime(2026, 1, 1, 9, 0)
    task_a = Task(TaskType.WALK, "A", start, duration=10, priority=1)
    task_b = Task(TaskType.WALK, "B", start + timedelta(minutes=9), duration=10, priority=1)
    pet.add_task(task_a)
    pet.add_task(task_b)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts() == [(task_a, task_b)]


def test_zero_duration_tasks_at_same_instant_are_not_flagged():
    # Documents a quirk of find_conflicts: with duration=0, end_a equals
    # start_a, so a second task at the exact same instant satisfies the
    # "starts at/after end_a" break condition and is never flagged, even
    # though both tasks occupy the same moment.
    owner, pet = make_owner_with_pet()
    same_time = datetime(2026, 1, 1, 9, 0)
    task_a = Task(TaskType.WALK, "A", same_time, duration=0, priority=1)
    task_b = Task(TaskType.WALK, "B", same_time, duration=0, priority=1)
    pet.add_task(task_a)
    pet.add_task(task_b)
    scheduler = Scheduler(owner)

    assert scheduler.find_conflicts() == []


def test_conflict_warning_labels_same_pet_vs_different_pets():
    owner, pet_a = make_owner_with_pet("Mochi")
    pet_b = Pet("Waffle", "cat", "Tabby", date(2020, 3, 1), 4.2)
    owner.add_pet(pet_b)
    start = datetime(2026, 1, 1, 9, 0)

    same_pet_task_1 = Task(TaskType.WALK, "Walk", start, 10, priority=1)
    same_pet_task_2 = Task(TaskType.FEEDING, "Feed", start + timedelta(minutes=5), 10, priority=1)
    pet_a.add_task(same_pet_task_1)
    pet_a.add_task(same_pet_task_2)

    cross_pet_task_1 = Task(TaskType.WALK, "Walk2", start + timedelta(hours=2), 10, priority=1)
    cross_pet_task_2 = Task(TaskType.FEEDING, "Feed2", start + timedelta(hours=2, minutes=5), 10, priority=1)
    pet_a.add_task(cross_pet_task_1)
    pet_b.add_task(cross_pet_task_2)

    scheduler = Scheduler(owner)
    warnings = scheduler.get_conflict_warnings()

    assert any("same pet" in w for w in warnings)
    assert any("different pets" in w for w in warnings)


def test_conflict_warning_handles_unassigned_task():
    owner, pet = make_owner_with_pet()
    start = datetime(2026, 1, 1, 9, 0)
    assigned = Task(TaskType.WALK, "Walk", start, 10, priority=1)
    unassigned = Task(TaskType.FEEDING, "Feed", start + timedelta(minutes=5), 10, priority=1)
    pet.add_task(assigned)
    # Append directly to the pet's task list (bypassing add_task) so this
    # task is scheduled but has no pet backlink, like an unassigned task.
    pet.tasks.append(unassigned)
    scheduler = Scheduler(owner)

    warnings = scheduler.get_conflict_warnings()

    assert any("Unassigned" in w for w in warnings)


def test_check_conflicts_dedups_chain_of_overlaps():
    owner, pet = make_owner_with_pet()
    start = datetime(2026, 1, 1, 9, 0)
    task_a = Task(TaskType.WALK, "A", start, duration=10, priority=1)
    task_b = Task(TaskType.WALK, "B", start + timedelta(minutes=8), duration=10, priority=1)
    task_c = Task(TaskType.WALK, "C", start + timedelta(minutes=16), duration=10, priority=1)
    pet.add_task(task_a)
    pet.add_task(task_b)
    pet.add_task(task_c)
    scheduler = Scheduler(owner)

    conflicting = scheduler.check_conflicts()

    assert conflicting == [task_a, task_b, task_c]


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_tasks_by_completion_status_false_is_not_ignored():
    owner, pet = make_owner_with_pet()
    done = Task(TaskType.WALK, "Done", datetime.now(), 10, priority=1)
    done.mark_complete()
    pending = Task(TaskType.WALK, "Pending", datetime.now(), 10, priority=1)
    pet.add_task(done)
    pet.add_task(pending)
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(is_completed=False) == [pending]
    assert scheduler.filter_tasks(is_completed=True) == [done]


def test_filter_tasks_by_duplicate_pet_names_matches_both():
    owner, pet_1 = make_owner_with_pet("Buddy")
    pet_2 = Pet("Buddy", "cat", "Tabby", date(2020, 1, 1), 4.0)
    owner.add_pet(pet_2)
    task_1 = Task(TaskType.WALK, "Walk 1", datetime.now(), 10, priority=1)
    task_2 = Task(TaskType.FEEDING, "Feed 1", datetime.now(), 10, priority=1)
    pet_1.add_task(task_1)
    pet_2.add_task(task_2)
    scheduler = Scheduler(owner)

    matches = scheduler.filter_tasks(pet_name="Buddy")

    assert set(matches) == {task_1, task_2}


# ---------------------------------------------------------------------------
# Pet age
# ---------------------------------------------------------------------------


def test_get_age_counts_birthday_today_as_already_had():
    today = date.today()
    birthdate = today.replace(year=today.year - 3)
    pet = Pet("Mochi", "dog", "Shiba Inu", birthdate, 18.5)

    assert pet.get_age() == 3


# ---------------------------------------------------------------------------
# Owner / Pet management
# ---------------------------------------------------------------------------


def test_remove_pet_with_unknown_id_is_a_no_op():
    owner, pet = make_owner_with_pet()

    owner.remove_pet("does-not-exist")

    assert owner.get_pets() == [pet]


def test_remove_task_with_unknown_id_is_a_no_op():
    _owner, pet = make_owner_with_pet()
    task = Task(TaskType.WALK, "Walk", datetime.now(), 10, priority=1)
    pet.add_task(task)

    pet.remove_task("does-not-exist")

    assert pet.get_tasks() == [task]


def test_get_task_summary_with_no_pets():
    owner = Owner("Alex", "alex@example.com", "555-1234")

    summary = owner.get_task_summary()

    assert "0 task(s) across 0 pet(s)" in summary


def test_update_weight_rejects_non_positive_values():
    pet = Pet("Mochi", "dog", "Shiba Inu", date(2021, 7, 6), 18.5)

    with pytest.raises(ValueError):
        pet.update_weight(0)

    with pytest.raises(ValueError):
        pet.update_weight(-1)

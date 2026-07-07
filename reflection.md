# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

A pet owner should be able to,
- Add a pet and their details.
- State their time availability.
- See and make changes to today's generated plan.

The first entities that come to mind are Owner, Pet, Task

Owner - Holds the information about the pet owner, like their name, day's schedule
Pet - Types of tasks for this type of pet
Task - Time needed, priority.

I worked with Claude and it suggested adding entities like Medication, Appointment, Veterinarian, TaskLog, Notification.

It also suggested stretch entities like  Medication, Appointment, Veterinarian, TaskLog, HealthRecord, and Caretaker..

I decided to go with Owner, Pet, Task, Scheduler.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I asked Claude to check if there any relationships or potential logic bottlenecks it missed to address.

Relationships:
- It stated that it missed implementing bidirectional relationship between Pet and Owner like Pet.owner and Owner.pets.
- One relationship issue is that Scheduler.tasks if disconnected from Pet.tasks
- The last issue it stated was there was no connection between Owner and Scheduler

Bottlenecks:
- Overdue logic is duplicated across Task and Scheduler classes
- check_conflicts() scope is undefined
- No ID generation strategy for class ids
- Recurring tasks have no regeneration logic

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers four things, 
1. Explicit Priority, if the owner says it is high priority, it gets the largest weight.
2. Task type based on their logical importance
3. Overdue status, high weightage when a task is overdue
4. Time, it is used in conflict detection and sorting


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Conflict detection is passive as in there is no way to see if tasks are overlapping just if they start at the same time. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used Claude across the full lifecycle of the project like Design brainstorming, implementation, concept explanation, verification, and testing.
- Concept explanation, validation, and testing were the most helpful prompts.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- The AI initially suggested to have a lot of classes to be implemented into the app. I decided to have it simple.
- I read what the AI is explaining and verified by checking the code changes. I wrote my own code in main.py to test logic.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Run with:

```
python -m pytest -v
```

My tests in `tests/test_pawpal.py` cover:
- **Recurring tasks** (`mark_complete`): non-recurring tasks return no next occurrence; daily/weekly tasks generate the next occurrence from the *original* scheduled time (not completion time), so a task completed late still produces a next occurrence anchored to the old schedule; the next occurrence is attached to the same pet; a task with no pet produces an orphaned next task; calling `mark_complete` twice on the same task spawns duplicate next-occurrences (an existing quirk, not a fix); `completed_at` is set.
- **Overdue / priority**: `is_overdue()` just before vs. just after its due boundary; always `False` once completed; `get_priority()`'s +10 overdue boost; and a case showing `Task.get_priority()` (0-minute threshold) and `Scheduler.get_score()` (30-minute threshold) can disagree on whether the same task counts as overdue.
- **Sorting/prioritization**: tie-breaking by soonest `scheduled_time`, completed tasks excluded from `prioritize_tasks()`, empty-list behavior, and `schedule_next()` returning `None` when a pet has no pending tasks.
- **Conflict detection**: back-to-back tasks are not a conflict, a 1-minute overlap is, zero-duration tasks at the exact same instant are *not* flagged (a quirk in `find_conflicts()`'s break condition), warning text correctly labels "same pet" vs. "different pets", an unassigned task is labeled "Unassigned", and a chain of overlapping tasks dedups correctly in `check_conflicts()`.
- **Filtering**: `is_completed=False` is respected (not treated as "no filter"), and filtering by a pet name shared by two pets matches both.
- **Pet age**: a birthday that falls exactly today already counts toward the age.
- **Owner/Pet management**: removing an unknown pet/task ID is a no-op, `get_task_summary()` handles zero pets, and `update_weight()` rejects zero/negative values.

These mattered because the scheduler's core value proposition is trustworthy prioritization and conflict warnings — if sorting, overdue detection, or conflict detection is subtly wrong, the owner gets bad recommendations without any error being raised. Several of these tests exist specifically to pin down real quirks I found in the implementation (the double-`mark_complete` duplication and the zero-duration conflict miss) so they don't silently change behavior later without a test failing.

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1, pluggy-1.6.0 -- .venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\svkri\Documents\CodePath\AI110\Week 4\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 31 items

tests/test_pawpal.py::test_task_completion_changes_status PASSED         [  3%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  6%]
tests/test_pawpal.py::test_mark_complete_non_recurring_returns_none PASSED [  9%]
tests/test_pawpal.py::test_mark_complete_daily_creates_next_occurrence_from_original_time PASSED [ 12%]
tests/test_pawpal.py::test_mark_complete_late_still_schedules_from_original_time_not_now PASSED [ 16%]
tests/test_pawpal.py::test_mark_complete_attaches_next_occurrence_to_same_pet PASSED [ 19%]
tests/test_pawpal.py::test_mark_complete_with_no_pet_creates_orphaned_next_task PASSED [ 22%]
tests/test_pawpal.py::test_mark_complete_called_twice_spawns_duplicate_next_occurrences PASSED [ 25%]
tests/test_pawpal.py::test_mark_complete_sets_completed_at PASSED        [ 29%]
tests/test_pawpal.py::test_is_overdue_false_just_before_due_boundary PASSED [ 32%]
tests/test_pawpal.py::test_is_overdue_true_just_past_boundary PASSED     [ 35%]
tests/test_pawpal.py::test_is_overdue_always_false_when_completed PASSED [ 38%]
tests/test_pawpal.py::test_get_priority_boosts_overdue_tasks PASSED      [ 41%]
tests/test_pawpal.py::test_get_priority_and_scheduler_score_can_disagree_on_overdue PASSED [ 45%]
tests/test_pawpal.py::test_prioritize_tasks_breaks_ties_by_soonest_scheduled_time PASSED [ 48%]
tests/test_pawpal.py::test_prioritize_tasks_excludes_completed_tasks PASSED [ 51%]
tests/test_pawpal.py::test_prioritize_tasks_empty_when_no_tasks PASSED   [ 54%]
tests/test_pawpal.py::test_schedule_next_returns_none_when_pet_has_no_pending_tasks PASSED [ 58%]
tests/test_pawpal.py::test_back_to_back_tasks_are_not_a_conflict PASSED  [ 61%]
tests/test_pawpal.py::test_overlapping_by_one_minute_is_a_conflict PASSED [ 64%]
tests/test_pawpal.py::test_zero_duration_tasks_at_same_instant_are_not_flagged PASSED [ 67%]
tests/test_pawpal.py::test_conflict_warning_labels_same_pet_vs_different_pets PASSED [ 70%]
tests/test_pawpal.py::test_conflict_warning_handles_unassigned_task PASSED [ 74%]
tests/test_pawpal.py::test_check_conflicts_dedups_chain_of_overlaps PASSED [ 77%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status_false_is_not_ignored PASSED [ 80%]
tests/test_pawpal.py::test_filter_tasks_by_duplicate_pet_names_matches_both PASSED [ 83%]
tests/test_pawpal.py::test_get_age_counts_birthday_today_as_already_had PASSED [ 87%]
tests/test_pawpal.py::test_remove_pet_with_unknown_id_is_a_no_op PASSED  [ 90%]
tests/test_pawpal.py::test_remove_task_with_unknown_id_is_a_no_op PASSED [ 93%]
tests/test_pawpal.py::test_get_task_summary_with_no_pets PASSED          [ 96%]
tests/test_pawpal.py::test_update_weight_rejects_non_positive_values PASSED [100%]

============================= 31 passed in 0.04s ==============================
```

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Confidence Level: ★★★★☆ (4/5)**

All 31 tests pass, and they exercise the boundary conditions I was most worried about (overlap edges, overdue thresholds, sort tie-breaking, recurring-task regeneration). I'm not giving 5 stars because the tests also surfaced two real quirks I chose to document rather than fix: `mark_complete()` has no guard against being called twice on the same task (it will silently spawn duplicate next-occurrences), and `find_conflicts()` fails to flag two zero-duration tasks scheduled at the exact same instant. Neither breaks the common case, but they're sharp edges a real user could hit.

With more time I would test: multi-owner isolation (confirming one owner's `Scheduler` never surfaces another owner's tasks), a recurring task chained through several `mark_complete()` calls in a row to check the interval keeps compounding correctly, an invalid/future `birthdate` passed to `Pet`, and conflict detection performance/correctness with a larger number of overlapping tasks (the current algorithm is O(n²) in the worst case for tasks that all overlap).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

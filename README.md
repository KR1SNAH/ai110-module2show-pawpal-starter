# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Priority scoring** — `Scheduler.get_score()` ranks tasks by priority x 10, plus a task-type weight x 5 (medication > appointment > feeding > walk), plus a bonus if the task is overdue.
- **Prioritized scheduling** — `Scheduler.prioritize_tasks()` and `Scheduler.schedule_next()` return pending tasks ranked by that score, soonest-scheduled first on ties.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks earliest-to-latest by their `scheduled_time`.
- **Filtering** — `Scheduler.filter_tasks()` narrows the task list by pet and/or completion status, and the two filters compose.
- **Overdue detection** — `Task.is_overdue()` and `Scheduler.get_overdue_tasks()` flag tasks past their scheduled end time plus a configurable grace period.
- **Conflict warnings** — `Scheduler.find_conflicts()` / `check_conflicts()` / `get_conflict_warnings()` detect overlapping task windows across all of an owner's pets and report them as plain-text warnings instead of crashing.
- **Daily & weekly recurrence** — `Task.mark_complete()` auto-generates and attaches the next occurrence for tasks with `TaskFrequency.DAILY` or `WEEKLY`, leaving the completed occurrence in place as history.
- **Owner & pet management** — add/remove pets and tasks, track pet age and weight, and summarize an owner's task load with `Owner.get_task_summary()`.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Sandy : Ginger Female Cat
  - feeding: Morning wet food @ 2026-07-06 16:24
  - medication: Flea prevention drops @ 2026-07-06 18:24
  - appointment: Annual vet checkup @ 2026-07-08 15:24
Tommy : Bicolor Ginger and White Male Cat
  - feeding: Morning dry food @ 2026-07-06 16:24
  - walk: Leash training session @ 2026-07-06 20:24
  - medication: Deworming tablet @ 2026-07-07 15:24
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(tasks=None)` | Sorts tasks earliest-to-latest using `key=lambda t: t.scheduled_time` on the `datetime` directly (no string parsing needed). Defaults to all of the owner's tasks if none are passed in. `Scheduler.prioritize_tasks()` covers priority-based ordering separately, via `_score()` (priority × 10 + task-type weight × 5 + a +100 overdue bonus). |
| Filtering | `Scheduler.filter_tasks(pet_name=None, is_completed=None)` | Filters the owner's tasks by pet name and/or completion status; leaving either argument as `None` skips that filter, so it composes (e.g. "Mochi's pending tasks"). |
| Conflict handling | `Scheduler.find_conflicts()`, `Scheduler.check_conflicts()`, `Scheduler.get_conflict_warnings()` | A sweep-line pass (sort by start time, compare against the running end time) detects overlapping time windows across *all* of an owner's pets — catching both a double-booked pet and two different pets needing the owner at once. `find_conflicts()` returns the raw `(task_a, task_b)` overlap pairs, `check_conflicts()` returns the distinct tasks involved, and `get_conflict_warnings()` turns each pair into a plain-text warning string (e.g. `"...overlaps with '...' -- same pet."`) instead of raising an exception, so a scheduling conflict never crashes the app. |
| Recurring tasks | `Task.mark_complete()`, `TaskFrequency` (`NONE`, `DAILY`, `WEEKLY`) | Completing a task with a non-`NONE` `frequency` creates and returns a **new** `Task` instance scheduled `+1 day` or `+1 week` out (via `_FREQUENCY_INTERVALS`) and attaches it to the same pet with `Pet.add_task()`. The completed occurrence is left in place as history rather than being mutated/reused. |

## 📸 Demo Walkthrough

### Main UI features

Running `streamlit run app.py` opens a single-page app with these interactive pieces:

- **Owner panel** — edit the owner's name, email, and phone; kept in `st.session_state` so it survives Streamlit reruns.
- **Add a Pet** — a form for name, species, breed, birthdate, weight, and medical notes; submitted pets appear in a live table with their computed age.
- **Schedule a Task** — a form to add a task to any existing pet, setting its type (feeding/walk/medication/appointment), description, date/time, duration, priority (1–5), and recurrence (none/daily/weekly).
- **Task list** — every task across all of the owner's pets, filterable by pet and by status (pending/completed), with a "Sort by time" control (none/ascending/descending).
- **Update or Remove a Task** — select any task from the filtered list to edit its details, mark it complete, or delete it.
- **Build Schedule** — an "overdue grace period" slider plus a "Generate schedule" button that shows the prioritized task order, flags overdue tasks, surfaces conflict warnings, and prints an owner-level task summary.

### Example workflow

1. **Add a pet** — fill out the "Add a Pet" form (e.g., "Mochi", a dog) and submit; it appears in the pets table with its computed age.
2. **Schedule a task** — use "Schedule a Task" to add a daily "Morning walk" for Mochi at 8:00 AM, priority 3. Add a second, overlapping task (e.g., "Vet checkup" at 8:10 AM) to see conflict detection in action later.
3. **View today's schedule** — click "Generate schedule" to see the prioritized task order, any overdue flags, and any conflict warnings for the day.
4. **Complete a task** — select the "Morning walk" under "Update or Remove a Task" and click "Mark complete"; since it repeats daily, its next occurrence is scheduled and attached to Mochi automatically.

### Key Scheduler behaviors shown

- **Sorting** — toggling "Sort by time" to Ascending/Descending re-orders the task table via `Scheduler.sort_by_time()`.
- **Prioritization** — "Generate schedule" ranks pending tasks with `Scheduler.prioritize_tasks()`, displaying each task's computed score and overdue status.
- **Conflict warnings** — the overlapping "Morning walk" and "Vet checkup" from step 2 trigger a warning for each overlapping pair from `Scheduler.get_conflict_warnings()`, instead of crashing the app.
- **Recurring tasks** — clicking "Mark complete" on the daily "Morning walk" calls `Task.mark_complete()`, which schedules and attaches its next occurrence one day later while keeping the completed occurrence in history.

### Sample CLI output

`main.py` builds an owner with two cats (Sandy and Tommy), gives each several morning tasks — including two identical "Morning dry food" entries for Tommy — and prints every task caught by `Scheduler.check_conflicts()`:

```
$ python main.py
Morning dry food 2026-07-07 02:09:25.218127
Morning wet food 2026-07-07 02:09:25.218127
Morning dry food 2026-07-07 02:09:25.218127
```

Tommy's two "Morning dry food" tasks and Sandy's "Morning wet food" task were all scheduled for the exact same start time (each built from the same `now + 1 hour` anchor in `main.py`), so all three overlap each other and are reported as conflicts. Sandy's medication, Sandy's vet appointment, and Tommy's walk/deworming tasks don't overlap with anything and are correctly left out. The print order comes from iterating a `set` of the conflicting tasks, so it isn't guaranteed to match scheduled-time order.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

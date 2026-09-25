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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
========================================
        ALL TASKS, SORTED BY TIME
========================================
  - [Sep 17, 03:13 PM] Weekly nail trim
  - [Sep 24, 03:13 PM] Morning walk
  - [Sep 25, 12:13 PM] Litter box scoop
  - [Sep 25, 11:13 PM] Evening medication
  - [Sep 25, 11:13 PM] Evening playtime

========================================
        FILTER: BISCUIT'S TASKS ONLY
========================================
  - Evening medication
  - Morning walk
  - Evening playtime

========================================
        FILTER: COMPLETED TASKS ONLY
========================================
  - Litter box scoop

========================================
        TODAY'S SCHEDULE
========================================

Scheduled:
  - Weekly nail trim (20 min)
  - Evening medication (5 min)
  - Evening playtime (15 min)

Deferred:
  - Morning walk (30 min)

Why these choices:
  - Scheduled 'Weekly nail trim' (20 min): it fit the time left, leaving 25 min.
  - Deferred 'Morning walk' (30 min): only 25 min left in the budget.
  - Scheduled 'Evening medication' (5 min): it fit the time left, leaving 20 min.
  - Scheduled 'Evening playtime' (15 min): it fit the time left, leaving 5 min.
  - Warning: 'Evening medication' and 'Evening playtime' overlap — both run at the same time.

  Conflicts detected:
  - 'Evening medication' overlaps 'Evening playtime'

========================================


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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(tasks)` | Sorts by scheduled `time`, with `task_id` breaking ties. Separate from `_sort_by_priority()`, which orders by how overdue a task is for actual scheduling decisions. |
| Filtering | `Owner.get_tasks_for_pet(pet_id)`, `Owner.get_tasks_by_status(is_completed)` | Return a filtered pet's tasks or tasks by completion status. Both return a new list so filtering never mutates the real task data. |
| Conflict handling | `Scheduler.find_conflicts(tasks)` | Flags any two pending tasks whose durations overlap, including non-adjacent overlaps (a long task colliding with a task two slots later, not just the next one). Completed tasks are excluded. Report-only, doesn't change what gets scheduled. Surfaced through `generate_plan()`'s `"conflicts"` key and warning messages. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task_id)` | Completing a "daily" or "weekly" task through `complete_task()` automatically generates its next occurrence, based on the original scheduled time plus the interval (not the completion time), so a late completion doesn't drift the schedule. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

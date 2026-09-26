# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks for their pets, then explains the plan it produced.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Work within real constraints, primarily the time available in a day and how overdue each task is
- Produce a daily plan and explain why it chose that plan

The system was designed first as a UML diagram, then implemented in Python, then connected to the Streamlit UI.

## What PawPal+ Does

The finished app supports:

- **Owner and pet information** — an owner name, a daily time budget, and one or more pets
- **Care tasks** — each with a description, date, start time, duration, and recurrence setting
- **Completion status** — tasks are pending or done
- **Recurrence** — completing a daily or weekly task automatically creates its next occurrence
- **Chronological sorting** — tasks display in scheduled-time order rather than insertion order
- **Filtering** — by pet and by completion status
- **Schedule generation** — fits due tasks into the owner's available minutes
- **Scheduled vs. deferred** — tasks that didn't fit the budget are listed separately, not dropped
- **Explanations** — a line-by-line account of why each task was scheduled or deferred
- **Conflict detection** — overlapping pending tasks are surfaced as visible warnings

Ordering for schedule generation is based on completion state, scheduled time, task duration, and task ID. There is no manual priority field.

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
streamlit run app.py   # the interactive app
python main.py         # the CLI demo shown below
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect the logic to the Streamlit UI in `app.py`.
7. Refine the UML so it matches what was actually built.

## 💻 Sample CLI Output

`python main.py` builds sample data for two pets and prints the result. It demonstrates sorting, both filters, the scheduled/deferred split, the explanations, and conflict detection:

```text
========================================
        ALL TASKS, SORTED BY TIME
========================================
  - [Sep 18, 11:20 AM] Weekly nail trim
  - [Sep 25, 11:20 AM] Morning walk
  - [Sep 26, 08:20 AM] Litter box scoop
  - [Sep 26, 10:20 AM] Evening medication
  - [Sep 26, 10:20 AM] Evening playtime

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
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Current results — **15 tests passing, 95% total coverage**, with `pawpal_system.py` at 89%:

```text
=================================================================== test session starts ===================================================================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/carliebosier/Documents/Howard Stuff/HU Fall 2026/Intro to AI/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.15.1
collected 15 items

tests/test_pawpal.py ...............                                                                                                                [100%]

===================================================================== tests coverage ======================================================================
____________________________________________________ coverage: platform darwin, python 3.14.7-final-0 _____________________________________________________

Name                   Stmts   Miss  Cover
------------------------------------------
conftest.py                0      0   100%
pawpal_system.py         112     12    89%
tests/test_pawpal.py     108      0   100%
------------------------------------------
TOTAL                    220     12    95%
=================================================================== 15 passed in 0.05s ====================================================================
```

![pytest verbose output listing all 15 tests as PASSED](screenshots/pytest--verbose.png)

![pytest coverage report showing 95% total coverage, 15 passed](screenshots/pytest--cov.png)

### Confidence Level: 4/5

I feel good about the core scheduling logic. All 15 tests pass with 95% coverage, and they cover the behaviors that actually matter — sorting, filtering, recurrence, and conflict detection — not just the easy happy paths.

I'm not giving it a full 5, though. While testing I found a real bug where completing a task could let its next occurrence show up as due immediately instead of the following day, and I had a separate bug in one of my own tests where I mixed up two task IDs. Both are fixed, but it was a good reminder that passing tests don't automatically mean the logic is airtight. About 11% of `pawpal_system.py` is still uncovered.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(tasks)` | Sorts chronologically by scheduled `time`, with `task_id` breaking ties. Distinct from `_sort_by_priority()`, which orders due tasks by completion state, scheduled time, duration, and task ID when building the plan. |
| Filtering | `Owner.get_tasks_for_pet(pet_id)`, `Owner.get_tasks_by_status(is_completed)` | Return one pet's tasks, or tasks matching a completion status. Both return a new list, so filtering never mutates the stored task data. |
| Conflict handling | `Scheduler.find_conflicts(tasks)` | Pairs up pending tasks whose durations overlap, including non-adjacent overlaps (a long task colliding with one two slots later). Completed tasks are excluded. Report-only — conflicts never change or block what gets scheduled, and surface through `generate_plan()`'s `"conflicts"` key and its explanations. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task_id)` | Completing a daily task advances one day; a weekly task advances seven. The next occurrence is based on the original scheduled time plus the interval, not the completion time, so a late completion doesn't drift the schedule. |

## 🎬 Demo Walkthrough

1. **Set up the owner.** Enter the owner name and the minutes available today in the **Owner** section.
2. **Add a pet.** Enter a name, pick a species, and click **Add pet**. Tasks can't be added until at least one pet exists.
3. **Add a care task.** Choose which pet it belongs to, then enter a title, duration, and frequency (daily, weekly, or as needed), plus the date and start time it's scheduled for.
4. **Review the task list.** The table shows every task in chronological order. Use **Filter by pet** and **Filter by status** (All / Pending / Completed) to narrow it down.
5. **Complete a recurring task.** Click the **Mark '…' done** button beneath the table. The task flips to `done` and, if it recurs, the next occurrence appears in the table with its new date.
6. **Generate the plan.** Click **Generate schedule**. The scheduler fits due tasks into the available minutes and lists what it booked.
7. **Read the split and the reasoning.** Tasks that fit appear under *Today's plan*; anything that exceeded the remaining budget appears under *Deferred*. The *Why the scheduler made these calls* panel explains each decision, with the minutes left after each one.
8. **Watch for conflicts.** If two pending tasks overlap in time, a warning appears at the top of the results and in the explanations. Conflicts are informational — they don't stop the schedule from being generated.


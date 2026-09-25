"""Tests for the PawPal+ core domain classes."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_marks_the_task_completed():
    """A new task starts incomplete and mark_complete() flips it to done."""
    task = Task(
        task_id="t1",
        description="Morning walk",
        time=datetime(2026, 9, 22, 8, 0),
        frequency="daily",
        duration_minutes=30,
    )

    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_attaches_the_task_to_the_pet():
    """A new pet has no tasks, and add_task() puts one on its list."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")

    assert len(pet.get_tasks()) == 0

    task = Task(
        task_id="t2",
        description="Evening medication",
        time=datetime(2026, 9, 22, 19, 0),
        frequency="daily",
        duration_minutes=5,
    )
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_find_conflicts_flags_overlapping_tasks():
    """A 30-minute task at 8:00 collides with a task starting at 8:10."""
    walk = Task(
        task_id="t1",
        description="Morning walk",
        time=datetime(2026, 9, 22, 8, 0),
        frequency="daily",
        duration_minutes=30,
    )
    pill = Task(
        task_id="t2",
        description="Morning medication",
        time=datetime(2026, 9, 22, 8, 10),
        frequency="daily",
        duration_minutes=5,
    )

    conflicts = Scheduler().find_conflicts([walk, pill])

    assert len(conflicts) == 1
    assert conflicts[0][0].task_id == "t1"
    assert conflicts[0][1].task_id == "t2"


def test_find_conflicts_returns_empty_when_tasks_do_not_overlap():
    """Back-to-back tasks are fine: one ending exactly when the next starts is no conflict."""
    walk = Task(
        task_id="t1",
        description="Morning walk",
        time=datetime(2026, 9, 22, 8, 0),
        frequency="daily",
        duration_minutes=30,
    )
    breakfast = Task(
        task_id="t2",
        description="Breakfast",
        time=datetime(2026, 9, 22, 8, 30),
        frequency="daily",
        duration_minutes=10,
    )

    assert Scheduler().find_conflicts([walk, breakfast]) == []


def test_find_conflicts_ignores_completed_tasks():
    """A finished task never conflicts, since completed tasks linger on a pet's list."""
    done_walk = Task(
        task_id="t1",
        description="Morning walk",
        time=datetime(2026, 9, 22, 8, 0),
        frequency="daily",
        is_completed=True,
        duration_minutes=30,
    )
    pill = Task(
        task_id="t2",
        description="Morning medication",
        time=datetime(2026, 9, 22, 8, 10),
        frequency="daily",
        duration_minutes=5,
    )

    assert Scheduler().find_conflicts([done_walk, pill]) == []


def test_find_conflicts_catches_non_adjacent_overlap():
    """A long task conflicts with every task it runs past, not just the one right after it."""
    walk = Task(
        task_id="t1",
        description="Long morning walk",
        time=datetime(2026, 9, 22, 8, 0),
        frequency="daily",
        duration_minutes=60,
    )
    pill = Task(
        task_id="t2",
        description="Morning medication",
        time=datetime(2026, 9, 22, 8, 10),
        frequency="daily",
        duration_minutes=5,
    )
    feed = Task(
        task_id="t3",
        description="Breakfast",
        time=datetime(2026, 9, 22, 8, 30),
        frequency="daily",
        duration_minutes=10,
    )

    conflicts = Scheduler().find_conflicts([walk, pill, feed])

    # The walk runs until 9:00, so it collides with both later tasks; the pill
    # ends at 8:15 and so clears the 8:30 breakfast.
    assert [(first.task_id, second.task_id) for first, second in conflicts] == [
        ("t1", "t2"),
        ("t1", "t3"),
    ]


def test_generate_plan_reports_conflicts():
    """generate_plan() surfaces overlaps under "conflicts" and warns about them."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    pet.add_task(
        Task(
            task_id="t1",
            description="Morning walk",
            time=datetime(2026, 9, 22, 8, 0),
            frequency="daily",
            duration_minutes=30,
        )
    )
    pet.add_task(
        Task(
            task_id="t2",
            description="Morning medication",
            time=datetime(2026, 9, 22, 8, 10),
            frequency="daily",
            duration_minutes=5,
        )
    )
    owner = Owner(owner_id="o1", name="Alex", available_time_minutes=45)
    owner.add_pet(pet)

    plan = Scheduler().generate_plan(owner, datetime(2026, 9, 22, 9, 0))

    assert len(plan["conflicts"]) == 1
    assert any("overlap" in explanation for explanation in plan["explanations"])
    # Reporting only: both tasks still fit the budget and stay scheduled.
    assert len(plan["scheduled"]) == 2
    assert plan["deferred"] == []

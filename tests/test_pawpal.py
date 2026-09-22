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

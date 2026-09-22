"""Core domain classes for PawPal+ (Owner, Pet, Task, Scheduler)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Task:
    """A single unit of pet care to be scheduled, such as a walk or a dose of medication."""

    task_id: str
    description: str
    time: datetime
    frequency: str
    is_completed: bool = False
    duration_minutes: int = 0

    def is_due(self, current_time: datetime) -> bool:
        """Report whether this task needs doing as of the given time."""
        if not self.is_completed:
            return True

        elapsed = current_time - self.time
        frequency = self.frequency.strip().lower()

        if frequency == "daily":
            return elapsed >= timedelta(hours=24)
        if frequency == "weekly":
            return elapsed >= timedelta(days=7)

        # Frequency parsing is simplified for now: anything that isn't "daily" or
        # "weekly" (e.g. "every 6 hours", "mon/wed/fri") is treated as always due.
        return True

    def mark_complete(self) -> None:
        """Record that this task was finished, stamping the completion time onto `time`."""
        self.is_completed = True
        self.time = datetime.now()


@dataclass
class Pet:
    """A pet's profile and the care tasks attached to it."""

    pet_id: str
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return every task attached to this pet."""
        return self.tasks


class Owner:
    """The person responsible for one or more pets and their daily time budget."""

    def __init__(
        self,
        owner_id: str,
        name: str,
        pets: list[Pet] | None = None,
        available_time_minutes: int = 0,
    ) -> None:
        """Create an owner with their pets and daily care time budget."""
        self.owner_id: str = owner_id
        self.name: str = name
        self.pets: list[Pet] = pets if pets is not None else []
        self.available_time_minutes: int = available_time_minutes

    def add_pet(self, pet: Pet) -> None:
        """Put a pet under this owner's care."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all of this owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Turns an owner's due tasks and time budget into a daily plan."""

    def generate_plan(self, owner: Owner, current_time: datetime) -> dict:
        """Fit the most urgent due tasks into the owner's time budget, explaining each call."""
        due_tasks = [task for task in owner.get_all_tasks() if task.is_due(current_time)]
        ordered_tasks = self._sort_by_priority(due_tasks)

        remaining_minutes = owner.available_time_minutes
        scheduled: list[Task] = []
        deferred: list[Task] = []
        explanations: list[str] = []

        for task in ordered_tasks:
            if self._fits(task, remaining_minutes):
                scheduled.append(task)
                remaining_minutes -= task.duration_minutes
                explanations.append(
                    f"Scheduled '{task.description}' ({task.duration_minutes} min): "
                    f"it fit the time left, leaving {remaining_minutes} min."
                )
            else:
                deferred.append(task)
                explanations.append(
                    f"Deferred '{task.description}' ({task.duration_minutes} min): "
                    f"only {remaining_minutes} min left in the budget."
                )

        return {"scheduled": scheduled, "deferred": deferred, "explanations": explanations}

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Order tasks most urgent first, judging urgency by how overdue each one is."""
        # Never-completed tasks outrank completed-but-recurring ones, then the
        # oldest `time` wins, since that is the task that has waited longest.
        return sorted(
            tasks,
            key=lambda task: (task.is_completed, task.time, task.duration_minutes, task.task_id),
        )

    def _fits(self, task: Task, remaining_minutes: int) -> bool:
        """Report whether a task still fits in the time left in the plan."""
        return task.duration_minutes <= remaining_minutes

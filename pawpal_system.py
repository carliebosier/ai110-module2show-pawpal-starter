"""Core domain classes for PawPal+ (skeleton stage — no logic implemented yet)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class Category(Enum):
    """The kind of care a task represents."""

    WALK = "walk"
    FEED = "feed"
    MED = "med"
    GROOM = "groom"
    ENRICHMENT = "enrichment"


class Priority(Enum):
    """How important a task is relative to the others competing for the same time."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Frequency(Enum):
    """How often a task recurs."""

    DAILY = "daily"
    WEEKLY = "weekly"
    EVERY_N_HOURS = "every_n_hours"
    SPECIFIC_DAYS = "specific_days"


@dataclass
class Task:
    """A single unit of pet care to be scheduled, such as a walk or a dose of medication."""

    task_id: str
    name: str
    category: Category
    duration_minutes: int
    priority: Priority
    frequency: Frequency
    last_completed_time: datetime | None = None

    def is_due(self, current_time: datetime) -> bool:
        """Report whether this task needs doing as of the given time."""
        raise NotImplementedError

    def mark_complete(self, current_time: datetime) -> None:
        """Record that this task was finished at the given time."""
        raise NotImplementedError

    def get_priority_score(self, current_time: datetime) -> float:
        """Rank this task against others by combining its priority with how overdue it is."""
        raise NotImplementedError


@dataclass
class Preferences:
    """The owner's daily constraints on when and how much care they can give."""

    wake_time: time
    sleep_time: time
    available_time_minutes: int

    def fits(self, task: Task) -> bool:
        """Report whether a single task is short enough to fit the available time."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet's profile and the care tasks attached to it."""

    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    dietary_notes: str
    medical_notes: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return every task attached to this pet."""
        raise NotImplementedError

    def update_profile(self, **kwargs) -> None:
        """Change one or more profile fields on this pet."""
        raise NotImplementedError


class Owner:
    """The person responsible for one or more pets and their care preferences."""

    def __init__(
        self,
        owner_id: str,
        name: str,
        pets: list[Pet],
        preferences: Preferences,
    ) -> None:
        """Create an owner with their pets and scheduling preferences."""
        self.owner_id: str = owner_id
        self.name: str = name
        self.pets: list[Pet] = pets
        self.preferences: Preferences = preferences

    def add_pet(self, pet: Pet) -> None:
        """Put a pet under this owner's care."""
        raise NotImplementedError

    def set_preferences(self, **kwargs) -> None:
        """Change one or more of this owner's scheduling preferences."""
        raise NotImplementedError

    def get_all_tasks_today(self, current_time: datetime) -> list[Task]:
        """Collect the tasks due as of the given time across all of this owner's pets."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """One day's care schedule, including what was left out and why."""

    date: date
    owner: Owner
    scheduled_tasks: list[Task]
    deferred_tasks: list[Task]
    explanations: list[str]

    def total_minutes(self) -> int:
        """Return the combined duration of the scheduled tasks."""
        raise NotImplementedError

    def get_summary(self) -> str:
        """Render this plan as readable text for display."""
        raise NotImplementedError


class Scheduler:
    """Turns a set of due tasks and a time budget into a daily plan."""

    def __init__(self, tasks: list[Task], available_time_minutes: int) -> None:
        """Create a scheduler for the given tasks and time budget."""
        self.tasks: list[Task] = tasks
        self.available_time_minutes: int = available_time_minutes

    def generate_plan(self, tasks: list[Task], available_time: int) -> DailyPlan:
        """Build a daily plan by fitting the highest-priority tasks into the available time."""
        raise NotImplementedError

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Order tasks most urgent first."""
        raise NotImplementedError

    def _fits(self, task: Task, remaining_minutes: int) -> bool:
        """Report whether a task still fits in the time left in the plan."""
        raise NotImplementedError

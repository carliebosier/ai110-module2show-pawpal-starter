"""Demo script for PawPal+: builds sample data and prints today's schedule."""

from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    now = datetime.now()

    # --- Owner ---
    owner = Owner(owner_id="o1", name="Alex", available_time_minutes=45)

    # --- Pets (at least two) ---
    biscuit = Pet(pet_id="p1", name="Biscuit", species="Dog")
    whiskers = Pet(pet_id="p2", name="Whiskers", species="Cat")

    # --- Tasks added out of order on purpose, to prove sort_by_time() actually sorts ---
    biscuit.add_task(
        Task(
            task_id="t2",
            description="Evening medication",
            time=now - timedelta(hours=1),  # due an hour ago
            frequency="daily",
            duration_minutes=5,
        )
    )
    biscuit.add_task(
        Task(
            task_id="t1",
            description="Morning walk",
            time=now - timedelta(days=1),  # last done yesterday -> due again
            frequency="daily",
            duration_minutes=30,
        )
    )
    whiskers.add_task(
        Task(
            task_id="t3",
            description="Weekly nail trim",
            time=now - timedelta(days=8),  # last done over a week ago -> due
            frequency="weekly",
            duration_minutes=20,
        )
    )
    # One already-completed task, so the status filter has something to find.
    whiskers.add_task(
        Task(
            task_id="t4",
            description="Litter box scoop",
            time=now - timedelta(hours=3),
            frequency="daily",
            duration_minutes=5,
            is_completed=True,
            completed_at=now - timedelta(hours=3),
        )
    )
    # Deliberately overlaps t2 (Evening medication, 5 min, same start time) so
    # Scheduler.find_conflicts() has something real to catch in this demo.
    biscuit.add_task(
        Task(
            task_id="t5",
            description="Evening playtime",
            time=now - timedelta(hours=1),  # same start time as t2 -> overlap
            frequency="daily",
            duration_minutes=15,
        )
    )

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    scheduler = Scheduler()

    # --- Sorting demo ---
    print("=" * 40)
    print("        ALL TASKS, SORTED BY TIME")
    print("=" * 40)
    for task in scheduler.sort_by_time(owner.get_all_tasks()):
        print(f"  - [{task.time.strftime('%b %d, %I:%M %p')}] {task.description}")

    # --- Filtering demo ---
    print("\n" + "=" * 40)
    print("        FILTER: BISCUIT'S TASKS ONLY")
    print("=" * 40)
    for task in owner.get_tasks_for_pet("p1"):
        print(f"  - {task.description}")

    print("\n" + "=" * 40)
    print("        FILTER: COMPLETED TASKS ONLY")
    print("=" * 40)
    completed = owner.get_tasks_by_status(is_completed=True)
    if completed:
        for task in completed:
            print(f"  - {task.description}")
    else:
        print("  (none completed yet)")

    # --- Generate today's plan (unchanged from Phase 2) ---
    plan = scheduler.generate_plan(owner, now)

    print("\n" + "=" * 40)
    print("        TODAY'S SCHEDULE")
    print("=" * 40)

    if plan["scheduled"]:
        print("\nScheduled:")
        for task in plan["scheduled"]:
            print(f"  - {task.description} ({task.duration_minutes} min)")
    else:
        print("\nScheduled: (nothing fit today's time budget)")

    if plan["deferred"]:
        print("\nDeferred:")
        for task in plan["deferred"]:
            print(f"  - {task.description} ({task.duration_minutes} min)")

    print("\nWhy these choices:")
    for line in plan["explanations"]:
        print(f"  - {line}")

    if plan["conflicts"]:
        print("\n Conflicts detected:")
        for first, second in plan["conflicts"]:
            print(f"  - '{first.description}' overlaps '{second.description}'")
    else:
        print("\nNo conflicts detected.")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
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
 
    # --- Tasks (at least three, with different times) ---
    biscuit.add_task(
        Task(
            task_id="t1",
            description="Morning walk",
            time=now - timedelta(days=1),  # last done yesterday -> due again
            frequency="daily",
            duration_minutes=30,
        )
    )
    biscuit.add_task(
        Task(
            task_id="t2",
            description="Evening medication",
            time=now,
            frequency="daily",
            duration_minutes=5,
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
 
    owner.add_pet(biscuit)
    owner.add_pet(whiskers)
 
    # --- Generate today's plan ---
    scheduler = Scheduler()
    plan = scheduler.generate_plan(owner, now)
 
    # --- Print a readable "Today's Schedule" ---
    print("=" * 40)
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
 
    print("\n" + "=" * 40)
 
 
if __name__ == "__main__":
    main()
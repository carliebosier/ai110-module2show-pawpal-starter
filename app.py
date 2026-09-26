from datetime import datetime
from uuid import uuid4

import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like available time and how overdue each task is.

This app is the interactive demo for the classes in `pawpal_system.py`.
"""
)

with st.expander("How the pieces fit together", expanded=False):
    st.markdown(
        """
- **Task** — one unit of care (description, duration, frequency).
- **Pet** — a profile plus the tasks attached to it (`add_task`, `get_tasks`).
- **Owner** — the person, their pets, and a daily time budget (`add_pet`, `get_all_tasks`).
- **Scheduler** — fits the most overdue due tasks into the budget and explains each call.

The UI below builds real objects and hands them to those methods. The `Owner` lives in
`st.session_state`, so it survives Streamlit's rerun-on-every-interaction.
"""
    )

st.divider()

# The whole object graph hangs off this one Owner, so it is the only thing that
# needs to live in session_state. Mutating it in place persists automatically.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id=f"owner-{uuid4().hex[:8]}",
        name="Jordan",
        available_time_minutes=120,
    )

owner: Owner = st.session_state.owner

# One Scheduler for the whole page: the task list sorts with it long before the
# "Generate schedule" button below ever runs.
scheduler = Scheduler()

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name, key="owner_name_input")
owner.available_time_minutes = int(
    st.number_input(
        "Time available today (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.available_time_minutes,
        step=15,
        key="owner_time_input",
    )
)

st.divider()

st.subheader("Pets")
st.caption("Add a pet, then attach care tasks to it below.")

pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    new_pet_name = st.text_input("Pet name", value="Mochi", key="new_pet_name")
with pet_col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

if st.button("Add pet"):
    if not new_pet_name.strip():
        st.warning("Give the pet a name first.")
    else:
        # Build the object here, hand the finished Pet to the Owner — the same
        # shape as Task construction below.
        pet = Pet(
            pet_id=f"pet-{uuid4().hex[:8]}",
            name=new_pet_name.strip(),
            species=new_pet_species,
        )
        owner.add_pet(pet)
        st.success(f"Added {pet.name} ({pet.species}).")

if not owner.pets:
    st.info("No pets yet. Add one above to start scheduling.")
    st.stop()

st.write(f"**{owner.name}** is caring for: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.divider()

st.subheader("Tasks")
st.caption("Tasks attach to a specific pet and feed straight into the scheduler.")

# Select by pet_id, not by the Pet itself: Streamlit deep-copies widget values,
# so a selectbox over Pet objects hands back a copy and add_task would mutate
# the copy instead of the Pet living in session_state.
pets_by_id = {pet.pet_id: pet for pet in owner.pets}
selected_pet_id = st.selectbox(
    "Which pet is this task for?",
    options=list(pets_by_id),
    format_func=lambda pet_id: f"{pets_by_id[pet_id].name} ({pets_by_id[pet_id].species})",
    key="task_pet_choice",
)
selected_pet: Pet = pets_by_id[selected_pet_id]

task_col1, task_col2, task_col3 = st.columns(3)
with task_col1:
    task_description = st.text_input("Task title", value="Morning walk", key="new_task_title")
with task_col2:
    task_duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20, key="new_task_duration"
    )
with task_col3:
    # Task has no priority field — Scheduler derives urgency from completion state
    # and how long a task has waited. `frequency` is what Task.is_due reads.
    task_frequency = st.selectbox(
        "Frequency", ["daily", "weekly", "as needed"], key="new_task_frequency"
    )

# When this task is due, rather than whenever the button happened to be clicked.
# Scheduler and Task.is_due both read `time`, so this is what makes a task land
# at 10 AM instead of "now", and what lets two tasks actually conflict.
time_col1, time_col2 = st.columns(2)
with time_col1:
    task_date = st.date_input("Date", value=datetime.now().date(), key="new_task_date")
with time_col2:
    task_time = st.time_input(
        "Start time", value=datetime.now().time().replace(second=0, microsecond=0), key="new_task_time"
    )

if st.button("Add task"):
    if not task_description.strip():
        st.warning("Give the task a description first.")
    else:
        task = Task(
            task_id=f"task-{uuid4().hex[:8]}",
            description=task_description.strip(),
            time=datetime.combine(task_date, task_time),
            frequency=task_frequency,
            duration_minutes=int(task_duration),
        )
        selected_pet.add_task(task)
        st.success(
            f"Added '{task.description}' to {selected_pet.name} "
            f"for {task.time.strftime('%b %d at %I:%M %p')}."
        )

# The button click already triggered this rerun, and this block runs after the
# mutation above, so the new task shows up without an explicit st.rerun().
st.markdown("#### Task list")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    # "" stands in for "every pet" so the options stay plain pet_id strings.
    pet_filter = st.selectbox(
        "Filter by pet",
        options=[""] + list(pets_by_id),
        format_func=lambda pet_id: "All pets" if not pet_id else pets_by_id[pet_id].name,
        key="task_pet_filter",
    )
with filter_col2:
    status_filter = st.radio(
        "Filter by status",
        options=["All", "Pending", "Completed"],
        horizontal=True,
        key="task_status_filter",
    )

visible_tasks = owner.get_tasks_for_pet(pet_filter) if pet_filter else owner.get_all_tasks()

if status_filter != "All":
    # get_tasks_by_status spans every pet, so intersect by id to keep the pet
    # filter above applied rather than overriding it.
    wanted_ids = {task.task_id for task in owner.get_tasks_by_status(status_filter == "Completed")}
    visible_tasks = [task for task in visible_tasks if task.task_id in wanted_ids]

# Chronological rather than insertion order — the scheduler's own ordering rule.
visible_tasks = scheduler.sort_by_time(visible_tasks)

pet_name_by_task_id = {task.task_id: pet.name for pet in owner.pets for task in pet.get_tasks()}

if not visible_tasks:
    st.caption("No tasks match these filters.")
else:
    st.dataframe(
        [
            {
                "Pet": pet_name_by_task_id[task.task_id],
                "Task": task.description,
                "Minutes": task.duration_minutes,
                "Frequency": task.frequency,
                "Status": "done" if task.is_completed else "pending",
                "Scheduled for": task.time.strftime("%b %d, %I:%M %p"),
            }
            for task in visible_tasks
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.caption("Completing a recurring task queues up its next occurrence.")
    # Record the click and act after the loop: complete_task appends the next
    # occurrence to the same list this loop is walking.
    completion_request: tuple[Pet, str] | None = None
    for task in visible_tasks:
        if task.is_completed:
            continue
        owning_pet = next(pet for pet in owner.pets if task in pet.get_tasks())
        if st.button(
            f"Mark '{task.description}' done ({owning_pet.name})",
            key=f"complete_{task.task_id}",
        ):
            completion_request = (owning_pet, task.task_id)

    if completion_request is not None:
        pet_to_update, task_id = completion_request
        upcoming = pet_to_update.complete_task(task_id)
        if upcoming is None:
            st.session_state.completion_note = "Marked done — this task does not recur."
        else:
            st.session_state.completion_note = (
                f"Marked done — next '{upcoming.description}' is set for "
                f"{upcoming.time.strftime('%b %d, %I:%M %p')}."
            )
        # Rerun so the table redraws with the completion and its next occurrence.
        st.rerun()

if "completion_note" in st.session_state:
    st.success(st.session_state.pop("completion_note"))

st.divider()

st.subheader("Build Schedule")
st.caption(
    f"Fits the most overdue tasks into {owner.available_time_minutes} minutes, most urgent first."
)

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.info("Add at least one task before generating a schedule.")
    else:
        plan = scheduler.generate_plan(owner, datetime.now())

        # Conflicts render on the page directly — a real scheduling collision is
        # the one thing the owner has to see without clicking anything open.
        for first, second in plan["conflicts"]:
            st.warning(
                f"⚠️ '{first.description}' and '{second.description}' overlap "
                f"— both are scheduled at the same time."
            )

        scheduled = plan["scheduled"]
        deferred = plan["deferred"]

        booked = sum(task.duration_minutes for task in scheduled)
        st.markdown(
            f"**{len(scheduled)} scheduled**, {len(deferred)} deferred — "
            f"{booked} of {owner.available_time_minutes} minutes booked."
        )

        st.markdown("#### Today's plan")
        if scheduled:
            st.success(f"{len(scheduled)} task(s) fit today's {booked}-minute plan.")
            st.table(
                [
                    {
                        "#": position,
                        "Task": task.description,
                        "Minutes": task.duration_minutes,
                        "Frequency": task.frequency,
                        "Scheduled for": task.time.strftime("%b %d, %I:%M %p"),
                    }
                    for position, task in enumerate(scheduler.sort_by_time(scheduled), start=1)
                ]
            )
        else:
            st.warning("Nothing fit in the time available.")

        if deferred:
            st.markdown("#### Deferred")
            st.table(
                [
                    {
                        "Task": task.description,
                        "Minutes": task.duration_minutes,
                        "Frequency": task.frequency,
                        "Scheduled for": task.time.strftime("%b %d, %I:%M %p"),
                    }
                    for task in scheduler.sort_by_time(deferred)
                ]
            )

        with st.expander("Why the scheduler made these calls", expanded=True):
            for explanation in plan["explanations"]:
                st.markdown(f"- {explanation}")

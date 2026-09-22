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

if st.button("Add task"):
    if not task_description.strip():
        st.warning("Give the task a description first.")
    else:
        task = Task(
            task_id=f"task-{uuid4().hex[:8]}",
            description=task_description.strip(),
            time=datetime.now(),
            frequency=task_frequency,
            duration_minutes=int(task_duration),
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task.description}' to {selected_pet.name}.")

# The button click already triggered this rerun, and this block runs after the
# mutation above, so the new task shows up without an explicit st.rerun().
for pet in owner.pets:
    tasks = pet.get_tasks()
    st.markdown(f"**{pet.name}'s tasks**")
    if not tasks:
        st.caption("No tasks yet.")
        continue
    st.table(
        [
            {
                "Task": task.description,
                "Minutes": task.duration_minutes,
                "Frequency": task.frequency,
                "Status": "done" if task.is_completed else "pending",
                "Last done / added": task.time.strftime("%b %d, %I:%M %p"),
            }
            for task in tasks
        ]
    )

st.divider()

st.subheader("Build Schedule")
st.caption(
    f"Fits the most overdue tasks into {owner.available_time_minutes} minutes, most urgent first."
)

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.info("Add at least one task before generating a schedule.")
    else:
        plan = Scheduler().generate_plan(owner, datetime.now())

        scheduled = plan["scheduled"]
        deferred = plan["deferred"]

        booked = sum(task.duration_minutes for task in scheduled)
        st.markdown(
            f"**{len(scheduled)} scheduled**, {len(deferred)} deferred — "
            f"{booked} of {owner.available_time_minutes} minutes booked."
        )

        st.markdown("#### Today's plan")
        if scheduled:
            for position, task in enumerate(scheduled, start=1):
                st.write(f"{position}. **{task.description}** — {task.duration_minutes} min ({task.frequency})")
        else:
            st.warning("Nothing fit in the time available.")

        if deferred:
            st.markdown("#### Deferred")
            for task in deferred:
                st.write(f"- {task.description} — {task.duration_minutes} min ({task.frequency})")

        with st.expander("Why the scheduler made these calls", expanded=True):
            for explanation in plan["explanations"]:
                st.markdown(f"- {explanation}")

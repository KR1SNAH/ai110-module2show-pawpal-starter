import streamlit as st
from datetime import date, datetime

from pawpal_system import Owner, Pet, Task, TaskType, TaskFrequency, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Owner persists in session_state so pets/tasks survive Streamlit reruns
# (the whole script re-executes on every widget interaction).
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "jordan@example.com", "555-0100")
owner = st.session_state.owner

st.subheader("Owner")
ocol1, ocol2, ocol3 = st.columns(3)
with ocol1:
    owner.name = st.text_input("Owner name", value=owner.name)
with ocol2:
    owner.email = st.text_input("Owner email", value=owner.email)
with ocol3:
    owner.phone = st.text_input("Owner phone", value=owner.phone)

st.markdown("### Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with pcol2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol3:
        breed = st.text_input("Breed", value="")
    pcol4, pcol5 = st.columns(2)
    with pcol4:
        birthdate = st.date_input("Birthdate", value=date(2022, 1, 1))
    with pcol5:
        weight = st.number_input("Weight (lbs)", min_value=0.1, value=20.0)
    medical_notes = st.text_input("Medical notes", value="")

    if st.form_submit_button("Add pet"):
        pet = Pet(pet_name, species, breed, birthdate, weight, medical_notes)
        owner.add_pet(pet)
        st.success(f"Added {pet.name} ({pet.get_age()} yr old {species}) to {owner.name}'s pets.")

if owner.get_pets():
    st.write("Current pets:")
    st.table(
        [
            {
                "Name": p.name,
                "Species": p.species,
                "Breed": p.breed,
                "Age": p.get_age(),
                "Weight": p.weight,
            }
            for p in owner.get_pets()
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Schedule a Task")

if owner.get_pets():
    # selectbox options are kept as plain strings (not Pet/TaskType objects) and
    # looked up afterward -- Streamlit's widget state is built for primitive values.
    pets_by_name = {p.name: p for p in owner.get_pets()}
    task_types_by_label = {t.value: t for t in TaskType}
    frequencies_by_label = {f.value: f for f in TaskFrequency}

    with st.form("add_task_form", clear_on_submit=True):
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            selected_pet_name = st.selectbox("Pet", list(pets_by_name.keys()))
        with tcol2:
            task_type_label = st.selectbox("Task type", list(task_types_by_label.keys()))
        description = st.text_input("Description", value="Morning walk")
        tcol3, tcol4, tcol5 = st.columns(3)
        with tcol3:
            scheduled_date = st.date_input("Date", value=date.today(), key="task_date")
        with tcol4:
            scheduled_clock = st.time_input("Time", value=datetime.now().time(), key="task_time")
        with tcol5:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        tcol6, tcol7 = st.columns(2)
        with tcol6:
            priority = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)
        with tcol7:
            frequency_label = st.selectbox("Repeats", list(frequencies_by_label.keys()))

        if st.form_submit_button("Add task"):
            selected_pet = pets_by_name[selected_pet_name]
            task_type = task_types_by_label[task_type_label]
            frequency = frequencies_by_label[frequency_label]
            scheduled_time = datetime.combine(scheduled_date, scheduled_clock)
            task = Task(
                task_type,
                description,
                scheduled_time,
                int(duration),
                priority,
                frequency=frequency,
            )
            selected_pet.add_task(task)
            st.success(
                f"Added '{description}' for {selected_pet.name} "
                f"at {scheduled_time.strftime('%Y-%m-%d %H:%M')}."
            )
else:
    st.info("Add a pet first before scheduling tasks.")

all_tasks = [(p, t) for p in owner.get_pets() for t in p.get_tasks()]
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Pet": p.name,
                "Type": t.task_type.value,
                "Description": t.description,
                "When": t.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Repeats": t.frequency.value,
                "Completed": t.is_completed,
            }
            for p, t in all_tasks
        ]
    )

    st.markdown("#### Update or Remove a Task")

    # task_id (a plain string) is used as the selectbox option, not the Task
    # object itself, since Streamlit's widget state is built for primitive values.
    tasks_by_id = {t.task_id: t for _, t in all_tasks}

    def _format_task(task_id: str) -> str:
        t = tasks_by_id[task_id]
        pet_name = t.pet.name if t.pet is not None else "Unassigned"
        status = "done" if t.is_completed else "pending"
        when = t.scheduled_time.strftime("%Y-%m-%d %H:%M")
        return f"[{status}] {pet_name} - {t.description} ({when})"

    # Outside the form so switching tasks immediately refreshes the fields below.
    selected_task_id = st.selectbox(
        "Select a task to update or remove",
        list(tasks_by_id.keys()),
        format_func=_format_task,
        key="manage_task_selector",
    )
    selected_task = tasks_by_id[selected_task_id]

    with st.form("manage_task_form"):
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            edited_description = st.text_input(
                "Description",
                value=selected_task.description,
                key=f"manage_description_{selected_task_id}",
            )
        with mcol2:
            edited_duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=selected_task.duration,
                key=f"manage_duration_{selected_task_id}",
            )
        mcol3, mcol4, mcol5 = st.columns(3)
        with mcol3:
            edited_date = st.date_input(
                "Date",
                value=selected_task.scheduled_time.date(),
                key=f"manage_date_{selected_task_id}",
            )
        with mcol4:
            edited_clock = st.time_input(
                "Time",
                value=selected_task.scheduled_time.time(),
                key=f"manage_time_{selected_task_id}",
            )
        with mcol5:
            edited_priority = st.slider(
                "Priority (1=low, 5=high)",
                min_value=1,
                max_value=5,
                value=selected_task.priority,
                key=f"manage_priority_{selected_task_id}",
            )

        ucol1, ucol2, ucol3 = st.columns(3)
        with ucol1:
            update_clicked = st.form_submit_button("Update task")
        with ucol2:
            complete_clicked = st.form_submit_button("Mark complete")
        with ucol3:
            remove_clicked = st.form_submit_button("Remove task")

        if update_clicked:
            selected_task.description = edited_description
            selected_task.duration = int(edited_duration)
            selected_task.priority = edited_priority
            selected_task.reschedule(datetime.combine(edited_date, edited_clock))
            st.success(f"Updated '{selected_task.description}'.")
        elif complete_clicked:
            next_task = selected_task.mark_complete()
            if next_task is not None:
                st.success(
                    f"Marked '{selected_task.description}' complete. Next occurrence "
                    f"scheduled for {next_task.scheduled_time.strftime('%Y-%m-%d %H:%M')}."
                )
            else:
                st.success(f"Marked '{selected_task.description}' complete.")
        elif remove_clicked:
            if selected_task.pet is not None:
                selected_task.pet.remove_task(selected_task.task_id)
            st.success(f"Removed '{selected_task.description}'.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

# Scheduler is bound to this owner and persists across reruns; its `tasks`
# property reads live from owner.pets, so it never needs to be refreshed
# when pets/tasks change elsewhere on the page.
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner)
scheduler = st.session_state.scheduler

scheduler.overdue_threshold = st.slider(
    "Overdue grace period (minutes)",
    min_value=0,
    max_value=120,
    value=scheduler.overdue_threshold,
    key="overdue_threshold_slider",
)

if st.button("Generate schedule"):
    st.session_state.schedule_generated = True

if st.session_state.get("schedule_generated"):
    prioritized = scheduler.prioritize_tasks()

    if prioritized:
        st.write("Prioritized task order (highest priority first):")
        st.table(
            [
                {
                    "Rank": rank,
                    "Pet": t.pet.name if t.pet is not None else "Unassigned",
                    "Type": t.task_type.value,
                    "Description": t.description,
                    "When": t.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                    "Score": scheduler.get_score(t),
                    "Overdue": t.is_overdue(scheduler.overdue_threshold),
                }
                for rank, t in enumerate(prioritized, start=1)
            ]
        )
        st.caption(
            "Score = priority x 10 + task-type weight x 5 + 100 if overdue. "
            "Ties break by soonest scheduled time."
        )
    else:
        st.info("No pending tasks to schedule.")

    overdue = scheduler.get_overdue_tasks()
    if overdue:
        st.error(
            f"{len(overdue)} task(s) are overdue: "
            + ", ".join(t.description for t in overdue)
        )

    conflict_warnings = scheduler.get_conflict_warnings()
    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")

    st.caption(owner.get_task_summary())

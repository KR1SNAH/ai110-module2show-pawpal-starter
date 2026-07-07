import streamlit as st
from datetime import date, datetime

from pawpal_system import Owner, Pet, Task, TaskType, TaskFrequency, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

TASK_TYPE_ICONS = {
    TaskType.FEEDING: "🍽️",
    TaskType.WALK: "🐾",
    TaskType.MEDICATION: "💊",
    TaskType.APPOINTMENT: "🩺",
}


def task_type_label(task_type: TaskType) -> str:
    return f"{TASK_TYPE_ICONS.get(task_type, '')} {task_type.value}".strip()


def status_badge(task: Task) -> str:
    return "✅ Done" if task.is_completed else "🕒 Pending"


def task_flags(task: Task, conflicting_ids: set, overdue_threshold: int) -> str:
    flags = []
    if task.is_overdue(overdue_threshold):
        flags.append("⏰ Overdue")
    if task.task_id in conflicting_ids:
        flags.append("⚠️ Conflict")
    return " ".join(flags) if flags else "—"


st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+ — a pet care planning assistant. Manage your pets and tasks from the
sidebar, then use the tabs below to see today's plan, browse all tasks, or generate a
prioritized schedule.
"""
)

with st.expander("Scenario"):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What this app does"):
    st.markdown(
        """
- Represents pet care tasks (what needs to happen, how long it takes, priority)
- Represents the pet and the owner (basic info and preferences)
- Builds a plan/schedule for a day that chooses and orders tasks based on constraints
- Explains the plan (why each task was chosen and when it happens)
"""
    )

# Owner persists in session_state so pets/tasks survive Streamlit reruns
# (the whole script re-executes on every widget interaction).
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "jordan@example.com", "555-0100")
owner = st.session_state.owner

# Scheduler is bound to this owner and persists across reruns; its `tasks`
# property reads live from owner.pets, so it never needs to be refreshed
# when pets/tasks change elsewhere on the page.
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner)
scheduler = st.session_state.scheduler

# --- Owner & Pets: pinned above the tabs, always visible on the main page --
# Kept out of the tabs (rather than as a 4th tab) since it's reference info
# you often want visible while working in Today/All Tasks/Schedule, not a
# destination you navigate away to. Collapsible so it doesn't dominate the
# page once you're not actively adding a pet.
with st.expander("🐾 Owner & Pets", expanded=not owner.get_pets()):
    ocol1, ocol2, ocol3 = st.columns(3)
    with ocol1:
        owner.name = st.text_input("Owner name", value=owner.name)
    with ocol2:
        owner.email = st.text_input("Owner email", value=owner.email)
    with ocol3:
        owner.phone = st.text_input("Owner phone", value=owner.phone)

    st.markdown("#### Add a Pet")
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
            st.success(f"Added {pet.name} ({pet.get_age()} yr old {species}).")

    st.markdown("#### Your Pets")
    if owner.get_pets():
        st.table(
            [
                {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.get_age(), "Weight": p.weight}
                for p in owner.get_pets()
            ]
        )
    else:
        st.caption("No pets yet. Add one above.")

st.divider()

# --- Main tabs: Today / All Tasks / Schedule --------------------------------
manage_tasks_tab, today_tab, schedule_tab = st.tabs(["🗂️ Manage Tasks", "🏠 Today's Schedule", "📅 Make a Schedule"])

with today_tab:
    st.subheader("Today's Tasks")

    if not owner.get_pets():
        st.info("Add a pet from the sidebar to get started.")
    else:
        today = date.today()
        todays_tasks = scheduler.sort_by_time(
            [t for t in scheduler.tasks if t.scheduled_time.date() == today]
        )

        if not todays_tasks:
            st.info("No tasks scheduled for today. Add one from the All Tasks tab.")
        else:
            conflicting_ids = {t.task_id for t in scheduler.check_conflicts()}

            header = st.columns([4, 1, 1, 2, 1, 1])
            for col, label in zip(header, ["Task", "Time", "Status", "Flags", "", ""]):
                col.markdown(f"**{label}**")

            for task in todays_tasks:
                pet_label = task.pet.name if task.pet is not None else "Unassigned"
                desc_col, time_col, status_col, flags_col, complete_col, remove_col = st.columns(
                    [4, 1, 1, 2, 1, 1]
                )
                desc_col.markdown(f"{task_type_label(task.task_type)} **{task.description}**  \n*{pet_label}*")
                time_col.write(task.scheduled_time.strftime("%H:%M"))
                status_col.write(status_badge(task))
                flags_col.write(task_flags(task, conflicting_ids, scheduler.overdue_threshold))
                if not task.is_completed:
                    if complete_col.button("✅", key=f"today_complete_{task.task_id}", help="Mark complete"):
                        task.mark_complete()
                else:
                    complete_col.write("")
                if remove_col.button("🗑️", key=f"today_remove_{task.task_id}", help="Remove task"):
                    if task.pet is not None:
                        task.pet.remove_task(task.task_id)

with manage_tasks_tab:
    st.subheader("Schedule a Task")

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
                selected_type_label = st.selectbox("Task type", list(task_types_by_label.keys()))
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
                task_type = task_types_by_label[selected_type_label]
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
        st.info("Add a pet from the sidebar before scheduling tasks.")

    st.divider()
    st.subheader("All Tasks")

    all_tasks = [(p, t) for p in owner.get_pets() for t in p.get_tasks()]
    if all_tasks:
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.get_pets()])
        with fcol2:
            status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
        with fcol3:
            sort_chronologically = st.radio("Sort by time", ("None", "Ascending", "Descending"))

        filtered_tasks = scheduler.filter_tasks(
            pet_name=None if pet_filter == "All" else pet_filter,
            is_completed=None if status_filter == "All" else (status_filter == "Completed"),
        )

        # Scheduler.sort_by_time() only sorts ascending -- it takes no direction
        # argument -- so "Descending" is done here by reversing that result.
        if sort_chronologically == "Ascending":
            display_tasks = scheduler.sort_by_time(filtered_tasks)
        elif sort_chronologically == "Descending":
            display_tasks = list(reversed(scheduler.sort_by_time(filtered_tasks)))
        else:
            display_tasks = filtered_tasks

        if display_tasks:
            conflicting_ids = {t.task_id for t in scheduler.check_conflicts()}
            st.table(
                [
                    {
                        "Pet": t.pet.name if t.pet is not None else "Unassigned",
                        "Type": task_type_label(t.task_type),
                        "Description": t.description,
                        "When": t.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                        "Duration (min)": t.duration,
                        "Priority": t.priority,
                        "Repeats": t.frequency.value,
                        "Status": status_badge(t),
                        "Flags": task_flags(t, conflicting_ids, scheduler.overdue_threshold),
                    }
                    for t in display_tasks
                ]
            )

            st.markdown("#### Update, Complete, or Remove a Task")

            # task_id (a plain string) is used as the selectbox option, not the Task
            # object itself, since Streamlit's widget state is built for primitive values.
            tasks_by_id = {t.task_id: t for t in display_tasks}

            def _format_task(task_id: str) -> str:
                t = tasks_by_id[task_id]
                pet_name = t.pet.name if t.pet is not None else "Unassigned"
                when = t.scheduled_time.strftime("%Y-%m-%d %H:%M")
                return f"{task_type_label(t.task_type)} {pet_name} - {t.description} ({when})"

            selected_task_id = st.selectbox(
                "Select a task",
                list(tasks_by_id.keys()),
                format_func=_format_task,
                key="manage_task_selector",
            )
            selected_task = tasks_by_id[selected_task_id]
            st.caption(f"Status: {status_badge(selected_task)}")

            # Complete/remove act immediately as plain buttons, separate from the
            # edit form below -- so editing a task's fields is never silently
            # discarded just because "Mark complete" or "Remove" was clicked instead.
            qcol1, qcol2 = st.columns(2)
            with qcol1:
                if not selected_task.is_completed and st.button(
                    "✅ Mark complete", key=f"complete_{selected_task_id}"
                ):
                    next_task = selected_task.mark_complete()
                    if next_task is not None:
                        st.success(
                            f"Marked '{selected_task.description}' complete. Next occurrence "
                            f"scheduled for {next_task.scheduled_time.strftime('%Y-%m-%d %H:%M')}."
                        )
                    else:
                        st.success(f"Marked '{selected_task.description}' complete.")
            with qcol2:
                if st.button("🗑️ Remove", key=f"remove_{selected_task_id}"):
                    if selected_task.pet is not None:
                        selected_task.pet.remove_task(selected_task.task_id)
                    st.success(f"Removed '{selected_task.description}'.")

            with st.expander("✏️ Edit task details"):
                with st.form("edit_task_form"):
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        edited_description = st.text_input(
                            "Description",
                            value=selected_task.description,
                            key=f"edit_description_{selected_task_id}",
                        )
                    with mcol2:
                        edited_duration = st.number_input(
                            "Duration (minutes)",
                            min_value=1,
                            max_value=240,
                            value=selected_task.duration,
                            key=f"edit_duration_{selected_task_id}",
                        )
                    mcol3, mcol4, mcol5 = st.columns(3)
                    with mcol3:
                        edited_date = st.date_input(
                            "Date",
                            value=selected_task.scheduled_time.date(),
                            key=f"edit_date_{selected_task_id}",
                        )
                    with mcol4:
                        edited_clock = st.time_input(
                            "Time",
                            value=selected_task.scheduled_time.time(),
                            key=f"edit_time_{selected_task_id}",
                        )
                    with mcol5:
                        edited_priority = st.slider(
                            "Priority (1=low, 5=high)",
                            min_value=1,
                            max_value=5,
                            value=selected_task.priority,
                            key=f"edit_priority_{selected_task_id}",
                        )

                    if st.form_submit_button("Save changes"):
                        selected_task.description = edited_description
                        selected_task.duration = int(edited_duration)
                        selected_task.priority = edited_priority
                        selected_task.reschedule(datetime.combine(edited_date, edited_clock))
                        st.success(f"Updated '{selected_task.description}'.")
        else:
            st.info("No tasks match the selected filters.")
    else:
        st.info("No tasks yet. Add one above.")

with schedule_tab:
    st.subheader("Build Schedule")

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
                        "Type": task_type_label(t.task_type),
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

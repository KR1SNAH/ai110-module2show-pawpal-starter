import streamlit as st
from datetime import date, datetime

from pawpal_system import Owner, Pet, Task, TaskType, TaskFrequency

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
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )

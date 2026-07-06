from pawpal_system import *
from datetime import date 

owner = Owner("Krishna", "svkrishna6342@gmail.com", "201-726-5025", "OWN001")

sandy = Pet("Sandy", "Cat", "Indie", date(2022, 12, 28), 6.0, "Ginger Female Cat")
tommy = Pet("Tommy", "Cat", "Indie", date(2022, 12, 28), 6.0, "Bicolor Ginger and White Male Cat")

owner.add_pet(sandy)
owner.add_pet(tommy)

now = datetime.now()

# Sandy's tasks
sandy.add_task(Task(TaskType.MEDICATION, "Flea prevention drops", now + timedelta(hours=3), 5, priority=5))
sandy.add_task(Task(TaskType.FEEDING, "Morning wet food", now + timedelta(hours=1), 15, priority=2))
sandy.add_task(Task(TaskType.APPOINTMENT, "Annual vet checkup", now + timedelta(days=2), 60, priority=3))

# Tommy's tasks
tommy.add_task(Task(TaskType.FEEDING, "Morning dry food", now + timedelta(hours=1), 10, priority=2))
tommy.add_task(Task(TaskType.FEEDING, "Morning dry food", now + timedelta(hours=1), 10, priority=2))
tommy.add_task(Task(TaskType.WALK, "Leash training session", now + timedelta(hours=5), 20, priority=1))
tommy.add_task(Task(TaskType.MEDICATION, "Deworming tablet", now + timedelta(days=1), 5, priority=5))

sandy.tasks[0].mark_complete()

scheduler = Scheduler(owner)

conflicts = scheduler.check_conflicts()

for task in conflicts:
    print(task.description, task.scheduled_time)

# for task in scheduler.sort_by_time(sandy.tasks):
#     print(task.description, task.scheduled_time)

# print("Pending tasks:")
# for task in scheduler.filter_tasks(sandy.name, False):
#     print(task.description, task.scheduled_time)
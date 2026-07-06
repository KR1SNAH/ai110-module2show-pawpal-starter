# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

A pet owner should be able to,
- Add a pet and their details.
- State their time availability.
- See and make changes to today's generated plan.

The first entities that come to mind are Owner, Pet, Task

Owner - Holds the information about the pet owner, like their name, day's schedule
Pet - Types of tasks for this type of pet
Task - Time needed, priority.

I worked with Claude and it suggested adding entities like Medication, Appointment, Veterinarian, TaskLog, Notification.

It also suggested stretch entities like  Medication, Appointment, Veterinarian, TaskLog, HealthRecord, and Caretaker..

I decided to go with Owner, Pet, Task, Scheduler.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I asked Claude to check if there any relationships or potential logic bottlenecks it missed to address.

Relationships:
- It stated that it missed implementing bidirectional relationship between Pet and Owner like Pet.owner and Owner.pets.
- One relationship issue is that Scheduler.tasks if disconnected from Pet.tasks
- The last issue it stated was there was no connection between Owner and Scheduler

Bottlenecks:
- Overdue logic is duplicated across Task and Scheduler classes
- check_conflicts() scope is undefined
- No ID generation strategy for class ids
- Recurring tasks have no regeneration logic

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers four things, 
1. Explicit Priority, if the owner says it is high priority, it gets the largest weight.
2. Task type based on their logical importance
3. Overdue status, high weightage when a task is overdue
4. Time, it is used in conflict detection and sorting


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Conflict detection is passive as in there is no way to see if tasks are overlapping just if they start at the same time. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used Claude across the full lifecycle of the project like Design brainstorming, implementation, concept explanation, verification, and testing.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

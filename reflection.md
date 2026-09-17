# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three Core Actions 
1. Add and manage a pet profile — The owner can register a pet (name, species, breed, age, weight, dietary/medical notes) so the system knows who it's caring for and can tailor task recommendations accordingly.
2. Schedule and track recurring care tasks — The owner can create tasks (feedings, walks, medications, grooming, enrichment) with a frequency, duration, and priority, so the system knows what needs to happen and how often.
3. Generate and view today's prioritized plan — The owner can ask the system to produce a daily schedule that fits available time, respects task priority/urgency (e.g., medication before optional enrichment), and explains why it ordered things that way.

Classes
- Pet
    - Attributes: pet_id, name, species, breed, age, weight, dietary_notes, medical_notes
    - Methods: add_task(task), get_tasks(), update_profile(**kwargs)
- Task
    - Attributes: task_id, name, category (walk/feed/med/groom/enrichment), duration_minutes, priority (e.g. enum: LOW/MEDIUM/HIGH/CRITICAL), frequency (daily, every N hours, specific days), preferred_time_window, is_completed
    - Methods: is_due(current_time), mark_complete(), get_priority_score()
- Owner
    - Attributes: owner_id, name, pets (list of Pet), preferences (e.g. preferred wake time, available time blocks, "no walks after 9pm")
    - Methods: add_pet(pet), set_preferences(**kwargs), get_all_tasks_today()
- Scheduler
    - Attributes: available_time_minutes, tasks (all due tasks across pets)
    - Methods: generate_plan(tasks, available_time), _sort_by_priority(), _explain_decision(task)
- DailyPlan
    - Attributes: date, owner, scheduled_tasks (ordered list), deferred_tasks, explanations
    - Methods: to_string() / display(), get_summary()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

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

# PawPal+ Project Reflection

## 1. System Design
**Three Core Actions**
1. Add and manage a pet profile — The owner can register a pet (name, species, breed, age, weight, dietary/medical notes) so the system knows who it's caring for and can tailor task recommendations accordingly.
2. Schedule and track recurring care tasks — The owner can create tasks (feedings, walks, medications, grooming, enrichment) with a frequency, duration, and priority, so the system knows what needs to happen and how often.
3. Generate and view today's prioritized plan — The owner can ask the system to produce a daily schedule that fits available time, respects task priority/urgency (e.g., medication before optional enrichment), and explains why it ordered things that way.

**Classes**
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


**a. Initial design**

- Briefly describe your initial UML design.
    My final UML design is built around exactly four core classes: `Task`, `Pet`, `Owner`, and `Scheduler`. `Owner` owns a list of `Pet`s through composition, and `Pet` owns a list of `Task`s the same way. `Scheduler` is connected to `Owner` and `Task` through dependency arrows rather than ownership, since it reads and processes their data — pulling due tasks and sorting them — without holding that data itself.

- What classes did you include, and what responsibilities did you assign to each?
    - Owner — holds an owner's id, name, list of Pets, and available time budget for the day; responsible for adding pets and collecting all tasks across every pet it manages.
    - Pet — holds a pet's basic profile info (species, name, id) and its list of Tasks; responsible for adding and retrieving tasks.
    - Task — represents a single recurring care item (walk, feeding, med, groom, enrichment); responsible for knowing its own schedule/frequency and completion status, and determining whether it's currently due.
    - Scheduler — the "brain" of the system; retrieves due tasks from an Owner's pets, sorts them by urgency, and decides what fits within the available time, returning a plan.

**b. Design changes**

- Did your design change during implementation? Yes
- If yes, describe at least one change and why you made it.
    - My first draft added two extra classes beyond the original four: `ScheduledTask` (to wrap a `Task` with a specific start/end time and its own completion flag) and `Recurrence` (to break frequency into `interval_hours` and `specific_days`). I added these after realizing that tracking completion directly on a recurring `Task` was technically wrong. A "daily walk" shouldn't itself be permanently marked "completed," since that status needs to reset each day. After review, I removed both extra classes and instead added a single `is_completed`/timestamp field directly on `Task`, keeping completion tracking self-contained.
    - My second draft also introduced `Preferences` (a class for wake/sleep time and available minutes) and `DailyPlan` (a class to hold scheduled tasks, deferred tasks, and explanations) as separate objects owned by `Owner` and produced by `Scheduler`. After confirming the assignment scope only called for four classes total, I put both into the existing structure instead of keeping them separate. `available_time_minutes` moved directly onto `Owner` as an attribute, and `Scheduler.generate_plan()` now returns a simple dictionary (with `scheduled`, `deferred`, and `explanations` keys) instead of a dedicated `DailyPlan` object. This kept the design at exactly four classes as required, at the cost of `Scheduler`'s return value being a plain dict rather than a typed object. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - There are three main things my scheduler cares about. First is the time budget. `_fits()` checks if a task's `duration_minutes` fits into whatever `available_time_minutes` is left, and once that runs out, everything else gets pushed to the deferred list instead of scheduled. Second is urgency. I don't have a separate priority field on `Task`, so instead `_sort_by_priority()` just ranks tasks by how overdue they are. Anything never completed goes first, then whichever has been waiting the longest. Third is conflicts. `find_conflicts()` checks if any two due tasks overlap in time, like a task running past its duration into when another one is supposed to start, and it flags that as a warning without actually changing the schedule.

- How did you decide which constraints mattered most?
    - I started with Time and Urgency, since without them the app can't really do its one job, which is telling you what to do today and in what order. Conflict detection came later, once I realized that even if two tasks both individually fit the time budget, they could still be scheduled at the exact same time, which obviously doesn't work in real life. I kept conflict detection as just a warning instead of having it auto-fix the schedule, because deciding which task "wins" a conflict felt like something the owner should decide, not something I wanted the scheduler quietly deciding for them.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - `find_conflicts()` only counts two tasks as conflicting if one's duration actually bleeds into the next one's start time, so it uses `>` instead of `>=`. That means back-to-back tasks, where one ends right as the next starts, aren't flagged as a conflict, which is what I want. But it also means a task with `duration_minutes=0` can technically never conflict with anything, even something at the exact same timestamp, since a zero-length task "ends" the same instant it starts.
- Why is that tradeoff reasonable for this scenario?
    - Allowing back-to-back tasks matters way more than catching a zero-duration edge case. If a walk ends at 8:00 and breakfast starts at 8:00, that's just a normal morning, not a conflict, and I didn't want the scheduler flagging that as a problem. Every real task in this app takes some actual time anyway (walks, feedings, meds all have a duration), so the zero-duration case basically never comes up in practice. I decided it wasn't worth adding special-case logic to catch something that isn't really a realistic scenario for this app.

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

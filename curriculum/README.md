# Learn to Program with BARE — A K-12 Curriculum

This is a complete, three-tier curriculum for teaching programming with the
**BARE IDE**, spanning roughly ages 8 to 18 (upper elementary through the
end of secondary school). It exists because BARE itself was designed for
exactly this purpose — a language small enough to fit on one screen, with
no punctuation-heavy syntax to trip up a first-timer, but with real
functions, real scope rules, and real data structures underneath, so
nothing a student learns here has to be unlearned later.

**Start here if you're a teacher**: read [teachers-guide.md](teachers-guide.md)
first, in full, before your first class. It covers setup, classroom
management, BARE-specific student misconceptions, grading philosophy, and
how the three tiers fit together. Everything in this README is just a map;
the guide is where the actual "how to teach this" lives.

---

## The three tiers

Each tier is a full semester of material (roughly 15-18 class sessions),
designed to be taught in order but also usable on its own — a school
running only one semester of intro CS can teach Tier 1 or Tier 2 alone and
get a complete, self-contained experience.

| Tier | Age / grade | Folder | Focus |
|---|---|---|---|
| **1 — BARE Beginnings** | ~8-10 (grades 3-5) | [tier1-beginnings/](tier1-beginnings/) | Sequencing, variables, `print`/`input`, `if`/`else`, `while`, first taste of randomness |
| **2 — BARE Builders** | ~11-13 (grades 6-8) | [tier2-builders/](tier2-builders/) | `sub`s and scope, lists, data conversion, debugging tools, the personal library |
| **3 — BARE Projects** | ~14-18 (grades 9-12) | [tier3-projects/](tier3-projects/) | Algorithmic thinking, recursion, program design, refactoring, a capstone project, and a bridge to "real" languages |

Each tier folder has three documents:

- **`lessons.md`** — the full set of lesson plans: objectives, timing,
  talking points, code to demonstrate, and differentiation notes. This is
  the teacher-facing document.
- **`worksheets.md`** — student-facing handouts, one section per lesson,
  meant to be printed or projected. No teacher commentary — just
  instructions and practice problems for students.
- **`assessment.md`** — short checkpoint quizzes at natural unit
  boundaries, plus a rubric for each tier's capstone project.

## How this relates to the rest of the BARE project

- [docs/user-guide.md](../docs/user-guide.md) and
  [docs/language-spec.md](../docs/language-spec.md) are the reference
  manuals for the IDE and the language itself — this curriculum teaches
  *from* them but doesn't replace them. Point older/faster students at the
  spec directly; it's written to be readable without a teacher in the room.
- [examples/](../examples/) has ready-to-run `.bare` programs
  (`fizzbuzz.bare`, `guessing_game.bare`, `rock_paper_scissors.bare`,
  `bubble_sort.bare`, and more) that several Tier 2 and Tier 3 lessons
  reference directly instead of reprinting the same code.
- The IDE's **personal library** feature (My Library panel, `Edit → Save
  Selection to Library`) is a teaching tool in its own right — Tier 2
  introduces it, and Tier 3 leans on it as the vehicle for teaching code
  reuse and refactoring. See `docs/user-guide.md §9`.

## A note on age ranges

Treat the age bands as a starting point, not a hard rule — a bright
9-year-old who's raced through Tier 1 should move to Tier 2 the same way a
strong reader gets moved up a reading level, and a 15-year-old brand new to
programming should start at Tier 1 rather than being dropped into Tier 3
underprepared. The teacher's guide has a short placement checklist for
exactly this.

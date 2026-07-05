# BARE Curriculum — Teacher's Guide

Read this in full before your first class. It's the "how" that sits
underneath the lesson plans in `tier1-beginnings/`, `tier2-builders/`, and
`tier3-projects/`.

---

## 1. Why BARE, and why this will work

BARE — **B**arely **A**dequate **R**untime **E**nvironment — was built as a
teaching language first. That shows up in ways that matter directly for
your classroom:

- **No punctuation tax.** No semicolons, no curly braces, no type
  annotations, no `def`/`function` boilerplate. A first program is
  `print "Hello, world!"` — nothing between a student's idea and the
  computer executing it except the words themselves. For an 8-year-old
  still building keyboard fluency, this is the difference between "I
  wrote a program" and "I fought a syntax error for ten minutes."
- **11 reserved words, total.** `print input if else end while sub return
  and or not`. You can put the entire keyword list on one small poster and
  a student can hold all of it in their head — there's no "there are also
  these 40 other keywords you'll meet later" looming in the background.
- **Real functions, real scope, real data structures.** Underneath the
  simplicity, `sub`s take parameters and return values the way functions
  do in every language a student will meet later, and BARE's scope rule
  (a `sub` truly cannot see outside variables — no exceptions, no
  `global` keyword to escape it) is *stricter* than Python's, not looser.
  Nothing taught here has to be quietly corrected in the next course.
- **It says so, out loud.** BARE's own language spec is explicit that
  missing features (no `elseif`, no exception handling, no classes) are
  deliberate pedagogy, not gaps: *"Where BARE's `if`/`else` nesting gets
  ugly in place of `elseif`, that ugliness is a teaching moment — here's
  why other languages added that feature. Productive struggle is the
  point."* Say this to students directly when they hit friction. It
  reframes "this language is missing something" as "you're about to
  understand why a feature exists," which is a much better place for a
  student to be standing.
- **The IDE is the whole environment.** There's no command line, no
  installing packages, no "why won't it compile" caused by environment
  drift between machines. Open the IDE, write code, click Run. This
  matters enormously for a shared classroom set of laptops.

## 2. Getting set up

- Install per the main [README](../README.md) — either the standalone
  build (`build_release.sh` output) for lab machines with no Python setup
  overhead, or `./setup.sh && ./run.sh` from source if you're comfortable
  maintaining that yourselves.
- **Every student gets their own machine profile**, not a shared login,
  if at all possible. Two IDE features are tied to the OS user account:
  - **Preferences** (theme, font size, tab width) are saved per profile —
    letting students set their own theme is a small but real point of
    ownership, especially for younger students.
  - The **personal library** (`~/.config/bare_ide/user_library.bare` on
    Linux/macOS) is per profile. This is introduced in Tier 2 and becomes
    central in Tier 3 — a shared login means students overwrite each
    other's saved functions.
  - If your lab uses shared/wiped machines, see the FAQ at the end of this
    guide for a workaround (save each student's library file externally
    between sessions).
- **There is no autosave to a server.** Students save `.bare` files like
  any other file. Set a convention early (e.g., a class folder structure
  like `Documents/BARE/<student-name>/`) and stick to it — "I lost my
  file" is a much smaller problem in week 1 than week 12.

## 3. How the curriculum is organized

Three tiers, each a semester (~15-18 sessions), each ending in a capstone
project:

1. **Tier 1 — BARE Beginnings** (~8-10): sequencing, variables, `if`/
   `else`, `while`, and just enough randomness to make a game. No `sub`s —
   that's a deliberate scope cut, not an oversight (see §7).
2. **Tier 2 — BARE Builders** (~11-13): `sub`s, scope, lists, the full
   builtin set, real debugging tool use, and the personal library.
3. **Tier 3 — BARE Projects** (~14-18): algorithmic thinking, recursion,
   program design and refactoring, a multi-day capstone, and an explicit
   bridge to what comes after BARE.

### Placement, not age

Use this checklist rather than birthdate to place a student:

- **Never programmed before, any age 8+**: start at Tier 1. Older
  beginners move through it faster (expect to compress 16 lessons into
  10-12 sessions with a 15-18 year old), but don't skip it — the concepts
  are genuinely foundational, not "baby's first program" filler.
- **Comfortable with variables/conditionals/loops in any language or in
  Scratch-style block programming**: start at Tier 2, lesson 1, which
  opens with a fast recap specifically for this case.
- **Already writes functions and understands parameters in some
  language**: can start at Tier 2 mid-way (around the lists unit) or at
  Tier 3 lesson 1, using Tier 3's opening diagnostic to confirm.
- If you're running a single mixed-age classroom, it's entirely
  reasonable to have three tiers running concurrently with students at
  different lesson numbers — every lesson plan lists roughly what a
  student needs to have finished going into it, so self-pacing works.

## 4. Teaching philosophy for this material

- **Productive struggle is a feature, not a failure of the lesson.** When
  a student's nested `if`/`else` gets three levels deep and ugly because
  BARE has no `elseif`, resist the urge to "fix" it for them by jumping
  ahead to a language that has one. Ask: *"What would make this nicer?
  What would you call that feature if you invented it?"* Most students
  invent `elseif` themselves within a minute or two, at which point you've
  taught them *why* it exists, not just that it does.
- **Read the error message out loud, together, every single time — for
  the whole first tier.** BARE's errors are one line, plain English, and
  point at a specific line number (`Error on line 7: cannot add string
  and boolean`). The single highest-leverage habit you can build in week
  one is: red squiggle or highlighted line appears → read the message →
  look at that line → form a hypothesis → only then start changing code.
  Students who skip straight to randomly editing code build a much worse
  habit that's hard to undo later.
- **Pair programming works well here specifically because the language is
  small.** One student can hold the entire keyword list in their head and
  talk their partner through what a line does — that's much harder in a
  language with a large surface area. Use "driver/navigator" pairs
  liberally, swap roles every 10-15 minutes.
- **"Ask three, then me."** Before a student raises a hand: (1) read the
  error message, (2) check the relevant section of `docs/language-spec.md`
  in the IDE's Language Spec tab, (3) ask a neighbor. This is especially
  effective in Tiers 2-3 where the spec is written to be student-readable
  on its own.
- **Show, don't just tell, with the debugger.** Tier 2 onward has a
  dedicated debugging lesson, but use breakpoints and the Variable Watch
  panel yourself, projected, from day one whenever a student asks "wait,
  what does this line actually do?" Watching a variable's value change
  line-by-line answers more "why doesn't my code work" questions than any
  explanation.

## 5. BARE-specific misconceptions and gotchas (know these before students find them)

These are real, verified behaviors of the language — not hypothetical —
and each one reliably surprises new students at a specific point in the
curriculum. Knowing them in advance turns a 15-minute confused detour into
a 30-second "oh, that's just how it works here."

| What trips students up | What's actually happening | Where it comes up |
|---|---|---|
| `0` and `""` (empty string) are **truthy**, not falsy | Only `false` and `null` are falsy in BARE (spec §5.3) — a deliberate departure from C-family languages, chosen specifically to avoid a beginner surprise where `if score` silently does the wrong thing when `score` is `0`. Ironically, this itself becomes the surprise for anyone who's dabbled in JavaScript or Python. | Tier 1, first `if` lesson |
| Single quotes (`'like this'`) don't work | BARE strings are double-quoted only. A student who's seen Python will try `'hello'` and get a syntax error. | Tier 1, first strings lesson |
| No `elseif`/`elif` | Nested `if`/`else` only. This is intentional (§4 above) — don't "fix" it by teaching a workaround pattern before students feel the friction themselves. | Tier 1-2, decision-making lessons |
| No `x += 1` | Only `x = x + 1`. Students coming from Scratch's "change x by 1" block or any C-family language reach for this reflexively. | Tier 1-2, loop counters |
| A `sub` cannot see outside variables — **at all**, no `global` keyword exists to escape it | This is BARE's strictest rule, and it's stricter than most students' next language will be. The failure mode is a runtime error (`'total' is not defined`) that looks like a bug but is the rule working correctly. | Tier 2, first `sub` lesson — give it its own full lesson, don't rush it |
| Division always produces a decimal-capable result | `10 / 4` is `2.5`, not `2` — there's only one numeric type in BARE (spec §2), no separate integer division. `10 / 2` prints as `5`, not `5.0`, because whole numbers display without a decimal point — but the underlying value is still the same float type either way. | Tier 1, math lesson |
| List and string indexes start at **0**, and negative indexes are a runtime error | `x[0]` is the first element; there's no `x[-1]` for "last element" the way Python has. | Tier 2, lists unit |
| `input()` always returns a **string** | Forgetting to run it through `num()` before doing arithmetic is the single most common Tier 1-2 bug — and `+` specifically makes it *worse* than a crash: `age + 1` where `age` came straight from `input()` as `"5"` doesn't error at all, it silently string-concatenates into `"51"`, because BARE's `+` auto-converts a number to text when the other side is a string. `-`, `*`, and comparisons *do* correctly error on a string, so the bug's visibility depends entirely on which operator a student happens to use first. Teach `input()` + `num()` as a fixed pair from day one, specifically because you can't count on `+` to catch the mistake for you. | Tier 1, `input()` lesson |
| No `try`/`catch` — an error stops the program, full stop | This is a design choice ("the lesson is prevention, not handling" — spec §13), not a missing feature to work around. Frame runtime errors as the program teaching you something, not as a crash to be suppressed. | All tiers |

## 6. Debugging as a taught skill

Don't treat the IDE's debugger (breakpoints, Step, Continue, Variable
Watch) as a "bonus feature" — it's the single best tool you have for
making a program's *execution* visible, which is the actual hard part of
early programming (most students can read code line by line; predicting
what it *does* is the skill). Tier 2 has a dedicated lesson for this, but
introduce breakpoints informally as early as Tier 1's `while` loop lessons
by projecting your own screen and stepping through a loop that isn't
behaving as a student expects.

## 7. Assessment and grading philosophy

- Each tier's `assessment.md` has short checkpoint quizzes (5-8 questions,
  10 minutes) at natural unit boundaries — use these formatively, not as
  high-stakes grades. The goal is surfacing which of the misconceptions in
  §5 are still live for a given student, not ranking students.
- Capstone projects are graded with the rubric in each tier's
  `assessment.md`, which weights **working correctly**, **code that's
  organized into sensible pieces** (subs/lists used where they help), and
  **the student's own explanation of their code** roughly equally — a
  program that works but that the student can't explain is a bigger red
  flag than one with a small bug the student can accurately describe.
- Don't grade on typing speed or on how quickly a student writes code
  syntax-error-free. That's fine motor skill and pattern memorization, not
  computational thinking, and it systematically disadvantages younger
  students and students with less keyboard experience.

## 8. Differentiation

- **Fast finishers**: every lesson plan has an "extension" note. The
  default extension across all three tiers is the same instinct: *"make
  it handle a case it doesn't handle yet"* — what if the input is
  negative, what if the list is empty, what if the user types letters
  instead of a number. This teaches robustness thinking without needing
  new syntax.
- **Struggling students**: the default support move is *reduce the
  program, not the concept* — strip a multi-part program down to the
  single line that's confusing, get that one line working and understood
  in isolation, then rebuild outward. Almost never simplify by skipping a
  concept entirely; BARE's small syntax surface means there's usually a
  three-line version of any confusing idea.
- **English language learners**: BARE's error messages and keywords are
  plain English with no jargon-heavy technical vocabulary beyond the
  eleven keywords themselves — this is one of the gentler languages
  available for this. Consider printing the keyword-and-symbol reference
  from `docs/language-spec.md §11` as a bilingual glossary handout.

## 9. Suggested pacing (one semester, one tier, 2 sessions/week)

Roughly 8-9 weeks of content at 2 sessions/week covers a tier's 15-18
lessons with room for a review day mid-semester and a two-session capstone
at the end. Running only 1 session/week roughly doubles that to a full
16-18 week semester — the lessons don't need to be compressed, just spread
out; do budget a "what did we do last week" recap at the start of each
session if you're on a weekly cadence, since a week's gap is a long time
for a student's mental model to hold.

## 10. FAQ / troubleshooting

- **Shared/wiped lab machines and the personal library**: have students
  export their library at the end of each session (File → Open My
  Library, then Save As to their personal network drive or USB drive) and
  import it back at the start of the next (open their saved copy, Save As
  back to the default location `~/.config/bare_ide/user_library.bare`
  shown in the IDE's title bar once opened). It's a manual step, but it's
  two clicks and solves the whole problem.
- **A student's program hangs (infinite loop)**: this is expected and
  fine — that's exactly what the **Stop** button is for, and the IDE
  stays fully responsive the entire time because the program runs on a
  background thread. Use it as a teaching moment about loop conditions
  rather than an emergency.
- **"My program printed nothing and no error either"**: almost always
  means every top-level statement is inside a `sub` that never got called,
  or a `while` condition that was false immediately. Ask the student to
  add a `print "got here"` as the very first line and see if even that
  shows up — this isolates "did my program run at all" from "did my logic
  work," which is a generally useful debugging split to teach explicitly.
- **A student wants to skip ahead to a "real" language**: encourage it —
  see Tier 3's final lesson, which is explicitly designed as a bridge and
  names what changes (error handling, more data types, more loop kinds,
  classes) and what doesn't (variables, conditionals, loops, functions,
  scope — the actual computational thinking, which transfers completely).

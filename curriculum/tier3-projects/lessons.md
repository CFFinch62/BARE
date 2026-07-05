# Tier 3 — BARE Projects (ages ~14-18)

Eighteen lessons, ~50 minute periods. This tier assumes some students are
arriving from Tier 2 and some are brand new to programming entirely —
Lessons 1-6 are a fast, consolidated pass through everything earlier tiers
built, sized for a class that can move quickly, followed by genuinely new
material: algorithmic thinking without built-in helpers, recursion,
real refactoring using the personal library, program design as its own
skill, a substantial capstone, and an explicit closing lesson on what
changes (and what doesn't) when students move on to another language.

---

## Lesson 1 — Kickoff and Diagnostic

**Objective**: Establish where each student is starting from, and set
expectations for the course.

**Teach**: Frame the semester: this course uses a small, deliberately
minimal language so the *thinking* — not the syntax — is the thing being
taught, and that thinking transfers completely to whatever language
students use next (Python, Java, JavaScript, C++, anything). Give the
15-minute diagnostic: a short program to read and predict the output of,
covering variables, `if`/`else`, `while`, and a `sub` with a return value.
Use results to identify who needs a Tier 1/2 refresher (assign
`tier2-builders` lessons as homework/catch-up reading, not a full redo).

**Guided practice**: Review the diagnostic answers as a class, focusing
discussion time on whichever concept the room got wrong most often.

**Independent practice**: None — diagnostic is the activity.

**Wrap-up**: Have every student write one sentence: "the thing about
programming I already feel confident about is ___, and the thing I want
to get better at is ___."

**Differentiation**: Students testing out of most of the diagnostic can
be pointed straight at Lesson 7 (algorithmic thinking) with Lessons 2-6 as
a reading-only reference.

---

## Lesson 2 — Syntax Bootcamp

**Objective**: Rapid, consolidated review of variables, `print`/`input`,
math, and string concatenation.

**Teach**: Move fast — this is review for most of the room. Cover in one
session what Tier 1 spent 7 lessons on: variables, all four math
operators, `input()`/`num()`, and string+number joining with `+`. Use
`docs/language-spec.md §1-4` as the reading students can self-check
against.

**Guided practice**: A rapid-fire "type and predict" sequence covering
each concept once.

**Independent practice**: A short diagnostic-style worksheet (Worksheet
2) — students who breeze through it have confirmed they're ready for the
pace of the rest of the course.

**Wrap-up**: Exit ticket — one line of code using a variable, a math
operator, and string concatenation all together.

**Differentiation**: Students still shaky here should get Tier 1's full
lesson set as structured homework over the next week, running parallel to
the rest of the class rather than blocking it.

---

## Lesson 3 — Conditionals and Truthiness, Properly Understood

**Objective**: Confidently use `if`/`else`, all comparison operators, and
`and`/`or`/`not`; understand BARE's truthiness rule as a *design choice*,
not a quirk to memorize.

**Teach**: Review syntax quickly, then spend the real time on the
*design* conversation: BARE treats only `false` and `null` as falsy —
`0` and `""` are both truthy. Ask: *"In a language where `0` were falsy,
what bug could that cause?"* (A score of exactly 0 silently skipping a
branch meant to handle it, for instance.) This is the kind of design
tradeoff conversation this tier should have regularly — not just "how do
I write this" but "why does the language work this way, and what would
change if it didn't."

**Guided practice**: A set of "what will this print, and why" problems
specifically targeting truthiness edge cases (`if 0`, `if ""`, `if not
false`).

**Independent practice**: Worksheet 3.

**Wrap-up**: Exit ticket — name one language feature (from any language
students have heard of) that is a genuine design tradeoff, not just "the
right way to do it." (Accept reasonable answers — the point is the habit
of thinking this way.)

**Differentiation**: *Extension* — research (or predict) how Python or
JavaScript's truthiness rules differ from BARE's, and what bug each choice
prevents or risks. *Support* — focus purely on correctly predicting
BARE's own behavior before comparing across languages.

---

## Lesson 4 — Loop Patterns

**Objective**: Recognize and write the four common `while` loop patterns:
counting, accumulating, validating, and searching-with-early-return.

**Teach**: Name and contrast all four explicitly, each with a short
example:
- **Counting**: `while i <= 10 ... i = i + 1`
- **Accumulating**: a running `total` built up across iterations
- **Validating**: `while` the input remains bad, keep asking
- **Sentinel**: `while` some stop signal hasn't been seen yet
Point out these are the same four ideas from Tiers 1-2, but naming the
*pattern* (not just the syntax) is what lets students recognize which one
a new problem calls for.

**Guided practice**: Give 4 short word problems; as a class, identify
which pattern each calls for before writing any code.

**Independent practice**: Worksheet 4 — write one loop of each pattern.

**Wrap-up**: Exit ticket — which pattern would you use to find the first
negative number in a list, and why?

**Differentiation**: *Extension* — a problem that needs two patterns
combined (e.g., validate input, then accumulate). *Support* — match
problems to patterns as a card-sort activity before writing any code.

---

## Lesson 5 — `sub`s as Abstraction

**Objective**: Reinforce `sub`s, parameters, `return`, and strict scope,
framed explicitly as *abstraction* — hiding detail behind a name.

**Teach**: Fast review of syntax, then the framing conversation: a `sub`
lets you *use* a piece of logic without re-reading or re-understanding how
it works every time — exactly like using `len()` without knowing how
BARE's Python implementation counts characters internally. Ask: *"What's
the interface of a `sub` — the part someone calling it needs to know —
versus its implementation, the part they don't?"* (Answer: the interface
is its name, parameters, and what it returns; the implementation is
everything inside `sub ... end`, which the caller shouldn't need to think
about at all.) Revisit the strict no-outside-access scope rule as *what
makes this abstraction trustworthy* — a `sub` you didn't write can't
secretly depend on or corrupt some variable in your program you don't
know about.

**Guided practice**: Given a `sub`'s name, parameters, and a one-line
description of what it returns, students write *calls* to it without
ever seeing its implementation — driving home the interface/implementation
split concretely.

**Independent practice**: Worksheet 5.

**Wrap-up**: Exit ticket — why does BARE's strict scope rule make a
`sub` easier to trust, not just harder to write?

**Differentiation**: *Extension* — write two different implementations of
the same `sub` signature (e.g., two different ways to compute a max of a
list) and confirm both are interchangeable from the caller's side.
*Support* — the "write calls without seeing the implementation" activity
alone is a complete goal.

---

## Lesson 6 — Lists as Data

**Objective**: Consolidate list creation, indexing, `append`/`len`, and
looping, framed as "modeling real data," not just syntax practice.

**Teach**: Fast review, then a modeling conversation: what real-world
things are naturally a list (a class roster, a shopping cart, a
leaderboard)? For each, what would you need to do with it (add, find,
total, sort — sorting is next lesson's hook)? Introduce a list of lists
briefly (`[[1, 2], [3, 4]]`, from the spec) as a preview for anyone who
wants to model a grid or table later, without requiring it yet.

**Guided practice**: As a class, model a shopping cart: a list of item
names and a matching list of prices, with a `sub` that computes the
total.

**Independent practice**: Worksheet 6.

**Wrap-up**: Exit ticket — name a real-world collection of things and
what you'd want to compute from it as a list in a program.

**Differentiation**: *Extension* — model the same data with two parallel
lists (names + prices) vs. discuss (without necessarily coding) how a list
of lists might combine them into one structure instead. *Support* — the
shopping cart example alone is a complete goal.

---

## Lesson 7 — Algorithmic Thinking: Search, Min, Max, Average

**Objective**: Write linear search, and min/max/average computations,
from scratch, understanding these as *algorithms*, not builtin magic.

**Teach**: Point out that BARE has no built-in "find," "max," or
"sort" — unlike `len()` or `append()`, these are things students will
write themselves, which is exactly the point of this lesson: understanding
what those operations actually *do*, step by step. Walk through
`examples/linear_search.bare`:
```
sub find_index(haystack, target)
    i = 0
    while i < len(haystack)
        if haystack[i] == target
            return i
        end
        i = i + 1
    end
    return -1
end
```
Point out the **early return** — the `sub` exits the moment it finds a
match, rather than finishing the loop pointlessly. Ask students to derive
a `max` sub themselves (track a "best so far" variable, updating it each
time something bigger is seen) before showing a model solution.

**Guided practice**: As a class, write `find_max(numbers)` together,
tracing through a specific list by hand first.

**Independent practice**: Worksheet 7.

**Wrap-up**: Exit ticket — why does `find_index` return `-1` instead of,
say, `0`, when nothing is found?

**Differentiation**: *Extension* — write `find_min` and a `sub` that
returns *both* the min and max (hint: what would you have to return — can
a `sub` only return one value? Yes; discuss what workaround this forces,
e.g. printing both from inside, or returning a list `[min, max]`).
*Support* — trace the given `find_index` example thoroughly by hand
before writing `find_max` independently.

---

## Lesson 8 — Algorithmic Thinking: Sorting

**Objective**: Understand and trace bubble sort; appreciate why sorting
is a harder problem than searching.

**Teach**: Walk through `examples/bubble_sort.bare` slowly:
```
numbers = [5, 2, 9, 1, 5, 6]

i = 0
while i < len(numbers)
    j = 0
    while j < len(numbers) - i - 1
        if numbers[j] > numbers[j + 1]
            temp = numbers[j]
            numbers[j] = numbers[j + 1]
            numbers[j + 1] = temp
        end
        j = j + 1
    end
    i = i + 1
end
```
This is the first **nested loop** many students will trace carefully —
budget real time for it. Trace the first full pass of the outer loop by
hand as a class on the board, watching the largest unsorted value "bubble"
to its correct position. Discuss the swap pattern (`temp` variable) as a
generally useful idiom, not specific to sorting.

**Guided practice**: Trace the second pass as a class, predicting how many
comparisons it will need compared to the first (one fewer — connect to
the `- i - 1` in the inner loop's bound).

**Independent practice**: Worksheet 8.

**Wrap-up**: Exit ticket — why does the inner loop's upper bound shrink
by one each time through the outer loop?

**Differentiation**: *Extension* — modify the example to sort in
descending order, and/or count and print the number of swaps performed.
*Support* — trace a shorter list (4 elements) fully by hand, one pass at a
time, before attempting modifications.

---

## Lesson 9 — Recursion, Properly

**Objective**: Write and trace recursive `sub`s confidently; understand
the call stack conceptually; recognize when recursion helps and when it
doesn't.

**Teach**: Revisit (or introduce, for new students) `examples/factorial.bare`,
then look at `examples/fibonacci.bare` — and point out explicitly that
this example is **iterative**, not recursive, despite Fibonacci being a
classic recursion example in most textbooks:
```
count = 15
a = 0
b = 1

i = 0
while i < count
    print a
    next = a + b
    a = b
    b = next
    i = i + 1
end
```
Ask: *"Why might someone choose this iterative version over a recursive
one?"* (It's more efficient — no repeated re-computation of the same
values, and no risk of an extremely deep call chain.) Then have students
write the recursive version themselves as the lesson's real exercise,
and compare.

**Guided practice**: As a class, trace `factorial(4)`'s full call stack,
then trace the iterative Fibonacci loop's variables (`a`, `b`, `next`)
through several iterations side by side, discussing which is easier to
trace by hand and why.

**Independent practice**: Worksheet 9 — write a recursive Fibonacci `sub`
and compare its behavior (not performance, which is hard to observe
directly, but *structure*) to the iterative version.

**Wrap-up**: Exit ticket — every recursive `sub` needs two things to be
correct. What are they? (A base case, and a step that moves *toward* that
base case with each call.)

**Differentiation**: *Extension* — discuss (or, for strong students,
verify by adding a counter) why recursive Fibonacci re-computes the same
values many times over for larger inputs, while the iterative version
doesn't. *Support* — tracing the given examples thoroughly is a complete
goal; writing new recursive code is the stretch target.

---

## Lesson 10 — Building Your Library, For Real

**Objective**: Treat the personal library as an ongoing refactoring
practice, not a one-time demo.

**Teach**: For students continuing from Tier 2, this is a refresher, into
real practice: Save `find_index`, `find_max`, and a sorting `sub` (wrap
Lesson 8's bubble sort logic in a `sub sort(numbers)` first, since the
example as written works directly on a list rather than as a callable
`sub` — worth doing together as an exercise in itself: *"how would we turn
this into something we could call and reuse?"*) to the library. Introduce
**File → Open My Library** for direct editing: rename a `sub`, delete an
old one that's been superseded, add a comment explaining what each one
does. Frame this explicitly as **refactoring** — improving existing code's
organization without changing what it does — a real professional practice,
not busywork.

**Guided practice**: As a class, open the library file directly and
reorganize it: group related `sub`s together with comment headers
(`# --- searching ---`, `# --- sorting ---`).

**Independent practice**: Worksheet 10 — save at least 3 general-purpose
`sub`s from this tier's lessons so far, then write a short new program
that uses two of them together.

**Wrap-up**: Exit ticket — what's the difference between adding a new
feature to a program and refactoring it?

**Differentiation**: *Extension* — write a `sub` general enough to handle
a case it wasn't originally written for (e.g., a `sort` that also works
correctly on an already-sorted or empty list — discuss what "empty list"
even does to the loop bounds). *Support* — saving and organizing 3
existing `sub`s is a complete goal.

---

## Lesson 11 — Debugging Like a Professional

**Objective**: Develop a systematic debugging process: reproduce, isolate,
hypothesize, test, fix.

**Teach**: Name the process explicitly, and practice it on a deliberately
tricky bug (an off-by-one in a search or sort `sub`, or a scope mistake).
Emphasize **rubber-duck debugging** — explaining your code line by line to
someone (or something) else, out loud, often reveals the bug before you
finish explaining. Pair this with the IDE's tools: a breakpoint isolates
*where*; Variable Watch confirms or refutes a hypothesis about *what* the
state actually is at that point, rather than what you assumed it was.

**Guided practice**: In pairs, one student narrates their hypothesis
about a bug out loud while the other only clicks Step/Continue on request
— separating "thinking" from "doing" deliberately.

**Independent practice**: Worksheet 11 — a multi-`sub` broken program,
with a written debugging log required (what did you try, what did you
learn, in order) alongside the fix.

**Wrap-up**: A few students share one line from their debugging log that
represents the moment they figured it out.

**Differentiation**: *Extension* — a program with two interacting bugs,
where fixing one reveals the other. *Support* — the paired
narrate/click roles above, with the teacher modeling the narration style
first.

---

## Lesson 12 — Program Design: Before You Type

**Objective**: Decompose a problem into `sub`s and data structures on
paper before writing any code.

**Teach**: Introduce a design process: (1) restate the problem in your own
words, (2) list the data you'll need and its shape (a single value? a
list? a list of lists?), (3) list the operations you'll need as `sub`
signatures — name, parameters, what it returns — *before* implementing any
of them, (4) sketch what a sample run looks like. Model this on the board
for a problem the class hasn't seen yet (e.g., a simple grade-book
program with letter-grade cutoffs).

**Guided practice**: As a class, design (not implement) a text-based
"vending machine" simulation this way — data, `sub` signatures, sample
run — entirely on paper/board.

**Independent practice**: Worksheet 12 — students design (not implement)
their own small program idea using this process, as practice for planning
the capstone next.

**Wrap-up**: Peer review in pairs: can your partner tell what your
program will do just from your `sub` signatures, without reading any
implementation?

**Differentiation**: This lesson is inherently differentiated — the
design process scales from a simple 2-`sub` program to a much more
ambitious one depending on student ambition; the process, not the
project's size, is what's being assessed.

---

## Lesson 13 — Capstone Planning

**Objective**: Apply the Lesson 12 design process to the actual capstone
project.

**Teach**: Present capstone options (full spec in `assessment.md`):
- **Text adventure game** — rooms as data, a "current room" variable,
  `sub`s for describing a room and handling a command.
- **Simulation** — something with repeated random events tracked over many
  trials (e.g., dice game statistics, a simple population/spread model).
- **Data processing tool** — takes a list of records (built into the
  program or entered by the user) and computes/searches/sorts over it.
- **Student's own proposal**, approved by the teacher, meeting the same
  minimum bar (at least 3 `sub`s, at least one list, at least one
  algorithm from Lessons 7-9 used meaningfully).

**Guided practice**: Peer design review, using Lesson 12's process as a
checklist.

**Independent practice**: Finalize a written design document: restated
problem, data shapes, `sub` signatures, sample run.

**Wrap-up**: Teacher approves each plan (or requests one revision) before
build days begin.

**Differentiation**: Scope, not process, is the differentiation lever —
a strong student's plan should have more `sub`s and a more ambitious data
shape, not a fundamentally different planning process.

---

## Lesson 14 — Capstone Build, Day 1

**Objective**: Implement the planned capstone, `sub` by `sub`.

**Teach**: No new syntax. Reinforce: implement and test one `sub` at a
time against its planned signature, rather than writing the whole program
and debugging it all at once — this is the single biggest lever on
whether build days go smoothly.

**Independent practice**: Full build session.

**Wrap-up**: Stand-up — each student names one working `sub` and one
thing they're stuck on.

**Differentiation**: Use the teacher's guide §8 support/extension moves;
fast finishers should be encouraged to save a general-purpose `sub` from
their capstone to their library mid-project, not just at the end.

---

## Lesson 15 — Capstone Build, Day 2

**Objective**: Continue implementation; begin integration testing of
`sub`s working together.

**Teach**: Shift framing from "does each piece work" to "does the whole
thing work together" — this is where scope and data-shape mismatches
between `sub`s tend to surface, and where the Lesson 11 debugging process
gets real exercise.

**Independent practice**: Full build session.

**Wrap-up**: Stand-up, same format as Lesson 14.

**Differentiation**: Same as Lesson 14.

---

## Lesson 16 — Code Review and Refactoring

**Objective**: Read and give feedback on a peer's code; refactor one's
own project based on feedback.

**Teach**: Establish review norms: comment on *clarity* (could you tell
what a `sub` does from its name and signature alone?) and *organization*
(is repeated logic pulled into a `sub`?), not on personal style
preferences. Pair students to review each other's near-finished capstones
using a short checklist (Worksheet 16).

**Guided practice**: Model reviewing one anonymized piece of code as a
class first, so students see the tone and specificity expected.

**Independent practice**: Peer review, then a focused refactoring pass
based on feedback received — at minimum, one renamed variable/`sub` for
clarity and one instance of repeated logic pulled into a `sub`, if either
applies.

**Wrap-up**: Exit ticket — what's one piece of feedback you received, and
what did you change because of it?

**Differentiation**: For projects already in strong shape, the review
partner's task shifts to "find the one edge case this doesn't handle yet."

---

## Lesson 17 — What Comes After BARE

**Objective**: Understand which concepts transfer directly to other
languages and which BARE features were deliberate teaching simplifications.

**Teach**: Go through `docs/language-spec.md §13` ("what's deliberately
not here") as a class, and for each missing feature, discuss what a
student will meet in its place in a language like Python or JavaScript:
- `elseif`/`elif` — same idea as chained `if`/`else`, just less nesting
- `try`/`catch` — handling an error instead of the program stopping
- Classes/objects — bundling data and the `sub`s that act on it together
- `for` loops — a `while` loop with the counter pattern built into the
  syntax
- Multiple return values, more numeric types, `global`-style scope options
Emphasize what's *not* on this list and therefore doesn't need
re-learning: variables, `if`/`else` logic itself, loop patterns, `sub`s/
functions and parameters/return values, scope as a concept, lists, and —
most importantly — the actual practice of designing before coding and
debugging systematically. That is the actual content of this course; BARE
was the vehicle.

**Guided practice**: As a class, sketch what one of the capstone's `sub`s
would look like written in Python or JavaScript syntax (a light syntax
comparison, not a full lesson in another language).

**Independent practice**: Worksheet 17 — a short reflection: which BARE
limitation are you most looking forward to *not* having in your next
language, and why?

**Wrap-up**: Discuss answers as a class.

**Differentiation**: Students with prior exposure to another language can
lead the "what does this look like elsewhere" discussion instead of the
teacher.

---

## Lesson 18 — Capstone Showcase and Reflection

**Objective**: Present the finished capstone and reflect on the semester.

**Teach**: Structure presentations around: what the program does, a live
run, one `sub` the presenter is proudest of and why, and the hardest bug
of the whole project. Collect projects using the rubric in
`assessment.md`.

**Wrap-up**: A closing written reflection: what's one thing you can do
now that you couldn't do at the start of the semester, and what's one
thing you're still curious about?

**Differentiation**: As in Tier 2, choose a presentation format (whole
class, small group, teacher-only) that will get the most honest
explanation out of each student.

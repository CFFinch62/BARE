# Tier 2 — BARE Builders (ages ~11-13)

Seventeen lessons, ~45-50 minutes each. This tier's center of gravity is
**`sub`s and scope** (Lessons 2-5 all build toward one idea, deliberately
slower than everything else) and **lists** (Lessons 6-8), then widens into
the full builtin set, real debugging practice on multi-part programs, a
first taste of recursion, and the **personal library** — which turns
"reusable code" from a concept into something students actually do.

Students entering this tier should be comfortable with everything in Tier
1 (variables, `if`/`else`, `while`, `input`/`num`). Lesson 1 opens with a
fast diagnostic recap for students arriving without Tier 1.

---

## Lesson 1 — Welcome Back, and Why We Need `sub`s

**Objective**: Recap Tier 1 concepts; motivate functions as a solution to
repeated code.

**Diagnostic (for students new to BARE)**: A 10-minute "type and predict"
warm-up covering variables, `if`/`else`, and a `while` loop — use it to
spot anyone who needs a Tier 1 refresher session before continuing.

**Teach**: Put up a program that computes the same formula (say, a
Fahrenheit-to-Celsius conversion) three separate times with three
different variable names, copy-pasted. Ask: *"What's annoying about
this? What happens if the formula itself had a mistake?"* (You'd have to
fix it in three places, and probably forget one.) That's the motivation
for everything in this tier's first third: a `sub` lets you write the
formula once and reuse it anywhere.

**Guided practice**: As a class, spot the repeated logic in the example
and discuss (without writing a `sub` yet — that's next lesson) what a
"fix once, use everywhere" version would need to look like.

**Independent practice**: Worksheet 1 — a "find the repetition" exercise
on a few short example programs.

**Wrap-up**: Exit ticket — what's the downside of copy-pasting the same
logic three times in a program?

**Differentiation**: *Extension* — count exactly how many places a
one-character bug in the repeated formula would need to be fixed.
*Support* — if Tier 1 concepts are shaky, spend this whole session on the
diagnostic and push the `sub` motivation to the start of Lesson 2.

---

## Lesson 2 — Your First `sub`

**Objective**: Define and call a `sub` with no parameters and no return
value.

**Vocabulary**: sub (subroutine), call.

**Teach**:
```
sub greet()
    print "Hello there!"
    print "Welcome to BARE."
end

greet()
greet()
greet()
```
Point out: the code between `sub greet()` and `end` doesn't run until
`greet()` is *called* — defining it and running it are two different
things, and this trips people up if not said explicitly. Call it multiple
times to make the "write once, use many times" payoff concrete.

**Guided practice**: As a class, turn a short block of repeated `print`
statements from Lesson 1's motivating example into a `sub`.

**Independent practice**: Worksheet 2.

**Wrap-up**: Exit ticket — does writing `sub greet()\n...\nend` by itself
print anything? Why or why not?

**Differentiation**: *Extension* — write two different `sub`s and call
them in an interesting order. *Support* — one `sub`, called three times,
is a complete goal for this lesson.

---

## Lesson 3 — `sub`s with Parameters

**Objective**: Pass values into a `sub` so it can behave differently each
time it's called.

**Vocabulary**: parameter, argument.

**Teach**:
```
sub greet(name)
    print "Hello, " + name + "!"
end

greet("Ada")
greet("Grace")
```
Emphasize: `name` inside the `sub` is a brand new variable that only
exists while that `sub` is running, and it gets its value from whatever's
passed in when the `sub` is called. Show a two-parameter example:
```
sub introduce(name, age)
    print name + " is " + age + " years old"
end

introduce("Sam", 12)
```

**Guided practice**: As a class, add a parameter to Lesson 2's `sub` so it
greets a specific name instead of always the same message.

**Independent practice**: Worksheet 3.

**Wrap-up**: Exit ticket — in `greet("Ada")`, which word is the parameter
and which is the argument? (`name` is the parameter, in the definition;
`"Ada"` is the argument, in the call.)

**Differentiation**: *Extension* — a three-parameter `sub`. *Support* —
stick to one parameter; two is next lesson's stretch if needed.

---

## Lesson 4 — `sub`s That Give Back an Answer: `return`

**Objective**: Use `return` to send a value back out of a `sub`, and use
that value in an expression.

**Teach**: Reuse the running Fahrenheit/Celsius motivation from Lesson 1
— this is `examples/temperature_converter.bare`:
```
sub to_celsius(fahrenheit)
    return (fahrenheit - 32) * 5 / 9
end

response = input("Enter a temperature in Fahrenheit: ")
fahrenheit = num(response)
celsius = to_celsius(fahrenheit)

print str(fahrenheit) + "F is " + str(celsius) + "C"
```
Point out: `to_celsius(fahrenheit)` is itself a value now — it can go on
the right side of `=`, inside a `print`, anywhere an expression could go.
Contrast with Lessons 2-3's `sub`s, which only ever printed — they never
handed anything back out.

**Guided practice**: As a class, write a `sub` that takes two numbers and
returns their average.

**Independent practice**: Worksheet 4.

**Wrap-up**: Exit ticket — what's the difference between a `sub` that
`print`s something and a `sub` that `return`s something?

**Differentiation**: *Extension* — a `sub` that returns a `true`/`false`
answer (e.g., "is this number even?") and is used directly inside an
`if`. *Support* — the average `sub`, called and printed once, is a
complete goal for this lesson.

---

## Lesson 5 — Scope: What a `sub` Can and Can't See

**Objective**: Understand that a `sub` cannot see variables from outside
itself — no exceptions — and that this is BARE's strictest rule.

**Warm-up**: Ask: "If I whisper a secret to just one friend in a group of
five, can everyone else hear it?" No — only the one you told directly.
That's how a `sub` works with variables: it only knows what you hand it
as a parameter.

**Teach**: Run this on purpose and let students watch it fail:
```
total = 100

sub double(n)
    print total       # runtime error: 'total' is not defined
    return n * 2
end

print double(5)
```
Read the error together: `'total' is not defined`. Ask: *"total is
clearly defined up there — so why does BARE say it isn't?"* Land the
rule: **a `sub` gets a completely fresh, empty scope with no access to
anything outside it — not even to read.** There is no `global` keyword in
BARE to work around this. Fix the example properly by passing `total` in
as a parameter instead. This is worth its own full lesson — don't rush
past it (see `teachers-guide.md §5`).

**Guided practice**: As a class, take 2-3 broken examples (each trying to
reach an outside variable from inside a `sub`) and fix each by adding the
right parameter.

**Independent practice**: Worksheet 5.

**Wrap-up**: Exit ticket — name one thing a `sub` is allowed to know
about, and one thing it's never allowed to know about.

**Differentiation**: *Extension* — predict, before running, exactly which
line of a 5-line broken example will error and what the error message
will say. *Support* — work through the single canonical broken example
above by hand, out loud, before touching the keyboard.

---

## Lesson 6 — Lists

**Objective**: Create a list, access elements by index, and print a whole
list.

**Vocabulary**: list, index.

**Teach**:
```
colors = ["red", "green", "blue"]
print colors
print colors[0]
print colors[1]
print colors[2]
```
Emphasize **0-indexing** explicitly and repeatedly: the *first* item is
`colors[0]`, not `colors[1]`. Show that asking for an index that doesn't
exist (`colors[5]`, or `colors[-1]`) is a runtime error — there's no
"last item" shortcut the way some languages have.

**Guided practice**: As a class, build a list of 5 favorite things and
print each one using its index.

**Independent practice**: Worksheet 6.

**Wrap-up**: Exit ticket — in a 4-item list, what's the index of the
*last* item?

**Differentiation**: *Extension* — a list of numbers; print the sum of
just the first and last elements. *Support* — a 3-item list, printing
each element one at a time with the index written down on paper first.

---

## Lesson 7 — Growing and Looping Through Lists

**Objective**: Use `append()` and `len()`, and loop through a list with a
`while` loop and an index counter.

**Teach**:
```
scores = [88, 92, 75]
append(scores, 100)
print scores          # [88, 92, 75, 100]
print len(scores)      # 4

i = 0
while i < len(scores)
    print scores[i]
    i = i + 1
end
```
Point out `len(scores)` in the loop condition — the loop works for a list
of *any* size without changing the code, which is exactly the point of
looping instead of writing `print scores[0]` through `print scores[3]` by
hand.

**Guided practice**: As a class, build a list, `append` three more items
one at a time (printing the list after each), then loop through and print
every item.

**Independent practice**: Worksheet 7.

**Wrap-up**: Exit ticket — why use `i < len(scores)` instead of a specific
number like `i < 4`?

**Differentiation**: *Extension* — loop through a list of numbers and
print only the ones greater than some value. *Support* — provide the loop
skeleton (`i = 0` / `while` / `i = i + 1`) and have the student fill in
just the `print scores[i]` line.

---

## Lesson 8 — Project: Class Roster

**Objective**: Combine `sub`s and lists into one program that manages a
small dataset.

**Teach**: Model planning on the board: what data are we storing (a list
of names, maybe a matching list of scores), what operations do we need
(add a student, print everyone, compute an average)? Sketch which parts
should be `sub`s before writing code.

**Guided practice**: As a class, build the "print everyone" `sub`
together:
```
sub print_roster(names)
    i = 0
    while i < len(names)
        print names[i]
        i = i + 1
    end
end
```

**Independent practice**: Students build a roster program with at least:
a list of names, a list of scores, a `sub` that prints the whole roster,
and a `sub` that computes and returns the average score.

**Wrap-up**: A few students share one `sub` from their program and
explain what it does.

**Differentiation**: *Extension* — a `sub` that finds and returns the
highest score. *Support* — names list and a single "print everyone" `sub`
is a complete goal; the average `sub` can be a stretch target.

---

## Lesson 9 — Validation Loops and Nested Decisions

**Objective**: Combine `while` and `if` to keep asking for input until
it's valid.

**Teach**:
```
age = num(input("Enter your age (0-120): "))
while age < 0 or age > 120
    print "That's not a valid age."
    age = num(input("Enter your age (0-120): "))
end
print "Thanks!"
```
Point out this is a *new* use of `while` — not "repeat N times" but
"repeat until this thing stops being a problem." Combine with a
multi-branch decision (weather advice, grade bands) reusing nested
`if`/`else` from Tier 1 but now with more branches, calling out again how
this motivates wanting `elseif`.

**Guided practice**: As a class, add validation to an existing program
from an earlier lesson (e.g., reject a negative score in the roster
project).

**Independent practice**: Worksheet 9.

**Wrap-up**: Exit ticket — what's different about a validation loop
compared to a counting loop?

**Differentiation**: *Extension* — validate two different inputs in the
same program. *Support* — validate a single simple condition (e.g.,
"must be positive") before combining conditions with `or`.

---

## Lesson 10 — Builtins in Depth: `round`, `num`, `str`

**Objective**: Use `round()`, and solidify `num()`/`str()` for real data
work.

**Teach**:
```
price = 19.999
print round(price, 2)     # 20.0 -> displayed as 20
average = 87.666
print round(average, 1)    # 87.7
```
Show `round()` rounds the way math class does (half rounds up, e.g.
`round(2.5, 0)` is `3`), not the "round to even" rule some other
languages use — reassure students this matches what they already know.
Revisit `str()`/`num()` explicitly as a matched pair: `num()` turns text
into a number you can do math with; `str()` turns a number into text you
can join with `+` (a reminder — Lesson 5 [Tier 1] showed `+` often does
this automatically, but `str()` is needed when joining two numbers as
text, e.g. building a fraction like `str(a) + "/" + str(b)`).

**Guided practice**: As a class, round a running average from the
roster project to 1 decimal place before printing it.

**Independent practice**: Worksheet 10.

**Wrap-up**: Exit ticket — what does `round(3.14159, 2)` print?

**Differentiation**: *Extension* — round the same number to 0, 1, and 3
decimal places and compare. *Support* — one rounding example, directly
tied to the roster project's average.

---

## Lesson 11 — Games with Randomness: Rock, Paper, Scissors

**Objective**: Combine `sub`s, lists, `random()`, and `and`/`or` into a
small game.

**Teach**: Walk through `examples/rock_paper_scissors.bare` together,
piece by piece:
```
sub beats(a, b)
    if a == "rock" and b == "scissors"
        return true
    end
    if a == "paper" and b == "rock"
        return true
    end
    if a == "scissors" and b == "paper"
        return true
    end
    return false
end

choices = ["rock", "paper", "scissors"]
computer = choices[random(0, 2)]
player = input("rock, paper, or scissors? ")
```
Ask students to predict what `choices[random(0, 2)]` does before
explaining it (pick a random index into the list — connects `random()`
back to Lesson 6's indexing).

**Guided practice**: Trace `beats("rock", "scissors")` by hand as a class
before running it.

**Independent practice**: Worksheet 11 — students modify or extend the
example (e.g., add a tie counter across multiple rounds).

**Wrap-up**: Exit ticket — what does `choices[random(0, 2)]` pick from,
and why `0` to `2` and not `1` to `3`?

**Differentiation**: *Extension* — add a "best of 5" loop around the
whole game. *Support* — trace through the existing example file by hand
before attempting modifications.

---

## Lesson 12 — Debugging Deep Dive

**Objective**: Use breakpoints, Step, and Variable Watch to debug a
multi-`sub` program.

**Teach**: Take a program with 2-3 `sub`s (the roster project works well)
and deliberately introduce a bug (e.g., an off-by-one in a loop bound, or
a `sub` that returns the wrong thing). Demonstrate live:
- Setting a breakpoint *inside a `sub`* and noticing Variable Watch shows
  only that `sub`'s own parameters and locals — a direct, visible
  consequence of Lesson 5's scope rule, worth calling back explicitly.
- Using Step to cross from the calling code into the `sub` and back out,
  watching the scope shown in Variable Watch change at that exact moment.

**Guided practice**: In pairs, students debug a provided broken multi-sub
program (Worksheet 12), narrating hypotheses to their partner before each
Step click.

**Independent practice**: Students find and fix the bug, then write one
sentence describing what the bug was and how they found it.

**Wrap-up**: A few pairs share their bug and how they found it.

**Differentiation**: *Extension* — the broken program has a second,
subtler bug for fast finishers to find. *Support* — teacher sets the
breakpoint and narrates the first pass; student takes over from there.

---

## Lesson 13 — A First Taste of Recursion

**Objective**: Understand a `sub` that calls itself, using factorial as
the example.

**Vocabulary**: recursion, base case.

**Teach**: Walk through `examples/factorial.bare`:
```
sub factorial(n)
    if n <= 1
        return 1
    else
        return n * factorial(n - 1)
    end
end

print factorial(5)     # 120
```
Trace it by hand on the board as a stack of calls: `factorial(5)` needs
`factorial(4)`, which needs `factorial(3)`, and so on down to
`factorial(1)`, which is the **base case** — the one that doesn't call
itself, and the reason the chain eventually stops. This connects directly
to Lesson 5's scope lesson: each call to `factorial` gets its own
completely separate `n`, which is exactly why this works and doesn't
confuse itself.

**Guided practice**: As a class, trace `factorial(4)` step by step,
writing out each nested call and its return value.

**Independent practice**: Worksheet 13.

**Wrap-up**: Exit ticket — what would happen if `factorial` had no base
case (no `if n <= 1`)?

**Differentiation**: *Extension* — write a recursive `sub` that counts
down from a number to 1. *Support* — tracing the given `factorial`
example by hand is a complete goal; writing a new recursive `sub` is a
stretch, not a requirement, at this age.

---

## Lesson 14 — Your Personal Library

**Objective**: Save a `sub` to the personal library and use it in a
different program.

**Teach**: Live demo:
1. Write a useful, general-purpose `sub` (e.g., the `to_celsius` from
   Lesson 4, or an `average` sub from the roster project).
2. Select the whole `sub ... end` block, then **Edit → Save Selection to
   Library**.
3. Open the **My Library** panel (View menu) — the `sub` now appears
   there.
4. **Start a brand-new, blank program** and call that `sub` by name —
   point out there's no import statement, nothing special; it just works,
   and the console says `Loaded from your library: ...` when you click
   Run.
5. Show double-clicking the library entry to insert a ready-to-fill-in
   call.

Frame this as the payoff for the whole tier: "you've been writing
reusable logic all semester with `sub`s — this is what makes it reusable
*across* programs, not just within one."

**Guided practice**: Each student saves one `sub` from an earlier lesson
to their library and confirms it works in a new blank program.

**Independent practice**: Worksheet 14 — save two more `sub`s and write a
short new program that uses all three together.

**Wrap-up**: Exit ticket — if you write a `sub` with the same name in
your current program as one already in your library, which one runs?

**Differentiation**: *Extension* — open the library file directly (File →
Open My Library) and add a comment above each saved `sub` explaining what
it does. *Support* — saving and reusing one `sub` successfully is a
complete goal for this lesson.

---

## Lesson 15 — Capstone Workshop, Day 1: Planning

**Objective**: Plan a multi-part capstone project before writing code.

**Teach**: Present the capstone options (see `assessment.md` for the
rubric all of these share):
- **Quiz Game** — a list of questions and answers, a scoring loop, and a
  final score report.
- **Rock-Paper-Scissors Tournament** — extend Lesson 11's game with a
  running score across multiple rounds and a "best of N" `sub`.
- **A project of the student's own design**, approved by the teacher,
  using at least two `sub`s and one list.

Require a short written plan before coding: what data will you store
(what lists/variables), what `sub`s will you need, and what will a sample
run look like (write out example output by hand).

**Guided practice**: Peer-review plans in pairs before building — a
partner should be able to read the plan and describe what the program
will do.

**Independent practice**: Finalize project plan.

**Wrap-up**: Teacher spot-checks each plan before the next session's build
time begins.

**Differentiation**: *Extension* — plan an additional feature beyond the
minimum. *Support* — the Quiz Game option with a provided data structure
template (list of question/answer pairs already sketched) is the lowest-
friction path.

---

## Lesson 16 — Capstone Workshop, Day 2: Build

**Objective**: Build the planned capstone project.

**Teach**: No new syntax — full build session, teacher circulating using
the "reduce the program" and "reduce the concept" support moves from
`teachers-guide.md §8` as needed.

**Independent practice**: Full session. Encourage students to get one
`sub` fully working and tested before moving to the next, rather than
writing the whole program at once and debugging everything simultaneously.

**Wrap-up**: Quick stand-up — each student states one thing that's
working and one thing they're stuck on, for the teacher to triage before
next session.

**Differentiation**: *Extension* — students who finish early save a
useful `sub` from their project to their library and help a peer.
*Support* — pair a stuck student with a peer for the last 10 minutes.

---

## Lesson 17 — Capstone Showcase

**Objective**: Present a finished project and explain design decisions.

**Teach**: Structure the showcase around three questions each presenter
answers (in addition to running their program):
1. What does your program do?
2. Which part are you most proud of?
3. What was the hardest bug, and how did you find it?

**Wrap-up**: Collect capstones using the rubric in `assessment.md`.

**Differentiation**: Presenting to the whole class vs. a small group vs.
just the teacher are all valid formats — match to what will get an honest,
low-anxiety explanation out of each student, since the explanation is
what's actually being assessed (see rubric).

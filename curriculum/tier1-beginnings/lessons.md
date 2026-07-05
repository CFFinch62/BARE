# Tier 1 — BARE Beginnings (ages ~8-10)

Sixteen lessons, roughly 40-45 minutes each. By the end, students can write
a program that talks to the user, makes decisions, repeats actions, and
uses randomness — no `sub`s yet (that's Tier 2's opening act, on purpose:
scope rules deserve full attention of their own, not a rushed mention at
the end of a packed semester).

Every lesson: **Objective**, **Warm-up** (2-5 min), **Teach**, **Guided
practice**, **Independent practice** (send students to the matching
section of `worksheets.md`), **Wrap-up**, **Differentiation**.

---

## Lesson 1 — Meet the IDE, Meet `print`

**Objective**: Launch the IDE, run a program, understand that a program is
a list of exact instructions the computer follows in order.

**Warm-up**: "Give me instructions to make a peanut butter sandwich" — write
them on the board exactly as literally as students give them ("open the
jar" before "get the peanut butter out" breaks it). This is the whole idea
of a program: exact steps, followed in order, no assumed knowledge.

**Teach**:
- Tour the IDE: editor (top), console (bottom), the Run button/F5.
- Type together:
  ```
  print "Hello, world!"
  ```
- Click Run. Point out: the console shows exactly what was inside the
  quotes, nothing more.
- Introduce comments: `# this is a note to yourself, the computer ignores it`.
- Try breaking it on purpose — delete a quote mark, click Run, look at the
  red squiggle and the console error together. Say explicitly: *"the
  computer isn't mad at you, it's telling you exactly what's confusing and
  which line."*

**Guided practice**: As a class, write three more `print` lines together,
each printing a different favorite thing (color, animal, food).

**Independent practice**: Worksheet 1 — five `print` statements plus one
intentional "fix the broken program" exercise.

**Wrap-up**: Exit ticket — "What are the two things a `print` statement
needs?" (the word `print`, and something in quotes.)

**Differentiation**: *Extension* — challenge fast finishers to print a
small picture using only text characters (a house, a smiley) across
multiple `print` lines. *Support* — pair with a confident typist; the
concept (not the typing) is the point at this stage.

---

## Lesson 2 — Strings and Joining Text

**Objective**: Understand that text in quotes is called a **string**, and
that `+` joins two strings together.

**Vocabulary**: string.

**Warm-up**: Ask: "What's inside the quotes in `print "Hi there"`?" Land on:
that whole chunk of text is called a *string* — like a string of beads,
it's a string of letters.

**Teach**:
```
print "Hello" + ", " + "world" + "!"
```
Run it, notice it prints as one joined line. Then show what happens with a
quote mark *inside* a string (it ends the string early — a syntax error) —
and the fix, `\"`:
```
print "She said \"hi\" to me"
```
Also show single quotes don't work in BARE (`'hello'` is an error) —
double quotes only, always.

**Guided practice**: Build a silly sentence together by joining 4-5 short
strings with `+`.

**Independent practice**: Worksheet 2 — join strings into sentences;
one problem requires an escaped quote.

**Wrap-up**: Exit ticket — what symbol joins two strings together?

**Differentiation**: *Extension* — build a "mad libs" style sentence using
5+ joined strings. *Support* — provide the strings already typed on paper;
the student just arranges the `+` symbols.

---

## Lesson 3 — Variables: Giving Values a Name

**Objective**: Store a value in a named variable and print it back.

**Vocabulary**: variable, assign.

**Warm-up**: "If I put your name on a sticky note and stick it to a box
with a toy inside, what's the sticky note for?" → a label so you can find
what's inside without remembering exactly where the box is. That's a
variable.

**Teach**:
```
name = "Ada"
print name
print "Hello, " + name + "!"
```
Point out `=` here means *store this value under this name*, not "equals"
like in math class yet (that distinction gets sharpened later, in Lesson
10, when `==` shows up). Show that a variable can change:
```
name = "Ada"
print name
name = "Grace"
print name
```
Naming rules: letters, no spaces, can't start with a number, pick names
that describe what's inside (`age` not `x`).

**Guided practice**: Students create 3 variables (their name, favorite
number, favorite color) and print each with a sentence around it.

**Independent practice**: Worksheet 3.

**Wrap-up**: Exit ticket — what does `favorite_color = "blue"` do?

**Differentiation**: *Extension* — reassign a variable 3 times and predict
what prints before running. *Support* — focus on just one variable used
twice, don't introduce three at once.

---

## Lesson 4 — Numbers and Math

**Objective**: Use `+ - * /` on numbers stored in variables.

**Warm-up**: Mental math relay — quick addition/multiplication questions,
energetic and fast.

**Teach**:
```
apples = 5
oranges = 3
total = apples + oranges
print total
```
Show all four operators. Show that `/` can produce a number with a
decimal point (`print 10 / 4` → `2.5`) — BARE only has one kind of number,
so there's no separate "whole number division"; `10 / 2` prints as `5`
(no `.0`) simply because it happens to come out even.

**Guided practice**: A "change from a purchase" problem worked as a class:
given a price and an amount paid, compute change.

**Independent practice**: Worksheet 4.

**Wrap-up**: Exit ticket — predict the output of `print 7 / 2` before
running it, then check.

**Differentiation**: *Extension* — order of operations: does
`2 + 3 * 4` print 20 or 14? Predict, then test, then explain. *Support* —
stick to one operator at a time before mixing them.

---

## Lesson 5 — Mixing Words and Numbers

**Objective**: Combine strings and numbers in one `print`, understanding
BARE automatically turns a number into text when it's joined with `+` to a
string.

**Warm-up**: Ask what happens if you try `print "I am " + 9 + " years old"`
— take guesses before running it.

**Teach**:
```
age = 9
print "I am " + age + " years old"
```
This works in BARE without any conversion step — the number quietly
becomes text the moment it's joined to a string with `+`. (Students will
meet a case in Lesson 6 where this automatic help *doesn't* apply, and
that contrast is exactly the point of that lesson — don't over-explain the
mechanism now, just establish that it works.)

**Guided practice**: Build an "About my pet" sentence mixing a name
(string) and an age (number) in one `print`.

**Independent practice**: Worksheet 5.

**Wrap-up**: Exit ticket — is `9` in `"I am " + 9 + " years old"` a string
or a number? (A number — BARE just displays it as text here.)

**Differentiation**: *Extension* — join three or more numbers and strings
in one line. *Support* — one number, one string, nothing more yet.

---

## Lesson 6 — Talking to the User: `input()`

**Objective**: Use `input()` to get text from the user and store it.

**Warm-up**: "How does the computer know your name if you never told it?"
— it doesn't, unless you ask.

**Teach**:
```
name = input("What's your name? ")
print "Nice to meet you, " + name + "!"
```
Now the important gotcha, demonstrated live:
```
age = input("How old are you? ")
print age * 7
```
Run it — this is a **runtime error**, because `input()` always hands back
a *string*, even if the user typed digits, and BARE won't silently do math
on text. Fix it with `num()`:
```
age = num(input("How old are you? "))
print age * 7
```
Land the rule hard: **anything from `input()` that you want to do math
with must go through `num()` first.** This single habit prevents the most
common bug of the whole semester.

One more twist worth showing, since a curious student will try it anyway:
`age + 1` (using `+` instead of `*`) does **not** crash — it silently
glues the `1` onto the string and prints `"51"` instead of `6`. `+` is the
one operator that quietly converts a number to text for you; every other
operator (and comparisons like `>`) correctly refuses to mix a string and
a number. That makes `+` the *sneakier* mistake — nothing tells you it's
wrong — which is exactly why the `num()` habit has to be automatic rather
than something you only remember once you see an error.

**Guided practice**: Ask the user for two numbers, print their sum.

**Independent practice**: Worksheet 6.

**Wrap-up**: Exit ticket — what does `input()` always give you back, no
matter what the user types?

**Differentiation**: *Extension* — ask for three numbers and print the
total and the difference. *Support* — provide the `num(input(...))` line
as a template to fill the prompt text into.

---

## Lesson 7 — Project: "About Me"

**Objective**: Combine Lessons 1-6 into one small complete program.

**Teach**: No new syntax. Model planning on the board first: *what will I
ask, in what order, what will I print back?* — before typing anything.
This is the first time students plan before they code; make it explicit
and call it out.

**Guided practice**: Build the first two questions together as a class
(name, then one more fact), then release students to add 2-3 more of their
own choosing, mixing strings and numbers.

**Independent practice**: Students finish their own "About Me" program:
at least 4 `input()` calls, a mix of text and number facts, and a
friendly printed summary at the end.

**Wrap-up**: Volunteers run their program for the class.

**Differentiation**: *Extension* — do some math with one of the numeric
answers before printing it back (e.g., "in 10 years you'll be ___").
*Support* — provide a checklist of the four required `input()` calls; the
content of the questions is still the student's own choice.

---

## Lesson 8 — Making Decisions: `if`

**Objective**: Use `if` to run code only when a condition is true.

**Vocabulary**: condition, boolean.

**Warm-up**: "If it's raining, bring an umbrella." Point out: this only
happens *if* the condition is true — on a sunny day, nothing about the
umbrella happens at all.

**Teach**:
```
age = num(input("How old are you? "))
if age >= 10
    print "You can join the big kids' club!"
end
```
Point out the `end` — every `if` needs one to say "the decision part is
over." Show that with no `else`, if the condition is false, nothing prints
at all — the program just moves on.

**Guided practice**: As a class, write an `if` that prints a message only
if a guessed number matches a secret number typed directly into the code.

**Independent practice**: Worksheet 8.

**Wrap-up**: Exit ticket — if the condition after `if` is false, what
happens?

**Differentiation**: *Extension* — an `if` with two unrelated conditions,
each with their own `end` (not yet `else` — that's next lesson).
*Support* — trace through the `if` by hand with a specific input value
before running it, predicting whether the `print` will happen.

---

## Lesson 9 — Two-Way Decisions: `if`/`else`

**Objective**: Use `else` to provide an alternative when a condition is
false.

**Teach**:
```
age = num(input("How old are you? "))
if age >= 10
    print "You can join the big kids' club!"
else
    print "You'll be old enough soon!"
end
```
Then show what happens with *more than two* outcomes — nested `if`/`else`:
```
score = num(input("Score: "))
if score >= 90
    print "A"
else
    if score >= 70
        print "B or C"
    else
        print "Keep practicing!"
    end
end
```
Note out loud that this nesting gets messy fast with more categories —
ask "what would you invent to make this nicer?" Some students will
independently propose something like `elseif`; validate that instinct
and mention that many languages do exactly that (see the teacher's guide,
§4, for why BARE doesn't).

**Guided practice**: As a class, build a 3-outcome nested `if`/`else`
(e.g., weather → "wear a coat" / "wear a jacket" / "wear a t-shirt").

**Independent practice**: Worksheet 9.

**Wrap-up**: Exit ticket — draw (in words) what happens if `score` is
exactly `70` in the example above.

**Differentiation**: *Extension* — a 4-outcome nested decision.
*Support* — start from the 2-outcome version only; nesting is next
lesson's stretch goal for a student still solidifying `if`/`else`.

---

## Lesson 10 — Comparing Things

**Objective**: Use `== != < > <= >=` confidently, and understand `true`/
`false` as values in their own right.

**Vocabulary**: boolean, `true`, `false`.

**Warm-up**: Ask students to answer true-or-false questions about the room
("the door is open", "there are more than 20 people here") — establish
that a *condition* is really just a true-or-false question.

**Teach**: Show all six comparison operators against a couple of example
values. Emphasize `==` (comparing) vs `=` (storing) — this is one of the
most common early typos:
```
score = 100          # = stores a value
print score == 100    # == asks a true-or-false question, prints true
```
Briefly note BARE's truthiness rule, concretely: only `false` and `null`
count as "false" for an `if` — everything else, including `0` and an empty
string `""`, counts as "true." Don't over-explain *why* at this age; just
make sure nobody walks away thinking `if 0` skips the block (it doesn't).

**Guided practice**: A quick round of "predict true or false" on the
board using variables with known values.

**Independent practice**: Worksheet 10.

**Wrap-up**: Exit ticket — what's the difference between `=` and `==`?

**Differentiation**: *Extension* — chain of comparisons using different
operators against the same two variables, predicting each. *Support* —
focus on `==` and `<`/`>` only; the full six-operator set can wait.

---

## Lesson 11 — Combining Conditions: `and`, `or`, `not`

**Objective**: Combine multiple true/false questions into one condition.

**Warm-up**: "You can go outside to play if it's not raining AND your
homework is done." Two conditions, both need to be true.

**Teach**:
```
temp = num(input("Temperature: "))
raining = input("Is it raining? (yes/no) ")

if temp > 60 and raining == "no"
    print "Great day for a bike ride!"
else
    print "Maybe stay in today."
end
```
Show `or` (either one being true is enough) and `not` (flips true/false)
with quick contrasting examples.

**Guided practice**: As a class, write an `and` condition and an `or`
condition for the same scenario and compare when each triggers
differently.

**Independent practice**: Worksheet 11.

**Wrap-up**: Exit ticket — with `and`, do both sides need to be true, or
just one?

**Differentiation**: *Extension* — a condition combining all three
(`and`, `or`, `not`) in one line. *Support* — `and` only this lesson;
introduce `or`/`not` in the next review cycle if needed.

---

## Lesson 12 — Repeating Yourself: `while`

**Objective**: Use a `while` loop to repeat an action a set number of
times, using a counter variable.

**Vocabulary**: loop, counter.

**Warm-up**: "Count out loud from 1 to 5 for me." Ask: what are you doing
after each number? (Checking: am I past 5 yet? If not, say the next one.)
That check-then-repeat is exactly a `while` loop.

**Teach**:
```
count = 1
while count <= 5
    print count
    count = count + 1
end
```
Trace it on the board line by line before running: what is `count` each
time through? Deliberately show the classic bug — forgetting
`count = count + 1` — and let the class watch the program never stop,
then use **Stop** to end it. This is a safe, expected way to meet infinite
loops for the first time.

**Guided practice**: Modify the loop as a class to count by 2s, then to
count backward from 5 to 1.

**Independent practice**: Worksheet 12.

**Wrap-up**: Exit ticket — what are the three things every counting loop
needs? (a starting value, a condition that eventually becomes false, and a
step that moves toward that.)

**Differentiation**: *Extension* — a loop that counts to a number the
*user* types in with `input()`. *Support* — trace the loop by hand,
writing down `count`'s value each pass, before typing any code.

---

## Lesson 13 — Loops That Use the User

**Objective**: Use a `while` loop with an accumulator (running total) and
with input gathered each time through.

**Teach**:
```
total = 0
count = 1
while count <= 3
    amount = num(input("Enter an amount: "))
    total = total + amount
    count = count + 1
end
print "Total: " + total
```
Point out `total` starting at `0` and growing each pass — a *running
total*, a very common loop pattern. Also show a **sentinel loop** — repeat
until the user types a specific stop word:
```
answer = ""
while answer != "quit"
    answer = input("Type a word (or 'quit' to stop): ")
    print "You typed: " + answer
end
```

**Guided practice**: As a class, build a loop that keeps asking for
numbers and adds them up until the user types `0`.

**Independent practice**: Worksheet 13.

**Wrap-up**: Exit ticket — where does `total` start, and why does it
matter that it starts there?

**Differentiation**: *Extension* — also track and print the *count* of
how many numbers were entered, and compute an average. *Support* — the
running-total pattern only; save the sentinel-loop variant for a
one-on-one follow-up.

---

## Lesson 14 — Tour: The IDE's Debugging Tools

**Objective**: Use breakpoints, Step, Continue, and the Variable Watch
panel to watch a program run one line at a time.

**Teach**: Using yesterday's accumulator loop (or a fresh short one),
demonstrate live:
1. Click in the line-number margin to set a breakpoint (a red dot).
2. Click **Run** — execution pauses right before that line.
3. Open **Variable Watch** (View menu) and watch `total` and `count`
   change as you click **Step** repeatedly.
4. Point out the scope-box shading around the loop body — it's showing
   the same nesting a student can see just by looking at indentation, as
   a visual double-check.

Frame this explicitly: *"This is how you answer 'why isn't my program
doing what I expect' without guessing — you watch it happen."*

**Guided practice**: In pairs, students set a breakpoint inside a loop
from an earlier lesson and step through it together, one narrating what
they expect before each Step click.

**Independent practice**: Worksheet 14 — a short "broken" program with a
logic bug (not a syntax error); students use Step + Variable Watch to find
and explain the bug in writing before fixing it.

**Wrap-up**: Exit ticket — what does the Variable Watch panel show you
while a program is paused?

**Differentiation**: *Extension* — set a breakpoint and predict every
variable's value at that point before actually looking at Variable Watch.
*Support* — teacher sets the breakpoint; the student just clicks Step and
narrates what changed.

---

## Lesson 15 — Randomness!

**Objective**: Use `random(min, max)` to generate unpredictable numbers.

**Teach**:
```
secret = random(1, 10)
print secret
```
Run it several times, noticing it changes. Explain `random(1, 10)` means
"any whole number from 1 to 10, including both ends, picked fresh each
time." Combine with what's already known:
```
secret = random(1, 10)
guess = num(input("Guess a number 1-10: "))
if guess == secret
    print "You got it!"
else
    print "Nope! It was " + secret
end
```

**Guided practice**: As a class, add a `while` loop around the guess so
the player can keep guessing until correct (this is most of next lesson's
capstone, built together first as scaffolding).

**Independent practice**: Worksheet 15.

**Wrap-up**: Exit ticket — does `random(1, 10)` ever produce `0` or `11`?

**Differentiation**: *Extension* — track and print how many guesses it
took. *Support* — the single-guess version is a complete, valid stopping
point.

---

## Lesson 16 — Capstone: Number Guessing Game + Showcase

**Objective**: Independently build a complete program combining
variables, `input`, `if`/`else`, `while`, and `random`.

**Teach**: No new syntax — this is a build day. Put the full spec on the
board:
1. Pick a secret number with `random`.
2. Let the player guess repeatedly with a `while` loop until correct.
3. After each wrong guess, tell them "too high" or "too low."
4. When they win, print how many guesses it took.

Remind students this is exactly `examples/guessing_game.bare` in spirit —
after they've built their own, showing them that file is a nice "you just
independently wrote something a real example program does" moment.

**Guided practice**: None — this is independent build time, with the
teacher circulating. Use the "reduce the program" support move (teacher's
guide §8) for anyone stuck: get just the `random` + one comparison working
first, then add the loop around it.

**Independent practice**: Full session(s) to build. Budget two sessions if
your schedule allows; one focused session is enough if the class has kept
pace with the rest of the tier.

**Wrap-up / Showcase**: Volunteers run their game for the class, or (with
larger classes) pair up to play each other's games. Ask each presenter one
question: *"What was the hardest part, and how did you figure it out?"* —
this is a better reflection prompt than "explain your code" because it
reinforces that debugging is the actual skill being assessed.

**Differentiation**: *Extension* — limit the player to a fixed number of
guesses (e.g., 6) and print a "you lose, the number was ___" message if
they run out. *Support* — a working single-guess version (Lesson 15's
independent practice) is an acceptable finished product for a struggling
student; the loop can be added with one-on-one help rather than gating
the whole showcase.

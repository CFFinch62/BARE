# Tier 1 Assessment

Three short checkpoint quizzes (5-10 minutes each, use formatively — see
`teachers-guide.md §7`) plus the capstone rubric. Answer keys included
after each quiz; keep them out of student view.

---

## Checkpoint 1 — Foundations (after Lesson 7)

Covers: `print`, strings, variables, numbers, `input()`/`num()`.

1. What will this print?
   ```
   print "Hi" + " " + "there"
   ```
2. What will this print?
   ```
   x = 5
   x = x + 1
   print x
   ```
3. This program crashes. Why, and how would you fix it?
   ```
   age = input("Age: ")
   print age * 2
   ```
4. Write one line of code that stores the number `7` in a variable called
   `count`.
5. What will this print?
   ```
   name = "Sam"
   pets = 2
   print name + " has " + pets + " pets"
   ```
6. True or False: `input()` always gives you back a number if the user
   types digits.
7. Trick question — does this one crash? What does it actually print if
   the user types `5`?
   ```
   age = input("Age: ")
   print age + 1
   ```

**Answer key**: 1. `Hi there`  2. `6`  3. Crashes because `age` is a
string and you can't multiply a string by a number directly — fix with
`age = num(input("Age: "))`  4. `count = 7`  5. `Sam has 2 pets`
6. **False** — `input()` always returns a string; use `num()` to convert it.
7. It does **not** crash — `+` quietly turns the `1` into text and joins
it on, printing `51` instead of `6`. This is why you can't rely on BARE
to catch a missing `num()` for you every time.

---

## Checkpoint 2 — Decisions (after Lesson 11)

Covers: `if`, `if`/`else`, comparison operators, `and`/`or`/`not`.

1. What will this print, if `age` is `8`?
   ```
   if age >= 10
       print "big kid"
   else
       print "little kid"
   end
   ```
2. What's the difference between `=` and `==`?
3. What will this print?
   ```
   print 5 == 5
   print 5 != 5
   ```
4. Fill in the blank so this prints "yes" only when both conditions are
   true:
   ```
   if temp > 70 ____ sunny == "yes"
       print "yes"
   end
   ```
5. What will this print?
   ```
   print not true
   ```
6. Is `0` treated as true or false in an `if` statement in BARE?

**Answer key**: 1. `little kid`  2. `=` stores a value into a variable;
`==` asks whether two values are equal (a true/false question)
3. `true` then `false`  4. `and`  5. `false`  6. **True** — only `false`
and `null` are treated as false in BARE; `0` counts as true.

---

## Checkpoint 3 — Loops and Debugging (after Lesson 14)

Covers: `while` loops, counters, accumulators, breakpoints/Step/Variable
Watch.

1. What will this print?
   ```
   count = 1
   while count <= 3
       print count
       count = count + 1
   end
   ```
2. What's wrong with this loop? (Don't run it unless you know where Stop
   is!)
   ```
   count = 1
   while count <= 5
       print count
   end
   ```
3. What three things does every counting loop need?
4. What does the Variable Watch panel show you, and when?
5. What's the difference between clicking **Step** and clicking
   **Continue** while a program is paused at a breakpoint?

**Answer key**: 1. `1`, `2`, `3` each on their own line  2. It never
updates `count`, so `count <= 5` is always true — infinite loop
3. A starting value, a condition that can become false, and a step that
moves toward that  4. The current value of every variable in scope,
while the program is paused (a breakpoint hit or Step mode)  5. **Step**
runs exactly one more statement and pauses again; **Continue** runs at
full speed until the next breakpoint or the program ends.

---

## Capstone Rubric — Number Guessing Game (Lesson 16)

Score each category 0-3. A 2 in every category is a solid, complete,
grade-level project; a 3 reflects going beyond what was asked.

| Category | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Correctness** | Doesn't run, or doesn't pick a random number / take guesses | Runs but gives wrong feedback (e.g., "too high" and "too low" reversed) | Works correctly for the core loop: picks a number, takes guesses, gives correct too-high/too-low feedback, ends on a correct guess | Also tracks and reports the guess count, or adds a guess limit |
| **Code organization** | No variables used meaningfully, or logic is a tangle of copy-pasted `if`s | Works, but variable names are unclear (`x`, `y`) or logic is more repetitive than it needs to be | Clear variable names, sensible use of `if`/`else` and `while`, no unnecessary repetition | Also handles an edge case unprompted (e.g., non-numeric input) |
| **Explanation** | Can't describe what their own code does | Can describe *what* it does but not *why* | Can walk through their code line by line and explain both what it does and why they wrote it that way | Can also explain what was hardest and how they debugged it |

A student scoring 2+ across all three categories has met the tier's goal.
Use scores of 0-1 as a signal to revisit the relevant lesson one-on-one
before moving to Tier 2, not as a final judgment.

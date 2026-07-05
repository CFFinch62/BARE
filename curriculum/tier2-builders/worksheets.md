# Tier 2 Student Worksheets

---

## Worksheet 1 — Spot the Repetition

For each short program below, circle or underline the part that's
repeated, and write one sentence: what would you have to do if that
repeated part had a mistake in it?

```
print "Circle area: " + (3.14 * 5 * 5)
print "Circle area: " + (3.14 * 8 * 8)
print "Circle area: " + (3.14 * 2 * 2)
```

---

## Worksheet 2 — Your First `sub`

1. Type and run:
   ```
   sub greet()
       print "Hello there!"
       print "Welcome to BARE."
   end

   greet()
   greet()
   ```
2. Write your own `sub` (no parameters) that prints a 3-line message, and
   call it twice.
3. **Predict, then run**: what happens if you delete the last `greet()`
   call from question 1 — do the `print` lines inside `greet` still run?

---

## Worksheet 3 — `sub`s with Parameters

1. Type and run:
   ```
   sub greet(name)
       print "Hello, " + name + "!"
   end

   greet("Ada")
   greet("Grace")
   ```
2. Add a second parameter so it also greets by a title (e.g., "Hello,
   Captain Ada!").
3. Write a `sub` with two number parameters that prints their product.

---

## Worksheet 4 — `return`

1. Type and run:
   ```
   sub to_celsius(fahrenheit)
       return (fahrenheit - 32) * 5 / 9
   end

   print to_celsius(212)
   print to_celsius(32)
   ```
2. Write a `sub` called `average` that takes two numbers and returns
   their average. Call it and print the result.
3. **Predict, then run**: what does this print?
   ```
   sub square(n)
       return n * n
   end

   print square(3) + square(4)
   ```

---

## Worksheet 5 — Scope

For each program, find the line that will cause a runtime error, and
rewrite the `sub` so it works correctly (hint: pass in what's missing as
a parameter).

```
score = 95

sub show_score()
    print score
end

show_score()
```

```
tax_rate = 0.08

sub total_with_tax(price)
    return price + (price * tax_rate)
end

print total_with_tax(20)
```

---

## Worksheet 6 — Lists

1. Type and run:
   ```
   colors = ["red", "green", "blue"]
   print colors
   print colors[0]
   print colors[1]
   print colors[2]
   ```
2. Make a list of your 5 favorite things and print the 1st, 3rd, and 5th
   items using their index.
3. **Predict, then run**: what error do you get from `colors[3]` on the
   3-item list above? Why?

---

## Worksheet 7 — Growing and Looping

1. Type and run:
   ```
   scores = [88, 92, 75]
   append(scores, 100)
   print scores
   print len(scores)

   i = 0
   while i < len(scores)
       print scores[i]
       i = i + 1
   end
   ```
2. Build a list of 4 numbers and write a loop that prints only the ones
   greater than 80.
3. Write a loop that adds up every number in a list and prints the total.

---

## Worksheet 8 — Class Roster Project

Build a program with:
- [ ] A list of at least 5 names
- [ ] A matching list of at least 5 scores
- [ ] A `sub print_roster(names)` that prints every name
- [ ] A `sub average_score(scores)` that returns the average

*Extension*: a `sub highest_score(scores)` that returns the largest value
in the list.

---

## Worksheet 9 — Validation Loops

1. Type and run, trying both valid and invalid ages:
   ```
   age = num(input("Enter your age (0-120): "))
   while age < 0 or age > 120
       print "That's not a valid age."
       age = num(input("Enter your age (0-120): "))
   end
   print "Thanks!"
   ```
2. Write a validation loop that keeps asking for a password until it's at
   least 6 characters long (hint: `len()`).

---

## Worksheet 10 — `round`, `num`, `str`

1. Type and run:
   ```
   print round(3.14159, 2)
   print round(3.14159, 0)
   print round(2.5, 0)
   ```
2. Ask the user for a price with `input()`/`num()`, and print it rounded
   to 2 decimal places.
3. Build a fraction string like `"3/4"` from two number variables using
   `str()` and `+`.

---

## Worksheet 11 — Rock, Paper, Scissors

1. Type and run `examples/rock_paper_scissors.bare` (ask your teacher
   where to find it, or open it directly in the IDE).
2. Trace `beats("paper", "rock")` by hand — what does it return, and why?
3. *Extension*: add a loop so the game plays 3 rounds and reports how many
   rounds the player won.

---

## Worksheet 12 — Debug It

This program is supposed to print each student's name along with their
score, but it has a bug. Use a breakpoint, Step, and Variable Watch to
find it, then fix it. Write one sentence describing the bug before you
fix it.

```
sub print_all(names, scores)
    i = 0
    while i <= len(names)
        print names[i] + ": " + scores[i]
        i = i + 1
    end
end

names = ["Sam", "Lee", "Ada"]
scores = [88, 92, 75]
print_all(names, scores)
```

---

## Worksheet 13 — Recursion

1. Type and run:
   ```
   sub factorial(n)
       if n <= 1
           return 1
       else
           return n * factorial(n - 1)
       end
   end

   print factorial(5)
   ```
2. On paper, trace `factorial(4)` step by step — write out each call and
   what it returns, in order, ending with the final answer.
3. *Extension*: write a recursive `sub countdown(n)` that prints every
   number from `n` down to `1`.

---

## Worksheet 14 — Your Library

1. Pick a `sub` you wrote in an earlier lesson (Lesson 4's `average`,
   Lesson 8's `average_score`, or one of your own). Select it and use
   **Edit → Save Selection to Library**.
2. Start a brand-new blank program and call that `sub` by name. Confirm
   it works and that the console shows a "Loaded from your library"
   message.
3. Save two more `sub`s to your library, then write a short new program
   that uses all three together.

---

## Worksheet 15 — Capstone Plan

Write a short plan (this is turned in, not typed into the IDE) answering:
1. Which capstone are you building (Quiz Game, Rock-Paper-Scissors
   Tournament, or your own idea)?
2. What data will you store? List every variable and list you expect to
   need.
3. What `sub`s will you need, and what does each one do?
4. Write out, by hand, what a sample run of your program would look like
   — the exact lines it would print.

---

## Worksheet 16-17 — Capstone Build and Showcase

No worksheet — this is build and presentation time. Refer to your
Worksheet 15 plan as you build, and update it if your design changes.
Before showcasing, make sure you can answer:
1. What does your program do?
2. Which part are you most proud of?
3. What was the hardest bug, and how did you find it?

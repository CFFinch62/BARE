# Tier 1 Student Worksheets

Print or project one section per lesson. Type each program into the BARE
IDE and click **Run** to check your work.

---

## Worksheet 1 — Meet `print`

1. Type and run:
   ```
   print "My name is ___"
   ```
   (fill in your own name inside the quotes)
2. Write three more `print` lines: one about your favorite animal, one
   about your favorite food, one about your favorite game.
3. **Fix it**: this program has a mistake. Find it and fix it so it runs.
   ```
   print "This line is broken
   ```
4. Add a comment (starts with `#`) above one of your `print` lines
   explaining what it does.

---

## Worksheet 2 — Joining Strings

1. Type and run:
   ```
   print "I like " + "pizza" + " and " + "ice cream"
   ```
2. Join four strings of your own into one silly sentence using `+`.
3. Make a sentence that includes a quote mark inside it, using `\"`, like:
   ```
   print "My teacher said \"great job!\""
   ```
4. **Predict first, then run**: what do you think this prints?
   ```
   print 'hello'
   ```

---

## Worksheet 3 — Variables

1. Type and run:
   ```
   my_name = "___"
   print "Hi, I'm " + my_name
   ```
2. Make three variables: `favorite_color`, `favorite_number`, `favorite_animal`.
   Print a sentence using each one.
3. Change `favorite_color` to a different value partway through your
   program and print it both before and after the change.
4. **Predict first, then run**: what prints, `"Ada"` or `"Grace"`?
   ```
   name = "Ada"
   name = "Grace"
   print name
   ```

---

## Worksheet 4 — Numbers and Math

1. Type and run:
   ```
   a = 12
   b = 4
   print a + b
   print a - b
   print a * b
   print a / b
   ```
2. Write a program with two variables for a price and a discount amount,
   and print the price after the discount.
3. **Predict first, then run**: `print 7 / 2` — what do you expect?
4. **Predict first, then run**: `print 2 + 3 * 4` — is it `20` or `14`?

---

## Worksheet 5 — Mixing Words and Numbers

1. Type and run:
   ```
   pet_name = "Rex"
   pet_age = 3
   print pet_name + " is " + pet_age + " years old"
   ```
2. Write your own "About my pet" (real or made up) using at least one
   string and one number joined with `+`.
3. Add a second number fact (like number of legs, or favorite treats
   count) to the same sentence.

---

## Worksheet 6 — `input()`

1. Type and run:
   ```
   name = input("What's your name? ")
   print "Hello, " + name + "!"
   ```
2. Ask the user for two numbers using `input()` and `num()`, and print
   their sum. Use this pattern for each number:
   ```
   n = num(input("Enter a number: "))
   ```
3. **Find the bug**: this program crashes. Why? Fix it.
   ```
   age = input("How old are you? ")
   print age * 7
   ```
4. **Predict first, then run** — this one is trickier. Does it crash? If
   not, what does it actually print, and why isn't it the number you
   expected?
   ```
   age = input("How old are you? ")
   print age + 1
   ```

---

## Worksheet 7 — "About Me" Project

Build a complete program that:
- [ ] Asks for the user's name
- [ ] Asks for at least 3 more facts (mix of words and numbers)
- [ ] Prints a friendly summary sentence using everything you asked
- [ ] Uses at least one `num()` if you asked for a number

*Extension*: do some math with one of the numbers before printing it back
(example: "in 10 years you'll be ___").

---

## Worksheet 8 — `if`

1. Type and run, trying a few different ages:
   ```
   age = num(input("How old are you? "))
   if age >= 10
       print "You can join the big kids' club!"
   end
   ```
2. Write an `if` that prints a message only when a typed-in number is
   greater than 100.
3. **Predict first, then run**: with `age = 5`, does anything print?

---

## Worksheet 9 — `if` / `else`

1. Type and run with a few different scores:
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
2. Build your own 3-outcome nested `if`/`else` (weather, bedtime, allowance
   — your choice).
3. **Predict first, then run**: what happens if `score` is exactly `90`?

---

## Worksheet 10 — Comparing Things

1. Type and run each of these with the same two variables, and predict
   each result before running:
   ```
   a = 8
   b = 3
   print a == b
   print a != b
   print a > b
   print a < b
   print a >= 8
   print a <= 3
   ```
2. **Find the bug**: this program doesn't do what it looks like it should.
   What's wrong?
   ```
   score = 100
   if score = 100
       print "Perfect!"
   end
   ```

---

## Worksheet 11 — `and`, `or`, `not`

1. Type and run with a few different combinations of answers:
   ```
   temp = num(input("Temperature: "))
   raining = input("Is it raining? (yes/no) ")
   if temp > 60 and raining == "no"
       print "Great day for a bike ride!"
   else
       print "Maybe stay in today."
   end
   ```
2. Rewrite it using `or` instead of `and` — how does the behavior change?
3. Write a condition using `not`.

---

## Worksheet 12 — `while` Loops

1. Type and run:
   ```
   count = 1
   while count <= 5
       print count
       count = count + 1
   end
   ```
2. Change it to count by 2s instead of 1s.
3. Change it to count backward from 5 to 1.
4. **Predict, very carefully, before running**: what happens if you delete
   the `count = count + 1` line? (Only run it if you know where the
   **Stop** button is!)

---

## Worksheet 13 — Loops with Input

1. Type and run:
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
2. Modify it to ask for 5 amounts instead of 3.
3. *Extension*: also print the average (total divided by count).

---

## Worksheet 14 — Debugging Practice

This program is supposed to print the numbers 1 through 5, but it has a
logic bug (it runs without crashing, but does the wrong thing). Set a
breakpoint on the first line inside the loop, use **Step** and **Variable
Watch**, and figure out what's wrong. Write down what you find *before*
fixing it.

```
count = 0
while count <= 5
    count = count + 1
    print count
end
```

---

## Worksheet 15 — Randomness

1. Type and run several times:
   ```
   print random(1, 10)
   ```
2. Write a program that picks a random number 1-6 (like a die) and prints
   whether it's "high" (4-6) or "low" (1-3).
3. Combine `random` with `input` and `if`: ask the player to guess a
   number 1-10, and tell them if they're right.

---

## Worksheet 16 — Capstone: Number Guessing Game

Build a complete program:
- [ ] Picks a secret number with `random(1, 100)`
- [ ] Lets the player guess repeatedly using a `while` loop
- [ ] After each wrong guess, says "too high" or "too low"
- [ ] When they win, prints how many guesses it took

*Extension*: limit the player to 6 guesses total, and print a "you lose,
the number was ___" message if they run out.

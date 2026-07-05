# Tier 3 Student Worksheets

---

## Worksheet 2 — Syntax Bootcamp Check

1. Write a program with a variable for a price, a variable for a
   quantity, and a `print` that reports the total cost.
2. What will this print?
   ```
   x = 5
   y = num("3")
   print x + y
   print "Total: " + (x + y)
   ```
3. What does `input()` always return, regardless of what the user types?

---

## Worksheet 3 — Truthiness Edge Cases

Predict the output of each, then run to check:
```
if 0
    print "A"
else
    print "B"
end
```
```
if ""
    print "A"
else
    print "B"
end
```
```
if not false
    print "A"
else
    print "B"
end
```
```
if null
    print "A"
else
    print "B"
end
```

---

## Worksheet 4 — Loop Patterns

Write one loop of each kind:
1. **Counting**: print every multiple of 3 from 3 to 30.
2. **Accumulating**: ask the user for 5 numbers and print their total.
3. **Validating**: keep asking for a number until the user enters one
   between 1 and 10.
4. **Sentinel**: keep asking for words until the user types `"stop"`,
   printing each word as it's entered.

---

## Worksheet 5 — Interfaces vs. Implementation

You're given these `sub` signatures and descriptions only — no
implementation. Write code that *calls* each one correctly (you can
invent reasonable variable names for the arguments):

- `is_valid_score(score)` — returns `true` if `score` is between 0 and 100.
- `letter_grade(score)` — returns a one-letter string grade for a score.
- `format_report(name, score, grade)` — returns a formatted report string.

Then write one sentence: what would change for you, as the caller, if the
*implementation* of `letter_grade` changed but its parameters and return
value stayed the same? (Nothing — that's the point of an interface.)

---

## Worksheet 6 — Lists as Data

Model a shopping cart:
- [ ] A list of item names
- [ ] A matching list of prices
- [ ] A `sub cart_total(names, prices)` that returns the sum of all prices
- [ ] A `sub print_receipt(names, prices)` that prints each item with its
      price, then the total

*Extension*: add a `sub apply_discount(prices, percent)` that returns a
new list with every price reduced by that percent.

---

## Worksheet 7 — Search, Min, Max

1. Type and run `examples/linear_search.bare`. Trace
   `find_index(names, "Grace")` by hand first — what index do you expect,
   and why?
2. Write `find_max(numbers)` from scratch: track a "best so far" value,
   updating it each time you see something bigger.
3. *Extension*: write `find_min(numbers)`, then a `sub` that returns
   both the min and max together (hint: a `sub` can only return one
   value — what would you return instead to get two answers out?).

---

## Worksheet 8 — Tracing Bubble Sort

1. Trace `examples/bubble_sort.bare` by hand on the list `[4, 1, 3, 2]`.
   Write out the list's contents after every full pass of the outer
   loop.
2. How many total passes did it take before the list was fully sorted?
3. *Extension*: modify the example so it sorts in descending order
   instead, and confirm on your traced example.

---

## Worksheet 9 — Recursion vs. Iteration

1. Type and run `examples/factorial.bare`. Trace `factorial(5)`'s full
   call stack on paper.
2. Type and run `examples/fibonacci.bare`. Note: this one is written as a
   loop, not recursion. Trace the values of `a`, `b`, and `next` for the
   first 5 iterations.
3. Now write a **recursive** version of Fibonacci:
   ```
   sub fib(n)
       if n <= 1
           return n
       else
           return fib(n - 1) + fib(n - 2)
       end
   end
   ```
   Confirm it produces the same sequence as the iterative version for the
   first several values.
4. Which version was easier to trace by hand? Which do you think does
   more total work for a large `n`, and why?

---

## Worksheet 10 — Building Your Library

1. Turn `examples/bubble_sort.bare`'s logic into a callable
   `sub sort(numbers)` that returns the sorted list.
2. Save `find_index`, `find_max` (from Worksheet 7), and your new `sort`
   `sub` to your personal library.
3. Open your library file directly (File → Open My Library) and add a
   one-line comment above each `sub` explaining what it does.
4. Write a short new program that uses at least two of your saved `sub`s
   together (for example: sort a list, then search it).

---

## Worksheet 11 — Debugging Log

This program has a bug. Find it using breakpoints/Step/Variable Watch,
and keep a written log as you go: what you tried, what you learned, in
order — before writing your fix.

```
sub average(numbers)
    total = 0
    i = 0
    while i < len(numbers)
        total = total + numbers[i]
        i = i + 1
    end
    return total / len(numbers) + 1
end

scores = [80, 90, 100]
print average(scores)
```

---

## Worksheet 12 — Design a Program (No Code Yet)

Pick a small program idea of your own (not your capstone yet — practice
first). Write, on paper:
1. A one-sentence restatement of what it does.
2. Every piece of data it needs, and its shape (single value? list?).
3. Every `sub` you'll need: name, parameters, what it returns — no
   implementation.
4. A sample run: the exact lines it would print, start to finish.

---

## Worksheet 16 — Code Review Checklist

Use this while reviewing a partner's capstone project:

- [ ] Can you tell what each `sub` does just from its name and
      parameters, without reading inside it?
- [ ] Is there any block of code repeated more than once that could be a
      `sub` instead?
- [ ] Are variable and `sub` names specific (`average_score`) rather than
      vague (`x`, `temp2`)?
- [ ] Can you find one input (a number, a list, a word) that might break
      this program? Try it.
- [ ] What is the one thing you'd change first if this were your code?

---

## Worksheet 17 — What Comes After BARE

Answer in a few sentences each:
1. Which BARE limitation (no `elseif`, no `try`/`catch`, no classes, no
   `for` loop, something else) are you most looking forward to *not*
   having in your next language, and why?
2. Name three things you learned this semester that you're confident will
   still be true in whatever language you learn next.

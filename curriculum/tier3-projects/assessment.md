# Tier 3 Assessment

Three checkpoints plus the capstone rubric and project spec.

---

## Checkpoint 1 — Foundations Review (after Lesson 6)

1. What will this print?
   ```
   if 0
       print "yes"
   else
       print "no"
   end
   ```
2. Name the four common loop patterns covered in Lesson 4.
3. What is the difference between a `sub`'s interface and its
   implementation?
4. What will this print?
   ```
   cart = ["book", "pen"]
   prices = [12, 2]

   sub cart_total(names, prices)
       total = 0
       i = 0
       while i < len(names)
           total = total + prices[i]
           i = i + 1
       end
       return total
   end

   print cart_total(cart, prices)
   ```

**Answer key**: 1. `yes` — only `false` and `null` are falsy in BARE, `0`
is truthy  2. Counting, accumulating, validating, sentinel  3. The
interface is what a caller needs to know (name, parameters, what it
returns); the implementation is the logic inside `sub ... end`, which the
caller shouldn't need to understand to use it correctly  4. `14`

---

## Checkpoint 2 — Algorithms and Recursion (after Lesson 9)

1. What does `find_index` return when the target isn't found in the list,
   and why that value specifically?
2. Trace by hand: after one full pass of bubble sort's outer loop over
   `[3, 1, 4, 1, 5]`, what does the list look like?
3. What are the two required parts of any correct recursive `sub`?
4. What will this print?
   ```
   sub factorial(n)
       if n <= 1
           return 1
       else
           return n * factorial(n - 1)
       end
   end

   print factorial(3)
   ```
5. Why is `examples/fibonacci.bare` written iteratively rather than
   recursively?

**Answer key**: 1. `-1` — a value that could never be a real index, so it
can't be confused with a valid result  2. `[1, 3, 1, 4, 5]` (the largest
remaining unsorted value, `5`, bubbles to the end)  3. A base case, and a
step that moves toward it with each recursive call  4. `6`  5. It avoids
recomputing the same values repeatedly and avoids a very deep chain of
calls — it's more efficient for the same result.

---

## Checkpoint 3 — Design and Debugging (after Lesson 12)

1. List the four steps of the design process from Lesson 12, in order.
2. What's the difference between commenting on a peer's code's *clarity*
   versus commenting on personal style preference, and why does code
   review focus on the former?
3. Describe, in your own words, the "reproduce, isolate, hypothesize,
   test, fix" debugging process.
4. Why is it better to implement and test one `sub` at a time rather than
   writing an entire multi-`sub` program before running it once?

**Answer key**: 1. Restate the problem; list the data and its shape; list
`sub` signatures before implementing them; sketch a sample run  2.
Clarity is about whether the code communicates what it does to another
reader; style preference is subjective taste — review focuses on clarity
because that's what actually affects whether the code is maintainable
3. Confirm the bug happens reliably; narrow down which part of the
program causes it; form a specific guess about the cause; check that
guess against what's actually true (e.g., with Variable Watch); only then
change the code  4. Because when several untested `sub`s interact, a bug
could be in any of them, or in how they interact — testing incrementally
means a new bug almost always comes from the piece you just added.

---

## Capstone Project Spec

Students choose one:

- **Text adventure game** — a set of rooms as data (e.g., a list of room
  names, or names + descriptions as parallel lists), a "current room"
  variable, a `sub` to describe the current room, and a `sub` to handle a
  typed command (movement, at minimum).
- **Simulation** — repeated random events tracked over many trials (dice
  statistics, a simple spread/growth model, a randomized game played many
  times with results tallied).
- **Data processing tool** — a list of records (built in or entered via
  `input()`), with `sub`s to search, sort, and summarize (e.g., average,
  min/max) the data.
- **Student's own proposal**, approved by the teacher.

**Minimum bar for any option**: at least 3 `sub`s with parameters and
return values, at least one list used meaningfully, and at least one
algorithm idea from Lessons 7-9 (search, sort, min/max, or recursion) used
somewhere in the logic — even a simple, adapted version.

## Capstone Rubric

Score each category 0-4.

| Category | 0-1 | 2 | 3 | 4 |
|---|---|---|---|---|
| **Correctness** | Doesn't run, or core requirements unmet | Runs, core requirements met with minor bugs in uncommon cases | Runs correctly for all normal cases | Also correctly handles at least one edge case (invalid input, empty list, boundary value) |
| **Design** | No evidence of planning; `sub`s added ad hoc as bugs appeared | A plan existed but the final program deviates from it without clear reason | Final program matches a sensible plan: clear data shapes, `sub`s with focused single purposes | Design also anticipated and cleanly accommodated a change or extension during building |
| **Algorithmic content** | No search/sort/recursion/min-max logic present where the project calls for it | Present but copied with minimal adaptation and little understanding shown | Present, adapted to the project's specific needs, and the student can explain how it works | Student can also explain a tradeoff involved (e.g., why this approach over an alternative) |
| **Code quality** | Significant repeated logic; unclear names throughout | Some repetition or unclear naming remains | Clear names, repeated logic factored into `sub`s, reasonably organized | Also reflects incorporation of peer review feedback from Lesson 16 |
| **Explanation** | Cannot describe how their own code works | Can describe what it does but not why it's structured that way | Can walk through the design, explain each `sub`'s role, and describe the hardest bug and how it was found | Can also articulate what they'd do differently with more time, showing genuine reflection |

A student averaging 3+ across all five categories has met the tier's
goal and is ready to carry these skills into any general-purpose
language.

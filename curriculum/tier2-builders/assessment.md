# Tier 2 Assessment

Three checkpoints plus the capstone rubric.

---

## Checkpoint 1 — `sub`s and Scope (after Lesson 5)

1. What will this print?
   ```
   sub square(n)
       return n * n
   end

   print square(4)
   print square(4) + 1
   ```
2. What's the difference between a `sub` that uses `print` and one that
   uses `return`?
3. This program crashes. Which line, and why?
   ```
   count = 10

   sub show_count()
       print count
   end

   show_count()
   ```
4. How would you fix the program in question 3 so it works?
5. True or False: BARE has a `global` keyword that lets a `sub` see
   outside variables if you need it to.

**Answer key**: 1. `16` then `17`  2. A `sub` using `print` displays
something directly and gives nothing back to use later; a `sub` using
`return` hands a value back so it can be stored, printed, or used in
another expression  3. The `print count` line inside `show_count`,
because `count` is not defined inside the `sub`'s scope — a `sub` cannot
see outside variables  4. Pass `count` in as a parameter:
`sub show_count(count) ... end`, called as `show_count(count)`
5. **False** — there is no `global` keyword; a `sub` can only access
what's passed in as a parameter.

---

## Checkpoint 2 — Lists (after Lesson 8)

1. What will this print?
   ```
   pets = ["cat", "dog", "fish"]
   print pets[0]
   print pets[2]
   ```
2. What will `pets[3]` do, given the list above?
3. What will this print?
   ```
   nums = [1, 2, 3]
   append(nums, 4)
   print len(nums)
   ```
4. Write a loop (using `while`) that prints every item in a list called
   `names`.
5. Why does a loop condition like `i < len(names)` work for a list of any
   size, instead of hardcoding a number?

**Answer key**: 1. `cat` then `fish`  2. Runtime error — index out of
range, since the list only has indexes 0, 1, 2  3. `4`  4.
```
i = 0
while i < len(names)
    print names[i]
    i = i + 1
end
```
5. Because `len(names)` always reflects the list's actual current size,
so the loop keeps working correctly even if the list grows or shrinks.

---

## Checkpoint 3 — Recursion and the Library (after Lesson 14)

1. What will this print?
   ```
   sub factorial(n)
       if n <= 1
           return 1
       else
           return n * factorial(n - 1)
       end
   end

   print factorial(4)
   ```
2. What is a "base case," and what would happen to `factorial` without
   one?
3. If you save a `sub` called `average` to your library, then write a
   brand-new program that also defines its own `sub average(...)`, which
   one runs when you call `average(...)` in that new program?
4. What line does the IDE print to the console when it loads functions
   from your library?
5. Where does the personal library file live on disk?

**Answer key**: 1. `24`  2. The base case is the condition that stops the
recursion from calling itself again (here, `n <= 1`); without it,
`factorial` would call itself forever until the program errors out
3. The program's own `sub average(...)` — a `sub` defined in the current
program takes priority over one from the library with the same name
4. `Loaded from your library: ...` (naming the functions it found)
5. `~/.config/bare_ide/user_library.bare` (on Linux/macOS).

---

## Capstone Rubric

Score each category 0-3.

| Category | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Correctness** | Doesn't run, or core feature missing entirely | Runs but a core feature is broken or gives wrong results in common cases | Works correctly for the project's core requirements (scoring, tournament logic, or the student's own approved spec) | Also handles at least one edge case cleanly (e.g., invalid input, empty list) |
| **Use of `sub`s and lists** | No `sub`s or lists used where they clearly should be | At least one `sub` and one list, but used superficially (e.g., a `sub` with no parameters where parameters would clearly help) | At least two `sub`s with parameters/return values, and at least one list used meaningfully in the program's logic | Also uses a `sub` saved from (or intended for) the personal library |
| **Code organization** | Logic is a tangle of copy-pasted blocks | Some repetition remains that a `sub` could have removed | Repeated logic is factored into `sub`s; variable and `sub` names are clear | Also cleanly separates "getting input," "computing," and "printing results" into distinct parts |
| **Explanation** | Can't describe what their own code does | Can describe *what* it does but not *why* it's built that way | Can walk through the program's `sub`s and explain both what each does and why | Can also explain the hardest bug and how the debugger (breakpoints/Step/Variable Watch) helped find it |

A student scoring 2+ across all four categories has met the tier's goal
and is ready for Tier 3.

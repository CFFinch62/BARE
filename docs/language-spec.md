# The BARE Language

BARE — **B**arely **A**dequate **R**untime **E**nvironment — is a small
procedural language built to teach the ideas underneath every other
language, without the syntax noise most languages accumulate over time.

The whole language fits on one screen: **11 keywords**, **one numeric
type**, **one loop**, **one way to define a reusable block of code**. If
you already know some other language, you can probably read every example
in this document without help. If BARE is your first language, everything
you need is written down here — nothing is assumed.

BARE programs only run inside the **BARE IDE** — there's no separate
command you type in a terminal. If you haven't opened the IDE yet, see
[user-guide.md](user-guide.md) first.

---

## 1. A first program

```
print "Hello, world!"
```

Type that into the editor and click **Run**. `print` is a keyword — not a
function you call with parentheses — followed by whatever expression you
want written to the console.

```
name = "Ada"
print "Hello, " + name + "!"
```

`+` between two strings joins them. There's no `printf`-style template
syntax to learn — string-building is just `+`.

---

## 2. Values

Every value in BARE is one of five kinds:

| Kind | Examples | Notes |
|---|---|---|
| Number | `5`, `3.14`, `-2` | One numeric type — no separate "integer" vs "decimal." `5` and `5.0` are the same value. |
| String | `"hello"` | Double quotes only. `'hello'` is a syntax error. |
| Boolean | `true`, `false` | Values, not keywords — same category as a number literal. |
| Null | `null` | What a variable holds before you assign anything meaningful — see §4. |
| List | `[1, 2, 3]` | Zero-indexed, can hold a mix of types, grows with `append()`. |

Strings support two escape sequences: `\"` for a literal quote inside a
string, and `\n` for a newline.

---

## 3. Variables

There's no `var`, `let`, or type declaration. The first time you assign to
a name, it exists:

```
score = 0        # score now exists, holds the number 0
score = "high"   # same variable — now holds a string instead
```

This is **dynamic typing**: a variable's type is whatever its current value
is, and it can change on the next assignment. There's no way to declare
"this variable must always be a number" — if you need that discipline,
write it into your own logic (or that's a feature of some *other*
language you'll meet later).

A variable that's never been assigned doesn't exist yet — reading it is a
runtime error (`'x' is not defined`), not `null`. `null` is a value you
assign or get back explicitly (e.g. a sub that returns nothing — see §6).

---

## 4. Operators

```
Arithmetic:   +  -  *  /  %  ^
Comparison:   ==  !=  <  >  <=  >=
Logical:      and  or  not
Assignment:   =
Indexing:     [ ]
```

`%` is remainder (`7 % 3` is `1`). `^` is exponent (`2 ^ 10` is `1024`).

**Precedence**, highest to lowest — the same order you'd guess from math
class, plus indexing/grouping binding tightest and `or` binding loosest:

| Precedence | Operators |
|---|---|
| 1 (tightest) | `( )` grouping, `[ ]` indexing |
| 2 | `^` (right-associative: `2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)`) |
| 3 | unary `-` |
| 4 | `*` `/` `%` |
| 5 | `+` `-` |
| 6 | `==` `!=` `<` `>` `<=` `>=` |
| 7 | `not` |
| 8 | `and` |
| 9 (loosest) | `or` |

**String + number** is a special case: `+` auto-converts a number to its
string form when the other side is a string, since `"Total: " + total` is
one of the most common things a beginner program does:

```
print "Total: " + 42        # "Total: 42" — the number becomes a string
```

Every *other* mix of types with an arithmetic operator is a runtime error
— `"5" - 1` does not guess that you meant the number 5. If you have a
string that holds a number and you want to do math with it, convert it
explicitly with `num()` (§8).

---

## 5. Truthiness

Only `false` and `null` are "falsy." Everything else — including `0` and
`""` (empty string) — is truthy:

```
if 0
    print "this DOES print"    # 0 is truthy in BARE!
end
```

This is different from most C-family languages on purpose. The usual
"`if 0` is false" rule surprises almost every beginner at least once;
BARE just doesn't have that rule. If you want to check "is this number
zero," write `if x == 0`, which says exactly what you mean.

---

## 6. Control flow

### if / else

```
if score >= 90
    print "A"
else
    if score >= 80
        print "B"
    else
        print "C or below"
    end
end
```

Notice there's no `elseif`. Every `if` needs its own `end`, so chaining
comparisons nests you one level deeper each time. This is deliberate —
see §10 — but if the nesting bothers you, that discomfort is itself the
lesson: you're feeling the exact problem `elseif` was invented to solve.

`else` is optional; a bare `if ... end` with no `else` is fine.

### while

BARE has exactly one loop. There's no `for`:

```
i = 0
while i < 5
    print i
    i = i + 1
end
```

Everything a `for` loop does, you write out by hand: initialize a counter,
check a condition, and remember to update the counter yourself. Forgetting
the update line gives you an infinite loop — which the IDE can stop for
you (see [user-guide.md](user-guide.md)) while you fix the bug.

### end

One keyword closes whatever block is currently open — `if`, `while`, or
`sub`. The parser tracks which block an `end` closes by nesting, the same
way parentheses nest; `end` itself carries no information about *which*
kind of block it's closing.

---

## 7. Subs

A `sub` is BARE's one construct for reusable code — there's no separate
"function" vs. "procedure" distinction. A `sub` that never hits `return`
just implicitly gives back `null`:

```
sub greet(name)
    print "Hello, " + name
end

greet("Ada")     # prints "Hello, Ada", returns null (unused here)
```

```
sub square(x)
    return x * x
end

print square(5)     # 25
```

**Scope**: a sub cannot see or change variables from outside it — no
`global` keyword exists to reach out. Everything a sub needs comes in as a
parameter; everything it produces goes out via `return`:

```
total = 100

sub double(n)
    print total       # runtime error: 'total' is not defined
    return n * 2
end
```

This is the single strictest rule in the language, and it's intentional:
it forces you to think in terms of "what does this piece of code need, and
what does it hand back" — the core skill functions exist to teach — rather
than letting a sub quietly depend on whatever global state happens to be
lying around when it's called.

Subs can call themselves (recursion). Each call gets its own fresh, empty
scope:

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

**The IDE's personal library**: if you're running in the BARE IDE, any
subs you've saved to your personal library (see
[user-guide.md §9](user-guide.md#9-building-your-own-library)) are loaded
automatically before your program runs — calling one is no different from
calling a sub defined earlier in the same file; it's still just an ordinary
`sub`, called by name, with no new keyword or syntax. This is an IDE
convenience layered on top of the language, not a change to it: BARE itself
has no import statement, no modules, and no notion of more than one file.
[`libraries/`](../libraries/) has ready-made subs — string, math,
trigonometry, and more — written in plain BARE and meant to be copied into
this personal library rather than written from scratch.

---

## 8. Lists

```
scores = [88, 92, 75]
print scores[0]          # 88 — zero-indexed
scores[0] = 100           # mutate in place
append(scores, 60)        # grow: scores is now [100, 92, 75, 60]
print len(scores)         # 4
```

Reading or writing past the end of a list (`scores[99]`) is a runtime
error, not silently `null` or an auto-grow — BARE halts and tells you the
line number rather than letting a mistake pass quietly (see §9).

Lists can hold a mix of types (`[1, "two", true]` is valid), and there's no
separate "array" vs. "list" distinction to learn.

---

## 9. Errors

BARE has no `try`/`catch`. Any runtime error halts the program immediately
and prints one line:

```
Error on line 7: cannot add string and boolean
Error on line 12: list index 5 out of range (list has 3 elements)
Error on line 3: 'total' is not defined
```

That's the entire error surface — one line number, one message, no stack
trace. This is on purpose: BARE is teaching you to *prevent* bugs through
correct logic, not to *handle* them after the fact through exception
machinery — that's a lesson for a later, more advanced language. See
[user-guide.md](user-guide.md) for how the IDE displays these visually
(squiggles, highlighted lines) while you're editing and running.

---

## 10. Built-in functions

None of these are keywords — which means this table, unlike the
keyword list, could grow in a future version without changing the
grammar:

| Function | Description |
|---|---|
| `len(x)` | Length of a string or list |
| `append(list, value)` | Appends `value` to `list`, returns the (mutated) list |
| `input(prompt)` | Prints `prompt`, waits for the user to type a line, returns it as a string |
| `str(x)` | Converts any value to its string form |
| `num(x)` | Converts a string to a number — runtime error if the string isn't numeric |
| `random(min, max)` | Random integer in `[min, max]`, inclusive on both ends |
| `round(x, decimals)` | Rounds `x` to `decimals` decimal places (half-up, e.g. `round(2.5, 0)` is `3`) |
| `time()` | Seconds elapsed on a monotonic clock — call it twice and subtract to time code |

`time()` doesn't return a wall-clock timestamp, only a number that's
meaningful when you subtract an earlier reading from a later one:

```
start = time()
count = 0
while count < 1000000
    count = count + 1
end
elapsed = time() - start
print "That took " + str(elapsed) + " seconds"
```

`input()` always returns a **string**, even if the user typed digits — run
it through `num()` before doing arithmetic on it:

```
response = input("Your age: ")
age = num(response)
print "Next year you'll be " + str(age + 1)
```

---

## 11. Keyword reference (all 11)

| Keyword | Role |
|---|---|
| `print` | Write an expression's value to the console |
| `input` | Read a line of text (also usable as `input(prompt)`) |
| `if` | Start a conditional block |
| `else` | Alternate branch of an `if` |
| `end` | Close the nearest open `if`, `while`, or `sub` |
| `while` | Start a loop that repeats while its condition is truthy |
| `sub` | Define a reusable named block of code |
| `return` | Exit a `sub`, optionally handing back a value |
| `and` | Logical AND (short-circuits) |
| `or` | Logical OR (short-circuits) |
| `not` | Logical negation |

`true`, `false`, and `null` are **not** on this list — they're literals,
resolved as values exactly like a number literal, not control-flow words.

---

## 12. Example programs

### FizzBuzz

```
n = 1
while n <= 20
    if n % 15 == 0
        print "FizzBuzz"
    else
        if n % 3 == 0
            print "Fizz"
        else
            if n % 5 == 0
                print "Buzz"
            else
                print n
            end
        end
    end
    n = n + 1
end
```

### Recursion

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

### Lists

```
scores = [88, 92, 75]
append(scores, 100)

total = 0
i = 0
while i < len(scores)
    total = total + scores[i]
    i = i + 1
end

print "Average: " + str(total / len(scores))
```

### Interactive input

```
secret = random(1, 100)
guess = 0
attempts = 0

print "I'm thinking of a number between 1 and 100."

while guess != secret
    response = input("Your guess: ")
    guess = num(response)
    attempts = attempts + 1

    if guess < secret
        print "Too low!"
    else
        if guess > secret
            print "Too high!"
        else
            print "Correct! You got it in " + str(attempts) + " attempts."
        end
    end
end
```

More runnable examples live in [examples/](../examples/) — open any of
them directly in the IDE.

---

## 13. What's deliberately not here (and why)

Every one of these was left out on purpose, not forgotten:

| Missing feature | Why |
|---|---|
| `for` loop | `while` + a manual counter teaches loop mechanics directly instead of hiding them |
| `elseif` | Nested `if`/`else` gets ugly on purpose — that ugliness is what motivates `elseif` in languages that have it |
| Classes / objects | Out of scope; BARE is procedural only |
| `try` / `catch` | Errors halt; the lesson is prevention, not handling |
| Multiple return values | One `return`, one value — nothing to unpack |
| Modules / imports | No import syntax or multi-file programs — the IDE auto-loads your personal library's subs (§7) as a convenience, but that's an IDE feature, not a language one |
| String formatting (`%s`-style) | `+` concatenation only — no mini-language inside strings to memorize |
| `global` keyword | Forces you to pass values through parameters and returns |

If a future version of BARE adds any of these, it'll be because the
teaching goal changed, not because someone forgot the list.

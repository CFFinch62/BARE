# BARE Language Specification
### *Barely Adequate Runtime Environment*
**A minimal procedural teaching language — Fragillidae Software IDE Suite**

---

## 1. Design Philosophy

BARE exists to answer one question for a student: *what is the smallest set of ideas a real programming language actually needs?*

Every keyword in BARE had to justify its existence by making something otherwise impossible to express. Where a feature could be a library function instead of syntax, it is a function. Where one keyword could close multiple block types, it does. The result is a language with 11 reserved words, one numeric type, one loop construct, and one procedure construct.

This scarcity is intentional pedagogy, not a limitation apologized for. When BARE's `if`/`else` nesting gets ugly in place of `elseif`, that ugliness is a teaching moment: *here's why other languages added that feature.* Productive struggle is the point.

BARE is:
- **Interpreted** — no compilation step, immediate feedback
- **Dynamically typed** — no type declarations anywhere
- **Procedural only** — no classes, no objects, no inheritance
- **IDE-locked** — BARE programs only run inside the BARE IDE; there is no standalone CLI interpreter distributed separately

---

## 2. Reserved Words (11 total)

```
print   input   if   else   end
while   sub     return
and     or      not
```

No other identifier is reserved. `true`, `false`, and `null` are literals, not keywords — they are resolved as values, the same as a number literal.

---

## 3. Lexical Grammar

### 3.1 Comments
```
# this is a comment, runs to end of line
```

### 3.2 Identifiers
```
identifier ::= letter (letter | digit | "_")*
letter     ::= "a".."z" | "A".."Z"
```
Case-sensitive. `count` and `Count` are different variables.

### 3.3 Literals

| Type | Example | Notes |
|---|---|---|
| Number | `5`, `3.14`, `-2` | Single numeric type, no int/float distinction |
| String | `"hello"` | Double-quoted only, no single-quote strings |
| Boolean | `true`, `false` | Literals, not keywords |
| Null | `null` | Default value of an unassigned variable |
| List | `[1, 2, 3]` | Zero-indexed, heterogeneous elements allowed |

### 3.4 Operators

```
Arithmetic:   +  -  *  /  %  ^
Comparison:   ==  !=  <  >  <=  >=
Logical:      and  or  not
Assignment:   =
Indexing:     [ ]
```

---

## 4. Grammar (EBNF)

```ebnf
program     ::= statement*

statement   ::= assignment
              | print_stmt
              | if_stmt
              | while_stmt
              | sub_def
              | return_stmt
              | call_stmt

assignment  ::= identifier "=" expression
print_stmt  ::= "print" expression
return_stmt ::= "return" expression?
call_stmt   ::= identifier "(" arg_list? ")"

if_stmt     ::= "if" expression NEWLINE
                statement*
                ("else" NEWLINE statement*)?
                "end"

while_stmt  ::= "while" expression NEWLINE
                statement*
                "end"

sub_def     ::= "sub" identifier "(" param_list? ")" NEWLINE
                statement*
                "end"

param_list  ::= identifier ("," identifier)*
arg_list    ::= expression ("," expression)*

expression  ::= or_expr
or_expr     ::= and_expr ("or" and_expr)*
and_expr    ::= not_expr ("and" not_expr)*
not_expr    ::= "not" not_expr | comparison
comparison  ::= additive (("==" | "!=" | "<" | ">" | "<=" | ">=") additive)*
additive    ::= multiplicative (("+" | "-") multiplicative)*
multiplicative ::= unary (("*" | "/" | "%") unary)*
unary       ::= "-" unary | power
power       ::= primary ("^" unary)?
primary     ::= NUMBER | STRING | "true" | "false" | "null"
              | identifier
              | identifier "[" expression "]"
              | identifier "(" arg_list? ")"
              | "[" arg_list? "]"
              | "(" expression ")"
```

---

## 5. Semantics

### 5.1 Variables
No declaration syntax exists. First assignment creates the variable in the current scope.
```
x = 5          # creates x
x = "now text" # same variable, new type — dynamic typing
```

### 5.2 Scope
- Global scope: the top level of the program.
- Sub scope: each `sub` call gets its own local scope. Subs **cannot** see or modify global variables directly — no `global` keyword exists in v1. This is deliberate: it forces students to pass values in as parameters and out via `return`, rather than reaching through scope walls.

### 5.3 Truthiness
Only `false` and `null` are falsy. Everything else — including `0` and `""` — is truthy. This is a deliberate departure from C-family convention, chosen because it removes a common beginner surprise ("why did `if 0` fail?").

### 5.4 The `end` keyword
`end` closes whichever block is currently open (`if`, `while`, or `sub`). It carries no information about which block it closes — the parser tracks that via a block stack. This is the single biggest keyword-economy decision in BARE.

### 5.5 Subs and `return`
A `sub` that never executes `return` implicitly returns `null` when it falls off the end. There is no distinction between "function" and "procedure" — one construct, one rule.

Subs support recursion — a sub may call itself, and its local scope is freshly created per call, exactly as it would be in any real language.

### 5.6 Lists
- Zero-indexed: `mylist[0]` is the first element.
- Mutable in place: `mylist[0] = 99` is valid.
- No fixed size; growth happens via the `append()` builtin.
- Out-of-range access halts the program with a runtime error (see §7).

### 5.7 Type Coercion
- `+` on two strings concatenates. `+` on a string and a number auto-converts the number to its string form (no explicit cast required for this one case, since it's the single most common beginner operation: `print "Total: " + total`).
- All other mixed-type arithmetic (e.g. `"5" - 1`) is a runtime error — BARE does not guess in ambiguous cases.

---

## 6. Operator Precedence (highest to lowest)

| Precedence | Operators |
|---|---|
| 1 (highest) | `()` grouping, list indexing `[ ]` |
| 2 | `^` (exponent, right-associative) |
| 3 | unary `-` |
| 4 | `*` `/` `%` |
| 5 | `+` `-` |
| 6 | `==` `!=` `<` `>` `<=` `>=` |
| 7 | `not` |
| 8 | `and` |
| 9 (lowest) | `or` |

---

## 7. Error Model

BARE has no `try`/`catch`. A runtime error halts execution immediately and prints a single-line diagnostic to the console pane:

```
Error on line 7: cannot add string and boolean
Error on line 12: list index 5 out of range (list has 3 elements)
Error on line 3: 'total' is not defined
```

This is intentional: the language teaches students to *prevent* errors through correct logic, not to *swallow* them through exception handling — a topic for a later, more advanced language.

---

## 8. Built-in Functions

These are ordinary callable names, not keywords, so this list can grow without touching the grammar.

| Function | Description |
|---|---|
| `len(x)` | Length of a string or list |
| `append(list, value)` | Appends value, returns the modified list |
| `input(prompt)` | Prints prompt, reads a line, returns as string |
| `str(x)` | Converts any value to its string form |
| `num(x)` | Converts a string to a number (runtime error if not numeric) |
| `random(min, max)` | Random integer in `[min, max]` inclusive |

---

## 9. Deliberately Omitted Features

| Feature | Rationale |
|---|---|
| `for` loop | `while` + manual counter teaches loop mechanics directly |
| `elseif` | Nested `if`/`else` — the resulting ugliness is itself instructive |
| Classes / OOP | Out of scope by design; procedural only |
| Try/catch | Errors halt; teaches prevention over handling |
| Multiple return values | One `return`, one value — no tuple unpacking to learn |
| Modules / imports | Single-file programs only; scaling is a later language's lesson |
| String formatting (`%s`-style) | `+` concatenation only — no mini-language to memorize |
| `global` keyword | Forces parameter-passing discipline in subs |

---

## 10. Example Programs

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

### Recursion (factorial)
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

---

## 11. Reserved for Future Versions (not in v1)

Explicitly out of scope for the initial release, but noted so an agent picking up this spec later doesn't reinvent conflicting syntax:

- `for` as sugar over `while` (once counting loops are internalized)
- `global` keyword for explicit scope-crossing
- File I/O builtins
- A second collection type (dictionary/map)

---

*Document version 1.0 — Fragillidae Software IDE Suite*

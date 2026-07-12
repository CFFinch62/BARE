# libraries/

Nine `.bare` files that build "missing" functionality — string manipulation,
math, trigonometry, dictionaries, sorting, list utilities, number
formatting, validation, console text UI — entirely out of BARE itself: 11
keywords, one loop, one collection type, and
[8 builtins](../docs/language-spec.md#10-built-in-functions). No Python, no
new interpreter code, nothing outside the language a student is learning.

That's the point of this folder. BARE doesn't have `sqrt()`, `sort()`,
`split()`, or a dictionary type — so each file below is a demonstration that
you don't strictly need them *built in* to get the result, just more code and
a clear head. `math_lib.bare`'s `math_sqrt` is Newton's method, worked out by
hand with a `while` loop; `data_lib.bare`'s dictionary is a plain list of
`[key, value]` pairs with a linear scan standing in for a hash table. It's
also, deliberately, the argument *for* richer languages: once you've written
`math_sqrt` yourself, `Math.sqrt()` stops looking like magic and starts
looking like a shortcut someone built for you after solving this exact
problem.

## The files

| File | Prefix | What it adds |
|---|---|---|
| [string_lib.bare](string_lib.bare) | `str_` | Reverse, upper/lower/title case, substring, search, trim, split/join, padding, repeat, replace, numeric check |
| [math_lib.bare](math_lib.bare) | `math_` | abs/sign/clamp, floor/ceil, sqrt (Newton's method), gcd/lcm, primality, factorial, max/min/sum/average/median |
| [trig_lib.bare](trig_lib.bare) | `trig_` | sin/cos/tan, asin/acos/atan/atan2, exp, natural log (ln), sqrt, deg/rad conversion, pi/e — all via Taylor series with range reduction |
| [data_lib.bare](data_lib.bare) | `dict_` / `set_` | A dictionary and a set, both built from BARE's one collection type: the list |
| [sort_lib.bare](sort_lib.bare) | `sort_` | Bubble, selection, and insertion sort; linear and binary search |
| [list_lib.bare](list_lib.bare) | `list_` | contains, index_of, count, slice, remove_at, insert_at, reverse, concat, unique |
| [format_lib.bare](format_lib.bare) | `format_` | Zero-padding, thousands separators, binary/hex conversion, Roman numerals, ordinals (1st, 2nd, 3rd...) |
| [validate_lib.bare](validate_lib.bare) | `valid_` | is-numeric, is-alpha, is-alnum, is-upper, is-lower, is-palindrome, is-leap-year, in-range |
| [tui_lib.bare](tui_lib.bare) | `tui_` | Boxes, banners, dividers, progress bars, numbered menus, aligned tables, and a busy-wait sleep — console output dressed up with plain strings (no color/cursor control — see the file header for why) |

Every sub is prefixed by its file so you can pull functions from several
files into the same personal library without name collisions — `str_reverse`
from `string_lib.bare` and a `sort_reverse`-style helper you write yourself
would never clash.

## How to use one of these functions in your own program

BARE has no `import` — see
[language-spec.md §13](../docs/language-spec.md#13-whats-deliberately-not-here-and-why)
for why that's on purpose. Two ways to get a function from here into a
program you're writing:

1. **Copy the whole file's worth of subs into your personal library.** Open
   the file here, select everything, paste it into **My Library** (or open
   `user_library.bare` directly via **File → Open My Library** and paste it
   in — see
   [user-guide.md §9](../docs/user-guide.md#9-building-your-own-library)).
   Every program you run afterward can call any of its functions by name,
   same as a builtin.
2. **Copy just the one `sub ... end` block you need**, the same way, if you
   don't want the whole file.

You can also just open one of these files directly in the IDE and read it —
running it does nothing (no `print`, no top-level statements, just `sub`
definitions), which is the same as running a personal library file as a
syntax check.

## Ground rules these files follow

- **Self-contained.** No file calls a sub defined in another file — copy
  `string_lib.bare` alone and every `str_*` function still works, without
  needing `math_lib.bare` too. Subs *within* the same file call each other
  freely (e.g. `str_to_title` calls `str_to_upper`).
- **No cheating with Python.** Every function is built from BARE's own
  operators and the same 8 builtins a student has access to — nothing here
  reaches outside the language.
- **Every function is hand-tested**, run through the real interpreter with
  known inputs and checked against expected output — not just read for
  plausibility. A couple of real bugs turned up doing this: `end` can't be
  used as a parameter name (it's a keyword) and an empty split delimiter
  used to infinite-loop, both fixed in the current files.
- **BARE's usual rules still apply.** No negative string/list indexing,
  indexing only past the end of a string or list is a runtime error, and a
  sub can only see its own parameters and locals — nothing global. If a
  function here takes a list and needs to "remove" something, it hands back
  a *new* list instead of shrinking the one you passed in (there's no
  builtin that can shrink a list), the same way `append()` is the only way
  BARE grows one.

# Problems 21-100: final status

BARE has no file I/O (no way to read an external file at all — see
docs/language-spec.md §10, the built-in table). A number of Project
Euler problems ship a companion data file (names.txt, a triangle, a
cipher, a set of Su Doku grids, etc.) that a normal solution reads at
runtime. In BARE the only option is to paste that data into the
program itself as a string or list literal, exactly the way
08_largest_product_in_a_series.bare, 11_largest_product_in_a_grid.bare,
13_large_sum.bare, and 18_maximum_path_sum.bare already do for their
(smaller) embedded data in problems 1-20.

Every problem from 21 to 100 was attempted, and all 80 now have a
working, independently-verified solution file — including all eleven
that needed an external data file pasted in:

| # | Problem | Data file |
|---|---|---|
| 22 | Names scores | names.txt (5,163 names) |
| 42 | Coded triangle numbers | words.txt (1,786 words) |
| 54 | Poker hands | poker.txt (1,000 hands) |
| 59 | XOR decryption | cipher.txt |
| 67 | Maximum path sum II | triangle.txt (100 rows) |
| 79 | Passcode derivation | keylog.txt (50 lines) |
| 81 / 82 / 83 | Matrix path sums (three variants) | matrix.txt (80x80 grid) |
| 89 | Roman numerals | roman.txt (1,000 numerals) |
| 96 | Su Doku | sudoku.txt (50 grids) |
| 98 | Anagramic squares | words.txt (reused) |
| 99 | Largest exponential | base_exp.txt (1,000 lines) |

## The one slow one: correct, and now confirmed to actually finish

60_prime_pair_sets.bare exists and is verified correct (its core logic
was checked against the problem's own {3,7,109,673}=792 four-prime
example at a small search limit before trusting it at the real scale),
but it is not really "solved" in the same sense as the other 99 —
it's a direct, line-for-line port of a hand-written Python reference
solution, kept specifically as a side-by-side comparison rather than
a "worked around what BARE lacks" example. Nothing about the algorithm
(sieve, trial-division primality, digit concatenation via arithmetic,
nested search for a matching quintet) is blocked by anything BARE is
missing. What BARE's design costs here is pure speed: the Python
original runs in about 29 seconds; run to completion in the BARE IDE,
this tree-walking-interpreter port took **2,279 seconds (38 minutes)**
— slow, and a real illustration of the interpreter-overhead cost, but
not the "order of HOURS" this doc originally guessed before anyone had
actually timed it. See the comment header in that file for the full
comparison, including two small differences from the original (no
dict, so it tracks a running best instead of collecting-then-
minimizing; and a latent sieve bug in the original that this port
fixes).

So: all 100 of the first 100 Project Euler problems have a correct,
independently-verified, working `.bare` file, and all 100 have now
been run to completion — problem 60 just takes 38 minutes instead of
seconds. See `../../../project_euler_performance.csv` (one level above
the BARE repo, alongside the other language ports) for the measured
time.

## Notable language-limitation workarounds along the way

A few of these needed more than "paste the data in" — they ran into an
actual BARE limitation and had to work around it:

- **No bignum type**: strings-as-numbers with hand-rolled add/multiply/
  subtract, used throughout (13, 16, 20, 25, 48, 55, 56, 57, 65, 66, 80,
  94, 97).
- **No sqrt()**: `x^0.5` (BARE's exponent operator accepts fractional
  exponents) plus a perfect-square check, used from problem 44 onward;
  problem 80 needed the actual DIGITS of a square root, so it uses the
  pencil-and-paper long-division method instead, entirely in bignum
  strings.
- **No log()**: problem 99 builds a natural log out of `x^(1/n) - 1`
  for a carefully chosen large n, using the same limit definition that
  makes `(1+1/n)^n` converge to e.
- **No bitwise operators at all**: problem 59's XOR cipher needed one
  built from scratch out of `%`, `/`, and comparisons.
- **No chr()**: also problem 59 — matching " the " in decrypted text is
  done as a numeric ASCII-code sequence, never as an actual string.
- **No sort**: problem 22 needed a real merge sort for 5,163 names;
  smaller sorts (54's 5-card poker hands) just use insertion sort.
- **No set/map/dict, only lists**: every "group items by a key" problem
  (49, 62, 90, 95, 98) uses a plain list of [key, [items...]] pairs,
  searched linearly.
- **Recursion depth**: BARE's interpreter is itself a Python program,
  and deep BARE recursion burns through Python's own stack limit long
  before a `while` loop at the same depth would even notice. 73 and 96
  both originally wanted straightforward recursion (a Stern-Brocot tree
  walk, and Su Doku backtracking) and were rewritten to use an explicit
  BARE list as a manual stack instead.

---
Final status: all 100 problems have a working, verified .bare file, and
all 100 have been run to completion. 99 run in a reasonable time; problem
60 is a deliberately-slow direct language-comparison port and took 38
minutes (2,279 seconds) — see above.

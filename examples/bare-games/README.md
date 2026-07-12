# bare-games/

BARE ports of games from [`examples/BASIC_Games/`](../BASIC_Games/) — the
classic *101 BASIC Computer Games* (Creative Computing / David Ahl, early
1970s-80s). The goal isn't nostalgia for its own sake: these games were
written against a language with real limits (no structured control flow,
line numbers, GOTO instead of loops), and BARE is a modern language with
its *own* real limits (no GOTO either, but also no globals-in-subs, no
GOSUB, no arrays-with-arbitrary-types-per-slot weirdness). Porting one to
the other is a genuine exercise in "how do I get this effect with what
I've actually got" — the same lesson [`libraries/`](../../libraries/) is
built around, applied to whole programs instead of individual functions.

See [PORT_STATUS.md](PORT_STATUS.md) for the full list of 109 distinct
games, which tier each falls in, and what's been ported so far.

## Conventions used across every port

These come up in nearly every file, so they're explained once here instead
of being re-explained in each game's header comment. Individual file
headers only note what's unusual about *that* game.

**Every file is self-contained.** No port calls a sub from `libraries/` —
if a game needs string padding or a square root, that logic is inlined
directly in the game file, the same way `examples/project-euler/` works.
This means you can open any single file and run it with nothing else
copied into your personal library first.

**Line numbers and GOTO don't exist in BARE, so control flow is
restructured, not translated line-by-line.** A BASIC pattern like:
```basic
200 PRINT "YOUR GUESS";
210 INPUT A
230 IF A=Y THEN 300
240 IF A>Y THEN 270
250 PRINT "TOO LOW.":GOTO 200
270 PRINT "TOO HIGH.":GOTO 200
300 PRINT "GOT IT!"
```
becomes a `while` loop with an explicit exit condition:
```
guess = -1
while guess != target
    guess = num(input("Your guess? "))
    if guess < target
        print "TOO LOW."
    end
    if guess > target
        print "TOO HIGH."
    end
end
print "GOT IT!"
```
For games with heavy, tangled GOTO (see PORT_STATUS.md's "tangle" rating),
this restructuring is most of the actual porting work — untangling 1970s
spaghetti into `while`/`if` is a legitimate, and sometimes non-obvious,
translation, not a mechanical find-and-replace.

**GOSUB doesn't share variables — BARE subs never do.** In BASIC, a
`GOSUB` subroutine can read and write every variable in the program. A
BARE `sub` sees only its own parameters. Every ported subroutine has its
inputs made explicit as parameters and its effect made explicit as a
return value — often the single biggest change from the original source.

**`PRINT ...;` (semicolon = stay on this line) becomes one `+`-built
string.** BARE's `print` always ends the line (see
[libraries/tui_lib.bare](../../libraries/tui_lib.bare)'s header for why —
same underlying constraint). Several BASIC lines that build up one visual
line via trailing semicolons collapse into a single `print` with
concatenation:
```basic
610 PRINT "GO ";
640 PRINT "SOUTH";
720 PRINT
```
becomes:
```
print "GO " + "SOUTH"
```

**`TAB(n)` becomes literal leading spaces.** BARE has no cursor/column
concept (again, see `tui_lib.bare`'s header). A title line like
`PRINT TAB(33);"HELLO"` becomes a string literal with 33 leading spaces
baked in. Where `TAB()` was used for tabular column alignment rather than
a one-off title, the port pads each field to a fixed width by hand
(build a string of the right number of spaces in a small loop) rather
than pulling in `tui_lib`, to keep the file self-contained.

**`RND` becomes `random()`.** BASIC's `RND(1)` returns a float in
`[0, 1)`, so idioms like `INT(100*RND(1))` (random integer in `[0, 99]`)
or `INT(6*RND(1)+1)` (random integer in `[1, 6]`) show up constantly.
BARE's `random(min, max)` is already an inclusive integer range, so these
usually get *simpler* in the port: `INT(6*RND(1)+1)` → `random(1, 6)`.
Watch the original's exact bounds when converting — an off-by-one here
silently changes the odds.

**Multi-value `INPUT X,Y` becomes two separate `input()` calls (or one
split by hand).** BARE's `input()` reads one line as one string; it has
no comma-parsing of its own. Most ports just ask twice
(`x = num(input("X? "))`, then `y = num(input("Y? "))`) since that's
clearer for a beginner than parsing a comma out of one line by hand.

**`LOG` used only for a "how many bits" trick doesn't need real log().**
A couple of games (`guess.bas`, `depthcharge.bas`) compute
`INT(LOG(N)/LOG(2))+1` purely to get "the number of times you can halve N"
— that's answered directly by a small counting loop (halve a copy of N
until it reaches 1, count the steps), no logarithm required. Games that
need *real* trigonometry or logarithms (physics/orbit simulations — see
PORT_STATUS.md's Tier 4) are deferred until a `trig_lib.bare` companion
library exists.

**Real-time delays (`FOR I=1 TO 2000:NEXT` used purely for pacing) are
dropped**, not ported. They controlled how fast text scrolled on a real
terminal; in an append-only console log they add nothing but a pause, and
BARE has no real sleep (see `tui_lib.bare`'s `tui_sleep` if a port
genuinely wants one — self-contained files inline the same busy-wait
instead of calling it).

**Flavor text and jokes are kept exactly as written**, including ones
that read as "illogical" out of context (e.g. `hello.bare`'s ending). The
original programs are frequently deadpan-absurd on purpose; that's the
game, not a bug to fix in translation.

**BARE's `[ ]` indexing doesn't chain.** `nodes[i][0]` is a parse error
(`expected newline after statement, got LBRACKET`) — only a bare variable
can be indexed, not the result of another index expression. Any game
using a list-of-lists (trees, records, grids-of-rows) needs the middle
step pulled into its own variable first:
```
node = nodes[i]      # one index on a variable — fine
print node[0]         # fine
print nodes[i][0]     # parse error — can't chain
```
This came up porting `animal.bare` (its decision tree is a list of
`["Q", question, yes_index, no_index]` / `["A", name]` nodes) and will
come up again on anything else with nested structure (Hexapawn's move
tables, Mastermind's guess history, grid-based board games).

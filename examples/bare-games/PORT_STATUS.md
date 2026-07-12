# Port status

109 distinct games identified in `examples/BASIC_Games/` (161 files, many
of which are duplicate/alternate ports of the same game). Tiers are a
starting estimate based on GOTO-tangle, size, and which BASIC features
each game leans on — expect some games to move tiers once we're actually
looking at the source up close.

**Status values:** `Ported` (in `bare-games/`, tested with scripted
input) · `Pending` · `Blocked` (needs a capability BARE doesn't have yet)
· `Skip` (not a standalone game, or non-runnable as archived).

---

## Tier 1 — straightforward (low GOTO tangle, no trig, mostly <100 lines)

| Game | Source file | Status |
|---|---|---|
| Hello | hello.bas | **Ported** |
| Guess | guess.bas | **Ported** |
| Hurkle | hurkle.bas | **Ported** |
| Hi-Lo | hi-lo.bas | **Ported** |
| Dice | dice.bas | **Ported** |
| Animal | animal.bas | **Ported** |
| Banner | banner.bas | Pending |
| Bounce | bounce.bas | **Ported** |
| Bulls and Cows | bullcow.bas | Pending |
| Bullseye | bullseye.bas | Pending |
| Bunny | bunny.bas | Pending |
| Buzzword | buzzword.bas | **Ported** |
| Calendar | calendar.bas | Pending |
| Change | change.bas | Pending |
| Chemist | chemist.bas | **Ported** |
| Chief | chief.bas | Pending |
| Depth Charge | depthcharge.bas | **Ported** |
| Diamond | diamnd.bas | **Ported** |
| Kinema | kinema.bas | **Ported** |
| Letter | letter.bas | **Ported** |
| Life | life.bas | Pending (prints each generation as a new frame, doesn't redraw in place) |
| Literary Quiz | litquiz.bas | Pending |
| Love | love.bas | Pending |
| Math Dice | mathd.bas | Pending |
| Mugwump | mugwump.bas | Pending (reuses the Newton's-method `math_sqrt` idea from `math_lib.bare`) |
| Name | name.bas | **Ported** |
| Nicomachus | nicomachus.bas | Pending |
| Number | number.bas | Pending |
| One Check | onecheck.bas | Pending |
| Pizza | pizza.bas | Pending |
| Poetry | poetry.bas | Pending |
| Reverse | reverse.bas | Pending |
| Rock Scissors | rockscissors.bas | **Ported** |
| Russian Roulette | russianroulette.bas | **Ported** |
| Stars | stars.bas | Pending |
| Synonym | synonym.bas | Pending |
| Train | train.bas | **Ported** |
| Trap | trap.bas | Pending |
| War | war.bas | Pending |
| Word | word.bas | Pending |

## Tier 2 — moderate (more GOSUB/DATA, medium tangle, ~100-250 lines)

| Game | Source file | Status |
|---|---|---|
| 23 Matches | 23matches.bas | Pending |
| Awari | awari.bas | Pending |
| Bagels | bagels.bas | Pending |
| Baseball | basbl1.bas | Pending |
| Batnum | batnum.bas | Pending |
| Bombardment | bombardment.bas | Pending |
| Bomber (WWII) | bombsaway.bas | Pending |
| Bowling | bowling.bas | Pending |
| Chomp | chomp.bas | Pending |
| Combat | combat.bas | Pending |
| Craps | craps.bas | Pending |
| Digits | digits.bas | Pending |
| Even Wins | evenwins.bas | Pending |
| Flip Flop | flipflop.bas | Pending (SIN/TAN/COS used only as a fake-PRNG trick — substitute `random()`) |
| Gomoko | gomoko.bas | Pending |
| Hammurabi | hammurabi.bas | Pending |
| Hangman | hangman.bas | Pending |
| Hexapawn | hexapawn.bas | Pending (iconic — the AI "learns" via a matchbox algorithm) |
| Hi-Q | highiq.bas | Pending |
| Horserace | horserace.bas | Pending |
| Life for Two | lifefortwo.bas | Pending |
| Lunar | lunar.bas | Pending (reuses `math_sqrt`) |
| Rocket | rocket.bas | Pending (reuses `math_sqrt`) |
| Ugly | ugly.bas | Pending |

## Tier 3 — big lifts (high tangle and/or 250+ lines)

| Game | Source file | Status |
|---|---|---|
| Acey Ducey | aceyducey.bas | Pending |
| Amazing (maze gen) | amazin.bas | Pending |
| Basketball | basket.bas | Pending |
| Battle | battle.bas | Pending |
| Bingo | bingo.bas | Pending |
| Blackjack | blkjac.bas | Pending (its lone `COS()` is a fake-PRNG trick, not real trig — substitute `random()`) |
| Boxing | boxing.bas | Pending |
| Bug | bug.bas | Pending |
| Bull/Bullfight | bullfight.bas | Pending |
| Can-Am | canam.bas | Pending |
| Checkers | checkr.bas | Pending |
| Civil War | civilwar.bas | Pending |
| Cube | cube.bas | Pending |
| Dogs | dogs.bas | Pending |
| Football | football.bas | Pending (use this or `fotbal.bas`, not `footbl.bas` — that PDP-11 port needs real trig; double check football.bas's own tangle before starting) |
| Fur Trader | furtrader.bas | Pending |
| Hockey | hockey.bas | Pending |
| King | king.bas | Pending |
| Mastermind | mastermind.bas | Pending |
| Monopoly | mnoply.bas | Pending (also needs its companion `mnopfl.bas` data-builder logic folded in) |
| Nim | nim.bas | Pending |
| Poker | poker.bas | Pending |
| Qubic | qubic.bas | Pending |
| Queen | queen.bas | Pending |
| Roulette | roulet.bas | Pending |
| Salvo | salvo.bas | Pending (reuses `math_sqrt`) |
| Slalom | slalom.bas | Pending |
| Slots | slots.bas | Pending |
| Space War | spcwar.bas | Pending (reuses `math_sqrt`) |
| Splat | splat.bas | Pending (reuses `math_sqrt`) |
| Stock Market | stock.bas | Pending |
| Super Star Trek | superstartrek.bas | Pending — **capstone candidate**: 425 lines but *low* GOTO tangle (GOSUB-structured, not spaghetti), so may port cleaner than its size suggests |
| Tic-Tac-Toe | tictactoe1.bas or tictactoe2.bas | Pending — do NOT use `tictac.bas` (see Skip list below) |
| Tower (Hanoi) | tower.bas | Pending |
| Weekday | weekday.bas | Pending |
| Yahtzee | yahtze.bas | Pending — **largest game in the set** (558 lines, 123 GOTO targets), stretch-goal capstone |

## Tier 4 — needs trig (now unblocked — `trig_lib.bare` exists)

`libraries/trig_lib.bare` now has sin/cos/tan/atan/atan2/exp/log, all
tested against Python's `math` module to 1e-8 (see
`../../libraries/README.md`). These games are ported the same
self-contained way as everything else — inline whatever `trig_lib`
functions each one needs directly into the game file, don't call across
to `libraries/`. Several also need `math_sqrt`'s Newton's-method approach
inlined too (marked below).

| Game | Source file | Needs |
|---|---|---|
| 3D Plot | 3dplot.bas | exp, sqrt (surface plot) |
| Boat | boat.bas | sin, cos, atan |
| Golf | golf.bas | tan, sqrt (trajectory) |
| Gunner | guner1.bas | sin (real artillery trajectory, not decorative) |
| Lem | rockt2.bas | sin, cos, sqrt |
| Orbit | orbit.bas | cos, sqrt (orbital mechanics) |
| Sine Wave | sinewave.bas | sin — literally the entire program |
| Target | target.bas | sin, cos (3-D targeting) |

All: Pending.

## Skip — not a standalone game, or non-runnable as archived

| File | Why |
|---|---|
| mnopfl.bas | Utility that builds Monopoly's data files; not a game itself (folded into the `mnoply.bas` port instead) |
| superstartrekins.bas | Instructions/title screen only, no game loop |
| tictac.bas | Ends with `CHAIN "DEMON "`, referencing an external program not present in this archive — use `tictactoe1.bas` or `tictactoe2.bas` instead |
| zoop.bas | Also ends with `CHAIN "DEMON "` (a save/wipe "easter egg" branch); the rest is a hardcoded Q&A matching raw ASCII codes typed at a specific 1970s terminal (`INPUT $A`), not a general input mechanic — not a standalone game |
| basic_syntax_evolution.html | Not a BASIC file |

---

## Notes for whoever picks this back up

- Conventions (GOTO→while, TAB()→spaces, self-contained files, etc.) are
  in [README.md](README.md) — read that before porting, not this file.
- When a game's tier turns out wrong once you're actually reading the
  source (a "Tier 1" that's secretly tangled, or a "Tier 3" that's
  simpler than its line count suggests), just move its row — this table
  is a plan, not a contract.
- Test every port with scripted stdin the way the pilot batch was tested
  (`printf '...' | PYTHONPATH=src python3 -m bare_core file.bare`), not
  just by reading the code. Games with hidden random targets can often be
  made deterministic for testing by choosing inputs that force the range
  down to one possibility (e.g. `guess.bare`'s pilot test used limit=1).
- Games with no quit path in the original (most of the simple ones) are
  intentionally infinite in the port too — that's a correct match to the
  original, not a bug. Testing them means accepting the process needs to
  be killed or stdin needs to run out, not that a clean exit exists.

## Where this stopped (2026-07-12)

Porting paused here by design, not because anything ran out: the ported
files in `bare-games/` are meant as **worked examples** of the porting
process, and everything still `Pending` is left as an open exercise for
a student to pick up and try on their own (extra credit, one game at a
time) rather than something this session needs to finish. `README.md`'s
conventions section plus the already-ported files are the reference
material for anyone doing that.

Ported so far: Hello, Guess, Hurkle, Hi-Lo, Dice, Animal, Bounce, Train,
Name, Buzzword, Letter, Russian Roulette, Chemist, Diamond, Depth
Charge, Rock Scissors, Kinema. Two Tier 1 games turned out gnarlier than
their tier suggested and were deliberately left for later/an ambitious
student rather than ported: **Banner** (a bitmap-font renderer, not a
text game) and **Bulls and Cows** (the computer runs its own
constraint-satisfaction AI to guess your number back).

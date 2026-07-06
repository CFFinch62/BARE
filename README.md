# BARE

**B**arely **A**dequate **R**untime **E**nvironment — a minimal procedural
teaching language with 11 reserved words, a single numeric type, one loop
construct, and one procedure construct.

BARE is part of the Fragillidae Programming Langauge Teaching Suite. It is **IDE-locked**:
there is no standalone interpreter — the editor, interpreter, and console
all live in one PyQt6 process.

![BARE IDE — editor with syntax highlighting and scope boxes, paused at a breakpoint with the Variable Watch panel open](docs/images/bare-ide-screenshot.png)

## Status

Feature-complete through Phase 6 of the implementation plan — core
interpreter, editor, syntax highlighting, threaded Run/Stop, step-debug
with breakpoints and Variable Watch, scope box coloring, and a Preferences
dialog — plus multi-file editor tabs and a file browser panel. See
[dev-docs/implementation-task-list.md](dev-docs/implementation-task-list.md)
for the full phase-by-phase history.

## Getting started

```bash
./setup.sh                    # creates venv, installs dev + ide extras
source venv/bin/activate
python -m pytest tests/ -v    # run the interpreter test suite
./run.sh                      # launch the IDE
```

To build a standalone executable (no Python install required to run it):

```bash
./build_release.sh            # installs PyInstaller extras, builds dist/bare-ide
```

## Documentation

| Doc | Audience | Covers |
|---|---|---|
| [docs/language-spec.md](docs/language-spec.md) | Anyone writing BARE programs | The full language: syntax, types, control flow, subs, builtins, examples |
| [docs/user-guide.md](docs/user-guide.md) | Anyone using the IDE | Editor tabs, the file browser, running/debugging programs, breakpoints, Preferences, the personal library |
| [curriculum/](curriculum/) | Teachers | A full K-12 learn-to-program curriculum built on BARE (see below) |
| [dev-docs/ARCHITECTURE.md](dev-docs/ARCHITECTURE.md) | Contributors | Component responsibilities, data flow, threading model |
| [dev-docs/TESTING_STRATEGY.md](dev-docs/TESTING_STRATEGY.md) | Contributors | Test pyramid, fixtures, how to run the suite |
| [dev-docs/BARE_language_spec.md](dev-docs/BARE_language_spec.md) | Contributors | The original design spec (grammar EBNF, rationale) this implementation was built from |
| [dev-docs/adding-a-builtin.md](dev-docs/adding-a-builtin.md) | Contributors | Step-by-step checklist for adding a new built-in function |

## Curriculum

[curriculum/](curriculum/) is a complete, three-tier learn-to-program
curriculum for classroom use, spanning roughly ages 8 to 18:

| Tier | Age / grade | Focus |
|---|---|---|
| [Tier 1 — BARE Beginnings](curriculum/tier1-beginnings/) | ~8-10 (grades 3-5) | Sequencing, variables, `print`/`input`, `if`/`else`, `while`, randomness |
| [Tier 2 — BARE Builders](curriculum/tier2-builders/) | ~11-13 (grades 6-8) | `sub`s and scope, lists, the full builtin set, debugging tools, the personal library |
| [Tier 3 — BARE Projects](curriculum/tier3-projects/) | ~14-18 (grades 9-12) | Algorithmic thinking, recursion, program design, refactoring, a capstone, and a bridge to other languages |

Each tier is a semester's worth of lesson plans, student worksheets, and
checkpoint quizzes/rubrics. Start with
[curriculum/teachers-guide.md](curriculum/teachers-guide.md) — it covers
classroom setup, BARE-specific student misconceptions worth knowing in
advance, and grading philosophy.

## Language quick reference

**11 keywords:** `print` `input` `if` `else` `end` `while` `sub` `return` `and` `or` `not`

**8 builtins:** `len(x)` `append(list, value)` `input(prompt)` `str(x)` `num(x)` `random(min, max)` `round(x, decimals)` `time()`

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

See [docs/language-spec.md](docs/language-spec.md) for the complete reference, or
[examples/](examples/) for runnable sample programs.

## Project layout

```
src/bare_core/   Lexer, parser, tree-walking interpreter — no GUI dependency
src/bare_ide/    PyQt6 IDE: editor, console, debugger, themes, settings
tests/           Unit + integration tests for bare_core (234 tests)
examples/        Sample .bare programs (FizzBuzz, factorial, lists, ...)
docs/            User-facing language spec and IDE user guide
curriculum/      K-12 learn-to-program curriculum: lesson plans, worksheets, assessments
dev-docs/        Design docs, implementation plan, architecture notes
installer/       PyInstaller spec (build_release.sh drives this)
```

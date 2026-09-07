# BARE Language — VS Code extension

Syntax highlighting, editor behaviours, snippets and one-key running for
[BARE](https://github.com/CFFinch62/BARE) (`.bare` files).

## Getting BARE

This extension highlights and runs `.bare` files — it does not bundle the
language. Get it from GitHub:

**<https://github.com/CFFinch62/BARE>**

BARE is free and open source under the **MIT License**, as is this extension.

```sh
git clone https://github.com/CFFinch62/BARE.git
cd BARE
./setup.sh                    # creates the venv and installs extras
./build_cli.sh                # builds dist/bare, the standalone runtime
cp dist/bare ~/.local/bin/bare
```

`build_cli.sh` is what this extension needs: a console runtime on your `PATH`.
`./run.sh` launches the IDE instead — see below for why you probably want both.

## The BARE IDE is still the main way in

BARE was built IDE-first: the editor, interpreter and console live in one
process, with scope-box colouring, step debugging, breakpoints and a Variable
Watch panel that this extension does not attempt to reproduce. If you are
learning BARE, or teaching from the curriculum, use the IDE.

This extension is for the other case — a `.bare` file open alongside the rest
of a project in VS Code — and it drives the **standalone runtime**, which
takes a filename and nothing else:

```sh
bare myprogram.bare
```

Set `bare.interpreterPath` if it is not on your `PATH`; the standalone runtime
installs to `~/.local/bin/bare`.

## What it does

**Syntax highlighting** for the whole language, which is not a large claim
here: BARE has **11 reserved words, 3 literal keywords and 7 builtins**. Each
group gets its own scope, `sub` definitions are scoped as definitions, and
string escapes are checked — `\n`, `\t`, `\\` and `\"` are the four the lexer
accepts, and anything else after a backslash is marked invalid.

Matching is case-sensitive, because the lexer compares the word as written:
`If` is an identifier, not a keyword.

**Editor behaviours** — `#` comment toggling, bracket matching, auto-closing
pairs, and indentation that follows BARE's block shape. Every block opens with
`if`, `while` or `sub` and closes with a bare `end` — there are no colons and
no `elif` — so indentation is a convention the editor maintains rather than
syntax, and folding is marker-based.

**Snippets** for the block forms plus the idioms BARE's small vocabulary makes
you write out by hand: a counted loop built from `while`, walking a string by
index, and reading a number through `num(input(...))`.

**Run** — `Ctrl+F5`, or the play button in the editor title bar.

**Problems panel** — a failing run's `Error on line N:` becomes a squiggle on
that line. Errors are cleared as soon as you edit the file.

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `bare.interpreterPath` | `bare` | Path to the standalone interpreter |
| `bare.saveBeforeRun` | `true` | Save before running |
| `bare.runInTerminal` | `true` | Run in a terminal so `input` works |

## Why there is no Check command

Every other extension in this suite has one, because every other language has a
parse-only mode. BARE's standalone runtime takes a filename and nothing else —
no flags — so the only way to surface an error is to run the program, and a
program that calls `input` would block a check forever.

Diagnostics therefore come from a real run. Turning `bare.runInTerminal` off
routes the run through an Output channel, which is what fills the Problems
panel; stdin is closed in that mode, so an `input` ends the program at once
rather than hanging.

If the standalone runtime grows a parse-only flag, a Check command is a small
addition here.

## Installing from source

```sh
cd editors/vscode
npx @vscode/vsce package
code --install-extension bare-language-0.1.0.vsix
```

## License

MIT — see [LICENSE](LICENSE).

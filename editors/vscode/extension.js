// BARE Language extension — the run command for .bare files.
//
// Syntax highlighting, editor behaviours and snippets are entirely
// declarative (package.json + the grammar + language-configuration.json);
// none of them need this file. Everything here exists only to run the
// standalone `bare` interpreter and turn its errors into entries in the
// Problems panel.
//
// There is deliberately no Check command. The standalone runtime takes a
// filename and nothing else -- no flags, no parse-only mode -- so the only
// way to surface an error is to run the program, and `input` would block a
// check forever. Diagnostics therefore come from a real run.

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

/** BARE reports `Error on line <n>: <message>`, or `Error: <message>` when it
 *  has no location (bare_core/errors.py: BareError.format). Neither names a
 *  file, so a located error is pinned to the file that was run and an
 *  unlocated one is left in the Output channel. */
const LOCATED_RE = /^Error on line (\d+):\s+(.*)$/;

let diagnostics = null;
let output = null;

function config() {
  return vscode.workspace.getConfiguration('bare');
}

function interpreter() {
  return config().get('interpreterPath', 'bare') || 'bare';
}

/** Quote a path for a shell command line (the terminal path). */
function shellQuote(p) {
  if (process.platform === 'win32') return `"${p}"`;
  return `'${String(p).replace(/'/g, `'\\''`)}'`;
}

async function activeBareDocument() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'bare') {
    vscode.window.showErrorMessage('BARE: no .bare file is active.');
    return null;
  }
  if (config().get('saveBeforeRun', true) && editor.document.isDirty) {
    await editor.document.save();
  }
  return editor.document;
}

/** Run in the integrated terminal — output appears live and `input` works.
 *  One reused terminal per workspace. */
function runInTerminal(doc) {
  let term = vscode.window.terminals.find((t) => t.name === 'BARE');
  if (!term) {
    term = vscode.window.createTerminal({
      name: 'BARE',
      cwd: path.dirname(doc.fileName),
    });
  }
  term.show(true);
  term.sendText(`${shellQuote(interpreter())} ${shellQuote(doc.fileName)}`);
}

/** Run as a child process — output goes to an Output channel and errors
 *  become squiggles in the editor via the Problems panel. */
function runInOutputChannel(doc) {
  if (!output) output = vscode.window.createOutputChannel('BARE');
  output.clear();
  output.show(true);

  const exe = interpreter();
  output.appendLine(`> ${exe} ${doc.fileName}`);
  output.appendLine('');

  const started = Date.now();
  const child = cp.spawn(exe, [doc.fileName], {
    cwd: path.dirname(doc.fileName),
  });

  let stderr = '';
  child.stdout.on('data', (d) => output.append(d.toString()));
  child.stderr.on('data', (d) => {
    const text = d.toString();
    stderr += text;
    output.append(text);
  });

  child.on('error', (err) => reportSpawnError(err, exe));

  child.on('close', (code) => {
    publishDiagnostics(doc, stderr);
    output.appendLine('');
    output.appendLine(
      `[exit ${code} in ${((Date.now() - started) / 1000).toFixed(2)}s]`
    );
  });

  // A program that calls `input` would otherwise wait forever on a pipe with
  // nothing behind it. Closing stdin makes it end at once instead.
  child.stdin.end();
}

function reportSpawnError(err, exe) {
  if (err.code === 'ENOENT') {
    vscode.window
      .showErrorMessage(
        `BARE: interpreter '${exe}' not found. Install the standalone runtime, or set bare.interpreterPath.`,
        'Open Settings'
      )
      .then((choice) => {
        if (choice === 'Open Settings') {
          vscode.commands.executeCommand(
            'workbench.action.openSettings',
            'bare.interpreterPath'
          );
        }
      });
  } else {
    vscode.window.showErrorMessage(`BARE: ${err.message}`);
  }
}

/** Turn `Error on line <n>: <message>` into an editor squiggle on the file
 *  that was run. An `Error: <message>` with no line carries no position, so it
 *  stays in the Output channel rather than being pinned to a wrong line. */
function publishDiagnostics(doc, stderr) {
  const items = [];

  for (const raw of stderr.split('\n')) {
    const m = LOCATED_RE.exec(raw.trim());
    if (!m) continue;

    // BARE reports 1-based lines and no column; underline the whole line.
    const lineNo = Math.max(0, parseInt(m[1], 10) - 1);
    const diag = new vscode.Diagnostic(
      new vscode.Range(lineNo, 0, lineNo, Number.MAX_SAFE_INTEGER),
      m[2],
      vscode.DiagnosticSeverity.Error
    );
    diag.source = 'bare';
    items.push(diag);
  }

  diagnostics.clear();
  if (items.length) diagnostics.set(doc.uri, items);
}

async function run() {
  const doc = await activeBareDocument();
  if (!doc) return;
  if (config().get('runInTerminal', true)) runInTerminal(doc);
  else runInOutputChannel(doc);
}

function activate(context) {
  diagnostics = vscode.languages.createDiagnosticCollection('bare');

  context.subscriptions.push(
    diagnostics,
    vscode.commands.registerCommand('bare.runFile', run),

    // A file's errors are stale the moment it is edited.
    vscode.workspace.onDidChangeTextDocument((e) => {
      if (e.document.languageId === 'bare') diagnostics.delete(e.document.uri);
    })
  );
}

function deactivate() {
  if (output) output.dispose();
}

module.exports = { activate, deactivate };

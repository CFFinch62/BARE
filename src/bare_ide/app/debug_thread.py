"""Interpreter Worker Thread for BARE IDE.

Runs the bare_core interpreter on a QThread so a long-running or infinite
BARE program (`while true ... end`) never freezes the GUI. Three
cooperative bridges connect the worker back to the main thread:

- Cancellation: stop() sets Interpreter.cancelled, which the interpreter
  checks between statements (bare_core/interpreter.py). The check raises
  BareRuntimeError, which run() distinguishes from a real error by testing
  self.interpreter.cancelled rather than matching the error message.
- Input: input() calls emit input_requested and block the worker thread on
  a threading.Event. The GUI thread calls provide_input() once the user
  submits a value, which sets the event and lets the worker continue.
  stop() also sets this event, so cancelling while input() is pending
  doesn't leave the worker stuck waiting forever.
- Step-debug: bare_core's Interpreter already calls a step_callback(line,
  env) before every statement (built for exactly this). _on_step pauses
  the worker thread on a second threading.Event whenever step_mode is on
  or the line is a breakpoint, and emits step_reached(line, variables) so
  the GUI can show the Variable Watch panel. resume() releases it.

If a library_program is supplied (the student's personal user_library.bare,
already lexed/parsed by main_window before the worker starts), its subs are
loaded into the interpreter's global scope before the main program runs.
"""

import threading
from typing import Iterable, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from bare_core.ast_nodes import Program
from bare_core.environment import Environment
from bare_core.errors import (
    BareError,
    BareLexerError,
    BareParseError,
    BareRuntimeError,
    SourceLocation,
)
from bare_core.interpreter import Interpreter


class InterpreterWorker(QThread):
    """Runs one parsed BARE program on a background thread.

    Signals:
        output_ready(str): 'print' output.
        input_requested(str): input() was called with this prompt — the
            GUI must eventually call provide_input() to unblock the worker.
        step_reached(int, object): paused before the statement on this line
            (step mode or a breakpoint); object is a variables dict from
            Environment.get_all_variables() — the current scope's locals if
            paused inside a sub, globals otherwise.
        error_occurred(str, object, str): (formatted message, line number
            or None, error_type: "parse" or "runtime").
        stopped(): execution was cancelled via stop().
        execution_finished(): always emitted last, on every code path.
    """

    output_ready = pyqtSignal(str)
    input_requested = pyqtSignal(str)
    step_reached = pyqtSignal(int, object)
    error_occurred = pyqtSignal(str, object, str)
    stopped = pyqtSignal()
    execution_finished = pyqtSignal()

    def __init__(
        self,
        program: Program,
        breakpoints: Optional[Iterable[int]] = None,
        step_mode: bool = False,
        library_program: Optional[Program] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.program = program
        self.library_program = library_program
        self.step_mode = step_mode
        self.breakpoints = set(breakpoints or ())
        self.interpreter = Interpreter(
            output_callback=self._on_output,
            input_callback=self._on_input_request,
            step_callback=self._on_step,
        )
        self._input_event = threading.Event()
        self._input_value = ""
        self._step_event = threading.Event()

    def stop(self):
        """Request cooperative cancellation. Safe to call from the GUI thread."""
        self.interpreter.cancelled = True
        self._input_event.set()  # unblock if currently waiting on input()
        self._step_event.set()  # unblock if currently paused on a step/breakpoint

    def provide_input(self, value: str):
        """Called from the GUI thread once the user submits a line."""
        self._input_value = value
        self._input_event.set()

    def resume(self, step_mode: bool):
        """Called from the GUI thread to release a paused worker.

        step_mode=True (Step) pauses again at the very next statement;
        step_mode=False (Continue) runs freely until the next breakpoint.
        """
        self.step_mode = step_mode
        self._step_event.set()

    def _on_output(self, text: str) -> None:
        self.output_ready.emit(text)

    def _on_input_request(self, prompt: str) -> str:
        self._input_event.clear()
        self.input_requested.emit(prompt)
        self._input_event.wait()
        if self.interpreter.cancelled:
            raise BareRuntimeError("execution stopped", SourceLocation(0))
        return self._input_value

    def _on_step(self, line: int, env: Environment) -> None:
        if not self.interpreter.cancelled and (self.step_mode or line in self.breakpoints):
            self._step_event.clear()
            self.step_reached.emit(line, env.get_all_variables())
            self._step_event.wait()
        if self.interpreter.cancelled:
            raise BareRuntimeError("execution stopped", SourceLocation(line))

    def run(self) -> None:
        try:
            if self.library_program is not None:
                try:
                    loaded = self.interpreter.load_library(self.library_program)
                except BareError as e:
                    if self.interpreter.cancelled:
                        self.stopped.emit()
                    else:
                        # Line numbers here refer to user_library.bare, not
                        # the open file — don't let _show_error highlight
                        # the wrong line in the student's editor for it.
                        self._emit_bare_error(e, prefix="In your library — ", suppress_line=True)
                    return
                if loaded:
                    self._on_output(f"Loaded from your library: {', '.join(loaded)}")
            self.interpreter.execute(self.program)
        except BareError as e:
            if self.interpreter.cancelled:
                self.stopped.emit()
            else:
                self._emit_bare_error(e)
        except Exception as e:  # pragma: no cover - defensive: an interpreter
            # bug shouldn't hang the GUI in "Running..." state forever.
            self.error_occurred.emit(f"Internal error: {e}", None, "runtime")
        finally:
            self.execution_finished.emit()

    def _emit_bare_error(self, e: BareError, prefix: str = "", suppress_line: bool = False) -> None:
        line = e.location.line if e.location else None
        error_type = "parse" if isinstance(e, (BareLexerError, BareParseError)) else "runtime"
        self.error_occurred.emit(f"{prefix}{e.format()}", None if suppress_line else line, error_type)

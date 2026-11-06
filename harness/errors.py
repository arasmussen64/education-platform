"""Turn errors into messages a beginner can act on.

Only lines from the learner's own file are shown, never the harness's, so
the messages read like Python's normal output for their program.
"""

from __future__ import annotations

import traceback
from pathlib import Path

from checks import SOLUTION_FILE


def _is_in(filename: str | None, target: str) -> bool:
    return filename is not None and Path(filename).name == target


def learner_frames(exc: BaseException, target: str = SOLUTION_FILE) -> list:
    """The traceback frames that belong to ``target``, oldest first."""
    return [
        frame
        for frame in traceback.extract_tb(exc.__traceback__)
        if _is_in(frame.filename, target)
    ]


def deepest_file(exc: BaseException) -> str | None:
    """The file name (without folders) where an error actually happened."""
    if isinstance(exc, SyntaxError):
        return Path(exc.filename).name if exc.filename else None
    frames = traceback.extract_tb(exc.__traceback__)
    return Path(frames[-1].filename).name if frames else None


def describe_error(exc: BaseException) -> str:
    """One line, such as: NameError: name 'x' is not defined (solution.py, line 3)."""
    if isinstance(exc, SyntaxError):
        name = Path(exc.filename).name if exc.filename else SOLUTION_FILE
        return f"SyntaxError: {exc.msg} ({name}, line {exc.lineno})"

    text = str(exc)
    summary = f"{type(exc).__name__}: {text}" if text else type(exc).__name__
    frames = learner_frames(exc)
    if frames:
        summary += f" ({SOLUTION_FILE}, line {frames[-1].lineno})"
    return summary


def learner_traceback(exc: BaseException) -> str:
    """A full traceback, like Python prints, trimmed to the learner's file."""
    lines: list[str] = []
    frames = learner_frames(exc)
    if frames:
        lines.append("Traceback (most recent call last):\n")
        lines.extend(traceback.format_list(frames))
    lines.extend(traceback.format_exception_only(exc))
    return "".join(lines)

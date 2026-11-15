"""tools/lab-capture and the copies inside labs are one script.

A lab's image is built from the lab's own folder, so a lab that ships the
capture script needs a copy of it there. The Capture workflow runs the one in
tools/. If they drifted apart, a recording made on a GitHub runner and one
made in a lab would no longer be read the same way.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "lab-capture"


def test_every_lab_copy_is_the_tool() -> None:
    copies = sorted((ROOT / "content" / "topics").glob("*/exercises/*/lab-capture"))
    assert copies, "no lab ships lab-capture any more: delete this test"
    for copy in copies:
        assert copy.read_bytes() == TOOL.read_bytes(), (
            f"{copy.relative_to(ROOT)} differs from tools/lab-capture"
        )


def test_the_tool_has_unix_line_endings() -> None:
    # The workflow runs it with bash on Linux, and Docker copies the lab
    # copies as they are: a carriage return would break the first line.
    assert b"\r" not in TOOL.read_bytes()

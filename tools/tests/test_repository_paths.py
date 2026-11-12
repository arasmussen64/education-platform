"""Every file in the repository must have a path short enough to check out
on Windows.

Git on Windows stops at 260 characters for a file and about 248 for a
folder, counting the checkout's own path in front. The owner's checkout is
about 45 characters deep and an agent's worktree inside it about 80, so a
path in the repository longer than about 165 can't be checked out there.
On 2026-11-12 an archive of prototypes with 178-character paths stopped
every new worktree from being made. 150 leaves room for a deeper checkout.
"""

import subprocess
from pathlib import Path

LIMIT = 150
ROOT = Path(__file__).resolve().parents[2]


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def test_every_path_fits_a_windows_checkout():
    files = tracked_files()
    assert files, "git ls-files listed nothing"
    too_long = [f"{len(path)}: {path}" for path in files if len(path) > LIMIT]
    assert not too_long, (
        f"These paths are longer than {LIMIT} characters, too long to check "
        "out on Windows inside a worktree. Shorten their folders:\n"
        + "\n".join(too_long)
    )

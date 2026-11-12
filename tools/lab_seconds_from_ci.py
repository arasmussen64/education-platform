"""Writes tools/lab-seconds.json from a Labs CI run's logs, so the next runs
split the labs evenly across their machines (tools/labcheck.py, shard_of).

Usage, from the repository root, with the GitHub CLI signed in:

    python -m uv run python tools/lab_seconds_from_ci.py RUN_ID

RUN_ID is a Labs workflow run that tested every lab (`gh run list --workflow
Labs`). Each share's log ends with one line a lab, such as
`ok     csa.net.dns/build-move-the-api (812 s)`; this reads those lines from
every share and keeps each lab's time. A lab that was retried on its own is
left out (its time isn't one a crowded machine would take), and so the file
keeps no time for it until a later run.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tools" / "lab-seconds.json"
REPO = "arasmussen64/education-platform"
LINE = re.compile(r"^\S*\s*(?:ok|BROKEN)\s+(\S+/\S+) \((\d+) s\)$")


def gh(*args: str) -> str:
    done = subprocess.run(["gh", *args], check=True, capture_output=True)
    return done.stdout.decode("utf-8", errors="replace")


def times_in(log: str) -> dict[str, int]:
    """The lab times in one share's log ("<timestamp> ok     topic/lab (N s)")."""
    found: dict[str, int] = {}
    for raw in log.splitlines():
        line = re.sub(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ", "", raw.strip())
        match = LINE.match(line)
        if match:
            found[match.group(1)] = int(match.group(2))
    return found


def main(run_id: str) -> int:
    jobs = json.loads(gh("run", "view", run_id, "--repo", REPO, "--json", "jobs"))[
        "jobs"
    ]
    seconds: dict[str, int] = {}
    for job in jobs:
        if not job["name"].startswith("Labs (share"):
            continue
        if job["status"] != "completed":
            print(f"{job['name']} hasn't finished; run this again once it has")
            return 1
        # CI's logs keep the terminal's colour codes; gh prints them only
        # when asked, and they're taken out before the lines are read.
        log = gh(
            "api",
            "--allow-escape-sequences",
            f"repos/{REPO}/actions/jobs/{job['databaseId']}/logs",
        )
        log = re.sub(r"\x1b\[[0-9;]*m", "", log)
        seconds.update(times_in(log))
    if not seconds:
        print("no lab times found in that run's logs", file=sys.stderr)
        return 1
    data = {
        "how": (
            "Each lab's contract time in seconds, from a full Labs CI run with"
            " four labs at once on each machine. Refresh it with"
            " tools/lab_seconds_from_ci.py RUN_ID; a lab not listed weighs the"
            " middle time."
        ),
        "run": run_id,
        "seconds": dict(sorted(seconds.items())),
    }
    OUT.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
    minutes = sum(seconds.values()) / 60
    print(f"{len(seconds)} labs, {minutes:.0f} minutes in all, written to {OUT.name}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))

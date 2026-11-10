"""Run one folder through the harness and print the report as JSON.

    python harness/cli.py check FOLDER
        Run FOLDER/test_exercise.py against FOLDER/solution.py (the Check button).

    python harness/cli.py run FOLDER [--stdin TEXT] [--seed N]
        Run FOLDER/solution.py like the Run button.

    python harness/cli.py trace FOLDER [--stdin TEXT] [--seed N]
        Run it like the Step through button, recording every step.

FOLDER becomes the working directory, as in the browser. The content
validator and the scenario tests call this in a fresh Python process, so
they run exactly what the browser runs. (Not bundled into the web app.)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="run the exercise's tests")
    check.add_argument("folder")
    run = commands.add_parser("run", help="run the program")
    run.add_argument("folder")
    run.add_argument("--stdin", default="", help="input typed so far")
    run.add_argument("--seed", type=int, default=None, help="random seed")
    trace = commands.add_parser("trace", help="run the program, recording each step")
    trace.add_argument("folder")
    trace.add_argument("--stdin", default="", help="input typed so far")
    trace.add_argument("--seed", type=int, default=None, help="random seed")
    args = parser.parse_args(argv)

    os.chdir(args.folder)
    sys.path[:0] = [str(HARNESS), "."]
    # Imported here, after the paths are set, exactly like the browser does.
    import program
    import testrunner
    import tracer

    if args.command == "check":
        report = testrunner.run_tests()
    elif args.command == "trace":
        report = tracer.trace_program(args.stdin, args.seed)
    else:
        report = program.run_program(args.stdin, args.seed)
    print(json.dumps(report))


if __name__ == "__main__":
    main()

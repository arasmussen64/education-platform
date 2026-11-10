"""The lab checker's local mode (ADR-0018): labs in containers on this machine.

A lab is an exercise with `runtime: lab` in content/. Its folder holds a
Dockerfile (the scenario), checks.yaml (what must be true when the lab is
done), solution.sh (the reference fix) and wrong/*.sh (fixes that must fail).

Run from the repository root:

    python -m uv run python tools/labcheck.py list
    python -m uv run python tools/labcheck.py start csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py check csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py stop  csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py test  csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py test  --all --jobs 4

`start` builds the lab's image and starts its container; `check` runs the
checks and prints the result to paste into the lab's box on the site; `stop`
removes the container. `test` is for authors and CI: the pristine container
must not pass, the reference solution must pass, every known-wrong fix must
fail at least one check. `--jobs` tests several labs at once.

A lab whose exercise.yaml says `lab: { init: systemd }` boots systemd as PID 1
in a privileged container, and the checker waits for the boot to finish before
asking it anything. If the image has /usr/local/lib/lab/teardown.sh, the
checker runs it before removing the container, so a lab can let go of what it
attached to Docker's machine (the loop devices behind its disks).

The checker only asks the container questions. It never changes it, except
when `test` applies a solution to a fresh container of its own.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml
from content_model import Exercise, Expect, LabCheck, LabChecks

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "topics"

# Goes into every result, so a future change in what a check means can be told
# apart from an old pass.
CHECKER_VERSION = "1"

# A check's command gets this long; a lab shouldn't need more.
CHECK_TIMEOUT_SECONDS = 30
# A systemd lab's first layer installs a lot; on a busy CI runner, with
# several builds at once, a quarter of an hour wasn't always enough.
BUILD_TIMEOUT_SECONDS = 1800
APPLY_TIMEOUT_SECONDS = 300
# systemd boots in a second or two. Long enough for a cloud-init first boot that runs apt against a broken
# user data, on a CI runner where every lab's containers boot at once now
# that the shared layers are warmed first. A healthy lab boots in seconds.
BOOT_TIMEOUT_SECONDS = 240

# The learner's account inside every lab image.
LEARNER = "learner"
HOME = f"/home/{LEARNER}"


class LabError(Exception):
    """Something the author or the machine has to fix; the message says what."""


@dataclass(frozen=True)
class Lab:
    topic_id: str
    exercise: Exercise
    folder: Path
    checks: list[LabCheck]

    @property
    def name(self) -> str:
        return f"{self.topic_id}/{self.exercise.id}"

    @property
    def image(self) -> str:
        return f"lab-{self.topic_id}-{self.exercise.id}:r{self.exercise.rev}"

    @property
    def container(self) -> str:
        return f"lab-{self.topic_id}-{self.exercise.id}"

    @property
    def init(self) -> str:
        return self.exercise.lab.init if self.exercise.lab else "none"


# --- Finding labs -------------------------------------------------------------------


def load_lab(topic_id: str, exercise_id: str, content: Path = CONTENT) -> Lab:
    folder = content / topic_id / "exercises" / exercise_id
    yaml_file = folder / "exercise.yaml"
    if not yaml_file.exists():
        raise LabError(f"no exercise at {folder.as_posix()}")
    exercise = Exercise.model_validate(
        yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    )
    if exercise.runtime != "lab":
        raise LabError(f"{topic_id}/{exercise_id} is a Python exercise, not a lab")
    checks_file = folder / "checks.yaml"
    if not checks_file.exists():
        raise LabError(f"{topic_id}/{exercise_id} has no checks.yaml")
    checks = LabChecks.model_validate(
        yaml.safe_load(checks_file.read_text(encoding="utf-8"))
    ).checks
    return Lab(topic_id, exercise, folder, checks)


def find_labs(content: Path = CONTENT) -> list[tuple[str, str]]:
    """Every (topic, exercise) whose exercise.yaml says runtime: lab."""
    found: list[tuple[str, str]] = []
    for yaml_file in sorted(content.glob("*/exercises/*/exercise.yaml")):
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
        if data.get("runtime") == "lab":
            found.append((yaml_file.parents[2].name, yaml_file.parent.name))
    return found


# --- Talking to Docker -----------------------------------------------------------


def docker_command() -> str:
    found = shutil.which("docker")
    if not found:
        raise LabError(
            "docker isn't installed or isn't on PATH. Labs need Docker Desktop "
            "(or Docker Engine) running on this machine."
        )
    return found


def docker(
    *args: str, timeout: int = CHECK_TIMEOUT_SECONDS, check: bool = True
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [docker_command(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise LabError(f"docker {args[0]} failed: {detail}")
    return completed


def build_image(lab: Lab, quiet: bool = True) -> None:
    if not (lab.folder / "Dockerfile").exists():
        raise LabError(f"{lab.name} has no Dockerfile")
    args = ["build", "-t", lab.image, str(lab.folder)]
    if quiet:
        args.insert(1, "-q")
    docker(*args, timeout=BUILD_TIMEOUT_SECONDS)


# A lab that attaches things to the machine Docker runs on (disks, say) can
# put a script here to let go of them. It runs just before the container is
# removed, because removing a container doesn't detach its loop devices.
TEARDOWN = "/usr/local/lib/lab/teardown.sh"


def is_running(name: str) -> bool:
    found = docker("inspect", "-f", "{{.State.Running}}", name, timeout=30, check=False)
    return found.returncode == 0 and found.stdout.strip() == "true"


def remove_container(name: str) -> None:
    """Removes a lab's container, after its teardown script if it has one."""
    if is_running(name):
        docker(
            "exec",
            name,
            "bash",
            "-c",
            f"[ -x {TEARDOWN} ] && {TEARDOWN} || true",
            timeout=60,
            check=False,
        )
    docker("rm", "-f", name, check=False)


def run_arguments(lab: Lab, name: str) -> list[str]:
    """The `docker run` arguments for a lab's container."""
    args = ["run", "-d", "--name", name, "--hostname", "lab"]
    if lab.init == "systemd":
        # systemd has to be PID 1, own a writable cgroup tree and have /run as
        # a tmpfs. A private cgroup namespace gives it a tree of its own, so
        # the limits a lab sets (MemoryMax=, CPUQuota=) apply inside the
        # container the way they do on a server; sharing the host's tree
        # doesn't (tried on Docker Desktop, 2026-11-09).
        args += [
            "--privileged",
            "--cgroupns=private",
            "--tmpfs",
            "/run",
            "--tmpfs",
            "/run/lock",
            lab.image,
            "/sbin/init",
        ]
    else:
        args += [lab.image]
    return args


def start_container(lab: Lab, name: str | None = None) -> str:
    """Starts a fresh container for the lab, booted if it boots; returns its name."""
    name = name or lab.container
    remove_container(name)
    docker(*run_arguments(lab, name), timeout=120)
    if lab.init == "systemd":
        wait_for_boot(name)
    return name


# What `systemctl is-system-running` says once boot is over: everything is up,
# or everything is up except a unit that failed (a lab may plant one).
BOOTED = {"running", "degraded"}


def wait_for_boot(
    container: str,
    timeout: float = BOOT_TIMEOUT_SECONDS,
    clock: Callable[[], float] = time.monotonic,
    pause: Callable[[float], None] = time.sleep,
) -> str:
    """Waits until systemd in the container has finished booting; returns its state.

    Checks run too early would see services that haven't started yet.
    """
    deadline = clock() + timeout
    state = "unknown"
    while True:
        completed = exec_in(container, "systemctl is-system-running", timeout=15)
        state = completed.stdout.strip() or completed.stderr.strip() or state
        if state in BOOTED:
            return state
        if clock() >= deadline:
            raise LabError(
                f"{container} didn't finish booting in {timeout:g} s "
                f"(systemd says: {state})"
            )
        pause(0.5)


def exec_in(
    container: str,
    command: str,
    user: str = "root",
    timeout: int = CHECK_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    return docker(
        "exec",
        "-u",
        user,
        "-w",
        HOME,
        container,
        "bash",
        "-c",
        command,
        timeout=timeout,
        check=False,
    )


def apply_script(container: str, script: Path) -> None:
    """Runs a solution or known-wrong fix inside the container, as the learner."""
    with tempfile.TemporaryDirectory() as workdir:
        copy = Path(workdir) / "apply.sh"
        # Scripts are stored with LF, but a Windows checkout may have CRLF.
        copy.write_bytes(script.read_bytes().replace(b"\r\n", b"\n"))
        docker("cp", str(copy), f"{container}:/tmp/apply.sh", timeout=60)
    result = exec_in(
        container, "bash /tmp/apply.sh", user=LEARNER, timeout=APPLY_TIMEOUT_SECONDS
    )
    if result.returncode != 0:
        detail = (result.stderr.strip() or result.stdout.strip())[-2000:]
        raise LabError(
            f"{script.name} failed in the container "
            f"(exit {result.returncode}):\n{detail}"
        )


# --- Running checks ---------------------------------------------------------------


@dataclass(frozen=True)
class CheckResult:
    id: str
    description: str
    passed: bool
    # Why it failed, for the author and the learner's terminal; not sent.
    detail: str


def evaluate(expect: Expect | None, stdout: str, exit_status: int) -> tuple[bool, str]:
    """Whether a command's output satisfies the expectation, and if not, why."""
    output = stdout.strip()
    if expect is None:
        return (exit_status == 0, f"exit status {exit_status}")
    wanted_exit = expect.exit if expect.exit is not None else 0
    if exit_status != wanted_exit:
        return (False, f"exit status {exit_status}, wanted {wanted_exit}")
    if expect.equals is not None and output != expect.equals.strip():
        return (False, f"printed {output!r}, wanted {expect.equals.strip()!r}")
    if expect.contains is not None and expect.contains not in output:
        return (False, f"printed {output!r}, which lacks {expect.contains!r}")
    if expect.not_contains is not None and expect.not_contains in output:
        return (False, f"printed {output!r}, which contains {expect.not_contains!r}")
    if expect.matches is not None and not re.search(expect.matches, output):
        return (False, f"printed {output!r}, which doesn't match /{expect.matches}/")
    numeric = {"lt": expect.lt, "lte": expect.lte, "gt": expect.gt, "gte": expect.gte}
    if any(bound is not None for bound in numeric.values()):
        # The first number in the output, so "85% /var" reads as 85.
        found = re.search(r"-?\d+(?:\.\d+)?", output)
        if not found:
            return (False, f"printed {output!r}, which isn't a number")
        value = float(found.group())
        if numeric["lt"] is not None and not value < numeric["lt"]:
            return (False, f"{value:g} is not below {numeric['lt']:g}")
        if numeric["lte"] is not None and not value <= numeric["lte"]:
            return (False, f"{value:g} is above {numeric['lte']:g}")
        if numeric["gt"] is not None and not value > numeric["gt"]:
            return (False, f"{value:g} is not above {numeric['gt']:g}")
        if numeric["gte"] is not None and not value >= numeric["gte"]:
            return (False, f"{value:g} is below {numeric['gte']:g}")
    return (True, "ok")


def run_checks(lab: Lab, container: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    for check in lab.checks:
        try:
            completed = exec_in(container, check.command)
        except subprocess.TimeoutExpired:
            results.append(
                CheckResult(check.id, check.description, False, "took too long")
            )
            continue
        passed, detail = evaluate(check.expect, completed.stdout, completed.returncode)
        if not passed and completed.stderr.strip():
            detail += f"; stderr: {completed.stderr.strip()[:300]}"
        results.append(CheckResult(check.id, check.description, passed, detail))
    return results


def result_json(lab: Lab, results: list[CheckResult]) -> dict[str, object]:
    """What the learner pastes into the site: which checks passed, nothing else."""
    return {
        "lab": lab.name,
        "rev": lab.exercise.rev,
        "checker": CHECKER_VERSION,
        "checked_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "passed": sum(result.passed for result in results),
        "total": len(results),
        "checks": [{"id": result.id, "passed": result.passed} for result in results],
    }


def title_of(check: CheckResult) -> str:
    return check.description.strip().splitlines()[0]


def print_results(
    results: list[CheckResult],
    show_detail: bool,
    say: Callable[[str], None] = print,
) -> None:
    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        line = f"  {mark}  {title_of(result)}"
        if show_detail and not result.passed:
            line += f"\n        {result.detail}"
        say(line)


# --- Commands ---------------------------------------------------------------------


def cmd_list(_: argparse.Namespace) -> int:
    labs = find_labs()
    if not labs:
        print("No labs yet.")
        return 0
    for topic_id, exercise_id in labs:
        print(f"{topic_id} {exercise_id}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    print(f"Building {lab.image} (the first time takes a minute)...")
    build_image(lab)
    start_container(lab)
    print(f"\n{lab.exercise.title}: the container is running.\n")
    print("Open a shell in it with:\n")
    print(f"    docker exec -it -u {LEARNER} -w {HOME} {lab.container} bash\n")
    print("When you think you're done, run the checks with:\n")
    print(
        "    python -m uv run python tools/labcheck.py check "
        f"{lab.topic_id} {lab.exercise.id}\n"
    )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    running = docker(
        "ps", "-q", "--filter", f"name=^{lab.container}$", timeout=30
    ).stdout.strip()
    if not running:
        raise LabError(
            f"{lab.container} isn't running. Start it with: "
            f"labcheck.py start {lab.topic_id} {lab.exercise.id}"
        )
    results = run_checks(lab, lab.container)
    print(f"{lab.exercise.title}\n")
    print_results(results, show_detail=True)
    passed = sum(result.passed for result in results)
    print(f"\n{passed} of {len(results)} checks passed.")
    result = result_json(lab, results)
    encoded = json.dumps(result, separators=(",", ":"))
    print("\nPaste this into the lab's box on the site to record it:\n")
    print(encoded)
    if args.json:
        Path(args.json).write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nSaved to {args.json}")
    return 0 if passed == len(results) else 1


def cmd_stop(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    remove_container(lab.container)
    print(f"Removed {lab.container}.")
    return 0


@dataclass
class ContractReport:
    lab: str
    problems: list[str]
    # What the run printed, kept so parallel runs can print each lab's whole.
    log: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def test_lab(
    lab: Lab,
    verbose: bool = True,
    say: Callable[[str], None] = print,
) -> ContractReport:
    """The contract: pristine fails, the solution passes, every wrong fix fails."""
    problems: list[str] = []
    if not verbose:
        say = lambda _: None  # noqa: E731
    say(f"== {lab.name}")
    say("  building the image...")
    build_image(lab)
    scratch = f"{lab.container}-test"
    try:
        say("  pristine container: the checks must not all pass")
        start_container(lab, scratch)
        pristine = run_checks(lab, scratch)
        if all(result.passed for result in pristine):
            problems.append("every check passes before any work is done")
        passing = sum(result.passed for result in pristine)
        say(f"    {passing} of {len(pristine)} pass before any work")

        solution = lab.folder / "solution.sh"
        if not solution.exists():
            problems.append("solution.sh is missing")
        else:
            say("  solution.sh: every check must pass")
            start_container(lab, scratch)
            apply_script(scratch, solution)
            solved = run_checks(lab, scratch)
            for result in solved:
                if not result.passed:
                    problems.append(
                        f"after solution.sh, {result.id} fails: {result.detail}"
                    )
            if verbose:
                print_results(solved, show_detail=True, say=say)

        for wrong in sorted(lab.folder.glob("wrong/*.sh")):
            say(f"  {wrong.name}: at least one check must fail")
            start_container(lab, scratch)
            apply_script(scratch, wrong)
            wrong_results = run_checks(lab, scratch)
            failing = [result.id for result in wrong_results if not result.passed]
            if not failing:
                problems.append(f"wrong/{wrong.name} passes every check")
            else:
                say(f"    fails {', '.join(failing)}")
    finally:
        remove_container(scratch)
    return ContractReport(lab.name, problems)


def first_line(text: str) -> str:
    """The first line of an error's message, or nothing."""
    return text.splitlines()[0] if text else ""


def test_quietly(topic_id: str, exercise_id: str) -> ContractReport:
    """One lab's contract run with its output kept, for running several at once.

    A machine problem (Docker down, an image that won't build) becomes a
    problem of that lab rather than ending the whole run.
    """
    log: list[str] = []
    try:
        report = test_lab(load_lab(topic_id, exercise_id), say=log.append)
    except LabError as error:
        report = ContractReport(f"{topic_id}/{exercise_id}", [f"labcheck: {error}"])
    except Exception as error:  # noqa: BLE001 - one lab's broken file mustn't end the run
        report = ContractReport(
            f"{topic_id}/{exercise_id}",
            [f"{type(error).__name__}: {first_line(str(error))}"],
        )
    report.log = log
    return report


def first_of_each_topic(targets: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """The first lab of every topic, in order: one build each warms the layer
    the topic's labs share."""
    seen: set[str] = set()
    firsts: list[tuple[str, str]] = []
    for topic, exercise in targets:
        if topic not in seen:
            seen.add(topic)
            firsts.append((topic, exercise))
    return firsts


def warm_images(
    targets: list[tuple[str, str]], say: Callable[[str], None] = print
) -> None:
    """Builds the first lab of each topic, one at a time, before a parallel
    run. A topic's labs share their heavy first layer, so after one build
    the rest come from the cache; built four at once from cold, they each
    install the same packages and can run past the build timeout."""
    for topic, exercise in first_of_each_topic(targets):
        say(f"warming {topic} with {exercise}...")
        try:
            build_image(load_lab(topic, exercise))
        except Exception as error:  # noqa: BLE001 - the parallel run reports it
            detail = str(error).splitlines()[0] if str(error) else ""
            say(f"  {type(error).__name__}: {detail}")


def cmd_test(args: argparse.Namespace) -> int:
    if args.all:
        targets = find_labs()
    elif args.topic and args.exercise:
        targets = [(args.topic, args.exercise)]
    else:
        raise LabError("test needs a topic and an exercise, or --all")
    jobs = max(1, args.jobs)
    if jobs == 1:
        reports = [test_lab(load_lab(topic, exercise)) for topic, exercise in targets]
    else:
        # Docker runs the containers side by side; each lab's output is
        # printed whole when it finishes, so the runs don't interleave.
        warm_images(targets)
        reports = []
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            for report in pool.map(lambda t: test_quietly(*t), targets):
                print("\n".join(report.log))
                reports.append(report)
    broken = [report for report in reports if not report.ok]
    print()
    for report in reports:
        status = "ok" if report.ok else "BROKEN"
        print(f"{status:6} {report.lab}")
        for problem in report.problems:
            print(f"       - {problem}")
    print(f"\n{len(reports) - len(broken)} of {len(reports)} labs keep their contract.")
    return 0 if not broken else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="name every lab").set_defaults(run=cmd_list)
    for name, run, text in (
        ("start", cmd_start, "build a lab's image and start its container"),
        ("check", cmd_check, "run a lab's checks and print the result to paste"),
        ("stop", cmd_stop, "remove a lab's container"),
    ):
        command = sub.add_parser(name, help=text)
        command.add_argument("topic")
        command.add_argument("exercise")
        if name == "check":
            command.add_argument("--json", help="also save the result to this file")
        command.set_defaults(run=run)
    test = sub.add_parser("test", help="prove a lab's contract (authors and CI)")
    test.add_argument("topic", nargs="?")
    test.add_argument("exercise", nargs="?")
    test.add_argument("--all", action="store_true", help="every lab in content/")
    test.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="how many labs to test at once (CI uses 4)",
    )
    test.set_defaults(run=cmd_test)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except LabError as error:
        print(f"labcheck: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

"""The lab checker's local mode (ADR-0018): labs in containers on this machine.

A lab is an exercise with `runtime: lab` in content/. Its folder holds a
Dockerfile (the scenario), checks.yaml (what must be true when the lab is
done), solution.sh (the reference fix) and wrong/*.sh (fixes that must fail).

Run from the repository root:

    python -m uv run python tools/labcheck.py list
    python -m uv run python tools/labcheck.py start csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py shell csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py check csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py stop  csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py status
    python -m uv run python tools/labcheck.py stop  --all
    python -m uv run python tools/labcheck.py test  csa.linux.shell build-log-report
    python -m uv run python tools/labcheck.py test  --all --jobs 4
    python -m uv run python tools/labcheck.py test  --all --jobs 4 --shard 0/4

`start` builds the lab's image and starts its container. Run again, it keeps
the work: a running lab is left alone, and a stopped one (after a restart of
Docker or the computer) is started again as it was. `start --fresh` is the
only way to throw the work away and begin again. `shell` opens a shell in the
lab as the learner; `check` runs the checks and prints the result to paste
into the lab's box on the site; `stop` removes the container and the work in
it. `status` lists every lab container this tool started, and `stop --all`
removes the ones `start` made.

`test` is for authors and CI: the pristine container must not pass, the
reference solution must pass, every known-wrong fix must fail at least one
check. `--jobs` tests several labs at once; `--shard I/N` takes every Nth
topic, which is how CI splits the run across machines.

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
import os
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
# systemd boots in a second or two. The limit is long enough for a cloud-init
# first boot that runs apt against a broken user data, on a CI runner where
# every lab's containers boot at once now that the shared layers are warmed
# first. A healthy lab still boots in seconds.
BOOT_TIMEOUT_SECONDS = 480

# The learner's account inside every lab image.
LEARNER = "learner"
HOME = f"/home/{LEARNER}"

# Every container this tool starts carries these two labels, so `status` and
# `stop --all` can find them all and can't touch anything else on the machine.
# The first names the lab ("topic/exercise"); the second says who started it:
# "learner" for `start`, "test" for a contract run's throwaway container.
LABEL_LAB = "labcheck.lab"
LABEL_ROLE = "labcheck.role"

# How every command is run, for the lines this tool tells the learner to type.
RUN = "python -m uv run python tools/labcheck.py"


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


# What the docker command says, in one version or another, when the engine
# behind it isn't running: the usual state of things just after the computer
# starts, before Docker Desktop has finished starting.
ENGINE_DOWN_SAYS = (
    "failed to connect to the docker api",
    "cannot connect to the docker daemon",
    "error during connect",
    "docker daemon is not running",
)
ENGINE_DOWN = (
    "Docker isn't answering. Start Docker Desktop, wait until it says the "
    "engine is running, and run the same command again."
)


def engine_is_down(message: str) -> bool:
    return any(says in message.lower() for says in ENGINE_DOWN_SAYS)


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
        if engine_is_down(detail):
            raise LabError(ENGINE_DOWN)
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


@dataclass(frozen=True)
class Found:
    """A lab's container, as Docker has it."""

    # "running", or one of the ways of not running: "exited" (it stopped,
    # as every container does when Docker or the computer restarts),
    # "paused" (the pause button in Docker Desktop), "created", "dead".
    status: str
    # The image it was started from: "lab-<topic>-<exercise>:r<rev>".
    image: str


def find_container(name: str) -> Found | None:
    """The container of that name, or None when there isn't one."""
    found = docker(
        "container",
        "inspect",
        "-f",
        "{{.State.Status}}|{{.Config.Image}}",
        name,
        timeout=30,
        check=False,
    )
    if found.returncode != 0:
        detail = found.stderr.strip() or found.stdout.strip()
        if "no such container" in detail.lower():
            return None
        if engine_is_down(detail):
            raise LabError(ENGINE_DOWN)
        raise LabError(f"docker couldn't say whether {name} exists: {detail}")
    status, _, image = found.stdout.strip().partition("|")
    return Found(status, image)


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


# A lab's disks are image files under this folder in its container, attached
# to Docker's machine as loop devices by the lab's own boot script (the
# storage labs' disks.sh is the pattern, in content/README.md).
LAB_DISKS = "/var/lib/lab/"

# Lets go of lab disks nobody can be using any more. A container that goes
# away without its teardown script (removed from the Docker Desktop window,
# or stopped by a restart) leaves its loop devices attached to Docker's
# machine, and a later lab can then pick up the dead lab's disk instead of
# its own. This runs in a helper container that can see the whole machine.
#
# A disk is let go of only when the filesystem its image file is on isn't
# mounted anywhere on the machine: that filesystem was a container's own, so
# the container is gone or stopped, and nothing can reach the file again. A
# running lab's disks never qualify, whatever the container is called.
# $1 is "detach"; anything else only reports. Prints "stale DEVICE FILE" for
# each disk it let go of, "in-use DEVICE FILE" for each it left alone.
STALE_DISKS = (
    """
# Two things must hold, or nothing below can be trusted. This container must
# see every process on Docker's machine (then this shell isn't process 1),
# and a file must report the device of the filesystem it is on (true when
# all of an image's layers are on one disk, as Docker keeps them).
[ "$$" != 1 ] || { echo "abort: no view of the machine's processes"; exit 0; }
mine=$(awk '$5 == "/" { print $3 }' /proc/self/mountinfo | tail -1)
[ -n "$mine" ] && [ "$mine" = "$(stat -c '%Hd:%Ld' /usr/bin/env)" ] \\
  || { echo "abort: files don't report their filesystem's device"; exit 0; }
for backing in /sys/block/loop*/loop/backing_file; do
  [ -e "$backing" ] || continue
  name=${backing#/sys/block/}
  name=${name%%/*}
  dev=/dev/$name
  case "$(cat "$backing" 2>/dev/null)" in LAB_DISKS*) ;; *) continue ;; esac
  [ -e "$dev" ] || mknod "$dev" b 7 "${name#loop}" 2>/dev/null || continue
  # Hold the device open while deciding. As long as it is held, the kernel
  # won't detach it, so it can't be handed to another lab between the look
  # and the letting go (tried on Docker Desktop, 2026-11-11).
  { exec 9< "$dev"; } 2>/dev/null || continue
  file=$(cat "$backing" 2>/dev/null)
  on=$(losetup -n -O BACK-MAJ:MIN "$dev" 2>/dev/null | tr -d ' ')
  case "$file" in
    LAB_DISKS*)
      if [ -n "$on" ]; then
        # Is the filesystem that file is on still mounted anywhere?
        if awk '{ print $3 }' /proc/[0-9]*/mountinfo 2>/dev/null | grep -qxF "$on"; then
          echo "in-use $dev $file"
        else
          [ "$1" = detach ] && losetup -d "$dev"
          echo "stale $dev $file"
        fi
      fi
      ;;
  esac
  exec 9<&-
done
exit 0
"""
).replace("LAB_DISKS", LAB_DISKS)


def has_disks(lab: Lab) -> bool:
    """Whether the lab attaches things to Docker's machine: such a lab ships
    a teardown script that lets go of them."""
    return (lab.folder / "teardown.sh").exists()


def detach_stale_disks(lab: Lab) -> list[str]:
    """Lets go of the disks dead labs left attached; returns their devices.

    Best effort: if the helper can't run, or can't be sure, nothing is
    touched and nothing is reported.
    """
    try:
        done = docker(
            "run",
            "--rm",
            "--privileged",
            # The helper has to see every process on Docker's machine.
            "--pid=host",
            lab.image,
            "bash",
            "-c",
            STALE_DISKS,
            "stale-disks",
            "detach",
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return []
    return [
        line.split()[1]
        for line in done.stdout.splitlines()
        if line.startswith("stale ") and len(line.split()) >= 2
    ]


def run_arguments(lab: Lab, name: str, role: str = "learner") -> list[str]:
    """The `docker run` arguments for a lab's container."""
    args = ["run", "-d", "--name", name, "--hostname", "lab"]
    args += ["--label", f"{LABEL_LAB}={lab.name}", "--label", f"{LABEL_ROLE}={role}"]
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
    """Starts a fresh container for the lab, booted if it boots; returns its name.

    Whatever container had that name is removed first, with the work in it:
    `start` only comes here when there is none, or when asked with --fresh.
    A name of its own means a contract run's throwaway container.
    """
    role = "test" if name else "learner"
    name = name or lab.container
    remove_container(name)
    docker(*run_arguments(lab, name, role), timeout=120)
    if lab.init == "systemd":
        wait_for_boot(name)
    return name


def restart_container(lab: Lab, found: Found) -> None:
    """Starts a lab's stopped container again, keeping everything in it.

    A container keeps its files when it stops, so this is a reboot of the
    lab's server, not a new one. Tried on all 79 labs with their solutions
    applied and the container killed (2026-11-10): every one booted again,
    77 within seven seconds and two storage labs after a minute and a half
    (systemd waits that long for a disk named in fstab), and 67 still passed
    every check. The other 12 had lost only what a reboot loses: a process
    started by hand, a mount, a control group, files on a tmpfs.
    """
    if found.status == "paused":
        docker("unpause", lab.container, timeout=60)
        return
    docker("start", lab.container, timeout=120)
    if lab.init == "systemd":
        wait_for_boot(lab.container)


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
            # Name the jobs still running, so a boot that hangs on CI says
            # which unit it was waiting for.
            jobs = exec_in(container, "systemctl list-jobs --no-pager", timeout=15)
            waiting = (jobs.stdout or jobs.stderr).strip() or "(no job list)"
            # And what each unit still starting has logged, since that's
            # where the reason is.
            units = [
                line.split()[1]
                for line in jobs.stdout.splitlines()[1:]
                if len(line.split()) >= 4 and line.split()[1].endswith(".service")
            ]
            logs = ""
            for unit in units[:3]:
                tail = exec_in(
                    container, f"journalctl -b -u {unit} --no-pager -n 40", timeout=15
                )
                logs += f"\n--- journal of {unit} ---\n{tail.stdout.strip()}"
            raise LabError(
                f"{container} didn't finish booting in {timeout:g} s "
                f"(systemd says: {state}); jobs still running:\n{waiting}{logs}"
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


# --- The learner's shell ----------------------------------------------------------

# What standard input can be, as far as opening a shell goes.
CONSOLE = "console"  # a real terminal: Docker can give a prompt through it
GIT_BASH_WINDOW = "git-bash-window"  # Git Bash's own window, with no console
NOT_A_TERMINAL = "not-a-terminal"  # a pipe or a file: commands sent in


def is_git_bash_pipe(pipe_name: str) -> bool:
    r"""Whether a Windows pipe of that name is Git Bash's terminal window.

    Git Bash's window (mintty) isn't a Windows console. To a Windows program
    such as docker, what the learner types there arrives through a pipe that
    Git Bash names like "\msys-1888ae32e00d56aa-pty0-from-master". Recent
    versions of Git for Windows put a real console behind the window, and
    then there is no such pipe.
    """
    name = pipe_name.lower()
    return ("msys-" in name or "cygwin-" in name) and "-pty" in name


def windows_input_kind(handle: int) -> str:
    """What a Windows file handle is: see terminal_kind."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
    kernel32.GetConsoleMode.restype = wintypes.BOOL
    kernel32.GetFileInformationByHandleEx.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    kernel32.GetFileInformationByHandleEx.restype = wintypes.BOOL
    # A console is the only thing that has a console mode. This is the test
    # Docker itself applies; isatty() isn't enough, since it is also true of
    # the "nul" device.
    mode = wintypes.DWORD()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return CONSOLE
    # Otherwise ask for the handle's name: FileNameInfo (2) fills in a length
    # in bytes, then the name as UTF-16.
    buffer = ctypes.create_string_buffer(4 + 2 * 1024)
    if kernel32.GetFileInformationByHandleEx(handle, 2, buffer, len(buffer)):
        length = int.from_bytes(buffer.raw[:4], "little")
        name = buffer.raw[4 : 4 + length].decode("utf-16-le", errors="replace")
        if is_git_bash_pipe(name):
            return GIT_BASH_WINDOW
    return NOT_A_TERMINAL


def terminal_kind(stream: object) -> str:
    """What a stream (standard input) is: CONSOLE, GIT_BASH_WINDOW or
    NOT_A_TERMINAL. An interactive shell needs the first."""
    try:
        descriptor = stream.fileno()  # type: ignore[attr-defined]
    except AttributeError, OSError, ValueError:
        return NOT_A_TERMINAL
    if os.name != "nt":
        return CONSOLE if os.isatty(descriptor) else NOT_A_TERMINAL
    import msvcrt

    try:
        return windows_input_kind(msvcrt.get_osfhandle(descriptor))
    except OSError:
        return NOT_A_TERMINAL


def shell_arguments(container: str, interactive: bool) -> list[str]:
    """The `docker exec` arguments that open bash in a lab as the learner.

    Python hands these to docker as a list, one argument each, so no shell
    in between gets to rewrite them. That matters in Git Bash, which turns
    an argument like /home/learner into C:/Program Files/Git/home/learner
    on its way to a Windows program, and docker then refuses the path.
    """
    # -i keeps standard input open; -t asks for a terminal in the container,
    # which is what gives a prompt, and only works from a real terminal.
    flags = ["-it"] if interactive else ["-i"]
    return ["exec", *flags, "-u", LEARNER, "-w", HOME, container, "bash"]


def run_attached(*args: str) -> int:
    """Runs docker joined to this terminal, until it ends; returns its exit status."""
    # Docker Desktop ends an interactive command with a "What's next" tip
    # about another of its products; this setting keeps that off the screen.
    quiet = {**os.environ, "DOCKER_CLI_HINTS": "false"}
    try:
        return subprocess.run(
            [docker_command(), *args], check=False, env=quiet
        ).returncode
    except KeyboardInterrupt:
        # Ctrl+C normally goes to the program in the lab's shell. If it
        # reached us instead, the shell is over.
        return 130


# --- Commands ---------------------------------------------------------------------


def cmd_list(_: argparse.Namespace) -> int:
    labs = find_labs()
    if not labs:
        print("No labs yet.")
        return 0
    for topic_id, exercise_id in labs:
        print(f"{topic_id} {exercise_id}")
    return 0


def command(verb: str, lab: Lab) -> str:
    """The line that runs one of this tool's commands on a lab."""
    return f"{RUN} {verb} {lab.topic_id} {lab.exercise.id}"


def revision_changed(lab: Lab, found: Found) -> str:
    """What to say when a lab's container was started from another revision."""
    return (
        f"{lab.name} has changed since you started it: your container is from "
        f"{found.image}, and the lab is now {lab.image}. The checks are for the "
        "new version, so the old container can't be checked against them. "
        "Begin the lab again (this removes the old container and the work in "
        f"it) with:\n\n    {command('start --fresh', lab)}"
    )


def print_next_steps(lab: Lab) -> None:
    print("Open a shell in it with:\n")
    print(f"    {command('shell', lab)}\n")
    print("When you think you're done, run the checks with:\n")
    print(f"    {command('check', lab)}\n")
    print("When you've finished with the lab, stop it with:\n")
    print(f"    {command('stop', lab)}\n")


def clear_stale_disks(lab: Lab) -> None:
    """Before a lab with disks boots: lets go of the disks that labs no
    longer running left attached, and says so."""
    if not has_disks(lab):
        return
    freed = detach_stale_disks(lab)
    if freed:
        print(
            f"Let go of {len(freed)} disk(s) that a lab no longer running had "
            "left attached to Docker's machine."
        )


def cmd_start(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    found = find_container(lab.container)
    if found is None or args.fresh:
        print(f"Building {lab.image} (the first time takes a minute)...")
        build_image(lab)
        if found is not None:
            # Only now, with the new image built: a build that fails leaves
            # the old container, and the work in it, where they were.
            print(f"Removing {lab.container} and the work in it, as --fresh asks.")
            remove_container(lab.container)
        # After the old container has gone, so its disks count as stale even
        # when it couldn't run its teardown script: a paused container can't
        # run anything, and it would leave two of each disk for the new one.
        clear_stale_disks(lab)
        try:
            start_container(lab)
        except LabError, subprocess.TimeoutExpired, KeyboardInterrupt:
            # A new lab that didn't come up has no work in it. Leave nothing
            # behind, or the next `start` would find it and call it running.
            remove_container(lab.container)
            raise
        print(f"\n{lab.exercise.title}: the lab is running, as new.\n")
        print_next_steps(lab)
        return 0
    if found.image != lab.image:
        raise LabError(revision_changed(lab, found))
    if found.status == "running":
        print(f"{lab.exercise.title}: the lab is already running, with your work")
        print("in it. Nothing was changed.\n")
    else:
        was = "paused" if found.status == "paused" else "stopped"
        print(f"{lab.name} was {was}. Starting it again, with your work in it...")
        if was == "stopped" and has_disks(lab):
            print("(A lab with disks takes a minute or two to boot again.)")
            # Its own disks from before it stopped are among the stale ones:
            # the boot attaches them afresh, and two of each would confuse it.
            clear_stale_disks(lab)
        try:
            restart_container(lab, found)
        except LabError as error:
            raise LabError(
                f"{error}\n\nThe lab didn't come back. If trying once more "
                "doesn't help, begin it again (this removes the container and "
                f"the work in it) with:\n\n    {command('start --fresh', lab)}"
            ) from None
        print(f"\n{lab.exercise.title}: the lab is running again.\n")
        if was == "stopped":
            # A stopped container is a server that was switched off: what was
            # on its disk is still there, what was only in memory is not.
            print("It came back the way a server comes back from a reboot: the")
            print("files and settings in it are as you left them.")
            if has_disks(lab):
                print("Whatever was only running, or only mounted, when it stopped")
                print("may need doing again (sudo mount -a mounts the disks again).")
            else:
                # Only the storage labs have taught mounting by then.
                print("Whatever was only running when it stopped, such as a")
                print("program you had started by hand, may need starting again.")
            print("Run the checks to see where you stand.\n")
    print_next_steps(lab)
    print("To throw the work away and begin the lab again:\n")
    print(f"    {command('start --fresh', lab)}\n")
    return 0


def running_container(lab: Lab) -> None:
    """Makes sure the lab's container is there, current and running; says
    what to do when it isn't. Nothing it advises removes the learner's work."""
    found = find_container(lab.container)
    if found is None:
        raise LabError(
            f"{lab.name} hasn't been started. Start it with:\n\n"
            f"    {command('start', lab)}"
        )
    if found.image != lab.image:
        raise LabError(revision_changed(lab, found))
    if found.status != "running":
        if found.status == "paused":
            was, why = "paused", "the pause button in Docker Desktop does that"
        else:
            was, why = (
                "stopped",
                "Docker Desktop or the computer was restarted, perhaps",
            )
        raise LabError(
            f"{lab.name} is {was}: its container is still there, with your "
            f"work in it, but it isn't running ({why}). Start it again, which "
            f"keeps the work, with:\n\n    {command('start', lab)}"
        )


# What `shell` says from Git Bash's own window when no console is behind it.
NO_CONSOLE = """this window can't hold the lab's shell.

Git Bash's own window isn't a Windows console, and Docker needs one to give
you a prompt inside the lab. Open PowerShell or Windows Terminal instead, go
to the repository folder with cd, and run the same command there:

    {shell}

Nothing is wrong with the lab: it is still running, with your work in it."""


def cmd_shell(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    running_container(lab)
    kind = terminal_kind(sys.stdin)
    if kind == GIT_BASH_WINDOW:
        raise LabError(NO_CONSOLE.format(shell=command("shell", lab)))
    if kind == NOT_A_TERMINAL:
        # Commands sent in on standard input (a pipe or a file): run them
        # and say nothing else, so the output is only theirs.
        return run_attached(*shell_arguments(lab.container, interactive=False))
    print(f"{lab.exercise.title}: you're in the lab now, as the user {LEARNER}.")
    print("Type exit when you want to come back to your own terminal.\n", flush=True)
    status = run_attached(*shell_arguments(lab.container, interactive=True))
    print("\nYou're back in your own terminal. The lab is still running.")
    print(f"  Run its checks:  {command('check', lab)}")
    print(f"  Go back in:      {command('shell', lab)}")
    print(f"  Stop it:         {command('stop', lab)}")
    return status


def cmd_check(args: argparse.Namespace) -> int:
    lab = load_lab(args.topic, args.exercise)
    running_container(lab)
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
    # A lab left running keeps using the computer (some are busy on purpose).
    print("\nThe lab is still running, with your work in it.")
    print(f"  Go back in:  {command('shell', lab)}")
    print(f"  Stop it when you've finished with it:  {command('stop', lab)}")
    return 0 if passed == len(results) else 1


@dataclass(frozen=True)
class Started:
    """A container this tool started, as `docker ps` lists it."""

    name: str
    # "running", "exited", "paused", "created"...
    state: str
    # "topic/exercise"
    lab: str
    # "learner" or "test"
    role: str


def started_containers() -> list[Started]:
    """Every container on this machine that carries this tool's labels."""
    listed = docker(
        "ps",
        "-a",
        "--filter",
        f"label={LABEL_LAB}",
        "--format",
        "{{.Names}}|{{.State}}|"
        f'{{{{.Label "{LABEL_LAB}"}}}}|{{{{.Label "{LABEL_ROLE}"}}}}',
        timeout=30,
    )
    found = []
    for line in listed.stdout.splitlines():
        parts = line.strip().split("|")
        if len(parts) == 4:
            found.append(Started(*parts))
    return sorted(found, key=lambda started: (started.role, started.lab))


# Docker's words for a container's state, in the words this tool uses.
STATE_WORDS = {"running": "running", "exited": "stopped", "paused": "paused"}


def cmd_status(_: argparse.Namespace) -> int:
    started = started_containers()
    if not started:
        print("No lab is running or stopped on this machine: nothing to stop.")
        return 0
    print("The labs on this machine:\n")
    for one in started:
        state = STATE_WORDS.get(one.state, one.state)
        whose = "" if one.role == "learner" else "   (a test run's)"
        print(f"  {state:8} {one.lab.replace('/', ' ')}{whose}")
    print(f"\nGo into a running one:  {RUN} shell <topic> <exercise>")
    print(f"Start a stopped one:    {RUN} start <topic> <exercise>")
    print(f"Stop one:               {RUN} stop <topic> <exercise>")
    print(f"Stop them all:          {RUN} stop --all")
    if any(one.role != "learner" for one in started):
        print(f"...and the test runs':  {RUN} stop --all --tests")
    print("\nStarting a stopped lab keeps the work in it. Stopping a lab removes")
    print("its container and the work in it.")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    if args.all:
        if args.topic or args.exercise:
            raise LabError("stop --all takes no lab name: it stops every lab")
        return stop_all(include_tests=args.tests)
    if not (args.topic and args.exercise):
        raise LabError("stop needs a topic and an exercise, or --all")
    lab = load_lab(args.topic, args.exercise)
    found = find_container(lab.container)
    if found is None:
        print(f"{lab.name} isn't started: there is nothing to stop.")
        return 0
    remove_container(lab.container)
    if found.status != "running":
        # A lab that had already stopped couldn't run its teardown script.
        clear_stale_disks(lab)
    print(f"Stopped {lab.name}: its container, and the work in it, are removed.")
    return 0


def stop_all(include_tests: bool) -> int:
    """Removes every container `start` made, and with --tests what `test` left."""
    started = started_containers()
    mine = [one for one in started if include_tests or one.role == "learner"]
    for one in mine:
        remove_container(one.name)
        print(f"Stopped {one.lab}: its container, and the work in it, are removed.")
    if not mine:
        print("No lab is running or stopped on this machine: nothing to stop.")
    left = len(started) - len(mine)
    if left:
        print(
            f"\n{left} container(s) of a test run are still here. A test removes "
            "its own when it ends; if one was cut short, remove what it left "
            f"with:\n\n    {RUN} stop --all --tests"
        )
    return 0


@dataclass
class ContractReport:
    lab: str
    problems: list[str]
    # What the run printed, kept so parallel runs can print each lab's whole.
    log: list[str] = field(default_factory=list)
    # True when this is the second run, on its own, after the checker gave
    # up on the first in the crowd.
    retried: bool = False

    @property
    def ok(self) -> bool:
        return not self.problems

    @property
    def gave_up(self) -> bool:
        """The contract wasn't tested: the checker itself stopped (a boot
        that didn't finish, a build that ran out of time), rather than a
        check that failed or a wrong fix that passed."""
        return bool(self.problems) and all(
            problem.startswith("labcheck: ") for problem in self.problems
        )


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
    except subprocess.TimeoutExpired as error:
        # A script that ran past its limit beside three other labs; alone it
        # may not. A script that truly hangs times out again on the retry.
        report = ContractReport(
            f"{topic_id}/{exercise_id}",
            [f"labcheck: timed out: {first_line(str(error))}"],
        )
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


def shard_of(targets: list[tuple[str, str]], shard: str) -> list[tuple[str, str]]:
    """The labs of every Nth topic, for `--shard I/N`. CI splits the run
    across machines by topic rather than by lab, so each machine builds the
    layer a topic's labs share only once; with about five labs a topic the
    shares come out even enough."""
    try:
        index_text, count_text = shard.split("/", 1)
        index, count = int(index_text), int(count_text)
    except ValueError:
        raise LabError(f"--shard wants I/N, like 0/4, not {shard!r}") from None
    if count < 1 or not 0 <= index < count:
        raise LabError(f"--shard {shard} is out of range: I runs from 0 to N-1")
    topics = sorted({topic for topic, _ in targets})
    mine = set(topics[index::count])
    return [(topic, exercise) for topic, exercise in targets if topic in mine]


def cmd_test(args: argparse.Namespace) -> int:
    if args.shard and not args.all:
        raise LabError("--shard goes with --all")
    if args.all:
        targets = find_labs()
        if args.shard:
            targets = shard_of(targets, args.shard)
            topics = sorted({topic for topic, _ in targets})
            print(f"shard {args.shard}: {len(targets)} labs in {', '.join(topics)}\n")
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
        # A lab the checker gave up on in the crowd (a boot that didn't
        # finish while every other lab's containers were booting too) gets
        # one more run, alone. A contract failure is never retried.
        for index, report in enumerate(reports):
            if not report.gave_up:
                continue
            print(f"\nretrying {report.lab} on its own: {report.problems[0]}")
            topic, exercise = report.lab.split("/", 1)
            retried = test_quietly(topic, exercise)
            retried.retried = True
            print("\n".join(retried.log))
            reports[index] = retried
    broken = [report for report in reports if not report.ok]
    print()
    for report in reports:
        status = "ok" if report.ok else "BROKEN"
        if report.retried:
            status += " (on its own, after the checker gave up in the crowd)"
        print(f"{status:6} {report.lab}")
        for problem in report.problems:
            print(f"       - {problem}")
    print(f"\n{len(reports) - len(broken)} of {len(reports)} labs keep their contract.")
    return 0 if not broken else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="name every lab").set_defaults(run=cmd_list)
    sub.add_parser(
        "status", help="list the lab containers this tool started"
    ).set_defaults(run=cmd_status)
    for name, run, text in (
        ("start", cmd_start, "start a lab, or carry on with it: the work is kept"),
        ("shell", cmd_shell, "open a shell in a running lab, as the learner"),
        ("check", cmd_check, "run a lab's checks and print the result to paste"),
    ):
        one = sub.add_parser(name, help=text)
        one.add_argument("topic")
        one.add_argument("exercise")
        if name == "start":
            one.add_argument(
                "--fresh",
                action="store_true",
                help="begin again: remove the lab's container and the work in it",
            )
        if name == "check":
            one.add_argument("--json", help="also save the result to this file")
        one.set_defaults(run=run)
    stop = sub.add_parser(
        "stop", help="remove a lab's container and the work in it, or --all of them"
    )
    stop.add_argument("topic", nargs="?")
    stop.add_argument("exercise", nargs="?")
    stop.add_argument(
        "--all", action="store_true", help="every lab that `start` started"
    )
    stop.add_argument(
        "--tests",
        action="store_true",
        help="with --all: also what an interrupted `test` run left behind",
    )
    stop.set_defaults(run=cmd_stop)
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
    test.add_argument(
        "--shard",
        help="with --all: this machine's share of the topics, as I/N (CI: 0/4 to 3/4)",
    )
    test.set_defaults(run=cmd_test)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except LabError as error:
        print(f"labcheck: {error}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as error:
        # Docker took longer than this tool waits for it. Say so, rather
        # than end in a page of Python's own error report.
        print(
            f"labcheck: Docker didn't answer within {error.timeout:g} seconds. "
            "The computer may be busy, or Docker Desktop still starting. "
            "Wait a moment and run the same command again.",
            file=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        print("\nlabcheck: stopped, because Ctrl+C was pressed.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())

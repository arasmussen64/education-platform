"""The lab checker's pure parts: expectations, discovery and the result, and
what its commands ask of Docker, with Docker stood in for. Its contract runs
need Docker, which CI's Labs job provides; pytest stays quick."""

import argparse
import io
import os
import subprocess
from pathlib import Path

import labcheck
import pytest
import yaml
from content_fixture import make_valid_tree, write
from content_model import Expect, LabCheck, LabChecks
from labcheck import (
    CHECKER_VERSION,
    CheckResult,
    LabError,
    evaluate,
    find_labs,
    load_lab,
    result_json,
    run_arguments,
    wait_for_boot,
)
from pydantic import ValidationError
from validate_content import validate

LAB_YAML = """id: lab-hello
stage: build
runtime: lab
rev: 2
title: Say hello in a file
prompt: Write hello into hello.txt.
skills: [print-text]
"""

CHECKS = """checks:
  - id: file-exists
    description: hello.txt exists.
    command: test -f /home/learner/hello.txt
  - id: says-hello
    description: It says hello.
    command: cat /home/learner/hello.txt
    expect:
      equals: hello
"""


def test_without_expect_exit_status_zero_passes() -> None:
    assert evaluate(None, "anything\n", 0) == (True, "exit status 0")
    assert evaluate(None, "", 1) == (False, "exit status 1")


def test_text_expectations() -> None:
    assert evaluate(Expect(equals="hello"), "hello\n", 0)[0]
    assert not evaluate(Expect(equals="hello"), "hello world\n", 0)[0]
    assert evaluate(Expect(contains="llo"), "hello\n", 0)[0]
    assert evaluate(Expect(not_contains="bye"), "hello\n", 0)[0]
    assert evaluate(Expect(matches=r"^h.llo$"), "hello\n", 0)[0]
    passed, why = evaluate(Expect(matches=r"^bye"), "hello\n", 0)
    assert not passed and "doesn't match" in why


def test_numeric_expectations_read_the_first_word() -> None:
    assert evaluate(Expect(lt=90), "85% /var\n", 0)[0]
    assert not evaluate(Expect(lt=90), "96%\n", 0)[0]
    assert evaluate(Expect(gte=1, lte=1), "1\n", 0)[0]
    passed, why = evaluate(Expect(gt=0), "none\n", 0)
    assert not passed and "isn't a number" in why


def test_an_expected_exit_status_is_checked_first() -> None:
    assert evaluate(Expect(exit=1), "", 1) == (True, "ok")
    passed, why = evaluate(Expect(exit=1, equals="x"), "x", 0)
    assert not passed and "wanted 1" in why


def test_labs_are_found_and_loaded(tmp_path: Path) -> None:
    content = tmp_path / "content" / "topics"
    lab = "t.hello/exercises/lab-hello"
    write(tmp_path, f"content/topics/{lab}/exercise.yaml", LAB_YAML)
    write(tmp_path, f"content/topics/{lab}/checks.yaml", CHECKS)
    write(
        tmp_path,
        "content/topics/t.hello/exercises/write-hello/exercise.yaml",
        "id: write-hello\nstage: write\nrev: 1\ntitle: W\nprompt: P\n",
    )
    assert find_labs(content) == [("t.hello", "lab-hello")]

    loaded = load_lab("t.hello", "lab-hello", content)
    assert loaded.name == "t.hello/lab-hello"
    assert loaded.image == "lab-t.hello-lab-hello:r2"
    assert loaded.container == "lab-t.hello-lab-hello"
    assert loaded.init == "none"
    assert [check.id for check in loaded.checks] == ["file-exists", "says-hello"]

    with pytest.raises(LabError, match="is a Python exercise"):
        load_lab("t.hello", "write-hello", content)
    with pytest.raises(LabError, match="no exercise"):
        load_lab("t.hello", "nothing", content)


def test_a_systemd_lab_boots_privileged_in_its_own_cgroup_namespace(
    tmp_path: Path,
) -> None:
    content = tmp_path / "content" / "topics"
    lab = "t.hello/exercises/lab-hello"
    write(tmp_path, f"content/topics/{lab}/checks.yaml", CHECKS)
    write(tmp_path, f"content/topics/{lab}/exercise.yaml", LAB_YAML)
    plain = run_arguments(load_lab("t.hello", "lab-hello", content), "box")
    assert plain == [
        "run",
        "-d",
        "--name",
        "box",
        "--hostname",
        "lab",
        # The labels `status` and `stop --all` find the container by.
        "--label",
        "labcheck.lab=t.hello/lab-hello",
        "--label",
        "labcheck.role=learner",
        "lab-t.hello-lab-hello:r2",
    ]
    assert "--privileged" not in plain

    write(
        tmp_path,
        f"content/topics/{lab}/exercise.yaml",
        LAB_YAML + "lab:\n  init: systemd\n",
    )
    booted = load_lab("t.hello", "lab-hello", content)
    assert booted.init == "systemd"
    args = run_arguments(booted, "box")
    assert "--privileged" in args and "--cgroupns=private" in args
    assert args[-2:] == ["lab-t.hello-lab-hello:r2", "/sbin/init"]
    # The host's cgroup tree stays out of it (see run_arguments).
    assert "/sys/fs/cgroup:/sys/fs/cgroup:rw" not in args


def test_waiting_for_boot_polls_until_systemd_is_up(monkeypatch) -> None:
    states = iter(["", "initializing", "starting", "degraded"])
    asked: list[str] = []

    def fake_exec(container: str, command: str, **_: object):
        asked.append(command)
        return subprocess.CompletedProcess([], 0, stdout=next(states) + "\n", stderr="")

    monkeypatch.setattr(labcheck, "exec_in", fake_exec)
    ticks = iter(range(100))
    state = wait_for_boot(
        "box", timeout=10, clock=lambda: next(ticks), pause=lambda _: None
    )
    assert state == "degraded"
    assert asked == ["systemctl is-system-running"] * 4


def test_waiting_for_boot_gives_up_and_says_what_systemd_said(monkeypatch) -> None:
    def stuck(container: str, command: str, **_: object):
        return subprocess.CompletedProcess([], 1, stdout="starting\n", stderr="")

    monkeypatch.setattr(labcheck, "exec_in", stuck)
    ticks = iter([0, 5, 11, 20])
    with pytest.raises(LabError, match=r"didn't finish booting in 10 s .*starting"):
        wait_for_boot(
            "box", timeout=10, clock=lambda: next(ticks), pause=lambda _: None
        )


def test_removing_a_running_container_runs_its_teardown_first(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_docker(*args: str, **_: object):
        calls.append(args)
        if args[0] == "inspect":
            return subprocess.CompletedProcess([], 0, stdout="true\n", stderr="")
        return subprocess.CompletedProcess([], 0, stdout="", stderr="")

    monkeypatch.setattr(labcheck, "docker", fake_docker)
    labcheck.remove_container("box")
    assert [call[0] for call in calls] == ["inspect", "exec", "rm"]
    assert labcheck.TEARDOWN in calls[1][-1]

    # A container that isn't running has nothing to let go of.
    calls.clear()
    monkeypatch.setattr(
        labcheck,
        "docker",
        lambda *args, **_: subprocess.CompletedProcess([], 1, stdout="", stderr=""),
    )
    labcheck.remove_container("gone")


def test_the_result_carries_only_what_the_site_needs(tmp_path: Path) -> None:
    content = tmp_path / "content" / "topics"
    lab = "t.hello/exercises/lab-hello"
    write(tmp_path, f"content/topics/{lab}/exercise.yaml", LAB_YAML)
    write(tmp_path, f"content/topics/{lab}/checks.yaml", CHECKS)
    loaded = load_lab("t.hello", "lab-hello", content)
    results = [
        CheckResult("file-exists", "hello.txt exists.", True, "ok"),
        CheckResult("says-hello", "It says hello.", False, "printed 'hi'"),
    ]
    result = result_json(loaded, results)
    assert result["lab"] == "t.hello/lab-hello"
    assert result["rev"] == 2
    assert result["checker"] == CHECKER_VERSION
    assert result["passed"] == 1 and result["total"] == 2
    assert result["checks"] == [
        {"id": "file-exists", "passed": True},
        {"id": "says-hello", "passed": False},
    ]
    # Details stay on the learner's machine.
    assert "detail" not in str(result) and "printed" not in str(result)


def test_warming_builds_the_first_lab_of_each_topic_in_order(monkeypatch) -> None:
    built: list[tuple[str, str]] = []
    monkeypatch.setattr(labcheck, "load_lab", lambda topic, exercise: (topic, exercise))
    monkeypatch.setattr(labcheck, "build_image", built.append)
    said: list[str] = []
    labcheck.warm_images(
        [("t.a", "x"), ("t.a", "y"), ("t.b", "z"), ("t.a", "w")], say=said.append
    )
    assert built == [("t.a", "x"), ("t.b", "z")]
    assert said == ["warming t.a with x...", "warming t.b with z..."]


def test_warming_reports_a_failed_build_and_goes_on(monkeypatch) -> None:
    def boom(lab: object) -> None:
        raise labcheck.LabError("docker build failed: no space left")

    monkeypatch.setattr(labcheck, "load_lab", lambda topic, exercise: (topic, exercise))
    monkeypatch.setattr(labcheck, "build_image", boom)
    said: list[str] = []
    labcheck.warm_images([("t.a", "x"), ("t.b", "y")], say=said.append)
    assert sum("warming" in line for line in said) == 2
    assert "  LabError: docker build failed: no space left" in said


def test_a_lab_the_checker_gave_up_on_is_retried_alone(monkeypatch, capsys) -> None:
    calls: list[str] = []

    def fake_quietly(topic: str, exercise: str) -> labcheck.ContractReport:
        name = f"{topic}/{exercise}"
        calls.append(name)
        if name == "t/boots-slowly" and calls.count(name) == 1:
            return labcheck.ContractReport(
                name,
                ["labcheck: lab-t-boots-slowly-test didn't finish booting in 480 s"],
            )
        if name == "t/really-broken":
            return labcheck.ContractReport(
                name, ["after solution.sh, a-check fails: exit status 1, wanted 0"]
            )
        return labcheck.ContractReport(name, [])

    monkeypatch.setattr(
        labcheck,
        "find_labs",
        lambda: [("t", "boots-slowly"), ("t", "really-broken"), ("t", "fine")],
    )
    monkeypatch.setattr(labcheck, "warm_images", lambda targets, say=print: None)
    monkeypatch.setattr(labcheck, "test_quietly", fake_quietly)

    exit_code = labcheck.cmd_test(
        argparse.Namespace(all=True, jobs=2, topic=None, exercise=None, shard=None)
    )

    out = capsys.readouterr().out
    # The one the checker gave up on ran again, alone; the contract failure didn't.
    assert calls.count("t/boots-slowly") == 2
    assert calls.count("t/really-broken") == 1
    assert "retrying t/boots-slowly on its own" in out
    retried_line = (
        "ok (on its own, after the checker gave up in the crowd) t/boots-slowly"
    )
    assert retried_line in out
    assert "BROKEN t/really-broken" in out
    assert exit_code == 1


def test_a_timeout_while_proving_counts_as_the_checker_giving_up(monkeypatch) -> None:
    def slow(topic: str, exercise: str):
        raise subprocess.TimeoutExpired(["docker", "exec", "lab", "bash"], 300)

    monkeypatch.setattr(labcheck, "load_lab", slow)
    report = labcheck.test_quietly("t", "slow")
    assert report.gave_up
    assert report.problems[0].startswith("labcheck: timed out:")


def test_shards_split_the_topics_and_cover_every_lab() -> None:
    targets = [(f"t{i}", f"lab{j}") for i in range(5) for j in range(2)]
    shards = [labcheck.shard_of(targets, f"{i}/4") for i in range(4)]
    # Every lab lands in exactly one shard, whole topics at a time.
    assert sorted(sum(shards, [])) == sorted(targets)
    assert shards[0] == [("t0", "lab0"), ("t0", "lab1"), ("t4", "lab0"), ("t4", "lab1")]
    assert shards[3] == [("t3", "lab0"), ("t3", "lab1")]


def test_a_shard_that_isnt_i_of_n_is_refused() -> None:
    for bad in ("4/4", "-1/4", "half", "1/0"):
        with pytest.raises(LabError):
            labcheck.shard_of([("t", "lab")], bad)


# --- The learner's commands, with Docker stood in for -----------------------------

NAME = "lab-t.hello-lab-hello"
IMAGE = "lab-t.hello-lab-hello:r2"
RUN = "python -m uv run python tools/labcheck.py"
# Kept, for the tests that put the real thing back over a stand-in.
REAL_DOCKER = labcheck.docker


def answer(code: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess([], code, stdout=stdout, stderr=stderr)


class FakeDocker:
    """Stands in for labcheck.docker: remembers every call, and answers the
    questions about containers from the ones it was told exist."""

    def __init__(
        self, containers: dict[str, tuple[str, str]] | None = None, listed: str = ""
    ) -> None:
        # name -> (status, image), as `docker container inspect` reports them.
        self.containers = dict(containers or {})
        # What `docker ps` prints: name|state|lab|role per line.
        self.listed = listed
        self.calls: list[tuple[str, ...]] = []
        # Verbs that fail when called, with what docker would say.
        self.failing: dict[str, str] = {}

    def __call__(self, *args: str, **options: object):
        self.calls.append(args)
        name = args[-1]
        if args[0] in self.failing:
            if options.get("check", True):
                raise LabError(f"docker {args[0]} failed: {self.failing[args[0]]}")
            return answer(1, stderr=self.failing[args[0]])
        if args[:2] == ("container", "inspect"):
            if name not in self.containers:
                return answer(
                    1, stderr=f"Error response from daemon: No such container: {name}"
                )
            return answer(stdout="|".join(self.containers[name]) + "\n")
        if args[0] == "inspect":
            # Docker counts a paused container as running.
            up = self.containers.get(name, ("", ""))[0] in ("running", "paused")
            return answer(0 if name in self.containers else 1, stdout=f"{up}\n".lower())
        if args[0] == "ps":
            return answer(stdout=self.listed)
        if args[0] == "rm":
            self.containers.pop(name, None)
        return answer()

    @property
    def verbs(self) -> list[str]:
        return [call[0] for call in self.calls]


def use_lab(
    tmp_path: Path, monkeypatch, docker: FakeDocker, extra_yaml: str = ""
) -> labcheck.Lab:
    """A lab on disk that every command finds, and the stand-in Docker."""
    folder = "content/topics/t.hello/exercises/lab-hello"
    write(tmp_path, f"{folder}/exercise.yaml", LAB_YAML + extra_yaml)
    write(tmp_path, f"{folder}/checks.yaml", CHECKS)
    write(tmp_path, f"{folder}/Dockerfile", "FROM ubuntu:24.04\n")
    lab = load_lab("t.hello", "lab-hello", tmp_path / "content" / "topics")
    monkeypatch.setattr(labcheck, "load_lab", lambda topic, exercise: lab)
    monkeypatch.setattr(labcheck, "docker", docker)
    return lab


def run_main(*argv: str) -> int:
    return labcheck.main(list(argv))


def test_start_builds_and_runs_a_lab_that_has_no_container(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker()
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert docker.verbs == ["container", "build", "inspect", "rm", "run"]
    out = capsys.readouterr().out
    assert "the lab is running, as new" in out
    # The learner is told to run this tool's own commands. Pasting a docker
    # command into Git Bash is what used to break.
    assert f"{RUN} shell t.hello lab-hello" in out
    assert f"{RUN} check t.hello lab-hello" in out
    assert f"{RUN} stop t.hello lab-hello" in out
    assert "docker exec" not in out


def test_start_leaves_a_running_lab_alone(tmp_path: Path, monkeypatch, capsys) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "t.hello", "lab-hello") == 0
    # It asked, and did nothing else: no build, no removal, no new container.
    assert docker.calls == [
        ("container", "inspect", "-f", "{{.State.Status}}|{{.Config.Image}}", NAME)
    ]
    out = capsys.readouterr().out
    assert "already running, with your work" in out
    assert f"{RUN} shell t.hello lab-hello" in out
    assert f"{RUN} start --fresh t.hello lab-hello" in out


def test_start_starts_a_stopped_lab_again_and_keeps_it(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker, "lab:\n  init: systemd\n")
    booted: list[str] = []
    monkeypatch.setattr(labcheck, "wait_for_boot", booted.append)
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert docker.verbs == ["container", "start"]
    assert docker.calls[-1] == ("start", NAME)
    # A lab that boots is waited for, as on its first start.
    assert booted == [NAME]
    out = capsys.readouterr().out
    assert "was stopped. Starting it again, with your work in it" in out
    assert "the lab is running again" in out
    assert "from a reboot" in out
    # Mounting is for the labs with disks; this one has none.
    assert "started by hand, may need starting again" in out
    assert "mount" not in out


def test_a_lab_with_disks_that_starts_again_says_how_to_mount_them(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker, "lab:\n  init: systemd\n")
    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    monkeypatch.setattr(labcheck, "wait_for_boot", lambda name: "running")
    monkeypatch.setattr(labcheck, "detach_stale_disks", lambda lab: [])
    assert run_main("start", "t.hello", "lab-hello") == 0
    out = capsys.readouterr().out
    assert "takes a minute or two to boot again" in out
    assert "sudo mount -a mounts the disks again" in out


def test_start_unpauses_a_paused_lab(tmp_path: Path, monkeypatch, capsys) -> None:
    docker = FakeDocker({NAME: ("paused", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert docker.verbs == ["container", "unpause"]
    out = capsys.readouterr().out
    assert "was paused" in out
    # Nothing was switched off, so there is no reboot to explain.
    assert "from a reboot" not in out


def test_start_fresh_is_the_only_way_to_remove_a_lab_in_progress(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "--fresh", "t.hello", "lab-hello") == 0
    # The old container gets its teardown, is removed, and a new one runs
    # (start_container makes sure the name is free: by then it is).
    assert docker.verbs == [
        "container",
        "build",
        "inspect",
        "exec",
        "rm",
        "inspect",
        "rm",
        "run",
    ]
    out = capsys.readouterr().out
    assert "Removing lab-t.hello-lab-hello and the work in it, as --fresh asks" in out
    assert "the lab is running, as new" in out


def test_start_refuses_a_container_from_an_older_revision_without_removing_it(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", "lab-t.hello-lab-hello:r1")})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "t.hello", "lab-hello") == 2
    assert docker.verbs == ["container"]
    err = capsys.readouterr().err
    assert "has changed since you started it" in err
    assert f"{RUN} start --fresh t.hello lab-hello" in err


def test_a_lab_that_wont_start_again_is_kept_and_fresh_is_offered(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    docker.failing["start"] = "OCI runtime create failed"
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "t.hello", "lab-hello") == 2
    assert "rm" not in docker.verbs and "run" not in docker.verbs
    err = capsys.readouterr().err
    assert "OCI runtime create failed" in err
    assert "The lab didn't come back" in err
    assert f"{RUN} start --fresh t.hello lab-hello" in err


def test_a_new_lab_that_doesnt_come_up_is_not_left_behind(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker()
    use_lab(tmp_path, monkeypatch, docker, "lab:\n  init: systemd\n")

    def never_boots(name: str) -> str:
        # By now the container exists, as far as Docker is concerned.
        docker.containers[name] = ("running", IMAGE)
        raise LabError(f"{name} didn't finish booting in 480 s")

    monkeypatch.setattr(labcheck, "wait_for_boot", never_boots)
    assert run_main("start", "t.hello", "lab-hello") == 2
    assert "didn't finish booting" in capsys.readouterr().err
    # It was removed again. Left there, the next `start` would have found a
    # running container and said the lab was already running.
    assert docker.verbs[-3:] == ["inspect", "exec", "rm"]
    assert docker.calls[-1] == ("rm", "-f", NAME)


def test_a_build_that_fails_leaves_the_old_lab_where_it_was(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    docker.failing["build"] = "no space left on device"
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("start", "--fresh", "t.hello", "lab-hello") == 2
    assert "rm" not in docker.verbs
    captured = capsys.readouterr()
    assert "no space left on device" in captured.err
    assert "Removing" not in captured.out


def test_ctrl_c_ends_in_a_sentence_not_a_traceback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    def interrupted(*args: str, **_: object):
        raise KeyboardInterrupt

    use_lab(tmp_path, monkeypatch, FakeDocker())
    monkeypatch.setattr(labcheck, "docker", interrupted)
    assert run_main("check", "t.hello", "lab-hello") == 130
    assert "stopped, because Ctrl+C was pressed" in capsys.readouterr().err


def test_check_on_a_stopped_lab_says_how_to_start_it_again_with_the_work(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("check", "t.hello", "lab-hello") == 2
    # It only asked: no check ran, and nothing was removed.
    assert docker.verbs == ["container"]
    err = capsys.readouterr().err
    assert "is stopped: its container is still there, with your work in it" in err
    assert "Start it again, which keeps the work" in err
    assert f"{RUN} start t.hello lab-hello" in err
    assert "--fresh" not in err


def test_check_on_a_paused_lab_names_the_pause_button_not_a_restart(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("paused", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("check", "t.hello", "lab-hello") == 2
    err = capsys.readouterr().err
    assert "is paused: its container is still there" in err
    assert "the pause button in Docker Desktop does that" in err
    assert "was restarted" not in err
    assert f"{RUN} start t.hello lab-hello" in err


def test_check_on_a_lab_never_started_says_so(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    use_lab(tmp_path, monkeypatch, FakeDocker())
    assert run_main("check", "t.hello", "lab-hello") == 2
    err = capsys.readouterr().err
    assert "t.hello/lab-hello hasn't been started" in err
    assert f"{RUN} start t.hello lab-hello" in err


def test_check_refuses_a_container_from_an_older_revision(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", "lab-t.hello-lab-hello:r1")})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("check", "t.hello", "lab-hello") == 2
    assert "exec" not in docker.verbs
    assert "has changed since you started it" in capsys.readouterr().err


def test_check_prints_the_result_and_reminds_that_the_lab_still_runs(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    # The stand-in answers every check with exit status 0 and no output:
    # the first check passes, the second wanted "hello".
    assert run_main("check", "t.hello", "lab-hello") == 1
    out = capsys.readouterr().out
    assert "1 of 2 checks passed." in out
    assert '{"lab":"t.hello/lab-hello","rev":2,' in out
    result_at = out.index('{"lab":')
    reminder_at = out.index("The lab is still running, with your work in it.")
    assert reminder_at > result_at
    assert f"{RUN} stop t.hello lab-hello" in out[reminder_at:]
    assert f"{RUN} shell t.hello lab-hello" in out[reminder_at:]


def test_the_shell_is_docker_exec_as_the_learner_in_their_home() -> None:
    assert labcheck.shell_arguments("box", interactive=True) == [
        "exec",
        "-it",
        "-u",
        "learner",
        "-w",
        "/home/learner",
        "box",
        "bash",
    ]
    # Commands sent in on standard input: no terminal is asked for.
    assert labcheck.shell_arguments("box", interactive=False)[1] == "-i"


def shell_with(
    kind: str, tmp_path: Path, monkeypatch, docker: FakeDocker
) -> list[tuple]:
    """Runs `shell` as if standard input were that kind of thing; returns
    what would have been handed to docker."""
    use_lab(tmp_path, monkeypatch, docker)
    handed: list[tuple] = []
    monkeypatch.setattr(labcheck, "terminal_kind", lambda stream: kind)
    monkeypatch.setattr(
        labcheck, "run_attached", lambda *args: handed.append(args) or 7
    )
    return handed


def test_shell_from_a_real_terminal_opens_an_interactive_shell(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    handed = shell_with(labcheck.CONSOLE, tmp_path, monkeypatch, docker)
    # The shell's own exit status is passed on.
    assert run_main("shell", "t.hello", "lab-hello") == 7
    assert handed == [
        ("exec", "-it", "-u", "learner", "-w", "/home/learner", NAME, "bash")
    ]
    out = capsys.readouterr().out
    assert "you're in the lab now, as the user learner" in out
    assert "Type exit" in out
    assert "You're back in your own terminal. The lab is still running." in out
    assert f"{RUN} stop t.hello lab-hello" in out


def test_shell_with_commands_on_standard_input_runs_them_and_says_nothing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    handed = shell_with(labcheck.NOT_A_TERMINAL, tmp_path, monkeypatch, docker)
    assert run_main("shell", "t.hello", "lab-hello") == 7
    assert handed == [
        ("exec", "-i", "-u", "learner", "-w", "/home/learner", NAME, "bash")
    ]
    assert capsys.readouterr().out == ""


def test_shell_in_a_git_bash_window_without_a_console_says_which_terminal_to_use(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    handed = shell_with(labcheck.GIT_BASH_WINDOW, tmp_path, monkeypatch, docker)
    assert run_main("shell", "t.hello", "lab-hello") == 2
    # Docker is never asked: its own error is what a beginner can't act on.
    assert handed == []
    err = capsys.readouterr().err
    assert "this window can't hold the lab's shell" in err
    assert "Open PowerShell or Windows Terminal" in err
    assert f"{RUN} shell t.hello lab-hello" in err
    assert "it is still running, with your work in it" in err


def test_shell_needs_a_running_lab(tmp_path: Path, monkeypatch, capsys) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    handed = shell_with(labcheck.CONSOLE, tmp_path, monkeypatch, docker)
    assert run_main("shell", "t.hello", "lab-hello") == 2
    assert handed == []
    assert "Start it again, which keeps the work" in capsys.readouterr().err

    docker.containers.clear()
    assert run_main("shell", "t.hello", "lab-hello") == 2
    assert "hasn't been started" in capsys.readouterr().err


def test_git_bash_window_pipes_are_told_from_other_pipes() -> None:
    # What the probes on the owner's PC showed (2026-11-11).
    assert labcheck.is_git_bash_pipe(r"\msys-1888ae32e00d56aa-pty0-from-master-nat")
    assert labcheck.is_git_bash_pipe(r"\cygwin-e022582115c10879-pty1-from-master")
    # A pipe from another program, and a file.
    assert not labcheck.is_git_bash_pipe(r"\uv\2-22292")
    assert not labcheck.is_git_bash_pipe(r"\Users\someone\commands.txt")
    assert not labcheck.is_git_bash_pipe("")


def test_a_pipe_or_a_file_is_not_a_terminal(tmp_path: Path) -> None:
    # Something with no file behind it at all, as pytest's own stdin is.
    assert labcheck.terminal_kind(io.StringIO("ls\n")) == labcheck.NOT_A_TERMINAL
    reader, writer = os.pipe()
    try:
        with os.fdopen(reader) as stream:
            assert labcheck.terminal_kind(stream) == labcheck.NOT_A_TERMINAL
    finally:
        os.close(writer)
    commands = tmp_path / "commands.txt"
    commands.write_text("ls\n", encoding="utf-8")
    with commands.open() as stream:
        assert labcheck.terminal_kind(stream) == labcheck.NOT_A_TERMINAL


@pytest.mark.skipif(os.name != "nt", reason="the nul device is a Windows thing")
def test_the_windows_nul_device_is_not_mistaken_for_a_console() -> None:
    # isatty() says yes to "nul", which is why the console is asked directly.
    with open("nul") as stream:
        assert os.isatty(stream.fileno())
        assert labcheck.terminal_kind(stream) == labcheck.NOT_A_TERMINAL


@pytest.mark.skipif(os.name != "nt", reason="Windows named pipes")
def test_a_git_bash_window_is_told_apart_by_the_name_of_a_real_pipe() -> None:
    # The names are read from the handle by Windows itself, so this makes
    # two real pipes: one named the way Git Bash names its window's, one not.
    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateNamedPipeW.restype = wintypes.HANDLE
    kernel32.CreateNamedPipeW.argtypes = (
        [wintypes.LPCWSTR] + [wintypes.DWORD] * 6 + [wintypes.LPVOID]
    )
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    invalid = wintypes.HANDLE(-1).value
    outbound, generic_read, open_existing = 0x2, 0x80000000, 3
    pid = os.getpid()
    for name, kind in (
        (f"msys-1888ae32e00d56aa-pty0-from-master-{pid}", labcheck.GIT_BASH_WINDOW),
        (f"labcheck-test-{pid}", labcheck.NOT_A_TERMINAL),
    ):
        path = rf"\\.\pipe\{name}"
        server = kernel32.CreateNamedPipeW(path, outbound, 0, 1, 512, 512, 0, None)
        assert server != invalid, ctypes.get_last_error()
        try:
            client = kernel32.CreateFileW(
                path, generic_read, 0, None, open_existing, 0, None
            )
            assert client != invalid, ctypes.get_last_error()
            with os.fdopen(msvcrt.open_osfhandle(client, os.O_RDONLY)) as stream:
                assert labcheck.terminal_kind(stream) == kind
        finally:
            kernel32.CloseHandle(server)


def test_the_shell_runs_docker_joined_to_the_terminal_without_its_tips(
    monkeypatch,
) -> None:
    seen: dict[str, object] = {}

    def fake_run(argv: list[str], **options: object):
        seen["argv"] = argv
        seen["options"] = options
        return subprocess.CompletedProcess(argv, 3)

    monkeypatch.setattr(labcheck, "docker_command", lambda: "docker")
    monkeypatch.setattr(labcheck.subprocess, "run", fake_run)
    assert labcheck.run_attached("exec", "-it", "box", "bash") == 3
    # A list, one argument each: no shell in between to rewrite a path.
    assert seen["argv"] == ["docker", "exec", "-it", "box", "bash"]
    options = seen["options"]
    assert isinstance(options, dict)
    assert options["env"]["DOCKER_CLI_HINTS"] == "false"
    # Nothing is captured: the learner's terminal is the shell's terminal.
    assert "capture_output" not in options and "stdin" not in options


def test_stop_removes_one_lab_and_says_the_work_went_with_it(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker({NAME: ("running", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    assert run_main("stop", "t.hello", "lab-hello") == 0
    assert docker.verbs == ["container", "inspect", "exec", "rm"]
    assert "its container, and the work in it, are removed" in capsys.readouterr().out

    docker.containers.clear()
    docker.calls.clear()
    assert run_main("stop", "t.hello", "lab-hello") == 0
    assert docker.verbs == ["container"]
    assert "isn't started: there is nothing to stop" in capsys.readouterr().out


LISTED = (
    "lab-t.b-lab-two|exited|t.b/lab-two|learner\n"
    "lab-t.a-lab-one|running|t.a/lab-one|learner\n"
    "lab-t.a-lab-one-test|running|t.a/lab-one|test\n"
)


def test_status_lists_every_lab_container_this_tool_started(
    monkeypatch, capsys
) -> None:
    docker = FakeDocker(listed=LISTED)
    monkeypatch.setattr(labcheck, "docker", docker)
    assert run_main("status") == 0
    # Found by the label this tool puts on what it starts, stopped ones too.
    assert docker.calls[0][:4] == ("ps", "-a", "--filter", "label=labcheck.lab")
    out = capsys.readouterr().out
    assert "  running  t.a lab-one\n" in out
    assert "  stopped  t.b lab-two\n" in out
    assert "  running  t.a lab-one   (a test run's)\n" in out
    assert f"{RUN} stop --all" in out

    docker.listed = ""
    assert run_main("status") == 0
    assert "No lab is running or stopped on this machine" in capsys.readouterr().out


def test_stop_all_removes_the_learners_labs_and_leaves_test_runs_alone(
    monkeypatch, capsys
) -> None:
    docker = FakeDocker(
        {"lab-t.a-lab-one": ("running", "x"), "lab-t.b-lab-two": ("exited", "x")},
        listed=LISTED,
    )
    monkeypatch.setattr(labcheck, "docker", docker)
    assert run_main("stop", "--all") == 0
    removed = [call[-1] for call in docker.calls if call[0] == "rm"]
    assert removed == ["lab-t.a-lab-one", "lab-t.b-lab-two"]
    # The running one got its teardown first; the stopped one has nothing to run.
    assert [call[1] for call in docker.calls if call[0] == "exec"] == [
        "lab-t.a-lab-one"
    ]
    out = capsys.readouterr().out
    assert "Stopped t.a/lab-one" in out and "Stopped t.b/lab-two" in out
    assert "1 container(s) of a test run are still here" in out
    assert f"{RUN} stop --all --tests" in out


def test_stop_all_with_tests_also_removes_what_a_test_run_left(
    monkeypatch, capsys
) -> None:
    docker = FakeDocker(listed=LISTED)
    monkeypatch.setattr(labcheck, "docker", docker)
    assert run_main("stop", "--all", "--tests") == 0
    removed = [call[-1] for call in docker.calls if call[0] == "rm"]
    assert removed == ["lab-t.a-lab-one", "lab-t.b-lab-two", "lab-t.a-lab-one-test"]
    assert "still here" not in capsys.readouterr().out


def test_stop_all_with_nothing_started_says_so(monkeypatch, capsys) -> None:
    docker = FakeDocker()
    monkeypatch.setattr(labcheck, "docker", docker)
    assert run_main("stop", "--all") == 0
    assert "rm" not in docker.verbs
    assert "nothing to stop" in capsys.readouterr().out


def test_stop_wants_a_lab_or_all_and_not_both(capsys) -> None:
    assert run_main("stop") == 2
    assert "stop needs a topic and an exercise, or --all" in capsys.readouterr().err
    assert run_main("stop", "--all", "t.hello", "lab-hello") == 2
    assert "stop --all takes no lab name" in capsys.readouterr().err


def test_a_contract_runs_container_is_labelled_as_a_test_runs(
    tmp_path: Path, monkeypatch
) -> None:
    docker = FakeDocker()
    lab = use_lab(tmp_path, monkeypatch, docker)
    labcheck.start_container(lab, f"{NAME}-test")
    assert "labcheck.role=test" in docker.calls[-1]
    labcheck.start_container(lab)
    assert "labcheck.role=learner" in docker.calls[-1]


# --- Docker that isn't there, or is slow -------------------------------------------

ENGINE_DOWN_SAID = (
    "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine;"
    " check if the path is correct and if the daemon is running: open "
    "//./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified."
)


def test_docker_not_running_is_said_in_words_a_beginner_can_act_on(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    def fake_run(argv: list[str], **_: object):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr=ENGINE_DOWN_SAID)

    use_lab(tmp_path, monkeypatch, FakeDocker())
    # The checker's real way of calling docker this time, over a docker
    # command that can't reach its engine.
    monkeypatch.setattr(labcheck, "docker", REAL_DOCKER)
    monkeypatch.setattr(labcheck, "docker_command", lambda: "docker")
    monkeypatch.setattr(labcheck.subprocess, "run", fake_run)
    for command in (["start"], ["check"], ["shell"], ["stop"]):
        assert run_main(*command, "t.hello", "lab-hello") == 2
        err = capsys.readouterr().err
        assert "Docker isn't answering. Start Docker Desktop" in err
        assert "npipe" not in err
    assert run_main("status") == 2
    assert "Docker isn't answering" in capsys.readouterr().err
    # Older versions of docker word it differently.
    assert labcheck.engine_is_down(
        "Cannot connect to the Docker daemon at unix:///var/run/docker.sock."
    )
    assert labcheck.engine_is_down("error during connect: this error may indicate...")
    assert not labcheck.engine_is_down("No such container: box")


def test_a_question_docker_cant_answer_is_not_taken_for_no_container(
    monkeypatch,
) -> None:
    docker = FakeDocker()
    docker.failing["container"] = "permission denied while trying to connect"
    monkeypatch.setattr(labcheck, "docker", docker)
    # "There is no such container" would send `start` off to make a new one.
    with pytest.raises(LabError, match="couldn't say whether box exists"):
        labcheck.find_container("box")


def test_docker_taking_too_long_ends_in_a_message_not_a_traceback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    def slow(*args: str, **_: object):
        raise subprocess.TimeoutExpired(["docker", *args], 30)

    use_lab(tmp_path, monkeypatch, FakeDocker())
    monkeypatch.setattr(labcheck, "docker", slow)
    assert run_main("start", "t.hello", "lab-hello") == 2
    err = capsys.readouterr().err
    assert "Docker didn't answer within 30 seconds" in err
    assert "Traceback" not in err


# --- Disks that dead labs left attached -------------------------------------------


def test_a_lab_with_a_teardown_script_is_a_lab_with_disks(
    tmp_path: Path, monkeypatch
) -> None:
    lab = use_lab(tmp_path, monkeypatch, FakeDocker())
    assert not labcheck.has_disks(lab)
    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    assert labcheck.has_disks(lab)


def test_stale_disks_are_let_go_of_by_a_helper_that_sees_the_whole_machine(
    tmp_path: Path, monkeypatch
) -> None:
    class Helper(FakeDocker):
        def __call__(self, *args: str, **options: object):
            super().__call__(*args, **options)
            return answer(
                stdout=(
                    "in-use /dev/loop4 /var/lib/lab/data1.img\n"
                    "stale /dev/loop2 /var/lib/lab/data1.img\n"
                    "stale /dev/loop3 /var/lib/lab/data2.img\n"
                )
            )

    docker = Helper()
    lab = use_lab(tmp_path, monkeypatch, docker)
    assert labcheck.detach_stale_disks(lab) == ["/dev/loop2", "/dev/loop3"]
    call = docker.calls[0]
    assert call[:4] == ("run", "--rm", "--privileged", "--pid=host")
    # The lab's own image, which has the tools; the script; and "detach".
    assert call[4:7] == (IMAGE, "bash", "-c")
    assert call[7] == labcheck.STALE_DISKS
    assert call[-1] == "detach"


def test_the_helper_script_only_lets_go_of_what_it_can_prove_is_stale() -> None:
    script = labcheck.STALE_DISKS
    # Only lab disks: image files under the labs' own folder.
    assert script.count("/var/lib/lab/*)") == 2
    # It gives up unless it can see the machine's processes...
    assert '[ "$$" != 1 ] ||' in script
    # ...holds the device open while it decides...
    assert 'exec 9< "$dev"' in script and "exec 9<&-" in script
    # ...and asks whether the file's filesystem is still mounted anywhere.
    assert "/proc/[0-9]*/mountinfo" in script
    # Detaching happens in one place, behind the word "detach".
    assert script.count("losetup -d") == 1
    assert '[ "$1" = detach ] && losetup -d "$dev"' in script
    # No backslash-n or Windows line ending for bash to trip over.
    assert "\r" not in script


def test_a_helper_that_fails_or_is_slow_changes_nothing(
    tmp_path: Path, monkeypatch
) -> None:
    docker = FakeDocker()
    docker.failing["run"] = "--pid=host is not allowed"
    lab = use_lab(tmp_path, monkeypatch, docker)
    assert labcheck.detach_stale_disks(lab) == []

    def slow(*args: str, **_: object):
        raise subprocess.TimeoutExpired(["docker", *args], 120)

    monkeypatch.setattr(labcheck, "docker", slow)
    assert labcheck.detach_stale_disks(lab) == []


def test_start_clears_stale_disks_before_a_lab_with_disks_boots(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    docker = FakeDocker()
    lab = use_lab(tmp_path, monkeypatch, docker)
    order: list[str] = []
    monkeypatch.setattr(
        labcheck,
        "detach_stale_disks",
        lambda lab: order.append("clear") or ["/dev/loop2"],
    )
    monkeypatch.setattr(
        labcheck, "start_container", lambda lab: order.append("start") or NAME
    )
    monkeypatch.setattr(
        labcheck, "restart_container", lambda lab, found: order.append("restart")
    )

    # A lab without disks never runs the helper.
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert order == ["start"]

    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    assert labcheck.has_disks(lab)
    order.clear()
    capsys.readouterr()
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert order == ["clear", "start"]
    assert "Let go of 1 disk(s) that a lab no longer running" in capsys.readouterr().out

    # A stopped lab's own disks from before are stale: cleared before it boots.
    docker.containers[NAME] = ("exited", IMAGE)
    order.clear()
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert order == ["clear", "restart"]

    # A running lab is left alone, and so is everything attached to it.
    docker.containers[NAME] = ("running", IMAGE)
    order.clear()
    assert run_main("start", "t.hello", "lab-hello") == 0
    assert order == []


def test_start_fresh_lets_go_of_stale_disks_only_once_the_old_lab_is_gone(
    tmp_path: Path, monkeypatch
) -> None:
    # A paused lab can't run its teardown script (Docker refuses to run
    # anything in a paused container), so removing it leaves its disks
    # attached. Cleared before the removal, they'd still be in use and be
    # kept; the new lab would then boot beside two of each.
    docker = FakeDocker({NAME: ("paused", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    events: list[str] = []
    monkeypatch.setattr(
        labcheck,
        "detach_stale_disks",
        lambda lab: events.append(f"clear with {len(docker.containers)} left") or [],
    )
    monkeypatch.setattr(
        labcheck, "start_container", lambda lab: events.append("start") or NAME
    )
    assert run_main("start", "--fresh", "t.hello", "lab-hello") == 0
    assert ("rm", "-f", NAME) in docker.calls
    assert events == ["clear with 0 left", "start"]


def test_stopping_a_lab_that_had_already_stopped_clears_what_it_left(
    tmp_path: Path, monkeypatch
) -> None:
    docker = FakeDocker({NAME: ("exited", IMAGE)})
    use_lab(tmp_path, monkeypatch, docker)
    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    cleared: list[str] = []
    monkeypatch.setattr(
        labcheck, "detach_stale_disks", lambda lab: cleared.append(lab.name) or []
    )
    # It couldn't run its teardown script, so the helper lets go of its disks.
    assert run_main("stop", "t.hello", "lab-hello") == 0
    assert "exec" not in docker.verbs and "rm" in docker.verbs
    assert cleared == ["t.hello/lab-hello"]

    # A running lab's teardown script does that itself.
    docker.containers[NAME] = ("running", IMAGE)
    cleared.clear()
    assert run_main("stop", "t.hello", "lab-hello") == 0
    assert cleared == []


def test_a_contract_run_never_runs_the_stale_disk_helper(
    tmp_path: Path, monkeypatch
) -> None:
    docker = FakeDocker()
    lab = use_lab(tmp_path, monkeypatch, docker)
    write(tmp_path, "content/topics/t.hello/exercises/lab-hello/teardown.sh", "exit 0")
    labcheck.start_container(lab, f"{NAME}-test")
    # CI and other test runs share one Docker: only `start` clears disks.
    assert not any("--pid=host" in call for call in docker.calls)


# --- A check's own time limit (ADR-0018, amended 2026-11-11) ------------------------

# The lab above with a third check that has to boot something slow.
SLOW_CHECKS = (
    CHECKS
    + """  - id: guest-boots
    description: The guest boots and reports two CPUs.
    command: ~/bin/shop-vm | grep -qx cpus=2
    timeout: 120
"""
)


def checks_from(text: str) -> list[LabCheck]:
    return LabChecks.model_validate(yaml.safe_load(text)).checks


def one_check() -> dict[str, object]:
    """A check as YAML gives it, before any timeout."""
    return {"id": "guest-boots", "description": "It boots.", "command": "true"}


def test_a_check_has_thirty_seconds_unless_it_asks_for_more() -> None:
    assert [check.timeout for check in checks_from(SLOW_CHECKS)] == [30, 30, 120]
    assert labcheck.CHECK_TIMEOUT_SECONDS == 30
    for allowed in (1, 300):
        check = {**one_check(), "timeout": allowed}
        assert (
            LabChecks.model_validate({"checks": [check]}).checks[0].timeout == allowed
        )


def test_a_timeout_is_whole_seconds_from_1_to_300_and_says_so() -> None:
    # YAML reads 2.5 and 30.0 as numbers with a fraction, "30" as text and
    # yes as true; none of them is read as some number of seconds.
    for wrong in (0, 301, -5, 2.5, 30.0, "30", True, None):
        check = {**one_check(), "timeout": wrong}
        with pytest.raises(ValidationError) as caught:
            LabChecks.model_validate({"checks": [check]})
        message = caught.value.errors()[0]["msg"]
        assert (
            "guest-boots: timeout is a whole number of seconds from 1 to 300, "
            "such as timeout: 120 (a check without one gets 30); "
            f"{wrong!r} isn't"
        ) in message


def test_a_labs_checks_may_take_ten_minutes_in_all() -> None:
    def lab_of(*timeouts: int | None) -> dict[str, object]:
        checks = []
        for number, seconds in enumerate(timeouts):
            check = {**one_check(), "id": f"check-{number}"}
            if seconds is not None:
                check["timeout"] = seconds
            checks.append(check)
        return {"checks": checks}

    LabChecks.model_validate(lab_of(300, 270, None))  # 600 seconds: allowed
    # A check without a timeout counts its 30 seconds.
    with pytest.raises(ValidationError, match="add up to 630 seconds, over the 600"):
        LabChecks.model_validate(lab_of(300, 270, None, None))
    # Twenty-one checks of 30 seconds each are too many as well.
    with pytest.raises(ValidationError, match="Lower the slow checks' timeout"):
        LabChecks.model_validate(lab_of(*[None] * 21))


def test_the_validator_tells_the_author_what_a_timeout_must_be(tmp_path: Path) -> None:
    tree = make_valid_tree(tmp_path)
    folder = "content/topics/t.hello/exercises/lab-report"
    write(
        tree,
        f"{folder}/exercise.yaml",
        "id: lab-report\nstage: write\nruntime: lab\nrev: 1\n"
        "title: A report\nprompt: Make a report.\nskills: [print-text]\n",
    )
    write(tree, f"{folder}/Dockerfile", "FROM ubuntu:24.04\n")
    write(tree, f"{folder}/solution.sh", "echo done > ~/report.txt\n")
    write(tree, f"{folder}/checks.yaml", SLOW_CHECKS)
    assert validate(tree, run=False).problems == []

    write(tree, f"{folder}/checks.yaml", SLOW_CHECKS.replace("120", "2.5"))
    assert validate(tree, run=False).problems == [
        f"{folder}/checks.yaml: checks.2: Value error, guest-boots: timeout is a "
        "whole number of seconds from 1 to 300, such as timeout: 120 (a check "
        "without one gets 30); 2.5 isn't"
    ]

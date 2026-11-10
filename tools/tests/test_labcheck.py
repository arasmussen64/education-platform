"""The lab checker's pure parts: expectations, discovery and the result. Its
contract runs need Docker, which CI's Labs job provides; pytest stays quick."""

import argparse
import subprocess
from pathlib import Path

import labcheck
import pytest
from content_fixture import write
from content_model import Expect
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
        "lab-t.hello-lab-hello:r2",
    ]

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

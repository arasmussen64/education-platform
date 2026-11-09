"""The lab checker's pure parts: expectations, discovery and the result. Its
contract runs need Docker, which CI's Labs job provides; pytest stays quick."""

from pathlib import Path

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

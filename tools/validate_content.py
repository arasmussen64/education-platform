"""Check everything in content/ before it can reach a learner (v1 spec, F2).

Run from the repository root:

    python -m uv run python tools/validate_content.py           # everything
    python -m uv run python tools/validate_content.py --no-run  # skip running code

It checks:
- every file's format (content_model.py), and that IDs match their folders;
- the topic map: tracks, modules, prerequisites, and no cycles;
- that "ready" topics have everything a topic needs (the content definition of
  done in docs/specs/v1.md);
- by running them through the shared harness, like the browser does: every
  reference solution passes its tests, every starter and known-wrong solution
  fails them, and every predict-the-output item prints what it claims.

It prints every problem it finds and exits with status 1 if there are any.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from content_model import (
    STAGES_WITH_FAILING_STARTER,
    Exercise,
    McqItem,
    PredictOutputItem,
    Topic,
    Track,
    recall_item,
)
from pydantic import BaseModel, TypeAdapter, ValidationError

ROOT = Path(__file__).resolve().parents[1]
HARNESS_CLI = ROOT / "harness" / "cli.py"
RUN_TIMEOUT_SECONDS = 20


@dataclass
class Report:
    root: Path
    problems: list[str] = field(default_factory=list)
    counts: Counter[str] = field(default_factory=Counter)

    def add(self, path: Path, message: str) -> None:
        where = path.relative_to(self.root).as_posix()
        self.problems.append(f"{where}: {message}")


@dataclass
class TopicFolder:
    path: Path
    topic: Topic
    recall: dict[str, McqItem | PredictOutputItem] = field(default_factory=dict)
    exercises: dict[str, tuple[Path, Exercise]] = field(default_factory=dict)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.recall or item_id in self.exercises


# --- Loading -------------------------------------------------------------------


def load(path: Path, shape: type[BaseModel] | TypeAdapter[Any], report: Report):
    """Read a YAML file and check its shape. Returns None if it's broken."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        report.add(path, f"isn't valid YAML: {exc}")
        return None
    try:
        if isinstance(shape, TypeAdapter):
            return shape.validate_python(data)
        return shape.model_validate(data)
    except ValidationError as exc:
        for error in exc.errors():
            where = ".".join(str(part) for part in error["loc"]) or "file"
            report.add(path, f"{where}: {error['msg']}")
        return None


def load_topic_folder(folder: Path, report: Report) -> TopicFolder | None:
    topic = load(folder / "topic.yaml", Topic, report)
    if topic is None:
        return None
    if topic.id != folder.name:
        report.add(folder / "topic.yaml", f"id {topic.id!r} must match its folder name")
    loaded = TopicFolder(folder, topic)

    for path in sorted((folder / "recall").glob("*.yaml")):
        item = load(path, recall_item, report)
        if item is None:
            continue
        if item.id != path.stem:
            report.add(path, f"id {item.id!r} must match the file name")
        loaded.recall[item.id] = item

    for path in sorted((folder / "exercises").glob("*/exercise.yaml")):
        exercise = load(path, Exercise, report)
        if exercise is None:
            continue
        if exercise.id != path.parent.name:
            report.add(path, f"id {exercise.id!r} must match its folder name")
        if exercise.id in loaded.recall:
            report.add(path, f"item id {exercise.id!r} is used twice in this topic")
        loaded.exercises[exercise.id] = (path.parent, exercise)
    return loaded


# --- The topic map ---------------------------------------------------------------


def check_tracks(
    tracks: dict[Path, Track], topics: dict[str, TopicFolder], report: Report
) -> None:
    placed: dict[str, Path] = {}
    for path, track in tracks.items():
        for module in track.modules:
            for topic_id in [*module.topics, module.checkpoint]:
                expected_kind = (
                    "checkpoint" if topic_id == module.checkpoint else "topic"
                )
                if topic_id not in topics:
                    report.add(
                        path, f"{module.id} lists {topic_id!r}, which doesn't exist"
                    )
                    continue
                if topics[topic_id].topic.kind != expected_kind:
                    report.add(path, f"{topic_id!r} must have kind: {expected_kind}")
                if topic_id in placed:
                    report.add(path, f"{topic_id!r} appears in more than one module")
                placed[topic_id] = path
    for topic_id, folder in topics.items():
        if topic_id not in placed:
            report.add(folder.path / "topic.yaml", "isn't in any track's modules")


def check_prerequisites(topics: dict[str, TopicFolder], report: Report) -> None:
    for folder in topics.values():
        for prerequisite in folder.topic.prerequisites:
            if prerequisite not in topics:
                report.add(
                    folder.path / "topic.yaml",
                    f"prerequisite {prerequisite!r} doesn't exist",
                )

    # Depth-first search for cycles: a topic can't (indirectly) depend on itself.
    state: dict[str, str] = {}  # "visiting" or "done"

    def visit(topic_id: str, trail: list[str]) -> None:
        if state.get(topic_id) == "done" or topic_id not in topics:
            return
        if state.get(topic_id) == "visiting":
            cycle = " -> ".join([*trail[trail.index(topic_id) :], topic_id])
            report.add(
                topics[topic_id].path / "topic.yaml",
                f"prerequisites go in a circle: {cycle}",
            )
            return
        state[topic_id] = "visiting"
        for prerequisite in topics[topic_id].topic.prerequisites:
            visit(prerequisite, [*trail, topic_id])
        state[topic_id] = "done"

    for topic_id in sorted(topics):
        visit(topic_id, [])


# --- Ready topics: the content definition of done ---------------------------------


def check_ready_topic(folder: TopicFolder, report: Report) -> None:
    topic = folder.topic
    topic_file = folder.path / "topic.yaml"

    def stage_of(item_id: str) -> str | None:
        if item_id in folder.exercises:
            return folder.exercises[item_id][1].stage
        if item_id in folder.recall:
            return folder.recall[item_id].type
        return None

    if topic.kind == "topic":
        lesson = folder.path / "lesson.mdx"
        lesson_text = lesson.read_text(encoding="utf-8") if lesson.exists() else ""
        if not lesson_text.strip():
            report.add(topic_file, "a ready topic needs a lesson.mdx")
        elif 0 not in resource_indexes(lesson_text):
            report.add(
                lesson, "the lesson must show the main resource: <Resource index={0} />"
            )
        if not topic.resources:
            report.add(topic_file, "a ready topic needs at least one resource")

        stages = Counter(stage_of(item_id) for item_id in topic.practice)
        recall_count = stages["mcq"] + stages["predict_output"]
        if stages["worked_example"] < 1:
            report.add(topic_file, "practice needs a worked example")
        if recall_count < 2:
            report.add(topic_file, "practice needs at least 2 recall items")
        if stages["fill_in"] < 1:
            report.add(topic_file, "practice needs a fill-in exercise")
        if stages["write"] < 1:
            report.add(topic_file, "practice needs a write exercise")

        if len(topic.review_pool) < 3:
            report.add(topic_file, "the review pool needs at least 3 items")
        review_stages = {stage_of(item_id) for item_id in topic.review_pool}
        if not review_stages & {"predict_output", "review_code"}:
            report.add(
                topic_file,
                "the review pool needs a predict-the-output or review_code item",
            )
        for item_id in topic.review_pool:
            if stage_of(item_id) not in {None, "mcq", "predict_output", "review_code"}:
                report.add(topic_file, f"{item_id!r} can't be a review item")
    elif topic.review_pool:
        report.add(topic_file, "checkpoints don't have review pools")

    if topic.prove.build is None or stage_of(topic.prove.build) != "build":
        report.add(topic_file, "prove.build must name a build exercise")
    if topic.prove.debug is None or stage_of(topic.prove.debug) != "debug":
        report.add(topic_file, "prove.debug must name a debug exercise")
    if topic.prove.explain is None:
        report.add(topic_file, "prove.explain is missing")


def resource_indexes(lesson_text: str) -> list[int]:
    """The N of every <Resource index={N} /> tag in a lesson."""
    return [int(n) for n in re.findall(r"<Resource\s+index=\{(\d+)\}", lesson_text)]


def check_references(folder: TopicFolder, report: Report) -> None:
    """Every item a topic names must exist, whatever the topic's status."""
    named = [*folder.topic.practice, *folder.topic.review_pool]
    named += [i for i in (folder.topic.prove.build, folder.topic.prove.debug) if i]
    for item_id in named:
        if not folder.has_item(item_id):
            report.add(
                folder.path / "topic.yaml", f"names {item_id!r}, which doesn't exist"
            )

    lesson = folder.path / "lesson.mdx"
    if lesson.exists():
        for index in resource_indexes(lesson.read_text("utf-8")):
            if index != 0:
                # The app shows resource 0 in the lesson and lists the rest
                # after it, so placing another one would show it twice.
                report.add(
                    lesson,
                    f"<Resource index={{{index}}}>: only the main resource "
                    "(index 0) goes in the lesson; the others are listed after it",
                )
            elif not folder.topic.resources:
                report.add(lesson, "<Resource index={0}> doesn't exist")


# --- Running code -------------------------------------------------------------------


class RunFailed(Exception):
    pass


def run_harness(command: str, files: dict[str, str], *extra: str) -> dict[str, Any]:
    """Run harness/cli.py on a temporary folder holding `files`."""
    with tempfile.TemporaryDirectory() as workdir:
        for name, text in files.items():
            (Path(workdir) / name).write_text(text, encoding="utf-8", newline="\n")
        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(HARNESS_CLI), command, workdir, *extra],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=RUN_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RunFailed(
                f"ran for over {RUN_TIMEOUT_SECONDS}s (a loop that never ends?)"
            ) from exc
    if completed.returncode != 0:
        raise RunFailed(completed.stderr.strip() or "the harness crashed")
    return json.loads(completed.stdout)


def all_pass(report: dict[str, Any]) -> bool:
    return (
        report["status"] == "ok"
        and report["total"] > 0
        and report["passed"] == report["total"]
    )


def describe(result: dict[str, Any]) -> str:
    if result["status"] == "error":
        return result["message"]
    failing = [r for r in result["results"] if r["outcome"] != "pass"]
    details = "; ".join(f"{r['name']}: {r['message']}" for r in failing[:3])
    return f"{result['passed']}/{result['total']} passed ({details})"


def check_exercise(folder: Path, exercise: Exercise, report: Report, run: bool) -> None:
    yaml_file = folder / "exercise.yaml"
    solution, tests, starter = (
        folder / "solution.py",
        folder / "test_exercise.py",
        folder / "starter.py",
    )
    for required in (solution, tests):
        if not required.exists():
            report.add(yaml_file, f"needs {required.name}")
    if exercise.stage in STAGES_WITH_FAILING_STARTER and not starter.exists():
        report.add(yaml_file, f"a {exercise.stage} exercise needs starter.py")
    if not run or not (solution.exists() and tests.exists()):
        return

    test_text = tests.read_text(encoding="utf-8")

    def check(code: Path) -> dict[str, Any] | None:
        report.counts["runs"] += 1
        try:
            return run_harness(
                "check",
                {
                    "solution.py": code.read_text(encoding="utf-8"),
                    "test_exercise.py": test_text,
                },
            )
        except RunFailed as exc:
            report.add(code, str(exc))
            return None

    result = check(solution)
    if result is not None and not all_pass(result):
        report.add(
            solution, f"the reference solution must pass every test: {describe(result)}"
        )

    if exercise.stage in STAGES_WITH_FAILING_STARTER and starter.exists():
        result = check(starter)
        if result is not None and all_pass(result):
            report.add(starter, "the starter must fail the tests, but it passes")

    for wrong in sorted(folder.glob("wrong/*.py")):
        result = check(wrong)
        if result is not None and all_pass(result):
            report.add(wrong, "a known-wrong solution must fail a test, but it passes")


def check_predict_output(path: Path, item: PredictOutputItem, report: Report) -> None:
    report.counts["runs"] += 1
    try:
        result = run_harness("run", {"solution.py": item.code})
    except RunFailed as exc:
        report.add(path, str(exc))
        return
    if result["error"]:
        report.add(path, f"the code crashes:\n{result['error']}")
    elif result["waiting_for_input"]:
        report.add(path, "the code asks for input; predict-the-output code must not")
    elif result["output"] != item.expected_output:
        expected, actual = item.expected_output, result["output"]
        report.add(
            path,
            f"expected_output is {expected!r}, but the code prints {actual!r}",
        )


# --- Putting it together ---------------------------------------------------------


def validate(root: Path = ROOT, run: bool = True) -> Report:
    report = Report(root)
    content = root / "content"

    tracks: dict[Path, Track] = {}
    for path in sorted((content / "tracks").glob("*.yaml")):
        track = load(path, Track, report)
        if track is not None:
            tracks[path] = track

    topics: dict[str, TopicFolder] = {}
    for folder in sorted(p for p in (content / "topics").glob("*") if p.is_dir()):
        loaded = load_topic_folder(folder, report)
        if loaded is None:
            continue
        if loaded.topic.id in topics:
            report.add(
                folder / "topic.yaml", f"topic id {loaded.topic.id!r} is used twice"
            )
            continue
        topics[loaded.topic.id] = loaded

    check_tracks(tracks, topics, report)
    check_prerequisites(topics, report)

    for folder in topics.values():
        report.counts[folder.topic.status] += 1
        check_references(folder, report)
        if folder.topic.status == "ready":
            check_ready_topic(folder, report)
        for item_path_id, item in folder.recall.items():
            report.counts["recall items"] += 1
            if isinstance(item, PredictOutputItem) and run:
                check_predict_output(
                    folder.path / "recall" / f"{item_path_id}.yaml", item, report
                )
        for exercise_folder, exercise in folder.exercises.values():
            report.counts["exercises"] += 1
            check_exercise(exercise_folder, exercise, report, run)

    report.counts["topics"] = len(topics)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check everything in content/.")
    parser.add_argument("--no-run", action="store_true", help="don't run any code")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    report = validate(args.root, run=not args.no_run)
    c = report.counts
    print(
        f"Checked {c['topics']} topics ({c['ready']} ready, {c['draft']} draft, "
        f"{c['planned']} planned), {c['exercises']} exercises, {c['recall items']} "
        f"recall items; ran {c['runs']} programs."
    )
    if report.problems:
        print(f"\n{len(report.problems)} problem(s):")
        for problem in report.problems:
            print(f"  - {problem}")
        return 1
    print("No problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

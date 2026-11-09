"""Check everything in content/ before it can reach a learner (v1 spec, F2).

Run from the repository root:

    python -m uv run python tools/validate_content.py           # everything
    python -m uv run python tools/validate_content.py --no-run  # skip running code

It checks:
- every file's format (content_model.py), and that IDs match their folders;
- the topic map: tracks, modules, prerequisites, and no cycles;
- that "ready" topics have everything a topic needs (the content definition of
  done in docs/specs/v1.md), and ready checkpoints a way through for a learner
  who's stuck, with every test naming the skills it checks (ADR-0012);
- by running them through the shared harness, like the browser does: every
  reference solution passes its tests, every starter and known-wrong solution
  fails them, and every predict-the-output item prints what it claims.

It prints every problem it finds and exits with status 1 if there are any.
"""

from __future__ import annotations

import argparse
import ast
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
    FOLLOW_UP_STAGES,
    STAGES_WITH_FAILING_STARTER,
    STAGES_WITH_HIDDEN_TESTS,
    Exercise,
    McqItem,
    Module,
    ParsonsItem,
    PredictOutputItem,
    Topic,
    Track,
    recall_item,
)
from pydantic import BaseModel, TypeAdapter, ValidationError

AnyItem = McqItem | PredictOutputItem | ParsonsItem | Exercise

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
    recall: dict[str, McqItem | PredictOutputItem | ParsonsItem] = field(
        default_factory=dict
    )
    exercises: dict[str, tuple[Path, Exercise]] = field(default_factory=dict)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.recall or item_id in self.exercises

    def stage_of(self, item_id: str | None) -> str | None:
        """An exercise's stage or a recall item's type; None if there's no such item."""
        if item_id in self.exercises:
            return self.exercises[item_id][1].stage
        if item_id in self.recall:
            return self.recall[item_id].type
        return None

    def items(self) -> list[tuple[Path, AnyItem]]:
        """Every question and exercise, with the file it came from."""
        found: list[tuple[Path, AnyItem]] = [
            (self.path / "recall" / f"{item.id}.yaml", item)
            for item in self.recall.values()
        ]
        found += [
            (folder / "exercise.yaml", exercise)
            for folder, exercise in self.exercises.values()
        ]
        return found


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


def checkpoints_of(module: Module) -> list[str]:
    """A module's checkpoint, and its capstone if it has one."""
    return [module.checkpoint, *([module.capstone] if module.capstone else [])]


def check_tracks(
    tracks: dict[Path, Track], topics: dict[str, TopicFolder], report: Report
) -> None:
    orders: dict[int, Path] = {}
    for path, track in tracks.items():
        if track.order in orders:
            report.add(
                path, f"order {track.order} is also {orders[track.order].name}'s"
            )
        orders[track.order] = path

    placed: dict[str, Path] = {}
    for path, track in tracks.items():
        for module in track.modules:
            for topic_id in [*module.topics, *checkpoints_of(module)]:
                expected_kind = (
                    "checkpoint" if topic_id in checkpoints_of(module) else "topic"
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
    stage_of = folder.stage_of

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
        recall_count = stages["mcq"] + stages["predict_output"] + stages["parsons"]
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
        if not review_stages & {"predict_output", "parsons", "review_code"}:
            report.add(
                topic_file,
                "the review pool needs a predict-the-output, Parsons or "
                "review_code item",
            )
        for item_id in topic.review_pool:
            review_kinds = {None, "mcq", "predict_output", "parsons", "review_code"}
            if stage_of(item_id) not in review_kinds:
                report.add(topic_file, f"{item_id!r} can't be a review item")
    elif topic.review_pool:
        report.add(topic_file, "checkpoints don't have review pools")

    if topic.prove.build is None or stage_of(topic.prove.build) != "build":
        report.add(topic_file, "prove.build must name a build exercise")
    if topic.prove.debug is None or stage_of(topic.prove.debug) != "debug":
        report.add(topic_file, "prove.debug must name a debug exercise")
    if topic.prove.explain is None:
        report.add(topic_file, "prove.explain is missing")

    if topic.kind == "topic":
        check_skills(folder, report)


def check_skills(folder: TopicFolder, report: Report) -> None:
    """A missed question must be able to come back as a different one on the
    same skill (ADR-0011)."""
    topic_file = folder.path / "topic.yaml"
    if not folder.topic.skills:
        report.add(topic_file, "a ready topic needs skills (ADR-0011)")

    follow_ups: Counter[str] = Counter()
    for path, item in folder.items():
        is_example = isinstance(item, Exercise) and item.stage == "worked_example"
        if not item.skills and not is_example:
            report.add(path, "needs at least one skill")
        if not isinstance(item, Exercise) or item.stage in FOLLOW_UP_STAGES:
            follow_ups.update(set(item.skills))

    for skill in folder.topic.skills:
        if follow_ups[skill.id] < 2:
            report.add(
                topic_file,
                f"skill {skill.id!r} needs at least 2 questions that can come "
                "back after a miss (recall items, or fill-in, write or "
                f"review_code exercises), but has {follow_ups[skill.id]}",
            )


# --- Checkpoints: a way through for a learner who's stuck (ADR-0012) ---------------

# The build, in this many partly written steps (the ADR says 3 or 4).
FEWEST_STEPS = 3
# Fresh versions of the build, so a second try can be fresh too.
FEWEST_VERSIONS = 2


@dataclass(frozen=True)
class CheckpointPlace:
    """Where a checkpoint sits in its track."""

    # The topics of its own module.
    module_topics: list[str]
    # Those and the topics of every module before it: the ones whose skills
    # its tests may name.
    topics_so_far: list[str]


def checkpoint_places(tracks: dict[Path, Track]) -> dict[str, CheckpointPlace]:
    places: dict[str, CheckpointPlace] = {}
    for track in tracks.values():
        so_far: list[str] = []
        for module in track.modules:
            so_far = [*so_far, *module.topics]
            places[module.checkpoint] = CheckpointPlace(list(module.topics), so_far)
            # A capstone ends a stage, so it builds on everything before it.
            if module.capstone:
                places[module.capstone] = CheckpointPlace(so_far, so_far)
    return places


def find_test_names(test_file: Path) -> list[str] | None:
    """The tests in a test file, found the way the harness finds them: every
    top-level function whose name starts with test_. None if it can't be read."""
    try:
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
    except OSError, SyntaxError:
        return None
    return [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def check_test_skills(
    folder: TopicFolder,
    topics: dict[str, TopicFolder],
    place: CheckpointPlace | None,
    report: Report,
) -> None:
    """The tests and skills that test_skills names must exist, whatever the
    checkpoint's status."""
    for exercise_folder, exercise in folder.exercises.values():
        if not exercise.test_skills:
            continue
        path = exercise_folder / "exercise.yaml"
        if folder.topic.kind != "checkpoint":
            report.add(
                path,
                "only checkpoint exercises have test_skills; "
                "a topic's items name their skills with skills:",
            )
            continue
        tests = find_test_names(exercise_folder / "test_exercise.py")
        for test, refs in exercise.test_skills.items():
            if tests is not None and test not in tests:
                report.add(
                    path,
                    f"test_skills names {test!r}, "
                    "which isn't a test in test_exercise.py",
                )
            for ref in refs:
                topic_id, skill_id = ref.split("/")
                target = topics.get(topic_id)
                if target is None:
                    report.add(path, f"{test}: topic {topic_id!r} doesn't exist")
                elif skill_id not in {skill.id for skill in target.topic.skills}:
                    report.add(
                        path, f"{test}: {topic_id} doesn't declare skill {skill_id!r}"
                    )
                elif place is not None and topic_id not in place.topics_so_far:
                    report.add(
                        path,
                        f"{test}: {topic_id!r} comes after this checkpoint, "
                        "so the checkpoint can't test its skills",
                    )


def check_ready_checkpoint(
    folder: TopicFolder,
    topics: dict[str, TopicFolder],
    place: CheckpointPlace | None,
    report: Report,
) -> None:
    """A ready checkpoint has a way through for a learner who's stuck, and
    every test of its builds and debug names the skills it checks."""
    topic = folder.topic
    topic_file = folder.path / "topic.yaml"

    for topic_id in place.module_topics if place else []:
        status = topics[topic_id].topic.status if topic_id in topics else "missing"
        if status != "ready":
            report.add(
                topic_file,
                "a ready checkpoint needs every topic of its module ready, "
                f"but {topic_id!r} is {status}",
            )

    unstuck = topic.unstuck
    if unstuck is None:
        report.add(
            topic_file,
            "a ready checkpoint needs unstuck: an example, steps and versions "
            "(ADR-0012)",
        )
        return
    if folder.stage_of(unstuck.example) != "worked_example":
        report.add(topic_file, "unstuck.example must name a worked example")

    if len(unstuck.steps) < FEWEST_STEPS:
        report.add(topic_file, f"unstuck.steps needs at least {FEWEST_STEPS} steps")
    for step in unstuck.steps:
        if folder.stage_of(step) != "fill_in":
            report.add(topic_file, f"unstuck step {step!r} must be a fill-in exercise")
        elif not folder.exercises[step][1].hints:
            report.add(topic_file, f"unstuck step {step!r} needs hints")

    if len(unstuck.versions) < FEWEST_VERSIONS:
        report.add(
            topic_file,
            f"unstuck.versions needs at least {FEWEST_VERSIONS} fresh versions "
            "of the build",
        )
    for version in unstuck.versions:
        if folder.stage_of(version) != "build":
            report.add(topic_file, f"unstuck version {version!r} must be a build")
        elif version == topic.prove.build:
            report.add(
                topic_file,
                f"unstuck version {version!r} is the build itself; "
                "versions must be fresh ones",
            )

    for item_id in [topic.prove.build, topic.prove.debug, *unstuck.versions]:
        if item_id not in folder.exercises:
            continue
        exercise_folder, exercise = folder.exercises[item_id]
        tests = find_test_names(exercise_folder / "test_exercise.py") or []
        missing = [test for test in tests if test not in exercise.test_skills]
        if missing:
            report.add(
                exercise_folder / "exercise.yaml",
                "every test needs the skills it checks in test_skills "
                f"(ADR-0012), but these have none: {', '.join(missing)}",
            )


def resource_indexes(lesson_text: str) -> list[int]:
    """The N of every <Resource index={N} /> tag in a lesson."""
    return [int(n) for n in re.findall(r"<Resource\s+index=\{(\d+)\}", lesson_text)]


def check_references(folder: TopicFolder, report: Report) -> None:
    """Every item and skill a topic names must exist, whatever its status."""
    declared = {skill.id for skill in folder.topic.skills}
    for path, item in folder.items():
        for skill in item.skills:
            if skill not in declared:
                report.add(
                    path, f"names skill {skill!r}, which topic.yaml doesn't declare"
                )

    named = [*folder.topic.practice, *folder.topic.review_pool]
    named += [i for i in (folder.topic.prove.build, folder.topic.prove.debug) if i]
    unstuck = folder.topic.unstuck
    if unstuck is not None:
        named += [i for i in (unstuck.example,) if i]
        named += [*unstuck.steps, *unstuck.versions]
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

    def check(code: str, where: Path) -> dict[str, Any] | None:
        report.counts["runs"] += 1
        try:
            return run_harness(
                "check", {"solution.py": code, "test_exercise.py": test_text}
            )
        except RunFailed as exc:
            report.add(where, str(exc))
            return None

    def check_file(code: Path) -> dict[str, Any] | None:
        return check(code.read_text(encoding="utf-8"), code)

    result = check_file(solution)
    if result is not None and not all_pass(result):
        report.add(
            solution, f"the reference solution must pass every test: {describe(result)}"
        )

    if exercise.stage in STAGES_WITH_FAILING_STARTER and starter.exists():
        result = check_file(starter)
        if result is not None and all_pass(result):
            report.add(starter, "the starter must fail the tests, but it passes")

    for wrong in sorted(folder.glob("wrong/*.py")):
        result = check_file(wrong)
        if result is not None and all_pass(result):
            report.add(wrong, "a known-wrong solution must fail a test, but it passes")

    if exercise.stage in STAGES_WITH_HIDDEN_TESTS:
        # The page hides why a hidden test failed, but shows a crash, which
        # should be in the learner's own code. An empty program can't crash,
        # so a crash here is in the tests, and would show how they work.
        result = check("", tests)
        for crashed in result["results"] if result else []:
            if crashed["outcome"] == "error":
                report.add(
                    tests,
                    f"{crashed['name']} crashes on an empty program "
                    f"({crashed['message']}); make it fail with an assert instead, "
                    "because the page shows crashes even in hidden tests",
                )


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


def check_parsons(path: Path, item: ParsonsItem, report: Report) -> None:
    """The lines in order must make a program that runs, without input or error."""
    report.counts["runs"] += 1
    program = "\n".join(item.lines) + "\n"
    try:
        result = run_harness("run", {"solution.py": program})
    except RunFailed as exc:
        report.add(path, str(exc))
        return
    if result["error"]:
        report.add(path, f"the lines in order crash:\n{result['error']}")
    elif result["waiting_for_input"]:
        report.add(path, "the lines ask for input; a Parsons program must not")


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
    places = checkpoint_places(tracks)

    for folder in topics.values():
        place = places.get(folder.topic.id)
        report.counts[folder.topic.status] += 1
        check_references(folder, report)
        check_test_skills(folder, topics, place, report)
        if folder.topic.status == "ready":
            check_ready_topic(folder, report)
            if folder.topic.kind == "checkpoint":
                check_ready_checkpoint(folder, topics, place, report)
        for item_path_id, item in folder.recall.items():
            report.counts["recall items"] += 1
            item_path = folder.path / "recall" / f"{item_path_id}.yaml"
            if isinstance(item, PredictOutputItem) and run:
                check_predict_output(item_path, item, report)
            elif isinstance(item, ParsonsItem) and run:
                check_parsons(item_path, item, report)
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

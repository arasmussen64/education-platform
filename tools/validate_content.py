"""Check everything in content/ before it can reach a learner (v1 spec, F2).

Run from the repository root:

    python -m uv run python tools/validate_content.py           # everything
    python -m uv run python tools/validate_content.py --no-run  # skip running code

It checks:
- every file's format (content_model.py), and that IDs match their folders;
- the topic map: tracks, modules, prerequisites, and no cycles;
- that "ready" topics have everything a topic needs (the content definition of
  done in docs/specs/v1.md), and ready checkpoints a way through for a learner
  who's stuck, with every test naming the skills it checks (ADR-0012), and
  further parts (prove.more) that are builds or debugs like their own;
- by running them through the shared harness, like the browser does: every
  reference solution passes its tests, every starter and known-wrong solution
  fails them, and every predict-the-output item prints what it claims;
- that a Parsons item's lines work in one order only: no other order, and no
  decoy put in place of a line, may run and print the same output (ADR-0016);
- that a multiple-choice explanation never names a choice by its position,
  because the app shuffles the choices;
- that a multiple-choice item's right answer doesn't stand out by its length:
  not over 1.5 times the longest wrong choice, and not the longest choice in
  more than half of a topic's items (mcq_lengths.py, which also explains the
  baseline of older items and --write-mcq-baseline);
- by running every predict_shell item's command in real bash (ADR-0017), in
  a temporary folder holding the item's files, and checking what it prints.
- that every estimate's working gives its answer and each known mistake's
  gives that mistake's value, and that the tolerance accepts the answer and
  none of the mistakes (ADR-0024). It's plain arithmetic, so --no-run checks it.
- the diagnostics the placement test walks (ADR-0021): their shape and ids.

It prints every problem it finds and exits with status 1 if there are any.
"""

from __future__ import annotations

import argparse
import ast
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

import arithmetic
import mcq_lengths
import parsons_orders
import yaml
from content_model import (
    FOLLOW_UP_STAGES,
    STAGES_WITH_FAILING_STARTER,
    STAGES_WITH_HIDDEN_TESTS,
    Diagnostic,
    EstimateItem,
    Exercise,
    LabChecks,
    McqItem,
    Module,
    ParsonsItem,
    PredictOutputItem,
    PredictShellItem,
    Topic,
    Track,
    recall_item,
)
from pydantic import BaseModel, TypeAdapter, ValidationError

AnyRecall = McqItem | PredictOutputItem | ParsonsItem | PredictShellItem | EstimateItem
AnyItem = AnyRecall | Exercise
# The recall kinds that ask the learner to produce an answer, the output or a
# number, rather than choose one. An estimate counts (ADR-0024).
PREDICT_KINDS = {"predict_output", "predict_shell", "estimate"}

ROOT = Path(__file__).resolve().parents[1]
HARNESS_CLI = ROOT / "harness" / "cli.py"
RUN_TIMEOUT_SECONDS = 20
# The quick first pass over a Parsons item's other orders (parsons_screen.py).
PARSONS_SCREEN = Path(__file__).resolve().parent / "parsons_screen.py"
SCREEN_TIMEOUT_SECONDS = 120
# How many fresh Python processes run at once when other orders are checked.
# Each is a separate process, so they can't get in each other's way.
ORDERS_AT_ONCE = 4


@dataclass
class Report:
    root: Path
    problems: list[str] = field(default_factory=list)
    counts: Counter[str] = field(default_factory=Counter)
    # Every item and topic that breaks an answer-length rule, including the
    # ones the baseline tolerates: what --write-mcq-baseline writes from.
    long_answers: mcq_lengths.Offenders = field(default_factory=mcq_lengths.Offenders)

    def add(self, path: Path, message: str) -> None:
        where = path.relative_to(self.root).as_posix()
        self.problems.append(f"{where}: {message}")


@dataclass
class TopicFolder:
    path: Path
    topic: Topic
    recall: dict[str, AnyRecall] = field(default_factory=dict)
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

# An apostrophe between letters written twice, as in don''t. Inside a
# single-quoted YAML scalar that is how an apostrophe is spelled, but in a
# block (|) or double-quoted scalar YAML keeps both, and the learner sees
# don''t on the page. The pattern skips '' used as an empty Python string.
DOUBLED_APOSTROPHE = re.compile(r"(?<=\w)''(?=[\w\s]|$)")


def doubled_apostrophes(data: Any) -> list[str]:
    """Every string in the loaded YAML that kept a doubled apostrophe."""
    if isinstance(data, str):
        return [data] if DOUBLED_APOSTROPHE.search(data) else []
    if isinstance(data, dict):
        return [s for value in data.values() for s in doubled_apostrophes(value)]
    if isinstance(data, list):
        return [s for value in data for s in doubled_apostrophes(value)]
    return []


def load(path: Path, shape: type[BaseModel] | TypeAdapter[Any], report: Report):
    """Read a YAML file and check its shape. Returns None if it's broken."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        report.add(path, f"isn't valid YAML: {exc}")
        return None
    except ValueError as exc:
        # YAML reads 2026-13-40 as a date (an estimate's prices_as_of), and a
        # date that doesn't exist raises this rather than a YAML error.
        report.add(path, f"has a value that can't be read: {exc}")
        return None
    for text in doubled_apostrophes(data):
        match = DOUBLED_APOSTROPHE.search(text)
        snippet = text[max(0, match.start() - 12) : match.end() + 12] if match else text
        report.add(
            path,
            f"keeps a doubled apostrophe ({snippet.strip()!r}): in a block or "
            "double-quoted scalar '' stays as two apostrophes, so write one",
        )
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
        recall_count = sum(stages[kind] for kind in ("mcq", "parsons", *PREDICT_KINDS))
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
        if not review_stages & {*PREDICT_KINDS, "parsons", "review_code"}:
            report.add(
                topic_file,
                "the review pool needs a predict-the-output, estimate, Parsons "
                "or review_code item",
            )
        for item_id in topic.review_pool:
            review_kinds = {None, "mcq", *PREDICT_KINDS, "parsons", "review_code"}
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


def find_check_ids(checks_file: Path) -> list[str] | None:
    """A lab's check ids, from checks.yaml. None if it can't be read."""
    try:
        data = yaml.safe_load(checks_file.read_text(encoding="utf-8"))
        return [check.id for check in LabChecks.model_validate(data).checks]
    except OSError, yaml.YAMLError, ValidationError:
        return None


def test_names_of(folder: Path, exercise: Exercise) -> list[str] | None:
    """What test_skills may name: test functions for Python, check ids for a lab."""
    if exercise.runtime == "lab":
        return find_check_ids(folder / "checks.yaml")
    return find_test_names(folder / "test_exercise.py")


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
        tests = test_names_of(exercise_folder, exercise)
        where = "checks.yaml" if exercise.runtime == "lab" else "test_exercise.py"
        for test, refs in exercise.test_skills.items():
            if tests is not None and test not in tests:
                report.add(
                    path,
                    f"test_skills names {test!r}, which isn't a test in {where}",
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
        tests = test_names_of(exercise_folder, exercise) or []
        missing = [test for test in tests if test not in exercise.test_skills]
        if missing:
            report.add(
                exercise_folder / "exercise.yaml",
                "every test needs the skills it checks in test_skills "
                f"(ADR-0012), but these have none: {', '.join(missing)}",
            )


# --- Checkpoints: further parts (ADR-0012, amended 2026-11-11) --------------------

# What a further part can be: one more build or debug, like the checkpoint's own.
PART_STAGES = ("build", "debug")


def check_more_parts(folder: TopicFolder, report: Report) -> None:
    """A ready checkpoint's further parts (prove.more) are each a build or a
    debug, their fresh versions are the same kind, a build part has a fresh
    version, and every test of them names the skills it checks."""
    topic_file = folder.path / "topic.yaml"
    for part in folder.topic.prove.more:
        stage = folder.stage_of(part.id)
        if stage not in PART_STAGES:
            report.add(
                topic_file,
                f"prove.more part {part.id!r} must be a build or debug exercise"
                + (f", but it's a {stage}" if stage else ""),
            )
            continue
        # The reason a build has fresh versions, a second try that can't be
        # passed from memory, holds for every build. A second debug waits
        # until learners are seen to need one, as ADR-0012 says.
        if stage == "build" and not part.versions:
            report.add(
                topic_file,
                f"prove.more part {part.id!r} is a build, so it needs at least 1 "
                "fresh version in versions: the same skills in another story",
            )
        for version in part.versions:
            if folder.stage_of(version) != stage:
                report.add(
                    topic_file,
                    f"prove.more version {version!r} must be a {stage}, "
                    f"like its part {part.id!r}",
                )
        for item_id in (part.id, *part.versions):
            check_every_test_names_skills(folder, item_id, report)


def check_every_test_names_skills(
    folder: TopicFolder, item_id: str, report: Report
) -> None:
    """Every test of a checkpoint's proof exercise names the skills it checks,
    so a failed one brings them back (ADR-0012)."""
    if item_id not in folder.exercises:
        return
    exercise_folder, exercise = folder.exercises[item_id]
    tests = test_names_of(exercise_folder, exercise) or []
    missing = [test for test in tests if test not in exercise.test_skills]
    if missing:
        report.add(
            exercise_folder / "exercise.yaml",
            "every test needs the skills it checks in test_skills "
            f"(ADR-0012), but these have none: {', '.join(missing)}",
        )


IMPORTS_NUMPY = re.compile(r"^\s*(import|from)\s+numpy\b", re.MULTILINE)


def check_packages(folder: TopicFolder, report: Report) -> None:
    """Code that imports a package must belong to a topic that declares it in
    packages: (ADR-0023); otherwise it works on GitHub and fails in the
    browser, where the package is loaded only for topics that ask."""
    declared = set(folder.topic.packages)
    sources: list[tuple[Path, str]] = [
        (path, path.read_text(encoding="utf-8"))
        for path in sorted(folder.path.rglob("*.py"))
    ]
    for path, item in folder.items():
        code = getattr(item, "code", None)
        if isinstance(code, str):
            sources.append((path, code))
        lines = getattr(item, "lines", None)
        if isinstance(lines, list):
            sources.append((path, "\n".join(str(line) for line in lines)))
    for path, source in sources:
        if IMPORTS_NUMPY.search(source) and "numpy" not in declared:
            report.add(
                path,
                "imports numpy, but topic.yaml doesn't list it under packages: "
                "(ADR-0023), so it would fail in the browser",
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
    named += folder.topic.prove.more_items()
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


def check_lab_base(dockerfile: Path, report: Report) -> None:
    """A lab that starts FROM a shared base (ADR-0018, third amendment) names
    one that exists in content/lab-bases/, in the form the checker reads, or
    the checker can't build it and Docker would go looking for it online."""
    import labcheck

    text = dockerfile.read_text(encoding="utf-8")
    if not labcheck.NAMES_A_BASE.search(text):
        return
    bases = report.root / "content" / "lab-bases"
    there = sorted(p.name for p in bases.glob("*") if (p / "Dockerfile").exists())
    listed = ", ".join(there) or "none yet"
    name = labcheck.base_named_in(text)
    if name is None:
        report.add(
            dockerfile,
            "a FROM line names a lab base in a form the checker can't read: write "
            "FROM lab-base-<name> alone on its line, with the name in lowercase "
            f"letters, digits and hyphens (the bases are: {listed})",
        )
    elif name not in there:
        report.add(
            dockerfile,
            f"starts FROM lab-base-{name}, but there is no "
            f"content/lab-bases/{name}/Dockerfile to build it from (the bases "
            f"are: {listed}); fix the name, or add that base",
        )


def check_lab(folder: Path, exercise: Exercise, report: Report, run: bool) -> None:
    """A lab (ADR-0018) needs its image, its checks and its solution. Its
    contract (pristine fails, the solution passes, wrong fixes fail) needs
    Docker, so it runs only with --labs; CI's Labs job runs it for every lab."""
    yaml_file = folder / "exercise.yaml"
    for name in ("Dockerfile", "checks.yaml", "solution.sh"):
        if not (folder / name).exists():
            report.add(yaml_file, f"a lab needs {name}")
    if (folder / "Dockerfile").exists():
        check_lab_base(folder / "Dockerfile", report)
    if (folder / "checks.yaml").exists():
        load(folder / "checks.yaml", LabChecks, report)
    # A lab's scenario may well include a Python program; what it can't have
    # is a Python exercise's files, which would mean two kinds of checks.
    for name in ("starter.py", "solution.py", "test_exercise.py"):
        if (folder / name).exists():
            report.add(
                folder / name,
                f"a lab has no {name}; its checks are in checks.yaml "
                "and its reference fix in solution.sh",
            )
    if (
        not run
        or report.problems
        and any(
            str(folder.relative_to(report.root).as_posix()) in p
            for p in report.problems
        )
    ):
        return
    import labcheck

    report.counts["labs run"] += 1
    try:
        lab = labcheck.load_lab(folder.parents[1].name, exercise.id, folder.parents[2])
        contract = labcheck.test_lab(lab, verbose=False)
    except labcheck.LabError as exc:
        report.add(yaml_file, str(exc))
        return
    for problem in contract.problems:
        report.add(yaml_file, f"the lab's contract is broken: {problem}")


def check_exercise(
    folder: Path, exercise: Exercise, report: Report, run: bool, labs: bool = False
) -> None:
    if exercise.runtime == "lab":
        check_lab(folder, exercise, report, run=labs)
        return
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
    """The lines in order must make a program that runs, without input or
    error, and no other arrangement of them may do the same job."""
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
    else:
        check_parsons_orders(path, item, result["output"], report)


def programs_that_finish(authored: str, programs: list[str]) -> list[int]:
    """Which of `programs` (by position) run to the end without an error.

    A quick first pass: parsons_screen.py runs them all inside one fresh
    Python process, in an empty temporary folder. Its answer is trusted only
    to rule programs out; the ones it lets through are run again one by one.
    """
    job = json.dumps({"authored": authored, "programs": programs})
    with tempfile.TemporaryDirectory() as workdir:
        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(PARSONS_SCREEN)],
                input=job,
                cwd=workdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=SCREEN_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RunFailed(
                "trying the other orders of the lines took over "
                f"{SCREEN_TIMEOUT_SECONDS}s"
            ) from exc
    # The answer is the last line it prints. No answer means it was stopped
    # part-way, by a program that ends the whole process, say.
    printed = completed.stdout.splitlines()
    if completed.returncode != 0 or not printed:
        raise RunFailed(
            "trying the other orders of the lines crashed:\n" + completed.stderr.strip()
        )
    answer = json.loads(printed[-1])
    if answer["carried_over"]:
        # The programs affected each other, so the first pass can't be
        # trusted: let every program through to be run on its own.
        return list(range(len(programs)))
    return answer["finished"]


def prints_the_same(program: str, output: str) -> bool:
    """Whether the program, run through the harness in a process of its own,
    finishes without an error and prints exactly `output`."""
    try:
        result = run_harness("run", {"solution.py": program})
    except RunFailed:
        return False
    return (
        not result["error"]
        and not result["waiting_for_input"]
        and result["output"] == output
    )


def arrangements_that_work(
    item: ParsonsItem, output: str, report: Report
) -> list[parsons_orders.Arrangement]:
    """The other arrangements of the item's lines that run without an error
    and print exactly `output`, which is what the author's order prints."""
    authored = "\n".join(item.lines) + "\n"
    tried = parsons_orders.arrangements(item.lines, item.distractors)
    report.counts["arrangements"] += len(tried)
    finished = programs_that_finish(authored, [each.program for each in tried])

    # Output is compared only here, one fresh process per program, because
    # programs that share a process can change what each other prints.
    candidates = [tried[position] for position in finished]
    report.counts["runs"] += len(candidates)

    def works(arrangement: parsons_orders.Arrangement) -> bool:
        return prints_the_same(arrangement.program, output)

    with ThreadPoolExecutor(ORDERS_AT_ONCE) as pool:
        verdicts = list(pool.map(works, candidates))
    return [each for each, ok in zip(candidates, verdicts, strict=True) if ok]


def check_parsons_orders(
    path: Path, item: ParsonsItem, output: str, report: Report
) -> None:
    """Only the author's order may work.

    The app accepts the author's order and nothing else, so another order of
    the same lines that runs and prints the same `output` is a working answer
    that gets marked wrong. The same goes for the author's order with a decoy
    in place of a line. Every order is tried for an item of up to 7 lines;
    for a longer one, every swap of two lines and every move of a run of
    lines (parsons_orders.py).
    """
    try:
        working = arrangements_that_work(item, output, report)
    except RunFailed as exc:
        report.add(path, str(exc))
        return

    # One problem for all the orders, naming the simplest (they are listed
    # simplest first), and one for each place a decoy works.
    orders = [each for each in working if not each.uses_decoy]
    if orders:
        more = ""
        if len(orders) == 2:
            more = "; 1 more order works too"
        elif len(orders) > 2:
            more = f"; {len(orders) - 1} more orders work too"
        report.add(
            path,
            "another order of the lines runs and prints the same output, so a "
            "learner who builds it would be marked wrong: "
            f"{orders[0].description}{more}. Make each line need the one before "
            "it, or join the lines that don't depend on each other",
        )
    for each in working:
        if each.uses_decoy:
            report.add(
                path,
                f"{each.description} and the program still runs and prints the "
                "same output, so a learner who uses the decoy would be marked "
                "wrong. Change the decoy so the program crashes or prints "
                "something else",
            )


# --- Running shell commands (ADR-0017) -----------------------------------------------

SHELL_TIMEOUT_SECONDS = 10


@functools.cache
def find_bash() -> str | None:
    """Where bash is, or None.

    On Windows that's Git Bash, found next to git. It is never the bash.exe
    that Windows puts on PATH, which is only a launcher for WSL. Set
    VALIDATOR_BASH to use a particular bash.
    """
    chosen = os.environ.get("VALIDATOR_BASH")
    if chosen:
        return chosen
    if sys.platform == "win32":
        git = shutil.which("git")
        if git:
            git_root = Path(git).resolve().parents[1]
            for candidate in ("usr/bin/bash.exe", "bin/bash.exe"):
                if (git_root / candidate).exists():
                    return str(git_root / candidate)
    found = shutil.which("bash")
    if found and sys.platform == "win32" and "windowsapps" in found.lower():
        return None
    return found


def run_shell(item: PredictShellItem, bash: str) -> tuple[str, str]:
    """Runs the item's command in a temporary folder holding its files, with
    nothing on stdin. Returns what it wrote to stdout and to stderr."""
    with tempfile.TemporaryDirectory() as workdir:
        for name, text in item.files.items():
            path = Path(workdir) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        env = {
            **os.environ,
            # The same sort order and the same messages on every machine,
            # whatever language it's set to, and no dotfiles: HOME is empty.
            "LC_ALL": "C",
            "LANG": "C",
            "LANGUAGE": "C",
            "TZ": "UTC",
            "HOME": workdir,
        }
        try:
            completed = subprocess.run(
                [bash, "--noprofile", "--norc", "-c", item.command],
                cwd=workdir,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=SHELL_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RunFailed(
                f"ran for over {SHELL_TIMEOUT_SECONDS}s (a command waiting for input?)"
            ) from exc
    return (
        completed.stdout.decode("utf-8", errors="replace"),
        completed.stderr.decode("utf-8", errors="replace"),
    )


def check_predict_shell(path: Path, item: PredictShellItem, report: Report) -> None:
    """The command must print exactly expected_output, and nothing to stderr.

    Errors go to stderr, so a command that fails (a typo, a missing tool, a
    file that isn't there) is caught here. An item that wants to show an
    error message redirects it with 2>&1, so it's compared like the rest.
    """
    bash = find_bash()
    if bash is None:
        report.add(
            path,
            "needs bash to run the command: install Git for Windows, or set "
            "VALIDATOR_BASH to the bash to use",
        )
        return
    report.counts["runs"] += 1
    try:
        output, errors = run_shell(item, bash)
    except RunFailed as exc:
        report.add(path, str(exc))
        return
    if errors.strip():
        report.add(
            path,
            "the command writes to stderr, which a learner can't see on the "
            f"page (use 2>&1 to show it):\n{errors.strip()}",
        )
    elif output != item.expected_output:
        expected = item.expected_output
        report.add(
            path, f"expected_output is {expected!r}, but the command prints {output!r}"
        )


# --- Estimate questions (ADR-0024) ---------------------------------------------------

# A number as a prompt writes it: 12, 0.0416 or 2,016. Commas only between
# groups of three, so "2, 8 and 12" is three numbers.
STATED_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+")
# An IPv4 address, a dotted quad: 10.20.30.77 states four numbers, 10, 20, 30
# and 77, not 10.2, 0.3 and 0.77 (Module 3's estimates give addresses).
DOTTED_QUAD = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
# An amount of money: a currency sign before a number ($0.046, € 12), or a
# currency code beside one (12 USD).
MONEY = re.compile(r"[$€£¥]\s?\d|\d\s?(?:USD|EUR|GBP)\b|\b(?:USD|EUR|GBP)\s?\d")
# Code in Markdown, left out before looking for money: in a command, $1 is
# the shell's first argument, not a dollar.
MARKDOWN_CODE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
# A number both YAML readers agree on. Python's (YAML 1.1) also reads 10_000,
# 012 (as 10) and 1:30 (as 90); the browser's (YAML 1.2) reads them as text,
# 12 and text, so a number written that way is wrong on the page.
PLAIN_NUMBER = re.compile(r"[-+]?(?:\.\d+|(?:0|[1-9]\d*)(?:\.\d*)?)(?:[eE][-+]?\d+)?")
YAML_NUMBER_TAGS = {"tag:yaml.org,2002:int", "tag:yaml.org,2002:float"}


def numbers_in(text: str) -> set[Fraction]:
    """Every number the text states, exactly. Each dotted quad's four octets
    are read first, and the address is then taken out of the text, so the
    general pattern doesn't also read it as decimals."""
    octets = {
        Fraction(octet)
        for quad in DOTTED_QUAD.findall(text)
        for octet in quad.split(".")
    }
    rest = DOTTED_QUAD.sub(" ", text)
    return octets | {
        Fraction(found.replace(",", "")) for found in STATED_NUMBER.findall(rest)
    }


def mentions_money(prompt: str) -> bool:
    return MONEY.search(MARKDOWN_CODE.sub("", prompt)) is not None


def numbers_read_differently(path: Path) -> list[str]:
    """Numbers in the file written in a way only Python's YAML reads as that
    number: their text as written."""
    found: list[str] = []

    def walk(node: yaml.Node | None) -> None:
        if isinstance(node, yaml.ScalarNode):
            if node.tag in YAML_NUMBER_TAGS and not PLAIN_NUMBER.fullmatch(node.value):
                found.append(node.value)
        elif isinstance(node, yaml.SequenceNode):
            for child in node.value:
                walk(child)
        elif isinstance(node, yaml.MappingNode):
            for key, value in node.value:
                walk(key)
                walk(value)

    walk(yaml.compose(path.read_text(encoding="utf-8")))
    return found


def decimals_of(number: int | float) -> int:
    """How many decimal places the number is written with: 28 has none, 27.5
    one. A sum is rounded to this many before it's compared with it."""
    exponent = Decimal(repr(number)).as_tuple().exponent
    return max(0, -exponent) if isinstance(exponent, int) else 0


def inside(value: Fraction, answer: Fraction, item: EstimateItem) -> bool:
    """Whether the tolerance accepts `value`, edges included, as the page does."""
    tolerance = item.tolerance
    if tolerance.percent is not None:
        allowed = abs(answer) * arithmetic.exact(tolerance.percent) / 100
    else:
        allowed = arithmetic.exact(tolerance.absolute or 0)
    return abs(value - answer) <= allowed


def check_estimate(path: Path, item: EstimateItem, report: Report) -> None:
    """An estimate is proved like an exercise (ADR-0004, ADR-0024): its working
    gives its answer, each known mistake's working gives that mistake's value,
    and the tolerance accepts the answer and none of the mistakes. It's plain
    arithmetic, so it's checked under --no-run too."""
    for written in numbers_read_differently(path):
        report.add(
            path,
            f"the number {written} reads differently in the browser, whose YAML "
            "doesn't take underscores, leading zeros or colons in numbers; write "
            "it as plain digits, like 10000",
        )
    given = {name: arithmetic.exact(value) for name, value in item.given.items()}
    answer = arithmetic.exact(item.answer)
    check_given(path, item, given, report)
    check_working(path, item, given, answer, report)
    check_mistakes(path, item, given, answer, report)
    if mentions_money(item.prompt) and item.prices_as_of is None:
        report.add(
            path,
            "the prompt holds an amount of money, so it needs prices_as_of and "
            "prices_source: the day the prices were read, and the page that "
            "shows today's",
        )


def check_given(
    path: Path, item: EstimateItem, given: dict[str, Fraction], report: Report
) -> None:
    """The learner works from the prompt, so every given number is in it."""
    stated = numbers_in(item.prompt)
    for name, value in given.items():
        if name in arithmetic.FUNCTIONS:
            report.add(
                path,
                f"given {name!r} has the name of a function the working can call; "
                "call it something else, like min_cores",
            )
        elif name in arithmetic.RESERVED_WORDS:
            report.add(
                path,
                f"given {name!r} is a word Python keeps for itself, so a sum "
                "can't use it as a name; call it something else, like "
                f"{name}_count",
            )
        if abs(value) not in stated:
            report.add(
                path,
                f"given {name} is {arithmetic.show(value)}, which the prompt doesn't "
                "state: write it in the prompt in digits, or if the learner must "
                "know it, put it in the working as a plain number",
            )


def check_working(
    path: Path,
    item: EstimateItem,
    given: dict[str, Fraction],
    answer: Fraction,
    report: Report,
) -> None:
    """The working gives the answer, and a learner who works it out exactly is
    marked right."""
    worked = work_out(path, "the working", item.working, given, report)
    if worked is not None:
        rounded = arithmetic.round_half_up(worked, decimals_of(item.answer))
        if rounded != answer:
            report.add(
                path,
                f"the working gives {arithmetic.show(worked)}, but the answer is "
                f"{arithmetic.show(answer)}",
            )
        elif not inside(worked, answer, item):
            report.add(
                path,
                f"the working gives {arithmetic.show(worked)} exactly, which the "
                f"tolerance doesn't accept around {arithmetic.show(answer)}, so a "
                "learner who works it out exactly is marked wrong; write the "
                "answer with more decimals, or widen the tolerance",
            )


def check_mistakes(
    path: Path,
    item: EstimateItem,
    given: dict[str, Fraction],
    answer: Fraction,
    report: Report,
) -> None:
    """Each known mistake's working gives its value, the tolerance turns every
    one of them away, and no two give the same number, so the page can name
    the one a learner made."""
    first_with: dict[Fraction, str] = {}
    for mistake in item.mistakes:
        value = arithmetic.exact(mistake.value)
        where = f"mistake {mistake.id!r}"
        wrong = work_out(
            path, f"the working of {where}", mistake.working, given, report
        )
        if wrong is not None:
            rounded = arithmetic.round_half_up(wrong, decimals_of(mistake.value))
            if rounded != value:
                report.add(
                    path,
                    f"{where}: its working gives {arithmetic.show(wrong)}, but its "
                    f"value is {arithmetic.show(value)}",
                )
        # The value as written, and the working's exact value: neither may pass.
        accepted = [
            v for v in (value, wrong) if v is not None and inside(v, answer, item)
        ]
        if accepted:
            report.add(
                path,
                f"{where} gives {arithmetic.show(accepted[0])}, which the tolerance "
                "accepts, so a learner who makes that mistake is marked right; "
                "narrow the tolerance, or drop the mistake if it isn't one",
            )
        if value in first_with:
            report.add(
                path,
                f"mistakes {first_with[value]!r} and {mistake.id!r} both give "
                f"{arithmetic.show(value)}, so the page can't tell which one a "
                "learner made; merge them",
            )
        first_with.setdefault(value, mistake.id)


def work_out(
    path: Path,
    what: str,
    text: str,
    given: dict[str, Fraction],
    report: Report,
) -> Fraction | None:
    """The value of a working, or None (and a problem) if it isn't a sum."""
    try:
        return arithmetic.evaluate(text, given)
    except arithmetic.NotArithmetic as exc:
        report.add(path, f"{what} ({text.strip()!r}) {exc}")
        return None


# --- Multiple-choice explanations ----------------------------------------------------

# "The last choice", "the second option", "the first and last answers".
POSITION = r"(?:first|second|third|fourth|last)"
CHOICE_BY_POSITION = re.compile(
    rf"\b{POSITION}(?:(?:,|,?\s+and|,?\s+or)\s+(?:the\s+)?{POSITION})*"
    r"\s+(?:choice|option|answer)s?\b",
    re.IGNORECASE,
)


def choice_named_by_position(item: McqItem) -> str | None:
    """What's wrong, if the explanation points at a choice by where it sits.

    The app shows the choices shuffled (choiceOrder in
    web/src/components/scramble.ts), so "the last choice" is whichever one
    happens to be shown last, not the one the author wrote last. Only the
    words choice, option and answer are looked for: "the last line" and "the
    first one" are everyday phrases about code.
    """
    match = CHOICE_BY_POSITION.search(item.explanation)
    if match is None:
        return None
    phrase = " ".join(match.group(0).split())
    return (
        f"the explanation says {phrase!r}, but the app shuffles the choices, so "
        "a position points at the wrong one; name the choice by what it says"
    )


# --- Multiple-choice answer lengths (mcq_lengths.py) ---------------------------------


def find_long_answers(folder: TopicFolder, found: mcq_lengths.Offenders) -> None:
    """Note each of the topic's multiple-choice items whose right answer is
    far longer than its wrong ones, and the topic itself if its right answers
    are usually the longest. Whether they're problems is decided at the end,
    once the baseline of older items has been read."""
    items = [item for item in folder.recall.values() if isinstance(item, McqItem)]
    for item in items:
        problem = mcq_lengths.item_problem(item)
        if problem:
            key = mcq_lengths.item_key(folder.topic.id, item.id)
            found.items[key] = (folder.path / "recall" / f"{item.id}.yaml", problem)
    problem = mcq_lengths.topic_problem(items)
    if problem:
        found.topics[folder.topic.id] = (folder.path / "topic.yaml", problem)


def report_long_answers(report: Report) -> None:
    """Report the long answers the baseline doesn't tolerate, and the
    baseline's own mistakes: an entry that's fixed, or one from the cloud
    track."""
    baseline_file = report.root / mcq_lengths.BASELINE
    try:
        baseline = mcq_lengths.read_baseline(baseline_file)
    except mcq_lengths.BadBaseline as exc:
        report.add(baseline_file, str(exc))
        baseline = mcq_lengths.Baseline()
    found = report.long_answers
    for path, message in mcq_lengths.problems(found, baseline, baseline_file):
        report.add(path, message)


# --- Putting it together ---------------------------------------------------------


def check_diagnostics(
    content: Path, topics: dict[str, TopicFolder], report: Report
) -> None:
    """The diagnostics the placement test walks (ADR-0021): each file's shape,
    and that its id matches its file name, like a topic's folder."""
    for path in sorted((content / "diagnostics").glob("*.yaml")):
        diagnostic = load(path, Diagnostic, report)
        if diagnostic is None:
            continue
        report.counts["diagnostics"] += 1
        if diagnostic.id != path.stem:
            report.add(
                path,
                f"id {diagnostic.id!r} doesn't match the file name {path.stem!r}",
            )
        for level in diagnostic.levels:
            if level.topic is not None and level.topic not in topics:
                report.add(
                    path,
                    f"level {level.id!r} names a topic that doesn't exist: "
                    f"{level.topic!r}",
                )
            for item in level.items:
                problem = choice_named_by_position(item)
                if problem:
                    report.add(path, f"item {item.id!r}: {problem}")
                # A level has too few items for the topic rule, so only the
                # item rule applies to a diagnostic.
                problem = mcq_lengths.item_problem(item)
                if problem:
                    key = mcq_lengths.diagnostic_key(diagnostic.id, item.id)
                    report.long_answers.items[key] = (
                        path,
                        f"item {item.id!r}: {problem}",
                    )


def check_topic(
    folder: TopicFolder,
    topics: dict[str, TopicFolder],
    place: CheckpointPlace | None,
    report: Report,
    run: bool,
    labs: bool,
) -> None:
    """Every check on one topic: the topic itself, its recall items and its
    exercises. The full run calls it for each topic in turn, and
    tools/generators/checks/validate_one.py calls it for the topics it's
    given, so the quick check can't fall behind the full one (it once skipped
    a checkpoint's further parts and the estimate checks)."""
    report.counts[folder.topic.status] += 1
    check_references(folder, report)
    check_packages(folder, report)
    check_test_skills(folder, topics, place, report)
    if folder.topic.status == "ready":
        check_ready_topic(folder, report)
        if folder.topic.kind == "checkpoint":
            check_ready_checkpoint(folder, topics, place, report)
            check_more_parts(folder, report)
    find_long_answers(folder, report.long_answers)
    for item_path_id, item in folder.recall.items():
        report.counts["recall items"] += 1
        item_path = folder.path / "recall" / f"{item_path_id}.yaml"
        if isinstance(item, McqItem):
            problem = choice_named_by_position(item)
            if problem:
                report.add(item_path, problem)
        if isinstance(item, EstimateItem):
            check_estimate(item_path, item, report)
        if isinstance(item, PredictOutputItem) and run:
            check_predict_output(item_path, item, report)
        elif isinstance(item, ParsonsItem) and run:
            check_parsons(item_path, item, report)
        elif isinstance(item, PredictShellItem) and run:
            check_predict_shell(item_path, item, report)
    for exercise_folder, exercise in folder.exercises.values():
        report.counts["exercises"] += 1
        if exercise.runtime == "lab":
            report.counts["labs"] += 1
        check_exercise(exercise_folder, exercise, report, run, labs)


def validate(root: Path = ROOT, run: bool = True, labs: bool = False) -> Report:
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
        check_topic(
            folder, topics, places.get(folder.topic.id), report, run=run, labs=labs
        )

    check_diagnostics(content, topics, report)
    report_long_answers(report)
    report.counts["topics"] = len(topics)
    return report


def write_mcq_baseline(root: Path) -> int:
    """Write tools/mcq_length_baseline.yaml from the content as it is now.

    Nothing is run. The first time, the file lists every item and topic that
    breaks an answer-length rule; after that, the command only removes the
    entries that have been fixed (mcq_lengths.write_baseline).
    """
    found = validate(root, run=False).long_answers
    baseline_file = root / mcq_lengths.BASELINE
    try:
        print(mcq_lengths.write_baseline(baseline_file, found))
        baseline = mcq_lengths.read_baseline(baseline_file)
    except mcq_lengths.BadBaseline as exc:
        print(f"{mcq_lengths.BASELINE.as_posix()}: {exc}")
        return 1
    left = mcq_lengths.problems(found, baseline, baseline_file)
    if left:
        print(
            f"{len(left)} items or topics break a rule and aren't on the list, "
            "so they need fixing. Run the validator to see them."
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check everything in content/.")
    parser.add_argument("--no-run", action="store_true", help="don't run any code")
    parser.add_argument(
        "--labs",
        action="store_true",
        help="also prove every lab's contract in Docker (slow; CI does this)",
    )
    parser.add_argument(
        "--write-mcq-baseline",
        action="store_true",
        help="write the list of older multiple-choice items whose answer length "
        "the validator tolerates, or drop its fixed entries, and stop "
        "(tools/mcq_lengths.py)",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.write_mcq_baseline:
        return write_mcq_baseline(args.root)

    report = validate(args.root, run=not args.no_run, labs=args.labs)
    c = report.counts
    labs_note = f", {c['labs']} of them labs" if c["labs"] else ""
    print(
        f"Checked {c['topics']} topics ({c['ready']} ready, {c['draft']} draft, "
        f"{c['planned']} planned), {c['exercises']} exercises{labs_note}, "
        f"{c['recall items']} recall items; ran {c['runs']} programs"
        + (f" and {c['labs run']} labs" if c["labs run"] else "")
        + (
            f"; tried {c['arrangements']} other arrangements of Parsons lines"
            if c["arrangements"]
            else ""
        )
        + "."
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

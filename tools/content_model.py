"""The shapes of the files in content/, as described in docs/specs/data-model.md.

Every model rejects unknown fields, so a typo like `titel:` is caught instead
of silently ignored.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

# Topic, module and track IDs look like "py.variables" or "py.m1.checkpoint".
TopicId = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")]
# Item IDs are unique within their topic and look like "fill-swap".
ItemId = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
Text = Annotated[str, Field(min_length=1)]
Rev = Annotated[int, Field(ge=1)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Module(Strict):
    id: TopicId
    title: Text
    topics: list[TopicId] = Field(min_length=1)
    checkpoint: TopicId
    # A capstone is a bigger checkpoint that ends a stage. It sits after
    # this module's own checkpoint and builds on every module before it.
    capstone: TopicId | None = None


class Track(Strict):
    id: TopicId
    title: Text
    summary: Text
    # Where the track comes in the app, lowest first. Each track has its own.
    order: Annotated[int, Field(ge=1)]
    modules: list[Module] = Field(min_length=1)


class Resource(Strict):
    title: Text
    url: Annotated[str, Field(pattern=r"^https://")]
    type: Literal["video", "reading", "interactive"]
    use: Literal["embed", "link"]
    license: Text
    start: Annotated[int, Field(ge=0)] | None = None
    end: Annotated[int, Field(ge=1)] | None = None

    @model_validator(mode="after")
    def times_fit(self) -> Resource:
        if (self.start is not None or self.end is not None) and self.type != "video":
            raise ValueError("start and end are only for videos")
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValueError("end must come after start")
        return self


class RubricItem(Strict):
    id: ItemId
    required: bool
    description: Text


class Explain(Strict):
    prompt: Text
    rubric: list[RubricItem] = Field(min_length=1)
    model_answer: Text

    @model_validator(mode="after")
    def has_required_point(self) -> Explain:
        if not any(item.required for item in self.rubric):
            raise ValueError("the rubric needs at least one required point")
        return self


class ProvePart(Strict):
    """One more part of a checkpoint, after its build and debug (ADR-0012,
    amended 2026-11-11): a build or debug exercise of its own."""

    id: ItemId
    # Fresh versions of this part, in other stories. A pass of any counts.
    versions: list[ItemId] = []


class Prove(Strict):
    build: ItemId | None = None
    debug: ItemId | None = None
    # Checkpoints only: further parts, shown as Part 3, Part 4 and so on.
    more: list[ProvePart] = []
    explain: Explain | None = None

    def more_items(self) -> list[str]:
        """Every exercise the further parts name: each part and its versions."""
        return [item for part in self.more for item in (part.id, *part.versions)]

    @model_validator(mode="after")
    def parts_are_all_different(self) -> Prove:
        # A pass of one exercise can only prove one part, so none is named twice.
        named = [item for item in (self.build, self.debug) if item]
        named += self.more_items()
        repeated = sorted({item for item in named if named.count(item) > 1})
        if repeated:
            raise ValueError(
                f"prove names {', '.join(repeated)} more than once; the build, "
                "the debug and each further part and version must be different "
                "exercises"
            )
        return self


class Skill(Strict):
    """Something a topic teaches. Its items name the skills they test."""

    id: ItemId
    description: Text


# A topic's skill, named from a checkpoint as "topic/skill", like
# "py.arithmetic/precedence".
SkillRef = Annotated[
    str, Field(pattern=r"^[a-z0-9]+(?:[.-][a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*$")
]


class Unstuck(Strict):
    """A checkpoint's way through for a learner who's stuck (ADR-0012)."""

    # A solved project like the build, in a different story: a worked example.
    example: ItemId | None = None
    # The build itself, in 3 or 4 partly written steps, with hints.
    steps: list[ItemId] = []
    # Fresh versions of the build: the same skills in different stories.
    versions: list[ItemId] = []

    @model_validator(mode="after")
    def no_repeats(self) -> Unstuck:
        ids = [*self.steps, *self.versions]
        if len(set(ids)) != len(ids):
            raise ValueError("steps and versions must all be different")
        return self


class Topic(Strict):
    id: TopicId
    kind: Literal["topic", "checkpoint"]
    # planned: an outline on the map. draft: being written. ready: learners see it.
    status: Literal["planned", "draft", "ready"]
    title: Text
    summary: Text
    prerequisites: list[TopicId] = []
    # Python packages the topic's code imports, beyond the standard library:
    # loaded into the browser's Python on demand, and installed for CPython
    # through uv at the same version (ADR-0023).
    packages: list[Literal["numpy"]] = []
    estimated_minutes: Annotated[int, Field(ge=1)]
    rev: Rev
    objectives: list[Text] = Field(min_length=1)
    resources: list[Resource] = []
    practice: list[ItemId] = []
    prove: Prove = Prove()
    review_pool: list[ItemId] = []
    # A missed question comes back as a different one testing the same
    # skill, so items name the skills they test (ADR-0011).
    skills: list[Skill] = []
    # Checkpoints only: the way through for a learner who's stuck (ADR-0012).
    unstuck: Unstuck | None = None

    @model_validator(mode="after")
    def skill_ids_are_unique(self) -> Topic:
        ids = [skill.id for skill in self.skills]
        if len(set(ids)) != len(ids):
            raise ValueError("skill ids must all be different")
        return self

    @model_validator(mode="after")
    def fits_its_kind(self) -> Topic:
        if self.kind == "topic" and self.unstuck is not None:
            raise ValueError("only checkpoints have unstuck")
        if self.kind == "checkpoint" and self.skills:
            raise ValueError(
                "checkpoints don't declare skills: their tests name skills of "
                "the module's topics, in test_skills"
            )
        return self

    @model_validator(mode="after")
    def further_parts_stand_alone(self) -> Topic:
        """prove.more is for checkpoints, and its exercises are proofs of their
        own, never part of the build's way through (ADR-0012)."""
        if self.prove.more and self.kind != "checkpoint":
            raise ValueError(
                "only checkpoints have prove.more; a topic proves itself with "
                "one build, one debug and an explain"
            )
        unstuck = self.unstuck or Unstuck()
        helps = {unstuck.example, *unstuck.steps, *unstuck.versions}
        shared = sorted(helps.intersection(self.prove.more_items()))
        if shared:
            raise ValueError(
                f"prove.more names {', '.join(shared)}, which unstuck names too; "
                "a further part and its versions must be exercises of their own"
            )
        return self


class McqItem(Strict):
    id: ItemId
    type: Literal["mcq"]
    rev: Rev
    prompt: Text
    choices: list[Text] = Field(min_length=2)
    answer: Annotated[int, Field(ge=0)]
    explanation: Text
    skills: list[ItemId] = []

    @model_validator(mode="after")
    def answer_is_a_choice(self) -> McqItem:
        if self.answer >= len(self.choices):
            raise ValueError("answer must be the index of one of the choices")
        if len(set(self.choices)) != len(self.choices):
            raise ValueError("choices must all be different")
        return self


class PredictOutputItem(Strict):
    id: ItemId
    type: Literal["predict_output"]
    rev: Rev
    prompt: Text
    code: Text
    expected_output: str
    explanation: Text
    skills: list[ItemId] = []


class ParsonsItem(Strict):
    """Scrambled lines of a short program, to put back in order (ADR-0016)."""

    id: ItemId
    type: Literal["parsons"]
    rev: Rev
    prompt: Text
    # The program's lines in the right order, each with its indentation.
    lines: list[str] = Field(min_length=3)
    # Lines that don't belong, mixed in with the real ones.
    distractors: list[str] = []
    explanation: Text
    skills: list[ItemId] = []

    @model_validator(mode="after")
    def lines_are_distinct(self) -> ParsonsItem:
        lines = [line.strip() for line in self.lines]
        if any(line == "" for line in lines):
            raise ValueError("lines must not be blank")
        if len(set(lines)) != len(lines):
            raise ValueError("lines must all be different, so the order can be checked")
        decoys = [line.strip() for line in self.distractors]
        if any(decoy == "" for decoy in decoys) or len(set(decoys)) != len(decoys):
            raise ValueError("distractors must be non-blank and all different")
        if set(decoys) & set(lines):
            raise ValueError("a distractor must be different from every line")
        return self


# A fixture file's path inside the item's folder: a plain name, or a few
# folders deep. Never absolute, and (checked below) never "." or "..".
FixturePath = Annotated[
    str, Field(pattern=r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$", max_length=120)
]

# Fixture files stay small: they're shown on the page and bundled with the item.
MAX_FIXTURE_CHARS = 4000


class PredictShellItem(Strict):
    """A shell command over a few small files, and what it prints (ADR-0017).

    The browser runs nothing: the validator runs the command in real bash,
    in a temporary folder holding just these files, and checks the output.
    """

    id: ItemId
    type: Literal["predict_shell"]
    rev: Rev
    prompt: Text
    # The files the command sees, by path, with their contents. The command
    # runs in a folder holding only these, so they are its whole world.
    files: dict[FixturePath, str] = {}
    # One line of bash, or a few. Portable across Linux and Git Bash.
    command: Text
    expected_output: str
    explanation: Text
    skills: list[ItemId] = []

    @model_validator(mode="after")
    def files_stay_inside_and_small(self) -> PredictShellItem:
        for path in self.files:
            if {".", ".."} & set(path.split("/")):
                raise ValueError(f"file path {path!r} must not have . or .. parts")
        if sum(len(text) for text in self.files.values()) > MAX_FIXTURE_CHARS:
            raise ValueError(
                f"the files hold more than {MAX_FIXTURE_CHARS} characters in all; "
                "keep them small enough to read on the page"
            )
        return self


RecallItem = Annotated[
    McqItem | PredictOutputItem | ParsonsItem | PredictShellItem,
    Field(discriminator="type"),
]
recall_item = TypeAdapter(RecallItem)

Stage = Literal["worked_example", "fill_in", "write", "build", "debug", "review_code"]

# Stages whose starter code must exist and must fail the tests.
STAGES_WITH_FAILING_STARTER = {"fill_in", "debug"}

# Stages whose tests are hidden: the learner sees what each test checks and
# whether it passed, but not why it failed (web/src/content/stages.ts).
STAGES_WITH_HIDDEN_TESTS = {"build", "review_code"}

# Exercises that can come back as a follow-up to a missed question (ADR-0011).
# Recall items always can; proof checks and worked examples never do.
FOLLOW_UP_STAGES = {"fill_in", "write", "review_code"}


class Step(Strict):
    """One labeled step of a worked example (subgoal labels)."""

    label: Text
    lines: Annotated[str, Field(pattern=r"^\d+(?:-\d+)?$")]
    note: Text


# Where an exercise runs: Python in the browser, or a lab container on the
# learner's machine, checked by tools/labcheck.py (ADR-0018).
Runtime = Literal["python", "lab"]


class LabOptions(Strict):
    """How the checker starts a lab's container (ADR-0018)."""

    # systemd labs run privileged with /sbin/init; the rest just sleep.
    init: Literal["none", "systemd"] = "none"


class Exercise(Strict):
    id: ItemId
    stage: Stage
    rev: Rev
    title: Text
    prompt: Text
    runtime: Runtime = "python"
    lab: LabOptions | None = None
    time_limit_ms: Annotated[int, Field(ge=100, le=30_000)] = 5000
    hints: list[Text] = []
    steps: list[Step] = []
    skills: list[ItemId] = []
    # Checkpoint builds and debugs only: the skills each test checks, as
    # "topic/skill", so a failed test brings them back (ADR-0012). For a lab,
    # the keys are check ids from checks.yaml instead of test names.
    test_skills: dict[str, Annotated[list[SkillRef], Field(min_length=1)]] = {}

    @model_validator(mode="after")
    def steps_only_for_worked_examples(self) -> Exercise:
        if self.stage == "worked_example" and not self.steps:
            raise ValueError("a worked example needs labeled steps")
        if self.stage != "worked_example" and self.steps:
            raise ValueError("only worked examples have steps")
        return self

    @model_validator(mode="after")
    def lab_options_only_for_labs(self) -> Exercise:
        if self.lab is not None and self.runtime != "lab":
            raise ValueError("lab options are only for runtime: lab")
        return self

    @model_validator(mode="after")
    def test_skill_keys_fit_the_runtime(self) -> Exercise:
        for key in self.test_skills:
            if self.runtime == "python" and not re.fullmatch(r"test_\w+", key):
                raise ValueError(f"{key!r} isn't a test name (test_...)")
            if self.runtime == "lab" and not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", key
            ):
                raise ValueError(f"{key!r} isn't a check id (like disk-has-room)")
        return self


# --- Labs (ADR-0018) -------------------------------------------------------------


class Expect(Strict):
    """What a lab check's command must produce. Without one, exit status 0."""

    exit: Annotated[int, Field(ge=0, le=255)] | None = None
    equals: str | None = None
    contains: Text | None = None
    not_contains: Text | None = None
    matches: Text | None = None
    lt: float | None = None
    lte: float | None = None
    gt: float | None = None
    gte: float | None = None

    @model_validator(mode="after")
    def says_something(self) -> Expect:
        if all(value is None for value in self.__dict__.values()):
            raise ValueError("expect needs at least one condition")
        return self


class LabCheck(Strict):
    """One check of a lab: a command run inside the container, read-only."""

    id: ItemId
    # What the learner sees: the first line is the check's name.
    description: Text
    command: Text
    expect: Expect | None = None


class LabChecks(Strict):
    checks: list[LabCheck] = Field(min_length=1)

    @model_validator(mode="after")
    def ids_are_unique(self) -> LabChecks:
        ids = [check.id for check in self.checks]
        if len(set(ids)) != len(ids):
            raise ValueError("check ids must all be different")
        return self


class DiagnosticLevel(Strict):
    """One rung of a diagnostic's ladder (ADR-0021): a few questions, and
    where to refresh the level until the platform teaches it itself."""

    id: ItemId
    title: Text
    summary: Text
    # A link to a free refresher. Recorded like any resource (ADR-0004).
    refresh: Resource
    # The topic that teaches this level, once it exists; the result page
    # links it instead of the refresher when it's ready.
    topic: TopicId | None = None
    items: list[McqItem] = Field(min_length=2)

    @model_validator(mode="after")
    def fits(self) -> DiagnosticLevel:
        if self.refresh.use != "link":
            raise ValueError("refresh must be a link, not an embed")
        if any(item.skills for item in self.items):
            raise ValueError(
                "diagnostic items don't name skills: there's no topic to relearn"
            )
        return self


class Diagnostic(Strict):
    """A ladder of levels the placement test walks like a track (ADR-0021)."""

    id: ItemId
    title: Text
    summary: Text
    levels: list[DiagnosticLevel] = Field(min_length=2)

    @model_validator(mode="after")
    def ids_are_unique(self) -> Diagnostic:
        level_ids = [level.id for level in self.levels]
        if len(set(level_ids)) != len(level_ids):
            raise ValueError("level ids must all be different")
        item_ids = [item.id for level in self.levels for item in level.items]
        if len(set(item_ids)) != len(item_ids):
            raise ValueError("item ids must all be different across the diagnostic")
        return self

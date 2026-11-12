"""The shapes of the files in content/, as described in docs/specs/data-model.md.

Every model rejects unknown fields, so a typo like `titel:` is caught instead
of silently ignored.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    TypeAdapter,
    model_validator,
)

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


# --- Estimate questions (ADR-0024) ------------------------------------------------

# A number in an estimate: an int or a decimal, never infinite, and never
# text that looks like a number ("28" in quotes reaches the browser as text).
Number = (
    Annotated[int, Field(strict=True)]
    | Annotated[float, Field(strict=True, allow_inf_nan=False)]
)
# The name of a given number, used in the working: like vcpus or price_per_hour.
GivenName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=40)]

# The widest percentage tolerance: the loosest target the cloud track's
# drills set is 30% ("within 30% before opening a calculator").
WIDEST_PERCENT = 30


class Tolerance(Strict):
    """How close a typed number must be to the answer to count as right.
    Exactly one of the two."""

    # Within this much either side of the answer; 0 means exactly.
    absolute: Number | None = None
    # Within this percentage of the answer, either side.
    percent: Number | None = None

    @model_validator(mode="after")
    def one_kind_in_range(self) -> Tolerance:
        if (self.absolute is None) == (self.percent is None):
            raise ValueError("give exactly one of absolute or percent")
        if self.absolute is not None and self.absolute < 0:
            raise ValueError("absolute can't be negative; 0 means exactly")
        if self.percent is not None and self.percent <= 0:
            raise ValueError(
                "percent must be above 0; for an exact answer, use absolute: 0"
            )
        if self.percent is not None and self.percent > WIDEST_PERCENT:
            raise ValueError(
                f"percent can be at most {WIDEST_PERCENT}, the widest target the "
                "track's drills set"
            )
        return self


class Mistake(Strict):
    """A wrong answer a learner is likely to give, and what went wrong."""

    id: ItemId
    value: Number
    # The wrong sum, written over the item's given numbers like `working`.
    working: Text
    # Shown first when the learner's answer matches this value.
    why: Text


class EstimateItem(Strict):
    """A number the learner works out and types, checked within a tolerance.

    The browser works nothing out: the validator works out the answer and
    every mistake from `given` (tools/arithmetic.py), and proves that the
    tolerance accepts the one and none of the others.
    """

    id: ItemId
    type: Literal["estimate"]
    rev: Rev
    # Holds every number the learner needs, and says how exact to be.
    prompt: Text
    # Shown after the number box, so the learner never types it.
    unit: Text
    answer: Number
    tolerance: Tolerance
    # The numbers the prompt states, by name, as the prompt writes them
    # (30 for "30%"). A number the learner must know instead, like a rule's
    # minimum, goes in the working as a plain number.
    given: dict[GivenName, Number] = Field(min_length=1)
    # The sum, over the given names, that gives the answer. Shown afterwards.
    working: Text
    mistakes: list[Mistake] = Field(min_length=1)
    explanation: Text
    skills: list[ItemId] = []
    # For a prompt with prices: the day they were read, and the page that
    # shows today's. Both or neither.
    prices_as_of: date | None = None
    prices_source: Annotated[str, Field(pattern=r"^https://")] | None = None

    @model_validator(mode="after")
    def fits_together(self) -> EstimateItem:
        ids = [mistake.id for mistake in self.mistakes]
        if len(set(ids)) != len(ids):
            raise ValueError("mistake ids must all be different")
        if (self.prices_as_of is None) != (self.prices_source is None):
            raise ValueError("give both prices_as_of and prices_source, or neither")
        if self.tolerance.percent is not None and self.answer == 0:
            raise ValueError(
                "a percentage of 0 is 0, so a percent tolerance needs an "
                "answer that isn't 0; use absolute"
            )
        return self


RecallItem = Annotated[
    McqItem | PredictOutputItem | ParsonsItem | PredictShellItem | EstimateItem,
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
    """How the checker starts and proves a lab's container (ADR-0018)."""

    # systemd labs run privileged with /sbin/init; the rest just sleep.
    init: Literal["none", "systemd"] = "none"
    # The restart trial (ADR-0018, third amendment): `labcheck test` restarts
    # the container once the solution passes, and every check must pass
    # again, so a fix a reboot would lose fails the contract. Opt-in; every
    # Module 3 lab opts in. Strictly true or false, so a YAML "yes" in quotes
    # or a 1 isn't quietly read as true.
    restart_trial: StrictBool = False


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


# How long a check's command may run, in seconds (ADR-0018, amended
# 2026-11-11). Thirty is plenty for a check that reads what the learner made.
# A check that has to run something slow to see it, such as booting a small
# VM, asks for more with `timeout:`, up to five minutes. A lab's checks may
# ask for ten minutes in all, because a learner whose lab is still broken
# waits for every one of them.
CHECK_SECONDS = 30
CHECK_SECONDS_MAX = 300
LAB_CHECK_SECONDS_MAX = 600


class LabCheck(Strict):
    """One check of a lab: a command run inside the container, read-only."""

    id: ItemId
    # What the learner sees: the first line is the check's name.
    description: Text
    command: Text
    expect: Expect | None = None
    # Seconds the command may run; at the limit it is stopped and fails.
    timeout: int = CHECK_SECONDS

    @model_validator(mode="before")
    @classmethod
    def timeout_is_whole_seconds(cls, data: object) -> object:
        """Says what a timeout must be. It looks at the value as YAML gave it,
        because Pydantic would quietly read "30" (text) as 30 seconds and
        true (YAML's yes) as 1."""
        if not isinstance(data, dict) or "timeout" not in data:
            return data
        seconds = data["timeout"]
        whole = isinstance(seconds, int) and not isinstance(seconds, bool)
        if not whole or not 1 <= seconds <= CHECK_SECONDS_MAX:
            raise ValueError(
                f"{data.get('id', 'this check')}: timeout is a whole number of "
                f"seconds from 1 to {CHECK_SECONDS_MAX}, such as timeout: 120 "
                f"(a check without one gets {CHECK_SECONDS}); {seconds!r} isn't"
            )
        return data


class LabChecks(Strict):
    checks: list[LabCheck] = Field(min_length=1)

    @model_validator(mode="after")
    def ids_are_unique(self) -> LabChecks:
        ids = [check.id for check in self.checks]
        if len(set(ids)) != len(ids):
            raise ValueError("check ids must all be different")
        return self

    @model_validator(mode="after")
    def fit_in_ten_minutes(self) -> LabChecks:
        # Every check counts, so this also stops a lab at 20 checks that all
        # have the usual 30 seconds; the message says how to get past that.
        total = sum(check.timeout for check in self.checks)
        if total > LAB_CHECK_SECONDS_MAX:
            raise ValueError(
                f"the checks' time limits add up to {total} seconds, over the "
                f"{LAB_CHECK_SECONDS_MAX} a lab's checks may take in all (a check "
                f"without a timeout counts {CHECK_SECONDS}): a learner whose lab "
                "is still broken waits for every one. Lower the slow checks' "
                "timeout, give quick checks a shorter one of their own (such as "
                "timeout: 10), or use fewer checks"
            )
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

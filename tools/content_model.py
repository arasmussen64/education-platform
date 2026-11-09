"""The shapes of the files in content/, as described in docs/specs/data-model.md.

Every model rejects unknown fields, so a typo like `titel:` is caught instead
of silently ignored.
"""

from __future__ import annotations

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


class Prove(Strict):
    build: ItemId | None = None
    debug: ItemId | None = None
    explain: Explain | None = None


class Skill(Strict):
    """Something a topic teaches. Its items name the skills they test."""

    id: ItemId
    description: Text


# A topic's skill, named from a checkpoint as "topic/skill", like
# "py.arithmetic/precedence".
SkillRef = Annotated[
    str, Field(pattern=r"^[a-z0-9]+(?:[.-][a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*$")
]
# A test function in test_exercise.py, like "test_tip".
TestName = Annotated[str, Field(pattern=r"^test_\w+$")]


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


RecallItem = Annotated[
    McqItem | PredictOutputItem | ParsonsItem, Field(discriminator="type")
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


class Exercise(Strict):
    id: ItemId
    stage: Stage
    rev: Rev
    title: Text
    prompt: Text
    time_limit_ms: Annotated[int, Field(ge=100, le=30_000)] = 5000
    hints: list[Text] = []
    steps: list[Step] = []
    skills: list[ItemId] = []
    # Checkpoint builds and debugs only: the skills each test checks, as
    # "topic/skill", so a failed test brings them back (ADR-0012).
    test_skills: dict[TestName, Annotated[list[SkillRef], Field(min_length=1)]] = {}

    @model_validator(mode="after")
    def steps_only_for_worked_examples(self) -> Exercise:
        if self.stage == "worked_example" and not self.steps:
            raise ValueError("a worked example needs labeled steps")
        if self.stage != "worked_example" and self.steps:
            raise ValueError("only worked examples have steps")
        return self

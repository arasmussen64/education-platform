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


class Track(Strict):
    id: TopicId
    title: Text
    summary: Text
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


class McqItem(Strict):
    id: ItemId
    type: Literal["mcq"]
    rev: Rev
    prompt: Text
    choices: list[Text] = Field(min_length=2)
    answer: Annotated[int, Field(ge=0)]
    explanation: Text

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


RecallItem = Annotated[McqItem | PredictOutputItem, Field(discriminator="type")]
recall_item = TypeAdapter(RecallItem)

Stage = Literal["worked_example", "fill_in", "write", "build", "debug", "review_code"]

# Stages whose starter code must exist and must fail the tests.
STAGES_WITH_FAILING_STARTER = {"fill_in", "debug"}


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

    @model_validator(mode="after")
    def steps_only_for_worked_examples(self) -> Exercise:
        if self.stage == "worked_example" and not self.steps:
            raise ValueError("a worked example needs labeled steps")
        if self.stage != "worked_example" and self.steps:
            raise ValueError("only worked examples have steps")
        return self

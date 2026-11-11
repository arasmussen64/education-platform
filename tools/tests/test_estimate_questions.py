"""The validator proves an estimate question (ADR-0024): its working gives
its answer, its known mistakes give their values, and the tolerance tells
them apart. Each test breaks the fixture's estimate in one way."""

from pathlib import Path

import pytest
from content_fixture import ESTIMATE, TOPIC, make_valid_tree, write
from validate_content import validate

TOPIC_DIR = "content/topics/t.hello"
ESTIMATE_FILE = f"{TOPIC_DIR}/recall/estimate-cost.yaml"


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    return make_valid_tree(tmp_path)


def problems(root: Path) -> list[str]:
    # Plain arithmetic, so it's all checked without running any code.
    return validate(root, run=False).problems


def estimate_with(tree: Path, *changes: tuple[str, str]) -> list[str]:
    """The problems found once the fixture's estimate has these changes."""
    text = ESTIMATE
    for old, new in changes:
        assert old in text, f"{old!r} isn't in the fixture's estimate"
        text = text.replace(old, new)
    write(tree, ESTIMATE_FILE, text)
    return problems(tree)


def assert_one_problem(found: list[str], fragment: str) -> None:
    """The item loads, and this is the only thing wrong with it."""
    assert len(found) == 1, found
    assert "estimate-cost.yaml" in found[0]
    assert fragment in found[0], found


def assert_refused(found: list[str], fragment: str) -> None:
    """The item doesn't load, for this reason (so its topic names an item
    that doesn't exist, too)."""
    assert any("estimate-cost.yaml" in p and fragment in p for p in found), found


def test_a_good_estimate_passes_and_counts_as_a_recall_item(tree: Path) -> None:
    report = validate(tree, run=False)
    assert report.problems == []
    assert report.counts["recall items"] == 5


def test_the_working_must_give_the_answer(tree: Path) -> None:
    found = estimate_with(tree, ("answer: 87.6", "answer: 90.0"))
    assert_one_problem(found, "the working gives 87.6, but the answer is 90")


def test_an_answer_may_be_rounded_but_the_exact_working_must_pass(
    tree: Path,
) -> None:
    # 87.6 rounds to 88, and 88 within 10% takes 87.6: fine.
    assert estimate_with(tree, ("answer: 87.6", "answer: 88")) == []
    # Exactly 88 doesn't take 87.6, so working it out exactly would fail.
    found = estimate_with(
        tree,
        ("answer: 87.6", "answer: 88"),
        ("{ percent: 10 }", "{ absolute: 0 }"),
    )
    assert_one_problem(
        found,
        "the working gives 87.6 exactly, which the tolerance doesn't accept "
        "around 88, so a learner who works it out exactly is marked wrong",
    )


def test_a_mistake_must_lie_outside_the_tolerance(tree: Path) -> None:
    # Eleven months' worth, 80.3, is within 10% of 87.6.
    found = estimate_with(
        tree,
        ("value: 73", "value: 80.3"),
        ("working: vm * hours", "working: (vm + disk) * hours * 11 / 12"),
    )
    assert_one_problem(
        found,
        "mistake 'vm-only' gives 80.3, which the tolerance accepts, so a "
        "learner who makes that mistake is marked right",
    )


def test_a_mistake_on_the_edge_of_the_tolerance_is_inside_it(tree: Path) -> None:
    # 10% of 87.6 is 8.76, so 78.84 is just accepted, as on the page.
    found = estimate_with(
        tree,
        ("value: 73", "value: 78.84"),
        ("working: vm * hours", "working: (vm + disk) * hours * 0.9"),
    )
    assert_one_problem(found, "mistake 'vm-only' gives 78.84, which the tolerance")


def test_a_mistake_working_must_give_its_value(tree: Path) -> None:
    found = estimate_with(tree, ("value: 73", "value: 74"))
    assert_one_problem(
        found, "mistake 'vm-only': its working gives 73, but its value is 74"
    )


def test_mistakes_give_different_values(tree: Path) -> None:
    found = estimate_with(
        tree,
        ("value: 2.88", "value: 73"),
        ("working: (vm + disk) * 24", "working: 730 * vm"),
    )
    assert_one_problem(found, "mistakes 'vm-only' and 'one-day' both give 73")


def test_mistakes_need_different_ids_and_at_least_one(tree: Path) -> None:
    found = estimate_with(tree, ("id: one-day", "id: vm-only"))
    assert_refused(found, "mistake ids must all be different")
    found = estimate_with(tree, ("mistakes:\n", "mistakes: []\nold_mistakes:\n"))
    assert_refused(found, "mistakes: List should have at least 1 item")


def test_every_given_number_is_stated_in_the_prompt(tree: Path) -> None:
    found = estimate_with(tree, ("Use 730 hours a month.", "A month is long."))
    assert_one_problem(
        found,
        "given hours is 730, which the prompt doesn't state: write it in the "
        "prompt in digits, or if the learner must know it, put it in the "
        "working as a plain number",
    )


def test_stated_numbers_may_have_commas_and_trailing_zeros(tree: Path) -> None:
    # 0.10 in the prompt is the given 0.1; 1,460 is 1460.
    found = estimate_with(
        tree,
        ("Use 730 hours a month.", "Use 1,460 hours for two months."),
        ("hours: 730", "hours: 1460"),
        ("answer: 87.6", "answer: 175.2"),
        ("value: 73", "value: 146"),
        ("(0.10 + 0.02) × 730 = 87.60", "(0.10 + 0.02) × 1460 = 175.20"),
    )
    assert found == []


def test_a_given_may_not_take_a_function_name(tree: Path) -> None:
    found = estimate_with(
        tree,
        ("hours: 730 }", "hours: 730, floor: 8 }"),
        ("Use 730 hours", "Use 730 hours (8 at least)"),
    )
    assert_one_problem(
        found, "given 'floor' has the name of a function the working can call"
    )


@pytest.mark.parametrize(
    ("working", "message"),
    [
        ("(vm + disk) * hour", "uses 'hour', which isn't one of the given numbers"),
        ("(vm + disk) *", "isn't a sum that can be read"),
        ("__import__('os').getcwd()", "can't use"),
    ],
)
def test_the_working_is_arithmetic_and_nothing_else(
    tree: Path, working: str, message: str
) -> None:
    found = estimate_with(
        tree, ("working: (vm + disk) * hours", f"working: {working!r}")
    )
    assert_one_problem(found, f"the working ({working!r}) {message}")


def test_a_mistake_working_is_arithmetic_too(tree: Path) -> None:
    found = estimate_with(tree, ("working: vm * hours", "working: vm * hourz"))
    assert_one_problem(
        found,
        "the working of mistake 'vm-only' ('vm * hourz') uses 'hourz', which "
        "isn't one of the given numbers",
    )


def test_a_prompt_with_money_needs_its_prices_dated(tree: Path) -> None:
    found = estimate_with(
        tree,
        ("prices_as_of: 2026-11-10\n", ""),
        ("prices_source: https://example.com/prices\n", ""),
    )
    assert_one_problem(
        found,
        "the prompt holds an amount of money, so it needs prices_as_of and "
        "prices_source",
    )


def test_price_fields_come_together(tree: Path) -> None:
    found = estimate_with(tree, ("prices_source: https://example.com/prices\n", ""))
    assert_refused(found, "give both prices_as_of and prices_source, or neither")


def test_a_dollar_sign_in_code_is_not_money(tree: Path) -> None:
    found = estimate_with(
        tree,
        (
            "A VM costs $0.10 an hour, and its disk $0.02 an hour.",
            "A VM's meter reads 0.10 an hour, and `awk '{print $1}'` "
            "reads its disk's, 0.02.",
        ),
        ("prices_as_of: 2026-11-10\n", ""),
        ("prices_source: https://example.com/prices\n", ""),
    )
    assert found == []


@pytest.mark.parametrize(
    ("tolerance", "message"),
    [
        ("{ percent: 10, absolute: 1 }", "give exactly one of absolute or percent"),
        ("{}", "give exactly one of absolute or percent"),
        ("{ percent: 40 }", "percent can be at most 30, the widest target"),
        (
            "{ percent: 0 }",
            "percent must be above 0; for an exact answer, use absolute: 0",
        ),
        ("{ absolute: -1 }", "absolute can't be negative"),
        ("{ factor: 2 }", "factor: Extra inputs are not permitted"),
    ],
)
def test_the_tolerance_is_one_kind_in_range(
    tree: Path, tolerance: str, message: str
) -> None:
    found = estimate_with(tree, ("{ percent: 10 }", tolerance))
    assert_refused(found, message)


def test_a_percent_tolerance_needs_an_answer_that_isnt_zero(tree: Path) -> None:
    found = estimate_with(tree, ("answer: 87.6", "answer: 0"))
    assert_refused(found, "a percent tolerance needs an answer that isn't 0")


@pytest.mark.parametrize("written", ["7_30", "0730"])
def test_numbers_are_written_the_way_the_browser_reads_them(
    tree: Path, written: str
) -> None:
    # Python's YAML reads 7_30 as 730 and 0730 as 472; the browser's reads
    # them as text and as 730.
    found = estimate_with(tree, ("hours: 730", f"hours: {written}"))
    assert any(
        f"the number {written} reads differently in the browser" in p for p in found
    ), found


def test_numbers_are_never_text(tree: Path) -> None:
    # "87.6" in quotes would reach the browser as text, so it's refused.
    found = estimate_with(tree, ("answer: 87.6", 'answer: "87.6"'))
    assert_refused(found, "Input should be a valid number")


# --- Where estimates count -------------------------------------------------------


def topic_with(tree: Path, *changes: tuple[str, str]) -> list[str]:
    text = TOPIC
    for old, new in changes:
        assert old in text, f"{old!r} isn't in the fixture's topic"
        text = text.replace(old, new)
    write(tree, f"{TOPIC_DIR}/topic.yaml", text)
    return problems(tree)


def test_an_estimate_counts_toward_the_recall_items_practice_needs(
    tree: Path,
) -> None:
    practice = (
        "practice: [example-hello, parsons-order, mcq-print, predict-print,\n"
        "  shell-count, estimate-cost, fill-hello, write-hello]"
    )
    exercises = "fill-hello, write-hello]"
    found = topic_with(
        tree, (practice, f"practice: [example-hello, estimate-cost, {exercises}")
    )
    assert any("practice needs at least 2 recall items" in p for p in found)
    found = topic_with(
        tree,
        (practice, f"practice: [example-hello, mcq-print, estimate-cost, {exercises}"),
    )
    assert found == []


def test_an_estimate_is_produced_so_it_meets_the_review_pool_rule(
    tree: Path,
) -> None:
    # The fixture has one multiple-choice item, so it's listed twice to make
    # a pool of three whose only answer that isn't a choice is the estimate.
    pool = "review_pool: [mcq-print, predict-print, review-hello]"
    found = topic_with(
        tree, (pool, "review_pool: [mcq-print, estimate-cost, mcq-print]")
    )
    assert found == []
    # Without it, the pool's only items are choices.
    found = topic_with(tree, (pool, "review_pool: [mcq-print, mcq-print, mcq-print]"))
    assert any(
        "the review pool needs a predict-the-output, estimate, Parsons or "
        "review_code item" in p
        for p in found
    )

"""tm-check, the threat-model labs' checker (content/lab-bases/tm/tm-check).

Every threat-modeling lab and Checkpoint 4 part 1 decide right from wrong
with it, so a wrong verdict here would pass wrong work or fail right work.
The models are in tm_cases.py: a reference model must pass every part, each
wrong model must fail the one part aimed at it and say why, a right model
for another story must fail, and a line that isn't in the format must get
a sentence a beginner can act on: the line's number and what was expected.
"""

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from tm_cases import (
    C2,
    CHECKOUT_MODEL,
    CHECKOUT_ONLY,
    CHECKOUT_REF,
    CHECKOUT_WRONG,
    PARCELS_MODEL,
    PARCELS_REF,
    change,
)

ROOT = Path(__file__).resolve().parents[2]
TM_CHECK = ROOT / "content" / "lab-bases" / "tm" / "tm-check"


def load():
    loader = importlib.machinery.SourceFileLoader("tm_check", str(TM_CHECK))
    spec = importlib.util.spec_from_loader("tm_check", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


tm = load()

# The parts a lab's checks run with a reference for each story.
CHECKOUT_PARTS = [
    "reads",
    "diagram",
    "boundaries",
    "stride",
    "findings",
    "ranking",
    "controls",
    "scope",
    "attack",
    "tree",
]
PARCELS_PARTS = [
    "reads",
    "diagram",
    "boundaries",
    "stride",
    "findings",
    "ranking",
    "controls",
    "attack",
    "tree",
    "abuse",
    "kept",
]


@pytest.fixture
def files(tmp_path):
    """Writes a model and a reference, and runs tm-check's own run() on them."""

    class Files:
        def model(self, text: str) -> str:
            path = tmp_path / "model.tm"
            path.write_bytes(text.encode("utf-8"))
            return str(path)

        def reference(self, ref: dict) -> str:
            path = tmp_path / "ref.json"
            path.write_text(json.dumps(ref), encoding="utf-8")
            return str(path)

        def say(self, part: str, text: str, ref: dict | None = None, *flags) -> str:
            args = [part, self.model(text)]
            if ref is not None:
                args.append(self.reference(ref))
            said, status = tm.run([*args, *flags])
            assert status == 0, said
            return said

        def failing(self, parts: list[str], text: str, ref: dict) -> dict[str, str]:
            said = {part: self.say(part, text, ref) for part in parts}
            return {part: words for part, words in said.items() if words != "ok"}

    return Files()


# --- the two reference models ------------------------------------------------


def test_the_checkout_model_passes_every_part(files) -> None:
    assert files.failing(CHECKOUT_PARTS, CHECKOUT_MODEL, CHECKOUT_REF) == {}


def test_the_checkout_model_passes_each_weakness_alone_and_the_rest(files) -> None:
    for only in ["1", "2", "3", "4", "5", "6", "rest"]:
        said = files.say("controls", CHECKOUT_MODEL, CHECKOUT_REF, "--only", only)
        assert said == "ok", only


def test_the_parcels_model_passes_every_part(files) -> None:
    assert files.failing(PARCELS_PARTS, PARCELS_MODEL, PARCELS_REF) == {}


def test_the_checkout_model_has_the_designers_64_lines() -> None:
    lines = [x for x in CHECKOUT_MODEL.splitlines() if x.strip() and x[0] != "#"]
    assert len(lines) == 64
    assert len(CHECKOUT_WRONG) == 25


# --- the wrong models ---------------------------------------------------------


@pytest.mark.parametrize("name", sorted(CHECKOUT_WRONG))
def test_a_wrong_model_fails_the_part_aimed_at_it_and_says_why(files, name) -> None:
    text, part, why = CHECKOUT_WRONG[name]
    assert files.failing(CHECKOUT_PARTS, text, CHECKOUT_REF) == {part: why}


@pytest.mark.parametrize("name", sorted(CHECKOUT_ONLY))
def test_a_wrong_control_fails_only_its_own_weakness(files, name) -> None:
    # Checkpoint 4 part 1 gives each high weakness a check of its own
    # ("controls --only N"), so one wrong choice brings back one skill.
    text = CHECKOUT_WRONG[name][0]
    aimed, rest_fails = CHECKOUT_ONLY[name]
    failed = [
        only
        for only in [1, 2, 3, 4, 5, 6]
        if files.say("controls", text, CHECKOUT_REF, "--only", str(only)) != "ok"
    ]
    assert failed == [aimed]
    rest = files.say("controls", text, CHECKOUT_REF, "--only", "rest")
    assert (rest != "ok") == rest_fails


def test_only_rest_still_minds_the_threats_no_weakness_narrows(files) -> None:
    # t6 (nobody signs a refund) answered with nothing at all, then with a
    # control the reference doesn't narrow away but the letter refuses.
    unanswered = change(
        "control c6 t6 audit-log record every refund with the staff member, "
        "time, order and amount\n",
        "",
    )
    ref = json.loads(json.dumps(CHECKOUT_REF))
    del ref["weak"][5]["controls"]
    said = files.say("controls", unanswered, ref, "--only", "rest")
    assert said == "a threat has neither a control nor an accept line"
    misfit = change("control c6 t6 audit-log", "control c6 t6 rate-limit")
    said = files.say("controls", misfit, ref, "--only", "rest")
    assert said == "a control is of a kind that doesn't answer its threat"


def test_a_medium_weakness_may_be_accepted_and_a_high_one_may_not(files) -> None:
    accepted = change(
        "control c6 t6 audit-log record every refund with the staff member, "
        "time, order and amount\n",
        "accept t6 refunds are few and the bank statement shows them\n",
    )
    assert files.say("controls", accepted, CHECKOUT_REF) == "ok"
    assert files.say("controls", accepted, CHECKOUT_REF, "--only", "6") == "ok"
    # Rated down to slip under the line and then accepted: the weakness's
    # own check goes by the design's rating, not the learner's.
    low = change(
        "top t1 t2 t3 t4 t5",
        "top t1 t3 t4 t5",
        change(
            C2,
            "accept t2 unpaid orders are rare\n",
            change("threat t2 f5 S 3 2 6", "threat t2 f5 S 1 2 2"),
        ),
    )
    said = files.say("controls", low, CHECKOUT_REF, "--only", "2")
    assert said == "a risk the design describes has no control"
    assert files.say("controls", low, CHECKOUT_REF, "--only", "rest") == "ok"
    assert files.say("findings", low, CHECKOUT_REF) != "ok"


def test_what_a_failure_says_never_names_a_part_of_the_model(files) -> None:
    # A check's message must not hand over the answer: no flow, element,
    # threat or zone of the design appears in any of them.
    names = set(CHECKOUT_REF["elements"]) | set(CHECKOUT_REF["flows"])
    names |= {f"t{n}" for n in range(1, 7)}
    names |= {zone for _, zone in CHECKOUT_REF["elements"].values()}
    for text, _part, _why in CHECKOUT_WRONG.values():
        for said in files.failing(CHECKOUT_PARTS, text, CHECKOUT_REF).values():
            words = {word.strip(".,:()") for word in said.split()}
            assert not words & names, said


def test_a_right_model_for_another_story_fails(files) -> None:
    # A model copied from the wrong lab reads, and its sums are right, but
    # it is not this design's.
    failed = files.failing(CHECKOUT_PARTS, PARCELS_MODEL, CHECKOUT_REF)
    assert failed["diagram"] == "the model leaves out a part the design names"
    assert {"boundaries", "findings", "scope", "attack"} <= set(failed)
    assert "reads" not in failed and "ranking" not in failed
    failed = files.failing(PARCELS_PARTS, CHECKOUT_MODEL, PARCELS_REF)
    assert {"diagram", "boundaries", "findings", "abuse", "kept"} <= set(failed)


def test_a_model_with_more_than_the_design_fails_the_diagram(files) -> None:
    extra = PARCELS_MODEL + "element cache store depot a cache nobody asked for\n"
    said = files.say("diagram", extra, PARCELS_REF)
    assert said == "the model has an element the design doesn't name"
    extra = PARCELS_MODEL + "flow f9 app maps a flow nobody asked for\n"
    said = files.say("diagram", extra, PARCELS_REF)
    assert said == "the model has a flow the design doesn't name"


# --- lines that aren't in the format ------------------------------------------

# (what to change in the checkout model, the line it is on, what must be said)
MALFORMED = [
    (
        ("zone office ", "zoen office "),
        3,
        'line 3: "zoen" is not a kind of line (did you mean "zone"?). '
        "A line starts with one of: zone, element, flow, threat, none, control, "
        "accept, top, attack, scope, goal, node, leaf, cheapest, abuse, test",
    ),
    (
        ("element web        process  edge", "element web        service  edge"),
        12,
        "line 12: an element is external, process or store, and this one says "
        '"service". An element line is written: '
        "element ID external|process|store ZONE words",
    ),
    (
        ("element web        process  edge", "element web        process  egde"),
        12,
        'line 12: there is no zone called egde above this line (did you mean "edge"?)',
    ),
    (
        (
            "element web        process  edge       storefront and checkout page",
            "element web process",
        ),
        12,
        "line 12: this line stops too soon: its zone is missing",
    ),
    (
        ("flow f3  web        orders-api", "flow f3  web        orders"),
        21,
        "line 21: there is no element called orders above this line",
    ),
    (
        ("flow f2  customer   psp ", "flow f1  customer   psp "),
        20,
        "line 20: the flow f1 is already defined on line 19",
    ),
    (
        ("threat t1 f6 S 3 3 9", "threat t1 f6 s 3 3 9"),
        37,
        'line 37: the letter is one of S T R I D E, a capital, and this one says "s"',
    ),
    (
        ("threat t1 f6 S 3 3 9", "threat t1 f6 Spoofing 3 3 9"),
        37,
        "line 37: the letter is one of S T R I D E",
    ),
    (
        ("threat t1 f6 S 3 3 9", "threat t1 f6 S 4 3 12"),
        37,
        'line 37: the likelihood is 1, 2 or 3, and this one says "4"',
    ),
    (
        ("threat t1 f6 S 3 3 9", "threat t1 f6 S 3 high 9"),
        37,
        'line 37: the impact is 1, 2 or 3, and this one says "high"',
    ),
    (
        ("threat t1 f6 S 3 3 9 An attacker", "threat t1 f6 S 3 3 An attacker"),
        37,
        'line 37: the risk is a whole number, and this one says "An"',
    ),
    (
        ("threat t1 f6 S 3 3 9", "threat t1 f66 S 3 3 9"),
        37,
        'line 37: there is no flow called f66 above this line (did you mean "f6"?)',
    ),
    (
        ("none f6 TID HTTPS", "none f6 T I D HTTPS"),
        50,
        "line 50: write the letters together with no spaces between them, as in TID",
    ),
    (
        ("none f6 TID HTTPS", "none f6 TXD HTTPS"),
        50,
        "line 50: the letters come from S T R I D E, capitals written together "
        '(TID), and this one says "TXD"',
    ),
    (
        (
            "none f6 E every page checks the staff role of the signed-in person",
            "none f6 E role check",
        ),
        51,
        "line 51: after the letters, say why there is nothing to record, "
        "in at least 5 words",
    ),
    (
        ("control c1 t1 mfa", "control c1 t1 2fa"),
        55,
        'line 55: "2fa" is not a kind of control (did you mean "mfa"?). The kinds '
        "are: access-proxy, allow-list, audit-log, authn, authz, encryption, "
        "input-validation, integrity, least-privilege, mfa, minimise-data, "
        "mutual-tls, patch, quota, rate-limit, redundancy, sandbox, secret-store, "
        "separation-of-duties, signing, tls",
    ),
    (
        ("control c1 t1 mfa", "control c1 t9 mfa"),
        55,
        "line 55: there is no threat called t9 above this line",
    ),
    (
        ("top t1 t2 t3 t4 t5", "top t1 t2 t3 t4 t5\ntop t1"),
        63,
        "line 63: there is already a top line, on line 62, and a model has one",
    ),
    (
        ("attack t1 T1110.004", "attack t1 1110"),
        63,
        "line 63: an ATT&CK technique is written T and four digits, with a "
        "sub-technique's three after a dot (T1110 or T1110.004), "
        'and this one says "1110"',
    ),
    (
        ("scope web        impacting", "scope web        in"),
        30,
        'line 30: the scope is cde, impacting or out, and this one says "in"',
    ),
    (
        (
            "scope stock-db   out firewalled, receives",
            "scope web out firewalled, receives",
        ),
        35,
        "line 35: web already has a scope line",
    ),
    (
        ("node n2 n1 and phish", "node n2 n1 both phish"),
        68,
        'line 68: a node is and or or, and this one says "both"',
    ),
    (
        ("leaf l1 n2 200 send", "leaf l1 n2 cheap send"),
        69,
        'line 69: a leaf\'s cost is a whole number, and this one says "cheap"',
    ),
    (
        ("leaf l4 n1 2000 bribe", "leaf l4 l3 2000 bribe"),
        72,
        "line 72: l3 is a leaf, one step, and nothing can sit under a leaf",
    ),
    (
        ("cheapest g1 100", "cheapest g1 100 dollars\ncheapest g1 100"),
        74,
        "line 74: g1 already has a cheapest line",
    ),
    (
        ("control c1 t1 mfa", "control c1 t1 ___"),
        55,
        "line 55: this line still has a gap (___) to fill in",
    ),
]


@pytest.mark.parametrize("case", MALFORMED, ids=[c[2][:60] for c in MALFORMED])
def test_a_line_out_of_format_gets_its_number_and_what_was_expected(
    files, case
) -> None:
    (old, new), number, expected = case
    text = change(old, new)
    said = files.say("reads", text)
    assert said.startswith(f"line {number}: "), said
    assert expected in said, said
    # Every other part points at the reads part instead of guessing.
    assert files.say("ranking", text) == tm.POINTER
    assert files.say("findings", text, CHECKOUT_REF) == tm.POINTER


def test_a_bad_line_also_shows_how_its_kind_of_line_is_written(files) -> None:
    said = files.say("reads", change("threat t1 f6 S 3 3 9", "threat t1 f6 S 3 3"))
    assert said.endswith(
        "A threat line is written: "
        "threat ID FLOW LETTER LIKELIHOOD IMPACT RISK A/An ... can ..."
    ), said


def test_a_threat_must_be_a_sentence_about_who_can_do_what(files) -> None:
    for words in [
        "Passwords can be guessed",
        "The attacker signs in to the back office with a stolen password",
        "attackers can sign in to the back office with a stolen password",
    ]:
        text = PARCELS_MODEL.replace(
            "An attacker on the internet can sign in as a driver with a phished "
            "password and redirect parcels",
            words,
        )
        said = files.say("reads", text)
        assert said.startswith("line 11: after the risk, write what can go wrong")


def test_a_name_used_above_its_own_line_is_told_to_move(files) -> None:
    lines = PARCELS_MODEL.splitlines(keepends=True)
    moved = "".join(lines[3:7] + lines[:3] + lines[7:])  # elements, then zones
    said = files.say("reads", moved)
    assert said == (
        "line 1: the zone internet is only defined on line 5, below this one. "
        "Move line 5 up: a line can only use names that the lines above it define"
    )


def test_comments_blank_lines_tabs_and_windows_line_endings_read(files) -> None:
    text = PARCELS_MODEL.replace("\n", "\r\n").replace("zone depot ", "zone\tdepot\t")
    text = "﻿# a comment\r\n\r\n" + text + "top  # not a second top: a comment\r\n"
    said = files.say("reads", text.replace("top t1 t2\r\n", "", 1) + "")
    assert said == "ok"
    assert files.say("reads", PARCELS_MODEL + "   # only a comment\n") == "ok"


def test_a_missing_empty_or_binary_model(files, tmp_path) -> None:
    missing = str(tmp_path / "nowhere.tm")
    said, status = tm.run(["reads", missing])
    assert (said, status) == (f"there is no model at {missing} yet", 0)
    assert tm.run(["tree", missing]) == (tm.POINTER, 0)
    said = files.say("reads", "# nothing yet\n\n")
    assert said == "the model is empty: it has no line of the format yet"
    # Nothing is wrong with nothing, so every other part says the same
    # instead of passing: an untouched lab has no check that reads "ok".
    for part in CHECKOUT_PARTS:
        assert files.say(part, "# nothing yet\n", CHECKOUT_REF) == said, part
    assert files.say("stride", "\n") == said
    assert tm.run(["reads", str(tmp_path)])[0].endswith("a model is a file")
    binary = tmp_path / "model.docx"
    binary.write_bytes(b"PK\x03\x04\xff\xfe\x00")
    assert "isn't plain text" in tm.run(["reads", str(binary)])[0]


def test_no_change_to_a_line_makes_any_part_crash(files) -> None:
    # Each line of both models cut short at every word, and each line
    # removed: whatever a learner leaves half-typed, every part answers in
    # a sentence.
    for model, ref, parts in [
        (CHECKOUT_MODEL, CHECKOUT_REF, CHECKOUT_PARTS),
        (PARCELS_MODEL, PARCELS_REF, PARCELS_PARTS),
    ]:
        reference = tm.read_reference(files.reference(ref))
        lines = model.splitlines()
        variants = []
        for i, line in enumerate(lines):
            words = line.split()
            for keep in range(len(words)):
                cut = " ".join(words[:keep])
                variants.append([*lines[:i], cut, *lines[i + 1 :]])
            variants.append(lines[:i] + lines[i + 1 :])
        unreadable = 0
        for variant in variants:
            try:
                m = tm.load(files.model("\n".join(variant) + "\n"))
            except tm.Bad as error:
                assert str(error).startswith("line "), error
                unreadable += 1
                continue
            for part in parts:
                said = tm.PARTS[part](m, reference, None)
                assert said is None or isinstance(said, str)
            for only in [1, 2, "rest"]:
                tm.controls(m, reference, only)
        # Most half-typed lines don't read; the rest reach every part.
        assert 0 < unreadable < len(variants)


# --- without a reference: what a learner can run -------------------------------


def test_a_learner_can_check_format_and_sums_without_a_reference(files) -> None:
    for part in ["reads", "stride", "ranking", "controls", "tree", "abuse"]:
        assert files.say(part, PARCELS_MODEL) == "ok", part
    said = files.say("ranking", change("threat t2 f5 S 3 2 6", "threat t2 f5 S 3 2 5"))
    assert said == "line 38: the risk says 5, and likelihood 3 times impact 2 is 6"
    said = files.say("controls", change("control c2 t2 signing", "control c2 t2 tls"))
    assert said == "a control is of a kind that doesn't answer its threat"
    said = files.say("tree", change("cheapest g1 100", "cheapest g1 250"))
    assert said == "the cheapest line isn't the cheapest path through the tree"


def test_the_parts_that_need_the_design_say_so_without_one(files) -> None:
    for part in ["diagram", "boundaries", "findings", "scope", "attack", "kept"]:
        said = files.say(part, CHECKOUT_MODEL)
        assert said == (
            f"the {part} part compares the model with the design's own answers, "
            "which only the lab's checks hold. By yourself you can run: "
            "reads, stride, ranking, controls, tree, abuse"
        )


# --- the rules one by one, on the second story ----------------------------------


def test_stride_rules(files) -> None:
    both = PARCELS_MODEL.replace("none f3 TRIDE", "none f3 STRIDE")
    said = files.say("stride", both)
    assert said == "a none line covers a letter that the same flow has a threat for"
    # Punctuation and the model's own names don't make two threats differ.
    same = PARCELS_MODEL.replace(
        "A driver can deny marking a parcel delivered because the app keeps no "
        "record of who did",
        "An attacker on the internet can sign in as a driver, with a phished "
        "password, and redirect parcels (f1).",
    )
    said = files.say("stride", same)
    assert said == "two threats read the same once the names are taken out"
    # A flow inside one zone needs no review.
    assert "f2" not in PARCELS_MODEL.split("threat", 1)[1]


def test_a_weakness_under_either_letter_and_its_none_lines(files) -> None:
    as_tampering = PARCELS_MODEL.replace("threat t2 f3 S 3 2 6", "threat t2 f3 T 3 3 9")
    as_tampering = as_tampering.replace("none f3 TRIDE", "none f3 RIDE")
    as_tampering = as_tampering.replace("none f1 TIDE", "none f1 TIDE") + (
        "threat t4 f3 S 1 1 1 An insider at the maps company can send reports "
        "under another company's name\naccept t4 the maps company vets its staff\n"
    )
    assert files.say("findings", as_tampering, PARCELS_REF) == "ok"
    # A design can say that neither letter may be waved through: then the
    # model records both, the forged sender and the changed route.
    ref = json.loads(json.dumps(PARCELS_REF))
    ref["weak"][1]["no_none"] = ["S", "T"]
    said = files.say("findings", PARCELS_MODEL, ref)
    assert said == (
        "something the design describes as weak is marked as nothing to record"
    )
    assert files.say("findings", as_tampering, ref) == "ok"


def test_two_threats_on_one_weakness_the_rated_one_stands_for_it(files) -> None:
    # A second, lesser spoofing threat written first doesn't hide the one
    # the design describes.
    text = PARCELS_MODEL.replace(
        "threat t1 f1 S 3 3 9",
        "threat t0 f1 S 1 2 2 An insider with a driver's unlocked phone can "
        "mark parcels as delivered\naccept t0 the phone locks after a minute\n"
        "threat t1 f1 S 3 3 9",
    )
    assert files.say("findings", text, PARCELS_REF) == "ok"
    assert files.say("controls", text, PARCELS_REF) == "ok"
    assert files.say("controls", text, PARCELS_REF, "--only", "1") == "ok"


def test_either_lets_a_pair_share_a_zone_or_not(files) -> None:
    apart = PARCELS_MODEL.replace(
        "zone maps-co the maps company",
        "zone maps-co the maps company\nzone cloud-db the cloud's managed database",
    ).replace("element parcels-db store depot", "element parcels-db store cloud-db")
    apart += (
        "none f2 STRIDE the database takes only the app's own role over a "
        "private link\n"
    )
    assert files.failing(PARCELS_PARTS, apart, PARCELS_REF) == {}
    ref = {key: value for key, value in PARCELS_REF.items() if key != "either"}
    said = files.say("boundaries", apart, ref)
    assert said == (
        "two parts the design puts on one network under one owner are in "
        "different zones"
    )


def test_ranking_rules(files) -> None:
    said = files.say("ranking", PARCELS_MODEL.replace("top t1 t2\n", ""))
    assert said == "the top line doesn't list every threat of risk 6 or more, once each"
    said = files.say("ranking", PARCELS_MODEL.replace("top t1 t2", "top t1 t2 t3"))
    assert said == "the top line doesn't list every threat of risk 6 or more, once each"
    said = files.say("ranking", PARCELS_MODEL.replace("top t1 t2", "top t1 t1"))
    assert said == "the top line doesn't list every threat of risk 6 or more, once each"


def test_tree_rules(files) -> None:
    no_tree = PARCELS_MODEL.split("goal g1")[0]
    said = files.say("tree", no_tree)
    assert said == "there is no attack tree: it starts with a goal line"
    lesser = PARCELS_MODEL.replace("goal g1 t1", "goal g1 t2")
    said = files.say("tree", lesser)
    assert said == "the attack tree's goal isn't one of the highest risks"
    empty = PARCELS_MODEL.replace(
        "leaf l3 n1 500 bribe a driver", "node n3 n1 or bribe"
    )
    assert files.say("tree", empty) == (
        "line 26: n3 has nothing under it: a goal or a node needs a leaf or a "
        "node below it"
    )
    no_cheapest = PARCELS_MODEL.replace("cheapest g1 120\n", "")
    said = files.say("tree", no_cheapest)
    assert said == "the attack tree has no cheapest line for its goal"
    # "and" adds its steps and "or" takes the cheapest: 100 + 20 against 500.
    for wrong in ["20", "100", "500", "620"]:
        text = PARCELS_MODEL.replace("cheapest g1 120", f"cheapest g1 {wrong}")
        said = files.say("tree", text)
        assert said == "the cheapest line isn't the cheapest path through the tree"


def test_abuse_rules(files) -> None:
    untested = PARCELS_MODEL.replace(
        "test x2 a2 post an unsigned report and expect it to be refused\n", ""
    )
    said = files.say("abuse", untested)
    assert said == "a risk of 6 or more has no abuse case with a test"
    not_a_story = PARCELS_MODEL.replace("As a rival, I post", "A rival posts")
    said = files.say("reads", not_a_story)
    assert said.startswith(
        "line 30: after the threat, write the abuse case as a story in the "
        "attacker's voice: As a/an ..., I ... so that ..."
    )


def test_kept_rules(files) -> None:
    deleted = "\n".join(
        line
        for line in PARCELS_MODEL.splitlines()
        if " t2 " not in f"{line} " and not line.startswith(("abuse a2", "test x2"))
    ).replace("top t1", "top t1")
    assert files.say("reads", deleted) == "ok"
    said = files.say("kept", deleted, PARCELS_REF)
    assert said == "a threat the approved model had is gone"
    # Fixing a kept threat (its letter, its rating) keeps it.
    fixed = PARCELS_MODEL.replace("threat t2 f3 S 3 2 6", "threat t2 f3 T 3 3 9")
    fixed = fixed.replace("none f3 TRIDE", "none f3 SRIDE")
    assert files.say("kept", fixed, PARCELS_REF) == "ok"


# --- --quiet, for debug labs ---------------------------------------------------


def test_quiet_says_the_same_sentence_whatever_is_wrong_in_a_part(files) -> None:
    by_part: dict[str, set[str]] = {}
    for text, part, _why in CHECKOUT_WRONG.values():
        said = files.say(part, text, CHECKOUT_REF, "--quiet")
        assert said != "ok"
        by_part.setdefault(part, set()).add(said)
    assert {part: len(said) for part, said in by_part.items()} == dict.fromkeys(
        by_part, 1
    )
    assert by_part["controls"] == {tm.QUIET["controls"]}
    assert set(by_part) == set(CHECKOUT_PARTS) - {"reads"}
    # A right model is still "ok", and a bad line is still named.
    assert files.say("findings", CHECKOUT_MODEL, CHECKOUT_REF, "--quiet") == "ok"
    said = files.say("reads", "zone\n", None, "--quiet")
    assert said.startswith("line 1: this line stops too soon: a name is missing")


# --- the command line, and a reference an author got wrong ---------------------


def test_usage_mistakes_end_with_status_2_and_a_sentence(files) -> None:
    model = files.model(PARCELS_MODEL)
    said, status = tm.run(["reeds", model])
    assert status == 2 and '"reeds" is not a part (did you mean "reads"?)' in said
    assert tm.run(["reads"])[1] == 2
    assert tm.run(["reads", model, "--loud"])[1] == 2
    assert tm.run(["controls", model, "--only", "1"])[1] == 2
    reference = files.reference(PARCELS_REF)
    assert tm.run(["findings", model, reference, "--only", "1"])[1] == 2
    assert tm.run(["controls", model, reference, "--only", "0"])[1] == 2
    assert tm.run(["controls", model, reference, "--only=2"]) == ("ok", 0)
    said, status = tm.run(["controls", model, reference, "--only", "3"])
    assert status == 2 and "it has 2 weaknesses" in said


def test_help_prints_the_format(files) -> None:
    said, status = tm.run(["--help"])
    assert status == 0
    for kind in tm.SHAPES:
        assert f"\n    {kind} " in said, kind
    for control in tm.ALL_CONTROLS:
        assert control in said, control
    assert tm.run([]) == (said, 0)


@pytest.mark.parametrize(
    "spoil, expected",
    [
        (lambda ref: ref.update(scoop={}), "unknown keys: ['scoop']"),
        (lambda ref: ref["flows"].update(f9=["app", "nowhere"]), "flow f9 must be"),
        (lambda ref: ref["weak"][0].update(flow="f7"), "weakness 1: its flow"),
        (lambda ref: ref["weak"][0].update(letters=["X"]), "weakness 1: letters"),
        (lambda ref: ref["weak"][0].update(L=4), "weakness 1: L must be"),
        (lambda ref: ref["weak"][0].update(controls=["2fa"]), "weakness 1: controls"),
        (lambda ref: ref["weak"][0].update(attack=["T1110.004"]), "weakness 1: attack"),
        (lambda ref: ref["weak"][0].update(why="x"), "weakness 1: unknown keys"),
        (lambda ref: ref.update(either=[["app", "nowhere"]]), '"either" must be'),
        (lambda ref: ref.update(kept={"t1": "f8"}), '"kept" must map'),
        (lambda ref: ref.update(scope={"app": "cde"}), '"scope" must name every'),
    ],
)
def test_a_reference_an_author_got_wrong_is_refused_loudly(
    files, spoil, expected
) -> None:
    ref = json.loads(json.dumps(PARCELS_REF))
    spoil(ref)
    said, status = tm.run(["reads", files.model(PARCELS_MODEL), files.reference(ref)])
    assert status == 2, said
    assert said.startswith("tm-check: the lab's reference is wrong")
    assert expected in said, said


def test_a_part_whose_answers_the_reference_lacks_is_refused(files) -> None:
    model, reference = files.model(PARCELS_MODEL), files.reference(PARCELS_REF)
    said, status = tm.run(["scope", model, reference])
    assert status == 2 and 'the scope part needs "scope"' in said
    said, status = tm.run(
        ["kept", files.model(CHECKOUT_MODEL), files.reference(CHECKOUT_REF)]
    )
    assert status == 2 and 'the kept part needs "kept"' in said


def test_it_runs_as_a_program_and_reads_a_reference_from_standard_input(
    tmp_path,
) -> None:
    model = tmp_path / "model.tm"
    model.write_bytes(CHECKOUT_MODEL.encode("utf-8"))

    def program(*args: str, stdin: str = "") -> tuple[str, int]:
        done = subprocess.run(
            [sys.executable, str(TM_CHECK), *args],
            input=stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert done.stderr == ""
        return done.stdout, done.returncode

    assert program("reads", str(model)) == ("ok\n", 0)
    reference = json.dumps(CHECKOUT_REF)
    assert program("findings", str(model), "-", stdin=reference) == ("ok\n", 0)
    assert program("scope", str(model), "-", "--quiet", stdin=reference) == ("ok\n", 0)
    said, status = program("findings", str(model), "-", stdin="{not json")
    assert status == 2 and "the lab's reference is wrong" in said


def test_the_script_keeps_a_direct_shebang_and_unix_line_endings() -> None:
    # Docker builds from the working tree: a CRLF after the shebang makes
    # the kernel look for "python3\r" and the lab says only "exit 127".
    data = TM_CHECK.read_bytes()
    assert data.startswith(b"#!/usr/bin/python3\n")
    assert b"\r" not in data

"""The shop of the payments-server lab base (content/lab-bases/pay): its audit
policy, what its audit writer writes for an event, and what shop-cli sends.

The audit labs' checks decide whether a learner's policy records the right
events and never a secret by reading this writer's lines, so a writer that
invented a field, or let a value start a new line, would pass wrong work.
"""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "content" / "lab-bases" / "pay"

# In the image the shop's programs find shop_events in /usr/local/lib/shop.
sys.path.insert(0, str(BASE / "shop"))
_writes, sys.dont_write_bytecode = sys.dont_write_bytecode, True
import shop_events  # noqa: E402

sys.dont_write_bytecode = _writes


def load(name: str):
    module_name = "pay_" + name.replace("-", "_")
    loader = importlib.machinery.SourceFileLoader(module_name, str(BASE / "bin" / name))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    # No __pycache__ beside the base's files: Docker builds from that folder.
    writes, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = writes
    return module


shop_cli = load("shop-cli")
WHEN = "2026-11-23T00:02:34Z"


def test_the_shops_events_are_the_nine_of_the_plan() -> None:
    assert shop_events.EVENTS == {
        "login.ok": ["user", "src", "outcome", "password", "session"],
        "login.failed": ["user", "src", "outcome", "password", "session"],
        "page.view": ["user", "src", "path"],
        "health.check": ["user", "src", "path"],
        "role.change": ["actor", "user", "old", "new", "src", "outcome"],
        "config.change": ["actor", "setting", "old", "new", "src", "outcome"],
        "refund": ["actor", "order", "amount", "src", "outcome", "token"],
        "export": ["actor", "table", "rows", "src", "outcome", "token"],
        "card.update": ["user", "card", "src", "outcome"],
    }


def test_the_images_policy_audits_sign_ins_only() -> None:
    text = (BASE / "shop" / "audit.conf").read_text(encoding="utf-8")
    audited, masked, problems = shop_events.parse_policy(text)
    assert audited == {"login.ok": ["user", "src", "outcome"]}
    assert masked == set()
    assert problems == []


def test_a_policy_names_events_fields_and_masks() -> None:
    audited, masked, problems = shop_events.parse_policy(
        "# what the auditors asked for\n"
        "audit refund actor order amount src outcome   # no token\n"
        "\n"
        "audit card.update user card src outcome\n"
        "mask card\n"
    )
    assert audited == {
        "refund": ["actor", "order", "amount", "src", "outcome"],
        "card.update": ["user", "card", "src", "outcome"],
    }
    assert masked == {"card"}
    assert problems == []


def test_a_line_it_cant_use_is_reported_by_number_and_left_out() -> None:
    audited, masked, problems = shop_events.parse_policy(
        "audit login.ok user src outcome\n"
        "audit refund actor order amount src outcome\n"
        "\n"
        "audit role.chnage actor user old new src outcome\n"
        "audit export actor colour\n"
        "record everything\n"
        "mask\n"
        "audit\n"
    )
    assert sorted(audited) == ["login.ok", "refund"]
    assert masked == set()
    assert problems == [
        'audit.conf line 4: no such event "role.chnage"',
        'audit.conf line 5: export has no field "colour"',
        'audit.conf line 6: no such word "record"',
        "audit.conf line 7: mask needs one field",
        "audit.conf line 8: audit needs an event",
    ]


def test_only_the_policys_fields_are_written_in_its_order() -> None:
    fields = {
        "actor": "ana",
        "order": "42",
        "amount": "19.99",
        "src": "203.0.113.9",
        "outcome": "ok",
        "token": "tok-secret",
    }
    audited = {"refund": ["outcome", "actor", "order", "amount", "src"]}
    line = shop_events.trail_line("refund", fields, audited, set(), WHEN)
    assert line == (
        "time=2026-11-23T00:02:34Z event=refund outcome=ok actor=ana order=42"
        " amount=19.99 src=203.0.113.9"
    )
    assert "tok-secret" not in line


def test_an_event_the_policy_doesnt_name_is_not_written() -> None:
    audited = {"refund": ["actor"]}
    assert (
        shop_events.trail_line("page.view", {"user": "ana"}, audited, set(), WHEN)
        is None
    )


def test_a_field_the_event_didnt_carry_is_never_made_up() -> None:
    audited = {"refund": ["actor", "order"]}
    line = shop_events.trail_line("refund", {"actor": "ana"}, audited, set(), WHEN)
    assert line == "time=2026-11-23T00:02:34Z event=refund actor=ana"


def test_a_masked_field_keeps_its_last_four_characters() -> None:
    audited = {"card.update": ["user", "card"]}
    fields = {"user": "ana", "card": "4242424242424242"}
    line = shop_events.trail_line("card.update", fields, audited, {"card"}, WHEN)
    assert line.endswith("user=ana card=************4242")
    assert "4242424242424242" not in line
    assert shop_events.mask("123") == "123"
    assert shop_events.mask("") == ""


def test_a_value_can_never_start_a_line_of_its_own() -> None:
    # Log injection: a value with a line break in it must stay one line.
    audited = {"refund": ["actor", "amount"]}
    fields = {
        "actor": "ana",
        "amount": "5.00\ntime=2026-01-01T00:00:00Z event=refund actor=mallory",
    }
    line = shop_events.trail_line("refund", fields, audited, set(), WHEN)
    assert "\n" not in line and "\r" not in line
    assert line.startswith("time=2026-11-23T00:02:34Z event=refund actor=ana amount=")
    assert shop_events.shown("a\rb") == "a\\rb"


@pytest.mark.parametrize(
    ("value", "written"),
    [
        ("ana", "ana"),
        ("", '""'),
        ("two words", '"two words"'),
        ('say "hi"', '"say \\"hi\\""'),
        ("a=b", '"a=b"'),
        ("back\\slash", "back\\\\slash"),
    ],
)
def test_values_are_written_so_they_read_back_one_way(value, written) -> None:
    assert shop_events.shown(value) == written


def test_shop_cli_fills_every_field_of_the_event() -> None:
    fields = shop_cli.fields_for("refund", ["order=42", "amount=19.99"])
    assert list(fields) == shop_events.EVENTS["refund"]
    assert fields["order"] == "42" and fields["amount"] == "19.99"
    assert fields["outcome"] == "ok" and fields["src"] == "127.0.0.1"
    assert fields["token"].startswith("tok-")


def test_shop_cli_makes_a_new_secret_each_time() -> None:
    first = shop_cli.fields_for("login.failed", [])
    second = shop_cli.fields_for("login.failed", [])
    assert first["outcome"] == "failed"
    assert first["password"] != second["password"]
    assert first["session"] != second["session"]


def test_shop_cli_keeps_a_value_with_an_equals_sign_whole() -> None:
    assert (
        shop_cli.fields_for("page.view", ["path=/search?q=a=b"])["path"]
        == "/search?q=a=b"
    )


def test_shop_cli_has_an_everyday_value_for_every_field() -> None:
    for event, fields in shop_events.EVENTS.items():
        for field in fields:
            assert shop_cli.everyday(event, field) != ""


def test_shop_cli_refuses_a_field_the_event_doesnt_have(capsys) -> None:
    with pytest.raises(SystemExit) as stopped:
        shop_cli.fields_for("refund", ["colour=red"])
    assert stopped.value.code == 2
    assert 'refund has no field "colour"' in capsys.readouterr().err
    with pytest.raises(SystemExit):
        shop_cli.fields_for("refund", ["just-a-word"])

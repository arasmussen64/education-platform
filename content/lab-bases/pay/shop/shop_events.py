"""What the shop can do, and how its audit writer writes it down.

Scenery for the payments-server labs: shop-cli (which makes the shop do
something) and shop-audit (which writes the audit trail) both read this
file, so they always agree on the events and their fields. Installed as
/usr/local/lib/shop/shop_events.py. Its cases are in
tools/tests/test_pay_shop.py.
"""

# Every event the shop can make, with the fields it carries. An audit policy
# (/etc/shop/audit.conf) chooses which events and which fields are written.
EVENTS = {
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

SOCKET = "/run/shop/audit.sock"
POLICY = "/etc/shop/audit.conf"


def parse_policy(text: str) -> tuple[dict[str, list[str]], set[str], list[str]]:
    """Reads an audit policy.

        audit EVENT FIELD...    record EVENT with these fields
        mask FIELD              write only the last four characters of FIELD

    Returns the fields to write for each audited event, the masked fields,
    and one sentence for every line that can't be used. A line with a
    problem is left out; the other lines still count.
    """
    audited: dict[str, list[str]] = {}
    masked: set[str] = set()
    problems: list[str] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        words = raw.split("#", 1)[0].split()
        if not words:
            continue
        where = f"audit.conf line {number}"
        if words[0] == "audit":
            if len(words) < 2:
                problems.append(f"{where}: audit needs an event")
                continue
            event, fields = words[1], words[2:]
            if event not in EVENTS:
                problems.append(f'{where}: no such event "{event}"')
                continue
            unknown = [field for field in fields if field not in EVENTS[event]]
            if unknown:
                problems.append(f'{where}: {event} has no field "{unknown[0]}"')
                continue
            audited[event] = fields
        elif words[0] == "mask":
            if len(words) != 2:
                problems.append(f"{where}: mask needs one field")
                continue
            masked.add(words[1])
        else:
            problems.append(f'{where}: no such word "{words[0]}"')
    return audited, masked, problems


def mask(value: str) -> str:
    """Only the last four characters, the rest as stars."""
    return "*" * max(len(value) - 4, 0) + value[-4:]


def shown(value: str) -> str:
    """A value as it is written in the trail: always on one line, so a
    value can never start a line that looks like another event."""
    value = value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    if value == "" or any(char in value for char in ' "='):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def trail_line(
    event: str,
    fields: dict[str, str],
    audited: dict[str, list[str]],
    masked: set[str],
    when: str,
) -> str | None:
    """The audit trail's line for one event, or None when the policy doesn't
    audit it. Only the fields the policy names are written, in its order;
    a field the event didn't carry is left out, never made up."""
    if event not in audited:
        return None
    parts = [f"time={when}", f"event={event}"]
    for field in audited[event]:
        if field not in fields:
            continue
        value = str(fields[field])
        if field in masked:
            value = mask(value)
        parts.append(f"{field}={shown(value)}")
    return " ".join(parts)

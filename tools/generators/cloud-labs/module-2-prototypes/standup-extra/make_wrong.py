"""Writes the stand-up lab's known-wrong fixes as variations of solution.sh,
so each differs from the reference by exactly one omission or mistake."""

import sys
from pathlib import Path

folder = Path(sys.argv[1])
solution = (folder / "solution.sh").read_text(encoding="utf-8").replace("\r\n", "\n")
wrong = folder / "wrong"
wrong.mkdir(exist_ok=True)


def variant(name: str, why: str, old: str, new: str) -> None:
    assert old in solution, f"{name}: {old!r} not in solution.sh"
    text = f"# Wrong: {why}\n" + solution.replace(old, new)
    (wrong / name).write_bytes(text.encode("utf-8"))


variant(
    "not-enabled.sh",
    "dc1's service is started but not enabled, so the domain is gone after the next reboot.",
    "sudo systemctl enable --now dc1",
    "sudo systemctl start dc1",
)
variant(
    "default-password-rules.sh",
    "the domain keeps its out-of-the-box password rules: 7 characters and no lockout.",
    "on-dc samba-tool domain passwordsettings set --min-pwd-length=14 --account-lockout-threshold=5\n",
    "",
)
variant(
    "policy-not-linked.sh",
    "the Group Policy object exists but is linked to nothing, so it applies to nobody.",
    "on-dc samba-tool gpo setlink 'OU=Shop,DC=ad,DC=shop,DC=test' \"$gpo\" -U Administrator --password='Shop-Admin-1'\n",
    "",
)
variant(
    "everyone-in-the-group.sh",
    "erin was added to linux-admins too, so the group no longer means what it says.",
    "on-dc samba-tool group addmembers linux-admins dana",
    "on-dc samba-tool group addmembers linux-admins dana,erin",
)
variant(
    "anyone-can-log-in.sh",
    "lab is joined but nobody restricted who may log in, so every domain account can.",
    "sudo realm permit -g linux-admins@ad.shop.test\n",
    "",
)
variant(
    "no-forwarder-on-dc.sh",
    "dc1 was given no forwarder, so a member that asks dc1 can't resolve the site's own names.",
    " \\\n  --option='dns forwarder = 10.0.9.1'",
    "",
)
print(sorted(p.name for p in wrong.glob("*.sh")))

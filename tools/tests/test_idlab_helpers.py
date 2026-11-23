"""The identity-lab base's smaller helpers (content/lab-bases/id/): the time
sync client's reading of a chrony.conf and of a time server's answer, and
the one file the base shares with another base, and kc-wait, which decides
whether Keycloak's unit counts as started.
"""

import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest
from idlab_files import BASE, ROOT, timesync

# --- timesync: the stand-in for chronyd's client side -----------------------------


def test_the_servers_are_the_files_server_and_pool_lines_in_order() -> None:
    conf = (
        "# Where this server gets its time from.\n"
        "server time.shop.test iburst\n"
        "  pool pool.shop.test iburst maxsources 2   # a pool\n"
        "#server old.shop.test\n"
        "driftfile /var/lib/chrony/chrony.drift\n"
        "server\n"
    )
    assert timesync.servers(conf) == ["time.shop.test", "pool.shop.test"]
    assert timesync.servers("") == []


def reply(seconds: float, leap: int = 0, stratum: int = 8) -> bytes:
    """A time server's 48-byte answer saying it is `seconds` (Unix time)."""
    whole = int(seconds)
    fraction = int((seconds - whole) * 2**32)
    head = bytes([(leap << 6) | (4 << 3) | 4, stratum]) + bytes(38)
    return head + struct.pack("!II", whole + timesync.NTP_EPOCH, fraction)


def test_the_answer_gives_the_servers_time_minus_ours() -> None:
    # Asked at 1000.0 by our clock, answered at 1000.2: our clock read
    # 1000.1 in the middle, and the server said 520.1. We are 480 s ahead.
    assert timesync.read_reply(reply(520.1), 1000.0, 1000.2) == pytest.approx(-480.0)
    assert timesync.read_reply(reply(2200.1), 1000.0, 1000.2) == pytest.approx(1200.0)


def test_a_server_that_says_it_has_no_time_is_not_believed() -> None:
    # Leap indicator 3 ("clock not synchronized") and stratum 0 are how a
    # time server says it never found a source of its own.
    with pytest.raises(timesync.Unsynchronised):
        timesync.read_reply(reply(520.1, leap=3), 1000.0, 1000.2)
    with pytest.raises(timesync.Unsynchronised):
        timesync.read_reply(reply(520.1, stratum=0), 1000.0, 1000.2)
    with pytest.raises(OSError):
        timesync.read_reply(b"short", 1000.0, 1000.2)


def test_the_machines_offset_is_whole_seconds_with_a_sign() -> None:
    assert timesync.parse_offset("+480\n") == 480
    assert timesync.parse_offset("-1200") == -1200
    assert timesync.parse_offset("+0") == 0
    assert timesync.parse_offset("") == 0
    # Something this client didn't write: it won't guess.
    assert timesync.parse_offset("2026-11-22 10:00:00") is None
    assert timesync.parse_offset("+8m") is None


# --- ca-whatif: one file, in two bases ------------------------------------------------

POLICY_COPY = ROOT / "content" / "lab-bases" / "policy" / "bin" / "ca-whatif"
ID_COPY = BASE / "bin" / "ca-whatif"


def test_the_identity_bases_copy_of_ca_whatif_is_the_policy_bases() -> None:
    """ca-whatif (the conditional-access "what if" tool) has one source, in
    the policy-lab base, and a copy in this base that must be the same
    bytes (Module 4's plan, section 4.1, decision 7): a lab on one base and
    a lab on the other must get the same verdicts. Neither file exists
    until the policy base is built, and then both must."""
    if not POLICY_COPY.exists() and not ID_COPY.exists():
        pytest.skip("ca-whatif isn't written yet (it arrives with the policy base)")
    assert POLICY_COPY.exists(), (
        f"{ID_COPY.relative_to(ROOT).as_posix()} exists without its source, "
        f"{POLICY_COPY.relative_to(ROOT).as_posix()}"
    )
    assert ID_COPY.exists(), (
        f"copy {POLICY_COPY.relative_to(ROOT).as_posix()} to "
        f"{ID_COPY.relative_to(ROOT).as_posix()}: the identity base needs it too"
    )
    assert ID_COPY.read_bytes() == POLICY_COPY.read_bytes(), (
        "the two copies of ca-whatif differ: change the policy base's, "
        "then copy it over the identity base's"
    )


# --- kc-wait: what makes "started" mean "answering" -----------------------------------

KC_WAIT = BASE / "lib" / "kc-wait"

# A python3 for kc-wait to find first on its PATH: it notes which of
# kcapi.py's verbs was asked for and answers as the test says.
STUB_PYTHON = """#!/bin/bash
echo "$2" >> "$STUB_LOG"
case $2 in
  ready) [ "$STUB_READY" = yes ] ;;
  apply-if-changed)
    echo "keycloak: shop.json, line 4: a gap" >&2
    exit "$STUB_APPLY"
    ;;
esac
"""


def run_kc_wait(tmp_path: Path, ready: str, apply_status: int):
    """Runs kc-wait with the stub python3 (and a sleep that doesn't) first
    on its PATH; returns the finished process and the verbs it asked for."""
    if sys.platform == "win32" or not shutil.which("bash"):
        pytest.skip("kc-wait is run on Linux only (CI), where bash is the lab's")
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    for name, text in (("python3", STUB_PYTHON), ("sleep", "#!/bin/bash\n")):
        (stubs / name).write_bytes(text.encode())
        (stubs / name).chmod(0o755)
    log = tmp_path / "asked"
    log.touch()
    env = {
        **os.environ,
        "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}",
        "STUB_LOG": str(log),
        "STUB_READY": ready,
        "STUB_APPLY": str(apply_status),
    }
    done = subprocess.run(
        ["bash", str(KC_WAIT)], env=env, capture_output=True, text=True, timeout=120
    )
    return done, log.read_text().split()


@pytest.mark.parametrize("status", [0, 1, 3])
def test_a_realm_file_that_cant_be_applied_doesnt_fail_keycloaks_start(
    tmp_path: Path, status: int
) -> None:
    # kc-wait is the unit's ExecStartPost. If it failed, systemd would start
    # Keycloak again, find the same file and go round for ever. So whatever
    # apply-if-changed says, the start is done; its line reaches the journal.
    done, asked = run_kc_wait(tmp_path, "yes", status)
    assert done.returncode == 0
    assert asked == ["ready", "apply-if-changed"]
    assert "keycloak: shop.json, line 4: a gap" in done.stderr


def test_a_keycloak_that_never_answers_does_fail_the_start(tmp_path: Path) -> None:
    done, asked = run_kc_wait(tmp_path, "no", 0)
    assert done.returncode == 1
    assert set(asked) == {"ready"} and len(asked) == 560
    assert "no answer" in done.stderr


def test_kc_wait_ends_the_start_itself() -> None:
    # The same promise read from the file, for machines where the two tests
    # above are skipped: apply-if-changed is never the script's last word
    # (no "exec"), its failure is swallowed, and the script ends with exit 0.
    lines = [
        line.strip()
        for line in KC_WAIT.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    applies = [line for line in lines if "apply-if-changed" in line]
    assert applies == ["python3 /usr/local/lib/idlab/kcapi.py apply-if-changed || true"]
    assert lines[-1] == "exit 0"


def test_the_federation_labs_base_fix_finds_nothing_to_change() -> None:
    """The first topic on this base (csa.sec.federation) worked around two
    faults with a script in each of its labs, base-fix, which rewrites the
    image's kcapi.py and kc-wait: each of these lines, if it is still
    there. Both faults are mended here, so the script must find none of
    them (a rewrite on top of the mended files would undo part of the
    mending), and both files must still be where it opens them. This test
    can go once no lab carries a base-fix."""
    replaced = [
        ("kcapi.py", 'DROPPED = ("id", "containerId", "subComponents")\n'),
        ("kcapi.py", '    data.pop("users", None)\n'),
        ("kc-wait", "exec python3 /usr/local/lib/idlab/kcapi.py apply-if-changed\n"),
    ]
    for name, line in replaced:
        text = (BASE / "lib" / name).read_text(encoding="utf-8")
        assert line not in text, f"base-fix would rewrite {name}: {line.strip()}"


# --- The base's shape -----------------------------------------------------------------


def test_every_script_in_the_base_has_unix_line_endings() -> None:
    # Docker builds from the working tree. A script saved with Windows line
    # endings fails in the image with "bad interpreter" (exit 127).
    crlf = [
        path.relative_to(BASE).as_posix()
        for path in sorted(BASE.rglob("*"))
        if path.is_file() and b"\r\n" in path.read_bytes()
    ]
    assert not crlf, f"Windows line endings in: {', '.join(crlf)}"


def test_every_python_script_in_the_base_is_python_312() -> None:
    # The lab image's Python is Ubuntu 24.04's 3.12, older than the one these
    # tests run on, and "ruff format" at the repository's own target writes
    # "except A, B:", which 3.12 refuses (test_policy_checklib.py has the
    # story). These files are formatted with --target-version py312.
    import ast

    scripts = [
        path
        for path in sorted(BASE.rglob("*"))
        if path.is_file()
        and (
            path.suffix == ".py"
            or path.read_bytes().startswith(b"#!/usr/bin/env python3")
        )
    ]
    assert BASE / "lib" / "kcapi.py" in scripts and BASE / "bin" / "signin" in scripts
    for script in scripts:
        ast.parse(script.read_text(encoding="utf-8"), feature_version=(3, 12))


def test_the_base_starts_from_the_network_base() -> None:
    import labcheck

    dockerfile = (BASE / "Dockerfile").read_text(encoding="utf-8")
    assert labcheck.base_named_in(dockerfile) == "net"
    assert Path(BASE.parent / "net" / "Dockerfile").exists()

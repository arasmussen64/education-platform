"""The identity-lab base's smaller helpers (content/lab-bases/id/): the time
sync client's reading of a chrony.conf and of a time server's answer, and
the one file the base shares with another base.
"""

import struct
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


def test_the_base_starts_from_the_network_base() -> None:
    import labcheck

    dockerfile = (BASE / "Dockerfile").read_text(encoding="utf-8")
    assert labcheck.base_named_in(dockerfile) == "net"
    assert Path(BASE.parent / "net" / "Dockerfile").exists()

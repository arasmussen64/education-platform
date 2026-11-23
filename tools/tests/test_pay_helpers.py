"""The payments-server lab base's helpers (content/lab-bases/pay), the parts
of them that are plain functions: what a check reads from journalctl
--verify, from OSV-Scanner's report and from OpenSCAP's output, the
benchmark's crosswalk, the scanner's database, and the two tampering tools.

The texts they are given here were captured from the real programs in the
base's image on 2026-11-22 (systemd 255.4-1ubuntu8.19, OSV-Scanner 2.7.0,
OpenSCAP 1.3.9); the programs themselves run in the probe lab's contract
and in the labs built on the base (csa.sec.audit, csa.sec.vulnerabilities,
csa.sec.compliance), not here.
"""

# The captured outputs and the data stream's XML are kept as the programs
# wrote them, long lines and all.
# ruff: noqa: E501

import importlib.machinery
import importlib.util
import io
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "content" / "lab-bases" / "pay"


def load(folder: str, name: str):
    path = BASE / folder / name
    module_name = "pay_" + name.replace("-", "_").removesuffix(".py")
    loader = importlib.machinery.SourceFileLoader(module_name, str(path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    # No __pycache__ beside the base's files: Docker builds from that folder.
    writes, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = writes
    return module


seal_range = load("lib", "seal-range")
scan_tsv = load("lib", "scan-tsv")
oscap_rules = load("lib", "oscap-rules")
refs = load("lib", "refs.py")
advisory_zip = load("lib", "advisory-zip")
lab_flip = load("bin", "lab-flip")
forge = load("bin", "lab-forge-journal")


# seal-range: journalctl --verify's own words, captured.

SEALED = """PASS: copy.journal
=> Validated from Mon 2026-11-23 00:04:21 UTC to Mon 2026-11-23 00:04:30 UTC, final 0 entries not sealed.
"""
SEALED_WITH_A_TAIL = """PASS: /var/log/journal/2478b1c16a084cbebc9e6e6294794ca4.audit/system.journal
=> Validated from Mon 2026-11-23 00:03:04 UTC to Mon 2026-11-23 00:03:10 UTC, final 2.725083s entries not sealed.
"""
FORGED = "PASS: forged.journal\n"
FLIPPED = """391840: Invalid hash (c85ec9b8ffaa3609 vs. d9c95d06d42df49c)
391840: Invalid object contents: Bad message
File corruption detected at flipped.journal:3741760 (of 8388608 bytes, 44%).
FAIL: flipped.journal (Bad message)
"""
WRONG_KEY = """38f980: Tag failed verification
File corruption detected at copy.journal:3733888 (of 8388608 bytes, 44%).
FAIL: copy.journal (Bad message)
"""
NO_KEY = """Journal file copy.journal has sealing enabled but verification key has not been passed using --verify-key=.
FAIL: copy.journal (Required key not available)
"""
CLEAN_RESTART = """392c98: Epoch sequence not continuous (13 vs 13)
File corruption detected at /var/log/journal/2478b1c16a084cbebc9e6e6294794ca4.audit/system.journal:3746968 (of 8388608 bytes, 44%).
FAIL: /var/log/journal/2478b1c16a084cbebc9e6e6294794ca4.audit/system.journal (Bad message)
"""


@pytest.mark.parametrize(
    ("output", "code", "line"),
    [
        (SEALED, 0, "sealed 2026-11-23T00:04:21Z 2026-11-23T00:04:30Z"),
        (SEALED_WITH_A_TAIL, 0, "sealed 2026-11-23T00:03:04Z 2026-11-23T00:03:10Z"),
        (FORGED, 0, "unsealed"),
        (FLIPPED, 1, "failed: Invalid hash (c85ec9b8ffaa3609 vs. d9c95d06d42df49c)"),
        (WRONG_KEY, 1, "failed: Tag failed verification"),
        (CLEAN_RESTART, 1, "failed: Epoch sequence not continuous (13 vs 13)"),
        ("FAIL: copy.journal (Bad message)\n", 1, "failed: Bad message"),
        ("", 0, "failed: journalctl --verify said nothing"),
        ("", 1, "failed: journalctl --verify stopped without saying why"),
    ],
)
def test_seal_range_reads_a_verification(output, code, line) -> None:
    assert seal_range.verdict(output, code) == line


def test_seal_range_reports_a_missing_key_in_journalctls_words() -> None:
    said = seal_range.verdict(NO_KEY, 1)
    assert said.startswith("failed: Journal file copy.journal has sealing enabled")


def test_a_validated_range_never_hides_a_failure() -> None:
    # A file that fails must say so even when journalctl also printed a
    # range for it: "sealed" has to mean the whole file verified.
    assert seal_range.verdict(SEALED + FLIPPED, 1).startswith("failed: ")
    assert seal_range.verdict(SEALED + FLIPPED, 0).startswith("failed: ")


def test_seal_ranges_compare_as_text() -> None:
    # Checks compare the range's end with a time from date -u +%FT%TZ.
    _, start, end = seal_range.verdict(SEALED, 0).split()
    assert start < end
    assert not end < "2026-11-23T00:04:30Z"
    assert end < "2026-11-23T00:04:31Z"


def test_seal_range_picks_the_file_being_written(tmp_path) -> None:
    folder = tmp_path / "var" / "abc.audit"
    folder.mkdir(parents=True)
    (folder / "system@000660e650796466-896679b7f6123504.journal~").write_bytes(b"old")
    (folder / "system.journal").write_bytes(b"live")
    roots = (str(tmp_path / "var"), str(tmp_path / "run"))
    assert seal_range.newest_file("audit", "abc", roots) == str(
        folder / "system.journal"
    )


def test_seal_range_looks_on_disk_before_memory(tmp_path) -> None:
    for root in ("var", "run"):
        (tmp_path / root / "abc.audit").mkdir(parents=True)
        (tmp_path / root / "abc.audit" / "system.journal").write_bytes(b"x")
    roots = (str(tmp_path / "var"), str(tmp_path / "run"))
    assert seal_range.newest_file("audit", "abc", roots).startswith(
        str(tmp_path / "var")
    )
    assert seal_range.newest_file("other", "abc", roots) is None


# scan-tsv: OSV-Scanner's JSON report, cut down to the fields it reads.


def finding(cve: str, name: str, fixed: str | None, extra=()) -> dict:
    events = [{"introduced": "0"}] + ([{"fixed": fixed}] if fixed else [])
    return {
        "id": f"UBUNTU-{cve}",
        "upstream": [cve],
        "affected": [
            {
                "package": {"ecosystem": "Ubuntu:22.04:LTS", "name": name},
                "ranges": [{"events": [{"introduced": "0"}, {"fixed": "0-jammy"}]}],
            },
            {
                "package": {"ecosystem": "Ubuntu:Pro:24.04:LTS", "name": name},
                "ranges": [{"events": [{"introduced": "0"}, {"fixed": "0-pro"}]}],
            },
            {
                "package": {"ecosystem": "Ubuntu:24.04", "name": name},
                "ranges": [{"type": "ECOSYSTEM", "events": events}],
            },
            *extra,
        ],
    }


def entry(name: str, binary: str, version: str, found: list[tuple[dict, str]]) -> dict:
    return {
        "package": {
            "name": name,
            "os_package_name": binary,
            "version": version,
            "ecosystem": "Ubuntu:24.04",
        },
        "vulnerabilities": [vulnerability for vulnerability, _ in found],
        "groups": [
            {"ids": [vulnerability["id"]], "max_severity": severity}
            for vulnerability, severity in found
        ],
    }


def test_scan_tsv_gives_one_line_per_finding_and_source_package() -> None:
    regresshion = finding("CVE-2024-6387", "openssh", "1:9.6p1-3ubuntu13.3")
    host_key = finding("CVE-2025-26465", "openssh", "1:9.6p1-3ubuntu13.8")
    chroot = finding("CVE-2025-32463", "sudo", "1.9.15p5-3ubuntu5.24.04.1")
    openssh = [(regresshion, "8.1"), (host_key, "6.8")]
    report = {
        "results": [
            {
                "source": {"path": "/var/lib/dpkg/status", "type": "os"},
                "packages": [
                    entry("sudo", "sudo", "1.9.15p5-3ubuntu5", [(chroot, "9.3")]),
                    # One source package, three binary packages: once each.
                    entry("openssh", "openssh-client", "1:9.6p1-3ubuntu13", openssh),
                    entry("openssh", "openssh-server", "1:9.6p1-3ubuntu13", openssh),
                    entry(
                        "openssh", "openssh-sftp-server", "1:9.6p1-3ubuntu13", openssh
                    ),
                ],
            }
        ]
    }
    assert scan_tsv.rows(report) == [
        ("CVE-2024-6387", "openssh", "1:9.6p1-3ubuntu13", "1:9.6p1-3ubuntu13.3", "8.1"),
        (
            "CVE-2025-26465",
            "openssh",
            "1:9.6p1-3ubuntu13",
            "1:9.6p1-3ubuntu13.8",
            "6.8",
        ),
        (
            "CVE-2025-32463",
            "sudo",
            "1.9.15p5-3ubuntu5",
            "1.9.15p5-3ubuntu5.24.04.1",
            "9.3",
        ),
    ]


def test_scan_tsv_with_no_findings_is_empty() -> None:
    assert scan_tsv.rows({"results": []}) == []


def test_scan_tsv_takes_the_fix_for_this_release_and_this_package() -> None:
    # The published records say "Ubuntu:24.04:LTS"; a scan says
    # "Ubuntu:24.04". A fix for another release, for Ubuntu Pro or for a
    # different package of the same record is never the answer.
    other = {
        "package": {"ecosystem": "Ubuntu:24.04:LTS", "name": "openssh-ssh1"},
        "ranges": [{"events": [{"introduced": "0"}, {"fixed": "0-ssh1"}]}],
    }
    record = finding("CVE-2025-26465", "openssh", "1:9.6p1-3ubuntu13.8", extra=[other])
    record["affected"][2]["package"]["ecosystem"] = "Ubuntu:24.04:LTS"
    package = {"name": "openssh", "version": "1", "ecosystem": "Ubuntu:24.04"}
    assert scan_tsv.fixed_in(record, package) == "1:9.6p1-3ubuntu13.8"


def test_scan_tsv_writes_a_dash_where_no_fix_is_named() -> None:
    record = finding("CVE-2025-26465", "openssh-ssh1", None)
    package = {"name": "openssh-ssh1", "version": "1", "ecosystem": "Ubuntu:24.04"}
    assert scan_tsv.fixed_in(record, package) == "-"
    report = {
        "results": [{"packages": [entry("openssh-ssh1", "x", "1", [(record, None)])]}]
    }
    assert scan_tsv.rows(report) == [("CVE-2025-26465", "openssh-ssh1", "1", "-", "-")]


def test_scan_tsv_names_the_cve() -> None:
    assert (
        scan_tsv.cve_of({"id": "UBUNTU-CVE-2025-1", "upstream": ["CVE-2025-1"]})
        == "CVE-2025-1"
    )
    assert scan_tsv.cve_of({"id": "UBUNTU-CVE-2025-2"}) == "CVE-2025-2"
    assert scan_tsv.cve_of({"id": "USN-1-1", "aliases": ["CVE-2025-3"]}) == "CVE-2025-3"


# oscap-rules: oscap's output has a carriage return before each tab.

OSCAP = (
    "--- Starting Evaluation ---\n\n"
    "Title\r\tEnsure PAM Enforces Password Requirements - Minimum Length\n"
    "Rule\r\txccdf_org.ssgproject.content_rule_accounts_password_pam_minlen\n"
    "Result\r\tfail\n\n"
    "Title\r\tDisable SSH Root Login\n"
    "Rule\r\txccdf_org.ssgproject.content_rule_sshd_disable_root_login\n"
    "Result\r\tpass\n\n"
    "Title\r\tEnsure /tmp Located On Separate Partition\n"
    "Rule\r\txccdf_org.ssgproject.content_rule_partition_for_tmp\n"
    "Result\r\tnotapplicable\n\n"
)


def test_oscap_rules_reads_the_result_blocks() -> None:
    assert oscap_rules.results(OSCAP) == {
        "accounts_password_pam_minlen": "fail",
        "sshd_disable_root_login": "pass",
        "partition_for_tmp": "notapplicable",
    }


def test_oscap_rules_gives_no_result_to_a_rule_cut_short() -> None:
    # A run that crashed after printing a rule's name: no result for it.
    cut = (
        OSCAP
        + "Title\r\tX\nRule\r\txccdf_org.ssgproject.content_rule_journald_storage\n"
    )
    assert "journald_storage" not in oscap_rules.results(cut)
    assert oscap_rules.results("") == {}


def test_oscap_rules_runs_named_rules_of_the_pinned_profile_with_no_tailoring() -> None:
    words = oscap_rules.command(
        [
            "journald_storage",
            "xccdf_org.ssgproject.content_rule_sshd_disable_root_login",
        ]
    )
    assert words == [
        "oscap",
        "xccdf",
        "eval",
        "--profile",
        "xccdf_org.ssgproject.content_profile_cis_level1_server",
        "--rule",
        "xccdf_org.ssgproject.content_rule_journald_storage",
        "--rule",
        "xccdf_org.ssgproject.content_rule_sshd_disable_root_login",
        "/usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml",
    ]
    assert "--tailoring-file" not in words


def test_oscap_rules_knows_a_crash_by_either_exit_status() -> None:
    # -11 from Python's subprocess, 139 from a shell.
    assert oscap_rules.CRASHED == {-11, 139}


def stand_in(monkeypatch, program: str, rules: list[str]) -> None:
    """Has oscap-rules run a Python one-liner in oscap's place."""
    monkeypatch.setattr(
        oscap_rules, "command", lambda _: [sys.executable, "-c", program]
    )
    monkeypatch.setattr(sys, "argv", ["oscap-rules", *rules])


def test_oscap_rules_prints_each_rule_in_the_order_asked(monkeypatch, capsys) -> None:
    program = f"import sys; sys.stdout.buffer.write({OSCAP.encode()!r}); sys.exit(2)"
    stand_in(
        monkeypatch,
        program,
        ["sshd_disable_root_login", "accounts_password_pam_minlen"],
    )
    with pytest.raises(SystemExit) as stopped:
        oscap_rules.main()
    # oscap's exit status 2 only says a rule failed: the results are the answer.
    assert stopped.value.code == 0
    assert capsys.readouterr().out == (
        "sshd_disable_root_login pass\naccounts_password_pam_minlen fail\n"
    )


def test_oscap_rules_says_unknown_for_a_rule_with_no_result(
    monkeypatch, capsys
) -> None:
    program = f"import sys; sys.stdout.buffer.write({OSCAP.encode()!r}); sys.exit(1)"
    stand_in(monkeypatch, program, ["no_such_rule", "partition_for_tmp"])
    with pytest.raises(SystemExit) as stopped:
        oscap_rules.main()
    assert stopped.value.code == 1
    assert (
        capsys.readouterr().out
        == "no_such_rule unknown\npartition_for_tmp notapplicable\n"
    )


def test_oscap_rules_stops_a_run_that_hangs_and_tries_once_more(
    monkeypatch, capsys
) -> None:
    # OpenSCAP hung for good in one whole-profile run of 28 (2026-11-22).
    monkeypatch.setenv("OSCAP_RULES_SECONDS", "0.3")
    stand_in(monkeypatch, "import time; time.sleep(60)", ["journald_storage"])
    with pytest.raises(SystemExit) as stopped:
        oscap_rules.main()
    assert stopped.value.code == 1
    said = capsys.readouterr()
    assert said.out == "journald_storage unknown\n"
    assert said.err.count("oscap hung") == 2


# refs.py: the data stream's shape, cut down.

STREAM = """<?xml version="1.0" encoding="utf-8"?>
<ds:data-stream-collection xmlns:ds="http://scap.nist.gov/schema/scap/source/1.2"
    xmlns:xccdf-1.2="http://checklists.nist.gov/xccdf/1.2">
  <xccdf-1.2:Benchmark>
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_cis_level1_server">
      <xccdf-1.2:select idref="xccdf_org.ssgproject.content_rule_sshd_disable_root_login" selected="true"/>
      <xccdf-1.2:select idref="xccdf_org.ssgproject.content_rule_journald_storage" selected="true"/>
      <xccdf-1.2:select idref="xccdf_org.ssgproject.content_rule_switched_off" selected="false"/>
    </xccdf-1.2:Profile>
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_stig">
      <xccdf-1.2:select idref="xccdf_org.ssgproject.content_rule_stig_only" selected="true"/>
    </xccdf-1.2:Profile>
    <xccdf-1.2:Group>
      <xccdf-1.2:Rule selected="false" id="xccdf_org.ssgproject.content_rule_sshd_disable_root_login">
        <xccdf-1.2:reference href="https://www.isaca.org/resources/cobit">APO01.06</xccdf-1.2:reference>
        <xccdf-1.2:reference href="http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r4.pdf">AC-6(2)</xccdf-1.2:reference>
        <xccdf-1.2:reference href="https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf">2.2.6</xccdf-1.2:reference>
        <xccdf-1.2:reference href="https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf">2.2.6</xccdf-1.2:reference>
        <xccdf-1.2:reference href="https://www.cisecurity.org/benchmark/ubuntu_linux/">5.1.20</xccdf-1.2:reference>
      </xccdf-1.2:Rule>
      <xccdf-1.2:Group>
        <xccdf-1.2:Rule selected="false" id="xccdf_org.ssgproject.content_rule_journald_storage">
          <xccdf-1.2:reference href="https://www.cisecurity.org/benchmark/ubuntu_linux/">6.1.2.4</xccdf-1.2:reference>
        </xccdf-1.2:Rule>
      </xccdf-1.2:Group>
      <xccdf-1.2:Rule selected="false" id="xccdf_org.ssgproject.content_rule_switched_off">
        <xccdf-1.2:reference href="https://www.cisecurity.org/benchmark/ubuntu_linux/">9.9</xccdf-1.2:reference>
      </xccdf-1.2:Rule>
      <xccdf-1.2:Rule selected="false" id="xccdf_org.ssgproject.content_rule_stig_only">
        <xccdf-1.2:reference href="https://www.cisecurity.org/benchmark/ubuntu_linux/">8.8</xccdf-1.2:reference>
      </xccdf-1.2:Rule>
    </xccdf-1.2:Group>
  </xccdf-1.2:Benchmark>
</ds:data-stream-collection>
"""
PROFILE = "xccdf_org.ssgproject.content_profile_cis_level1_server"


def test_refs_lists_the_profiles_rules_once_each_sorted() -> None:
    assert refs.refs(io.BytesIO(STREAM.encode()), PROFILE) == [
        ("journald_storage", "cis-ubuntu-24.04", "6.1.2.4"),
        ("sshd_disable_root_login", "cis-ubuntu-24.04", "5.1.20"),
        ("sshd_disable_root_login", "nist-800-53r4", "AC-6(2)"),
        ("sshd_disable_root_login", "pci-dss-4.0", "2.2.6"),
    ]


def test_refs_follows_the_profile_asked_for() -> None:
    stig = refs.refs(
        io.BytesIO(STREAM.encode()), "xccdf_org.ssgproject.content_profile_stig"
    )
    assert stig == [("stig_only", "cis-ubuntu-24.04", "8.8")]
    with pytest.raises(LookupError):
        refs.refs(io.BytesIO(STREAM.encode()), "no_such_profile")


def test_refs_names_six_frameworks_and_says_which_800_53() -> None:
    assert sorted(refs.FRAMEWORKS.values()) == [
        "cis-ubuntu-24.04",
        "hipaa",
        "iso-27001-2013",
        "nist-800-171",
        "nist-800-53r4",
        "pci-dss-4.0",
    ]


# advisory-zip: the scanner's database.


def test_the_advisory_zip_is_the_same_bytes_every_time(tmp_path) -> None:
    records = {"b.json": '{"id": "B"}', "a.json": '{"id": "A"}'}
    advisory_zip.write_zip(
        str(tmp_path / "one" / "all.zip"), advisory_zip.database(records)
    )
    advisory_zip.write_zip(
        str(tmp_path / "two" / "all.zip"), advisory_zip.database(records)
    )
    first = (tmp_path / "one" / "all.zip").read_bytes()
    assert first == (tmp_path / "two" / "all.zip").read_bytes()
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        assert archive.namelist() == ["a.json", "b.json"]
        assert archive.read("a.json") == b'{"id": "A"}'


def test_the_advisory_zip_names_the_release_as_the_scanner_does() -> None:
    record = '{"package":{"ecosystem":"Ubuntu:24.04:LTS","name":"sudo"}},{"ecosystem":"Ubuntu:Pro:24.04:LTS"}'
    [(_, text)] = advisory_zip.database({"r.json": record})
    assert '"ecosystem":"Ubuntu:24.04","name":"sudo"' in text
    # Ubuntu Pro's entries are another ecosystem and stay as they are.
    assert '"Ubuntu:Pro:24.04:LTS"' in text


def test_the_committed_records_are_the_seven_of_the_story_as_published() -> None:
    names = sorted(path.name for path in (BASE / "data" / "advisories").glob("*.json"))
    assert names == [
        "UBUNTU-CVE-2024-12084.json",
        "UBUNTU-CVE-2024-32487.json",
        "UBUNTU-CVE-2024-6387.json",
        "UBUNTU-CVE-2025-26465.json",
        "UBUNTU-CVE-2025-32462.json",
        "UBUNTU-CVE-2025-32463.json",
        "UBUNTU-CVE-2025-48384.json",
    ]
    for name in names:
        text = (BASE / "data" / "advisories" / name).read_text(encoding="utf-8")
        assert '"Ubuntu:24.04:LTS"' in text, name


# The two tampering tools.


def test_lab_flip_changes_the_first_match_and_nothing_else() -> None:
    data = b"..amount=19.99..amount=19.99.."
    changed, at = lab_flip.flip(data, b"amount=19.99", b"amount=91.99")
    assert changed == b"..amount=91.99..amount=19.99.."
    assert at == 2
    assert len(changed) == len(data)


def test_lab_flip_refuses_what_would_move_bytes() -> None:
    with pytest.raises(ValueError):
        lab_flip.flip(b"amount=19.99", b"19.99", b"191.99")
    with pytest.raises(ValueError):
        lab_flip.flip(b"amount=19.99", b"", b"")
    with pytest.raises(LookupError):
        lab_flip.flip(b"amount=19.99", b"20.00", b"91.99")


def test_the_forger_rewrites_messages_only() -> None:
    export = (
        b"__CURSOR=s=1\n_PID=42\nMESSAGE=event=refund amount=19.99\n\n"
        b"__CURSOR=s=2\nSYSLOG_IDENTIFIER=amount=19.99\nMESSAGE=event=refund amount=19.99\n\n"
    )
    forged = forge.rewrite(export, b"amount=19.99", b"amount=1.00")
    assert forged.count(b"MESSAGE=event=refund amount=1.00\n") == 2
    assert b"SYSLOG_IDENTIFIER=amount=19.99\n" in forged
    assert forge.rewrite(export, b"", b"") == export

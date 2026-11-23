"""The payments-server lab base's frozen data (content/lab-bases/pay/data)
and snapshot.py, which made it: the extracts keep real rows unchanged, the
story's seven CVEs are in every file a lab looks them up in, NIST's
controls read as the printed document does, and the image's first layer is
the one every systemd lab shares.

The lessons of three topics quote numbers from these files, so a test names
the ones the plan relies on.
"""

import csv
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "content" / "lab-bases" / "pay"
DATA = BASE / "data"


def load():
    spec = importlib.util.spec_from_file_location("pay_snapshot", BASE / "snapshot.py")
    module = importlib.util.module_from_spec(spec)
    # No __pycache__ beside the base's files: Docker builds from that folder.
    writes, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = writes
    return module


snapshot = load()


def test_evenly_spreads_and_is_the_same_every_time() -> None:
    items = list(range(100))
    assert snapshot.evenly(items, 4) == [0, 25, 50, 75]
    assert snapshot.evenly(items, 4) == snapshot.evenly(items, 4)
    assert snapshot.evenly([1, 2], 5) == [1, 2]


def test_the_epss_extract_keeps_the_header_and_whole_rows() -> None:
    text = (
        "#model_version:v2026.06.15,score_date:2026-11-10T12:00:24Z\n"
        "cve,epss,percentile\n"
        "CVE-1999-0001,0.04753,0.91956\n"
        "CVE-2025-32463,0.563,0.99059\n"
        "CVE-2025-324630,0.1,0.2\n"
    )
    assert snapshot.epss_extract(text, {"CVE-2025-32463"}) == (
        "#model_version:v2026.06.15,score_date:2026-11-10T12:00:24Z\n"
        "cve,epss,percentile\n"
        "CVE-2025-32463,0.563,0.99059\n"
    )


def test_the_kev_extract_keeps_seven_columns_newest_first() -> None:
    catalog = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2025-48384",
                "vendorProject": "Git",
                "product": "Git",
                "vulnerabilityName": "left out",
                "dateAdded": "2025-08-25",
                "dueDate": "2025-09-15",
                "knownRansomwareCampaignUse": "Unknown",
                "forensicTriage": "No",
            },
            {
                "cveID": "CVE-2025-32463",
                "vendorProject": "Sudo",
                "product": "Sudo, with a comma",
                "dateAdded": "2025-09-29",
                "dueDate": "2025-10-20",
                "knownRansomwareCampaignUse": "Unknown",
            },
            {"cveID": "CVE-2020-1", "dateAdded": "2021-01-01"},
        ]
    }
    assert snapshot.kev_extract(catalog, {"CVE-2025-48384", "CVE-2025-32463"}) == (
        "cveID,vendorProject,product,dateAdded,dueDate,knownRansomwareCampaignUse,forensicTriage\n"
        'CVE-2025-32463,Sudo,"Sudo, with a comma",2025-09-29,2025-10-20,Unknown,\n'
        "CVE-2025-48384,Git,Git,2025-08-25,2025-09-15,Unknown,No\n"
    )


def test_ssvc_comes_from_cisas_container_only() -> None:
    record = {
        "containers": {
            "cna": {
                "metrics": [{"other": {"type": "ssvc", "content": {"options": []}}}]
            },
            "adp": [
                {"title": "CVE Program Container"},
                {
                    "title": "CISA ADP Vulnrichment",
                    "metrics": [
                        {"cvssV3_1": {"baseScore": 9.3}},
                        {
                            "other": {
                                "type": "ssvc",
                                "content": {
                                    "options": [
                                        {"Exploitation": "active"},
                                        {"Automatable": "no"},
                                        {"Technical Impact": "total"},
                                    ]
                                },
                            }
                        },
                    ],
                },
            ],
        }
    }
    assert snapshot.ssvc_of(record) == ("active", "no", "total")
    assert snapshot.ssvc_of({"containers": {"adp": [{"metrics": []}]}}) is None
    assert snapshot.ssvc_of({}) is None


def test_where_vulnrichment_keeps_a_cve() -> None:
    assert snapshot.ssvc_path("CVE-2025-32463") == "2025/32xxx/CVE-2025-32463.json"
    assert snapshot.ssvc_path("CVE-2024-6387") == "2024/6xxx/CVE-2024-6387.json"
    assert snapshot.ssvc_path("CVE-2002-0367") == "2002/0xxx/CVE-2002-0367.json"


def test_parameters_are_written_as_the_printed_document_writes_them() -> None:
    params = {
        "n": {"label": "number"},
        "t": {"label": "organization-defined time period"},
        "pick": {
            "select": {
                "how-many": "one-or-more",
                "choice": ["lock for {{ insert: param, t }}", "notify"],
            }
        },
    }
    prose = (
        "Limit to {{ insert: param, n }} attempts in {{ insert: param, t }} ;"
        " then {{ insert: param, pick }} ."
    )
    assert snapshot.fill(prose, params) == (
        "Limit to [Assignment: organization-defined number] attempts in"
        " [Assignment: organization-defined time period]; then [Selection (one or"
        " more): lock for [Assignment: organization-defined time period]; notify]."
    )
    assert snapshot.fill("{{ insert: param, gone }}", {}) == (
        "[Assignment: organization-defined value]"
    )


def test_a_control_is_written_with_its_enhancements() -> None:
    control = {
        "id": "ac-7",
        "title": "Unsuccessful Logon Attempts",
        "props": [{"name": "label", "value": "AC-7"}],
        "params": [{"id": "n", "label": "number"}],
        "parts": [
            {
                "name": "statement",
                "parts": [
                    {
                        "name": "item",
                        "props": [{"name": "label", "value": "a."}],
                        "prose": "Enforce a limit of {{ insert: param, n }} attempts.",
                    }
                ],
            },
            {"name": "guidance", "prose": "Why it matters."},
            {"name": "assessment-objective", "prose": "left out"},
        ],
        "controls": [
            {
                "id": "ac-7.1",
                "title": "Automatic Account Lock",
                "props": [
                    {"name": "label", "value": "AC-7(1)"},
                    {"name": "status", "value": "withdrawn"},
                ],
            }
        ],
    }
    assert snapshot.control_text(control) == (
        "AC-7 Unsuccessful Logon Attempts\n\n"
        "Control:\n"
        "a. Enforce a limit of [Assignment: organization-defined number] attempts.\n\n"
        "Discussion:\nWhy it matters.\n\n"
        "AC-7(1) Automatic Account Lock\n\nWithdrawn.\n"
    )


# The committed files.


def rows(name: str) -> list[dict]:
    lines = (DATA / name).read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith("#")]
    return list(csv.DictReader(lines))


def test_every_story_cve_can_be_looked_up() -> None:
    epss = {row["cve"] for row in rows("epss-2026-11-10.csv")}
    ssvc = {row["cve"] for row in rows("ssvc.csv")}
    for cve in snapshot.STORY:
        assert cve in epss, cve
        assert cve in ssvc, cve
        assert (DATA / "advisories" / f"UBUNTU-{cve}.json").exists(), cve


def test_the_numbers_the_plan_quotes() -> None:
    # The vulnerabilities brief's worked example reads these three lines.
    epss = {row["cve"]: row for row in rows("epss-2026-11-10.csv")}
    kev = {row["cveID"]: row for row in rows("kev-2026.11.10.csv")}
    ssvc = {row["cve"]: row for row in rows("ssvc.csv")}
    assert (epss["CVE-2025-32463"]["epss"], epss["CVE-2025-32463"]["percentile"]) == (
        "0.563",
        "0.99059",
    )
    assert kev["CVE-2025-32463"]["dateAdded"] == "2025-09-29"
    assert ssvc["CVE-2025-32463"] == {
        "cve": "CVE-2025-32463",
        "exploitation": "active",
        "automatable": "no",
        "technical_impact": "total",
    }
    # Two of the seven are in KEV; a lookup of the others finds nothing.
    assert sorted(set(kev) & set(snapshot.STORY)) == [
        "CVE-2025-32463",
        "CVE-2025-48384",
    ]


def test_the_extracts_hold_enough_others_to_make_a_lookup_real() -> None:
    assert len(rows("epss-2026-11-10.csv")) == 77
    assert len(rows("kev-2026.11.10.csv")) == 52
    first = (DATA / "epss-2026-11-10.csv").read_text(encoding="utf-8").splitlines()[0]
    assert first == "#model_version:v2026.06.15,score_date:2026-11-10T12:00:24Z"
    assert list(rows("kev-2026.11.10.csv")[0]) == snapshot.KEV_COLUMNS


def test_nists_controls_are_there_with_their_parameters() -> None:
    names = sorted(path.name for path in (DATA / "nist-800-53r5").glob("*.txt"))
    assert names == [
        "AC-6.txt",
        "AC-7.txt",
        "AU-11.txt",
        "AU-9.txt",
        "IA-5.txt",
        "SI-2.txt",
    ]
    ac7 = (DATA / "nist-800-53r5" / "AC-7.txt").read_text(encoding="utf-8")
    assert (
        "a. Enforce a limit of [Assignment: organization-defined number] consecutive"
        " invalid logon attempts by a user during a [Assignment: organization-defined"
        " time period]; and" in ac7
    )
    ac6 = (DATA / "nist-800-53r5" / "AC-6.txt").read_text(encoding="utf-8")
    assert "Non-privileged Access for Nonsecurity Functions" in ac6
    for name in names:
        text = (DATA / "nist-800-53r5" / name).read_text(encoding="utf-8")
        assert "{{" not in text, name


def test_no_data_file_has_windows_line_endings() -> None:
    # Docker builds from the working tree, and checks compare these files'
    # checksums with the image's.
    for path in sorted(BASE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            assert b"\r\n" not in path.read_bytes(), path.relative_to(BASE).as_posix()


def test_sources_names_every_data_file() -> None:
    sources = (DATA / "SOURCES.md").read_text(encoding="utf-8")
    for name in ("epss-2026-11-10.csv", "kev-2026.11.10.csv", "ssvc.csv"):
        assert f"`{name}`" in sources
    for word in ("CC BY-SA 4.0", "CC0 1.0", "BSD-3-Clause", "No licence is stated"):
        assert word in sources


# The Dockerfile.


def first_run(dockerfile: Path) -> str:
    text = dockerfile.read_text(encoding="utf-8")
    found = re.search(r"^RUN .*?(?=^\S|\Z)", text, re.MULTILINE | re.DOTALL)
    return re.sub(r"\n\s*\n.*", "", found.group(0), flags=re.DOTALL).strip()


def test_the_first_layer_is_the_one_every_systemd_lab_shares() -> None:
    ours = first_run(BASE / "Dockerfile")
    assert ours == first_run(ROOT / "content" / "lab-bases" / "net" / "Dockerfile")
    assert ours.startswith("RUN apt-get update") and ours.endswith("shop")


def test_each_download_is_pinned_by_version_and_checksum() -> None:
    text = (BASE / "Dockerfile").read_text(encoding="utf-8")
    downloads = re.findall(r"curl -fsSL -o (\S+) (https://\S+)", text)
    assert [url for _, url in downloads] == [
        "https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64",
        "https://github.com/ComplianceAsCode/content/releases/download/v0.1.82/scap-security-guide-0.1.82.zip",
    ]
    for target, _ in downloads:
        assert re.search(
            rf'echo "[0-9a-f]{{64}}  {re.escape(target)}" \| sha256sum -c -', text
        )
    # And the README records the same versions.
    readme = (BASE / "README.md").read_text(encoding="utf-8")
    assert "2.7.0" in readme and "0.1.82" in readme


def test_every_file_the_dockerfile_copies_is_there() -> None:
    text = (BASE / "Dockerfile").read_text(encoding="utf-8")
    sources = re.findall(r"^COPY (\S+) \S+$", text, re.MULTILINE)
    assert sources
    for source in sources:
        assert (BASE / source).exists(), source
    # No private key is in the repository: the root test key is made at build.
    assert "ssh-keygen" in text
    assert not list(BASE.rglob("*key*"))

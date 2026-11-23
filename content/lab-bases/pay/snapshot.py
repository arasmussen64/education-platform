"""Makes the frozen data files in data/ from their public sources.

Run by an author, on their own machine, on the day the snapshot is taken
(never at image build: the build must give the same files every time):

    python content/lab-bases/pay/snapshot.py

It downloads what data/SOURCES.md lists, keeps a small extract of each, and
writes the files with Unix line endings. Nothing here runs in a lab. After
running it, update the dates and counts in data/SOURCES.md and the README,
and run the base's tests and the labs that read the files: the lessons quote
these numbers.

The pure functions (everything but fetch and main) are tested in
tools/tests/test_pay_snapshot.py.
"""

import csv
import gzip
import io
import json
import re
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"

# The story: the seven vulnerabilities in the five packages the base pins at
# their Ubuntu 24.04 release versions.
STORY = [
    "CVE-2024-6387",
    "CVE-2024-12084",
    "CVE-2024-32487",
    "CVE-2025-26465",
    "CVE-2025-32462",
    "CVE-2025-32463",
    "CVE-2025-48384",
]

# The day of the snapshot, and the commit of cisagov/kev-data that held the
# catalog on that day.
EPSS_DATE = "2026-11-10"
KEV_COMMIT = "6b8d7ba579672e4f84e2b1f255724aa97c8455b4"

EPSS_URL = f"https://epss.empiricalsecurity.com/epss_scores-{EPSS_DATE}.csv.gz"
KEV_URL = (
    "https://raw.githubusercontent.com/cisagov/kev-data/"
    f"{KEV_COMMIT}/known_exploited_vulnerabilities.json"
)
SSVC_URL = "https://raw.githubusercontent.com/cisagov/vulnrichment/develop/{path}"
OSV_URL = "https://api.osv.dev/v1/vulns/UBUNTU-{cve}"
OSCAL_URL = (
    "https://raw.githubusercontent.com/usnistgov/oscal-content/main/"
    "nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"
)

KEV_COLUMNS = [
    "cveID",
    "vendorProject",
    "product",
    "dateAdded",
    "dueDate",
    "knownRansomwareCampaignUse",
    "forensicTriage",
]

# The controls the compliance labs quote, each with its enhancements.
CONTROLS = ["ac-6", "ac-7", "au-9", "au-11", "ia-5", "si-2"]

OTHERS_IN_KEV = 50
OTHERS_NOT_IN_KEV = 20


def evenly(items: list, count: int) -> list:
    """count items spread evenly over the list, the same ones every time."""
    if count >= len(items):
        return list(items)
    step = len(items) / count
    return [items[int(index * step)] for index in range(count)]


def cve_key(cve: str) -> tuple[int, int]:
    """CVE-2025-32463 as (2025, 32463), for sorting as the catalogues do."""
    _, year, number = cve.split("-")
    return int(year), int(number)


def epss_extract(text: str, wanted: set[str]) -> str:
    """The EPSS file's own two header lines, then the wanted CVEs' rows in
    the file's order."""
    lines = text.splitlines()
    kept = lines[:2] + [line for line in lines[2:] if line.split(",")[0] in wanted]
    return "\n".join(kept) + "\n"


def kev_extract(catalog: dict, wanted: set[str]) -> str:
    """The columns the labs use, for the wanted CVEs, newest listing first."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(KEV_COLUMNS)
    rows = [v for v in catalog["vulnerabilities"] if v["cveID"] in wanted]
    rows.sort(key=lambda v: (v["dateAdded"], cve_key(v["cveID"])), reverse=True)
    for row in rows:
        writer.writerow([row.get(column, "") for column in KEV_COLUMNS])
    return out.getvalue()


def ssvc_of(record: dict) -> tuple[str, str, str] | None:
    """(exploitation, automatable, technical impact) from a CVE record's CISA
    ADP container, or None when CISA wrote no SSVC decision points for it."""
    for adp in record.get("containers", {}).get("adp", []):
        for metric in adp.get("metrics", []):
            other = metric.get("other") or {}
            if other.get("type") != "ssvc":
                continue
            options = {}
            for option in other["content"]["options"]:
                options.update(option)
            return (
                options["Exploitation"],
                options["Automatable"],
                options["Technical Impact"],
            )
    return None


def ssvc_path(cve: str) -> str:
    """Where vulnrichment keeps a CVE: 2025/32xxx/CVE-2025-32463.json."""
    year, number = cve_key(cve)
    return f"{year}/{number // 1000}xxx/{cve}.json"


INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([^\s}]+)\s*\}\}")


def fill(prose: str, params: dict) -> str:
    """OSCAL prose with each parameter written as SP 800-53 prints it:
    [Assignment: organization-defined number]."""

    def shown(match: re.Match) -> str:
        param = params.get(match.group(1))
        if param is None:
            return "[Assignment: organization-defined value]"
        if "select" in param:
            select = param["select"]
            how = " (one or more)" if select.get("how-many") == "one-or-more" else ""
            choices = "; ".join(fill(c, params) for c in select.get("choice", []))
            return f"[Selection{how}: {choices}]"
        label = param.get("label", "value")
        if not label.startswith("organization-defined"):
            # The catalogue's newer parameters leave the words out; the
            # printed SP 800-53 has them in every assignment.
            label = f"organization-defined {label}"
        return f"[Assignment: {label}]"

    # The catalogue's prose leaves a space after a parameter ("... ; and").
    return re.sub(r"\s+([;,.\]])", r"\1", INSERT.sub(shown, prose))


def label_of(part: dict) -> str:
    for prop in part.get("props", []):
        if prop["name"] == "label" and prop.get("class") != "sp800-53a":
            return prop["value"]
    return ""


def statement_lines(part: dict, params: dict, depth: int = 0) -> list[str]:
    lines = []
    prose = fill(part.get("prose", ""), params)
    label = label_of(part) if depth else ""
    if prose or label:
        lines.append("  " * max(depth - 1, 0) + f"{label} {prose}".strip())
    for child in part.get("parts", []):
        if child.get("name") == "item":
            lines.extend(statement_lines(child, params, depth + 1))
    return lines


def control_text(control: dict, inherited: dict | None = None) -> str:
    """One control, with its enhancements, as plain text."""
    params = dict(inherited or {})
    for param in control.get("params", []):
        params[param["id"]] = param
    label = label_of(control) or control["id"].upper()
    lines = [f"{label} {control['title']}", ""]
    status = [p["value"] for p in control.get("props", []) if p["name"] == "status"]
    if "withdrawn" in status:
        lines += ["Withdrawn.", ""]
    for part in control.get("parts", []):
        if part.get("name") == "statement":
            lines += ["Control:"] + statement_lines(part, params) + [""]
        elif part.get("name") == "guidance":
            lines += ["Discussion:", fill(part.get("prose", ""), params), ""]
    text = "\n".join(lines)
    for enhancement in control.get("controls", []):
        text += "\n" + control_text(enhancement, params)
    return text


def find_control(catalog: dict, control_id: str) -> dict:
    for group in catalog["catalog"]["groups"]:
        for control in group.get("controls", []):
            if control["id"] == control_id:
                return control
    raise KeyError(control_id)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "lab-data-snapshot"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def write(path: Path, text: str) -> None:
    # write_bytes, not write_text: on Windows write_text would write CRLF.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    print(f"{path.relative_to(DATA.parent).as_posix()}: {len(text.encode('utf-8'))} bytes")


def main() -> None:
    epss = gzip.decompress(fetch(EPSS_URL)).decode("utf-8")
    kev = json.loads(fetch(KEV_URL))
    in_kev = sorted({v["cveID"] for v in kev["vulnerabilities"]}, key=cve_key)
    scored = [line.split(",")[0] for line in epss.splitlines()[2:]]
    recent = [
        cve
        for cve in scored
        if cve.startswith(("CVE-2024-", "CVE-2025-")) and cve not in set(in_kev)
    ]
    others_kev = evenly([c for c in in_kev if c not in STORY], OTHERS_IN_KEV)
    others = set(others_kev) | set(evenly(recent, OTHERS_NOT_IN_KEV))
    wanted = set(STORY) | others

    write(DATA / f"epss-{EPSS_DATE}.csv", epss_extract(epss, wanted))
    write(DATA / f"kev-{kev['catalogVersion']}.csv", kev_extract(kev, wanted))
    print(f"KEV catalog {kev['catalogVersion']}: {kev['count']} entries")

    rows = ["cve,exploitation,automatable,technical_impact"]
    for cve in sorted(wanted, key=cve_key):
        try:
            points = ssvc_of(json.loads(fetch(SSVC_URL.format(path=ssvc_path(cve)))))
        except OSError:
            points = None
        if points:
            rows.append(",".join((cve, *points)))
        elif cve in STORY:
            raise SystemExit(f"{cve}: no SSVC decision points, and the story needs them")
    write(DATA / "ssvc.csv", "\n".join(rows) + "\n")

    for cve in STORY:
        record = fetch(OSV_URL.format(cve=cve)).decode("utf-8")
        json.loads(record)
        write(DATA / "advisories" / f"UBUNTU-{cve}.json", record.rstrip("\n") + "\n")

    catalog = json.loads(fetch(OSCAL_URL))
    version = catalog["catalog"]["metadata"]["version"]
    print(f"SP 800-53 catalogue version {version}")
    for control_id in CONTROLS:
        text = control_text(find_control(catalog, control_id))
        write(DATA / "nist-800-53r5" / f"{control_id.upper()}.txt", text.rstrip() + "\n")


if __name__ == "__main__":
    main()

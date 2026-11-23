#!/usr/bin/python3
"""refs.py DATA-STREAM PROFILE: the benchmark's own crosswalk, as a table.

ComplianceAsCode writes, beside every rule, which controls of which
frameworks the rule supports. This prints them for the rules a profile
selects, one line each, tab-separated and sorted:

    rule <TAB> framework <TAB> control
    sshd_disable_root_login	pci-dss-4.0	2.2.6

Run once, when the image is built, to make /usr/share/lab-pay/refs.tsv.
Its cases are in tools/tests/test_pay_helpers.py.
"""

import sys
import xml.etree.ElementTree as ET

XCCDF = "{http://checklists.nist.gov/xccdf/1.2}"
RULE_PREFIX = "xccdf_org.ssgproject.content_rule_"

# The frameworks the labs use, by the address the data stream gives each
# reference. The data stream has more (COBIT, ISA 62443, the STIGs ...);
# they are left out. Note which NIST SP 800-53 this is: revision 4.
FRAMEWORKS = {
    "https://www.cisecurity.org/benchmark/ubuntu_linux/": "cis-ubuntu-24.04",
    "https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf": "pci-dss-4.0",
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r4.pdf": "nist-800-53r4",
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-171.pdf": "nist-800-171",
    "https://www.gpo.gov/fdsys/pkg/CFR-2007-title45-vol1/pdf/CFR-2007-title45-vol1-chapA-subchapC.pdf": "hipaa",
    "https://www.iso.org/contents/data/standard/05/45/54534.html": "iso-27001-2013",
}


def refs(stream, profile: str) -> list[tuple[str, str, str]]:
    """(rule, framework, control) for every rule the profile selects, from a
    data stream given as a path or an open file."""
    selected: set[str] | None = None
    found: set[tuple[str, str, str]] = set()
    for _, element in ET.iterparse(stream):
        if element.tag == f"{XCCDF}Profile":
            if element.get("id") == profile:
                selected = {
                    select.get("idref")
                    for select in element.iter(f"{XCCDF}select")
                    if select.get("selected") == "true"
                }
            element.clear()
        elif element.tag == f"{XCCDF}Rule":
            rule = element.get("id", "")
            for reference in element.findall(f"{XCCDF}reference"):
                framework = FRAMEWORKS.get(reference.get("href", ""))
                control = (reference.text or "").strip()
                if framework and control:
                    found.add((rule, framework, control))
            element.clear()
    if selected is None:
        raise LookupError(f"no profile called {profile}")
    return sorted(
        (rule.removeprefix(RULE_PREFIX), framework, control)
        for rule, framework, control in found
        if rule in selected
    )


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: refs.py DATA-STREAM PROFILE", file=sys.stderr)
        sys.exit(2)
    try:
        rows = refs(sys.argv[1], sys.argv[2])
    except (OSError, LookupError, ET.ParseError) as error:
        print(f"refs.py: {error}", file=sys.stderr)
        sys.exit(1)
    for row in rows:
        print("\t".join(row))


if __name__ == "__main__":
    main()

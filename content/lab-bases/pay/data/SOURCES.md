# Where the payments-server labs' data comes from

Every file here is a small, frozen extract of a public source, taken once so that a lab gives the same answers on every day. `snapshot.py`, in the folder above, made them on 2026-11-22 from the sources as they stood on the dates below. Nothing here is updated by a lab or by the image build. In the image they are in `/usr/share/lab-pay/`.

| File | What it is | Source | Licence |
| --- | --- | --- | --- |
| `advisories/UBUNTU-CVE-*.json` | Seven Ubuntu security advisories in OSV format, each copied whole: CVE-2025-32463 and CVE-2025-32462 (sudo), CVE-2024-6387 and CVE-2025-26465 (OpenSSH), CVE-2024-32487 (less), CVE-2024-12084 (rsync), CVE-2025-48384 (git) | `https://api.osv.dev/v1/vulns/UBUNTU-CVE-...`, read 2026-11-22. The records are Canonical's, from [canonical/ubuntu-security-notices](https://github.com/canonical/ubuntu-security-notices) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (that repository's licence). Attribution: Canonical Ltd., Ubuntu security notices. These copies are shared under the same licence |
| `epss-2026-11-10.csv` | EPSS scores and percentiles of 2026-11-10 (model v2026.06.15) for the seven CVEs above and 70 others, with the file's own two header lines | `https://epss.empiricalsecurity.com/epss_scores-2026-11-10.csv.gz`, the daily file that [FIRST's EPSS pages](https://www.first.org/epss/data_stats) link to | **No licence is stated.** FIRST says EPSS "makes the data freely and openly accessible". Shipped as a small extract with this attribution: EPSS, by FIRST.org and Empirical Security, scores of 2026-11-10 |
| `kev-2026.11.10.csv` | Seven columns of CISA's Known Exploited Vulnerabilities catalog, version 2026.11.10 (1,779 entries on that day), for the two of the seven CVEs that are in it and 50 others | [cisagov/kev-data](https://github.com/cisagov/kev-data) at commit `6b8d7ba579672e4f84e2b1f255724aa97c8455b4` | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (its `LICENSE`) |
| `ssvc.csv` | CISA's SSVC decision points (exploitation, automatable, technical impact) for the seven CVEs and for those of the others that CISA has assessed | The CISA ADP container of each CVE record in [cisagov/vulnrichment](https://github.com/cisagov/vulnrichment), branch `develop`, read 2026-11-22 | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (its `LICENSE`) |
| `nist-800-53r5/*.txt` | Six controls of NIST SP 800-53 Rev. 5 (release 5.2.0) with their enhancements, as plain text: AC-6, AC-7, AU-9, AU-11, IA-5, SI-2. Each parameter is written as the printed document writes it, `[Assignment: organization-defined ...]` | NIST's OSCAL catalogue, `nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json` in [usnistgov/oscal-content](https://github.com/usnistgov/oscal-content), read 2026-11-22 | Public domain in the United States, CC0 elsewhere (its `LICENSE.md`) |
| `examples/10-vendor.conf` | An SSH drop-in that lets root log in, for a worked example | Written for the labs | The repository's own |

The "others" are there so that looking a CVE up is a real lookup: 50 entries spread evenly through the KEV catalog, and 20 CVEs of 2024 and 2025 that are not in it, spread evenly through the EPSS file. They are real rows, unchanged.

Two more files are made when the image is built, from a download that is not in this repository:

| File in the image | What it is | Source | Licence |
| --- | --- | --- | --- |
| `scap/ssg-ubuntu2404-ds.xml` | The benchmark OpenSCAP reads: ComplianceAsCode's data stream for Ubuntu 24.04 | Release 0.1.82 of [ComplianceAsCode/content](https://github.com/ComplianceAsCode/content) (the base's README has the checksums) | BSD-3-Clause |
| `refs.tsv` | Which controls of which frameworks each rule of the CIS Level 1 Server profile supports | Made from that data stream's `<reference>` elements by `lib/refs.py` | BSD-3-Clause, as its source |

## What may not be here

The text of PCI DSS (copyright PCI SSC), of ISO/IEC 27001 (sold by ISO), of the CIS Benchmarks (free to download after registering, for non-commercial use) and of the AICPA's criteria may not be copied into a lab or a lesson. The labs use those documents' identifiers (`pci-dss-4.0 8.3.6`, `cis-ubuntu-24.04 5.1.20`), which are facts, and NIST's text, which is free to copy.

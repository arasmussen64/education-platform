# Writing brief: `csa.sec.vulnerabilities` (topic 48), Vulnerability management

Design only; nothing here is in the repository. Sources were read on 2026-11-12 and each fact carries its URL. Lab mechanics marked **tried** ran on 2026-11-12 in Docker Desktop 29.8.2 on the owner's PC, in privileged systemd containers on `ubuntu:24.04`; everything started was removed afterwards. Prototype files: `prototypes/audit-vuln-compliance/vuln-probe/` (the image's Dockerfile and the seven advisory records) and `captured/` (`osv-vertical.txt`, `osv-table.txt`, `epss-extract-2026-11-10.csv`, `kev-extract-2026.11.10.csv`); `dl/bod-table1.png` is BOD 26-04's Table 1 as CISA publishes it. The server labs run on the shared base in [lab-base-sec.md](lab-base-sec.md) (sections 2 to 4 are this topic's).

## 1. What the learner will be able to do

1. Run a vulnerability scan of a server's packages with a real scanner (OSV-Scanner), offline, and read each finding: the advisory, the package, the installed and fixed versions, the severity. Explain why a distribution's own advisories are the ones to trust for its packages (backported fixes).
2. Tell apart what **CVSS** (how bad the flaw is, from its vector), **EPSS** (the probability that exploitation activity is seen in the next 30 days) and **CISA's KEV catalog** (evidence that it *is* being exploited) each say, read a vector string, and decide when they disagree.
3. **Prioritise** with the asset's context: is it reachable from the internet, could an attacker automate the attack, would they get total or partial control. Apply a written policy (CISA's BOD 26-04 decision table is the model) to get each finding's remediation timeline, and say when a finding also needs forensic triage.
4. Set and compute **patch SLAs**: due dates in calendar days from the right start (PCI DSS 6.3.3's month for critical and high patches; BOD 26-04's 3, 14 or 60 days or "fix on system upgrade"), and handle the finding that can't be fixed in time with a written exception: owner, compensating control, expiry.
5. **Fix and prove it**: patch from a repository, restart what still runs the old code, rescan; keep a register and report mean time to remediate, the share fixed within SLA, and the backlog.

**The six-month core:**

- Scan, prioritise, fix, verify, track: the loop never ends, and a finding isn't fixed until a rescan says so and nothing runs the old code.
- CVSS is severity, EPSS is likelihood (next 30 days), KEV is evidence. A KEV entry beats any EPSS number; a high EPSS beats a high CVSS with no exploit in sight; exposure to the internet raises everything.
- On Ubuntu, trust Ubuntu's advisories: `1.9.15p5-3ubuntu5.24.04.1` is fixed although upstream says "before 1.9.17p1".
- BOD 26-04: exposed + in KEV + total control is 3 days and forensic triage; most other KEV entries 14 days; exposed and automatable 3 days; the rest 14, 60 or "on upgrade". The clock starts at the earlier of the KEV listing and the day you found it. PCI DSS: critical and high patches within a month of release; internal scans every three months.
- MTTR is the average days to fix; SLA compliance is fixed-on-time over fixed; a backlog shrinks only if fixes per week beat new findings per week.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.sec.threat-modeling]`. Topic 39's brief (read 2026-11-12 once it appeared beside this one) owns **likelihood**, **impact**, **risk** (likelihood × impact on stated scales), the risk matrix, residual risk, the four responses (mitigate, eliminate, transfer, accept) and ranking a list; this topic turns those into per-finding numbers and timelines, and its exceptions are topic 39's "accept, written down, with a reason". "Vulnerability" and "exploit" are defined here in one sentence each unless topic 39's final lesson does.

**Builds on (for the writer, not `prerequisites:`):**

| Topic | What this topic uses |
| --- | --- |
| `csa.linux.packages` | `apt update`/`upgrade`, `install --only-upgrade`, the `-security` pocket, `apt-mark hold`, version strings and `dpkg -l`, a package repository built into the image, `/var/run/reboot-required` and "a restart picks up the new code", mutable against immutable servers and "replace the fleet". Its labs already patch from an image's own repository; this topic never re-teaches it. |
| `csa.linux.hardening` | scan before, fix, scan after; exceptions with a reason and a compensating control (its `mcq-prove-with-scan`). |
| `csa.linux.services` | `systemctl restart`, `systemctl cat` with drop-ins, `ActiveEnterTimestamp`. |
| `csa.linux.shell`, `csa.linux.scripting` | `grep`, `awk -F`, `sort`, `cut`, a script with `chmod +x`. **New here:** awk's two-file join (`NR==FNR { … ; next }`), in the fill-in with a gap; `date -d "2026-11-09 + 3 days" +%F` for due dates (GNU `date`, which Git Bash also has), in the lesson and the write's prompt. |
| `csa.net.cidr`, `csa.net.nat` | public against private addresses: what "exposed to the internet" means for a server. |
| `csa.sec.audit` (topic 46) | if taken first: "forensic triage" looks for signs of use in the audit trail. Not required. |

**Terms this topic must define itself:** CVE and CVE ID, CNA (one sentence), advisory, affected and fixed version, source and binary package, backport, lockfile (one sentence), SBOM (one sentence; Module 20 owns it), vulnerability scanner and its database, false positive and false negative; CVSS, base/threat/environmental/supplemental metrics and the names CVSS-B, CVSS-BT, CVSS-BE, CVSS-BTE, vector string, the severity ratings; EPSS and its percentile; KEV and its fields (`dateAdded`, `dueDate`, `knownRansomwareCampaignUse`, `forensicTriage`); SSVC and its decision points (exploitation, automatable, technical impact); exposure; remediation (patch, mitigation, isolation, removal); SLA, due date, calendar day; exception (risk acceptance), compensating control; register; MTTR; SLA compliance; backlog; BOD (a binding operational directive, one sentence).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `scan-and-read` | What a scanner compares (installed versions against advisories) and where it looks (the package database; lockfiles; image layers); running OSV-Scanner offline; reading a finding; the distro's advisories and backports; why scanners disagree (different databases, different scores). |
| `cvss-epss-kev` | What each measures and who publishes it; reading a CVSS 3.1 and 4.0 vector (AV, AC, PR, UI, scope, C/I/A); the ratings (None 0.0, Low 0.1 to 3.9, Medium 4.0 to 6.9, High 7.0 to 8.9, Critical 9.0 to 10.0); "whose score"; EPSS as a 30-day probability and its percentile; KEV's criteria and fields; which to trust when they disagree. |
| `prioritise` | The asset's context (exposure, what it holds), SSVC's decision points, BOD 26-04's sixteen-row table as a policy, forensic triage, reachability as a reason to record rather than to ignore. |
| `patch-slas` | Timelines from a policy; due dates in calendar days from the earlier of KEV listing and discovery; PCI DSS 6.3.3 and 11.3.1; exceptions with owner, compensating control and expiry; "found late is already overdue". **A calculation skill: four estimate items.** |
| `remediate-and-track` | Patching from a repository, holds and pins that block it, restarting what runs old code, rescanning; the register; MTTR, SLA compliance and backlog arithmetic; rebuilding images rather than patching an immutable fleet. **A calculation skill: four estimate items.** |

## 4. Lesson plan

About 2,200 words (17 minutes), around NCSC's guidance as the main resource.

1. **The loop (NCSC, "Vulnerability management principles").** Know what you have, find what's wrong with it, decide what first, fix it, check, keep a record, again next week. NCSC's points: update by default, respond to active exploitation first, triage when there's no fix, and "deciding not to update is a senior-level risk decision". The picture: a car recall list. The manufacturer publishes recalls (advisories); you check your car's model and year (installed version); some recalls say "brakes may fail", others "the radio may reset" (severity); some are already causing crashes (exploitation).
2. **What a scanner actually does (lesson only).** It reads what's installed (on Ubuntu the package database, `/var/lib/dpkg/status`; for an app, its **lockfile**, the list of libraries with exact versions) and looks each one up in a **vulnerability database** of advisories, each naming the package, the versions affected and the first fixed version. That's all: it doesn't attack anything. Two consequences: it is only as good as its database, and it must read **the distribution's own** advisories. Ubuntu fixes old versions by patching them (a **backport**): upstream says sudo "before 1.9.17p1" is vulnerable, but Ubuntu's fixed package is `1.9.15p5-3ubuntu5.24.04.1` (fact 9). A scanner that compared upstream version numbers would flag a patched server forever. Name the common scanners (Trivy, Grype, OSV-Scanner, and the clouds' own: Amazon Inspector, Defender for Cloud, Artifact Analysis; Module 20 builds those), and say why the lab freezes a small copy of real Ubuntu advisories: the real database is hundreds of megabytes and changes daily (fact 11), and the lab's answers must not.
3. **Reading a finding (the lab's captured scan, fact 10).** `UBUNTU-CVE-2025-32463: Sudo before 1.9.17p1 allows local users to obtain root access …` / `Severity: '9.3'; Minimal Fix Version: '1.9.15p5-3ubuntu5.24.04.1'`. The ID (Ubuntu's record for **CVE-2025-32463**: a CVE ID names one flaw everywhere), the package, the installed version, the fix, the score.
4. **CVSS: how bad (FIRST's specification, fact 1).** A **vector string** describes the flaw: `AV:N` (attack from the network) or `AV:L` (local), `AC` complexity, `PR` privileges the attacker needs, `UI` whether a user must do something, scope, and the damage to confidentiality, integrity and availability. The **base score** (0 to 10) and its rating. Version 4.0 (2023-11-01, document 1.2 of 2024-06-18) renames temporal to **threat** metrics and asks users to add threat and **environmental** metrics ("Consumers of CVSS should enrich the Base metrics…"), naming the result CVSS-B, -BT, -BE or -BTE. Two lessons the lab shows: a score is about the flaw in general, not your server; and **whose score**: for CVE-2025-32462 MITRE scored 2.8 while Ubuntu's record also carries an 8.8 vector, and the scanner showed 8.8 (fact 13). Read the vector, not just the number.
5. **EPSS: how likely (FIRST's EPSS page, fact 2).** "the probability that a published CVE will be exploited in the wild in the next 30 days", recalculated every day for every CVE, with a **percentile** (how it ranks among all CVEs). In the lab's snapshot (2026-11-10): OpenSSH's CVE-2024-6387 0.995, less's CVE-2024-32487 0.006 (fact 5). The lesson supplies what a probability means for a backlog: 200 findings at 0.02 each is about four expected to see exploitation activity within the month.
6. **KEV: it's happening (CISA's KEV page, BOD text, fact 3).** CISA adds a vulnerability only when it has a CVE ID, "reliable evidence of exploitation in the wild" and clear remediation guidance. 1,779 entries in catalog 2026.11.10, each with `dateAdded`, `dueDate`, `knownRansomwareCampaignUse` and, since BOD 26-04, `forensicTriage`. The contrast the lab's data makes (fact 5): git's CVE-2025-48384 is in KEV with an EPSS of 0.044, and OpenSSH's CVE-2024-6387 is not in KEV with 0.995. **Evidence beats prediction**: a KEV entry comes first whatever its EPSS; among the rest, EPSS orders better than CVSS alone.
7. **Your context, and a policy (BOD 26-04, fact 4; SSVC).** The same flaw matters more on an internet-facing payments server than on an internal batch host. CISA's **SSVC** asks: is it being exploited (none, proof of concept, active), can an attacker automate it, does it give partial or total control; CISA's Vulnrichment publishes those values per CVE (fact 6). **BOD 26-04** (10 June 2026, replacing BOD 22-01 and 19-02) turns four yes/no questions (publicly exposed? in KEV? automatable? total control?) into sixteen rows of calendar-day timelines: **3 days and forensic triage** for exposed + KEV + total control, and for internal + KEV + automatable + total; 3 days for exposed + KEV + automatable + partial and for exposed + not KEV + automatable + total; 14 days for most other KEV rows and some exposed ones; 60 days; and "fix on system upgrade" for internal, not-KEV, not-automatable findings. It binds US federal agencies only, but it's a well-made, free policy that companies adopt; the lab's shop does. Remediation means the flaw is gone: "patching, decommissioning the system, or another action". **Forensic triage**: before you patch a flaw that has surely been used, look for signs it was used here (topic 46's audit trail).
8. **SLAs and dates (PCI DSS via Microsoft's quotation, fact 7; BOD 26-04).** PCI DSS 6.3.3: "Critical or high-security patches/updates … are installed within one month of release"; others "within an appropriate time frame … (for example, within three months of release)"; 11.3.1: internal scans "at least once every three months". BOD 26-04's clock starts when CISA lists the CVE in KEV **or** when you find it, whichever comes first: a KEV entry found a year late is already overdue on the day you find it. Calendar days, weekends included; `date -d "2026-11-09 + 3 days" +%F` prints `2026-11-12`. When a fix can't be made in time: a written **exception** with an owner, the reason, a compensating control (block the port, turn off the feature) and an expiry date, never an open-ended one. FedRAMP's timelines are changing in 2026 (fact 8): the lesson names that, not numbers.
9. **Fix, and prove the fix (lesson only; retrieval of `csa.linux.packages`).** Patch from the repository (`apt-get install --only-upgrade`), then two traps: a **hold** or a **pin** that silently keeps the old version, and a daemon that keeps running the **old code from memory** until it restarts. SSH announces its version to anyone who connects (`OpenSSH_9.6p1 Ubuntu-3ubuntu13` before, `…ubuntu13.20` after), which is how an outside scanner sees an unrestarted server. Then rescan. On a fleet built from images (immutable servers), the fix is a new image and a redeploy, not `apt` on each machine.
10. **Track (lesson only).** A **register**: one row per finding, with asset, due date, owner, status. Three numbers: **MTTR** (mean days from found to fixed), **SLA compliance** (fixed within SLA ÷ fixed), and the **backlog**'s direction (new per week against fixed per week). A finding on a machine you don't own is still tracked, with its owner named.

**Read now:** NCSC's "Vulnerability management" (the main resource, about 550 words), FIRST's EPSS page, CISA's KEV catalog page ("About" and the column descriptions), and BOD 26-04's sections "Required Actions" and Table 1. Optional: FIRST's CVSS v4.0 specification, section 2 (Base metrics) as reference.

## 5. Verified facts

All read on 2026-11-12.

| # | Claim | Source |
| --- | --- | --- |
| 1 | CVSS v4.0 specification, document version 1.2 (2024-06-18; first published 2023-11-01): ratings None 0.0, Low 0.1 to 3.9, Medium 4.0 to 6.9, High 7.0 to 8.9, Critical 9.0 to 10.0 (Table 22); "Consumers of CVSS should enrich the Base metrics with Threat and Environmental metric values"; nomenclature CVSS-B, -BT, -BE, -BTE; FIRST "licenses it to the public freely for use", with attribution, and publishers give "both the score and the vector string". | https://www.first.org/cvss/v4.0/specification-document ; https://www.first.org/cvss/v4-0/ |
| 2 | EPSS "estimates the probability that a published CVE will be exploited in the wild in the next 30 days"; scores published daily for every CVE, with percentiles; data as CSV, API (`api.first.org/epss/`) and the `empiricalsec/epss_scores` repository; FIRST says EPSS "makes the data freely and openly accessible" (no licence stated). FIRST's research page names a v5 as current; the 2026-11-10 file's header says `model_version:v2026.06.15`. | https://www.first.org/epss/ ; https://www.first.org/epss/research ; https://epss.empiricalsecurity.com/epss_scores-2026-11-10.csv.gz |
| 3 | KEV: CISA adds a vulnerability only with a CVE ID, clear remediation guidance and "reliable evidence of exploitation in the wild"; catalog version 2026.11.10 (released 2026-11-10T19:03Z) has 1,779 entries; fields `cveID, vendorProject, product, vulnerabilityName, dateAdded, shortDescription, requiredAction, dueDate, knownRansomwareCampaignUse, forensicTriage, notes, cwes`; 361 entries "Known" ransomware use; 103 with `forensicTriage` "Yes"; entries added since 2026-06-10 have due dates 3 days (126) or 14 days (36) after `dateAdded`. Data under CC0 1.0 (cisagov/kev-data `LICENSE`). | https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json ; https://raw.githubusercontent.com/cisagov/kev-data/develop/LICENSE ; BOD 22-01 page (criteria) |
| 4 | **BOD 26-04**, "Prioritizing Security Updates Based on Risk", issued 2026-06-10, "supersedes and revokes" BOD 19-02 and BOD 22-01. Four variables: publicly exposed, in the KEV, automatable by adversary, technical impact. Table 1 (an image; read and transcribed 2026-11-12), calendar days: rows 1 Y/Y/Y/Total "3 days & forensic triage"; 2 Y/Y/Y/Partial 3; 3 Y/Y/N/Total "3 days & forensic triage"; 4 Y/Y/N/Partial 14; 5 Y/N/Y/Total 3; 6 Y/N/Y/Partial 14; 7 Y/N/N/Total 14; 8 Y/N/N/Partial 60; 9 N/Y/Y/Total "3 days & forensic triage"; 10 N/Y/Y/Partial 14; 11 N/Y/N/Total 14; 12 N/Y/N/Partial 14; 13 N/N/Y/Total 60; 14 N/N/Y/Partial 60; 15 N/N/N/Total "Fix on system upgrade"; 16 N/N/N/Partial "Fix on system upgrade". Timelines start when CISA adds the CVE to KEV or the agency identifies it on an asset, whichever first. Remediation: the vulnerability "eliminated through patching, decommissioning the system, or another action". | https://www.cisa.gov/news-events/directives/bod-26-04-prioritizing-security-updates-based-risk (Table 1 image `BOD_26-04_Table_1_Remediation_Timelines_0.png`, saved as `dl/bod-table1.png`) |
| 5 | The lab's snapshot (EPSS 2026-11-10, KEV 2026.11.10): CVE-2025-32463 (sudo) EPSS 0.563, KEV added 2025-09-29; CVE-2025-48384 (git) 0.04379, KEV added 2025-08-25; CVE-2024-6387 (OpenSSH) 0.99506, not KEV; CVE-2024-12084 (rsync) 0.72514, not KEV; CVE-2024-32487 (less) 0.00628, not KEV; CVE-2025-26465 (OpenSSH) 0.07723; CVE-2025-32462 (sudo) 0.04477; CVE-2021-44228 (Log4j) 0.99999, KEV 2021-12-10. | `captured/epss-extract-2026-11-10.csv`, `captured/kev-extract-2026.11.10.csv` |
| 6 | CISA Vulnrichment (CC0 1.0) SSVC values: CVE-2025-32463 active/no/total; CVE-2025-48384 active/no/total; CVE-2024-6387 poc/no/total; CVE-2024-12084 poc/yes/total; CVE-2024-32487 none/yes/total; CVE-2025-26465 poc/no/total; CVE-2025-32462 none/no/partial; CVE-2021-44228 active/yes/total. CISA's SSVC outcomes are Track, Track*, Attend, Act. | https://github.com/cisagov/vulnrichment (each CVE's JSON, `adp` metrics of type `ssvc`) ; https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc |
| 7 | PCI DSS v4 as Microsoft quotes it: 6.3.1 vulnerabilities identified "using industry-recognized sources" and "assigned a risk ranking"; 6.3.3 "Critical or high-security patches/updates … are installed within one month of release" and "All other applicable security patches/updates are installed within an appropriate time frame … (for example, within three months of release)"; 11.3.1 internal scans and 11.3.2 external scans "at least once every three months". | https://learn.microsoft.com/en-us/entra/standards/pci-requirement-6 ; https://learn.microsoft.com/en-us/entra/standards/pci-requirement-11 |
| 8 | FedRAMP is replacing its Rev 5 remediation windows (30 days for critical and high, 90 moderate, 180 low, from the POA&M playbook) with the Vulnerability Detection and Response rules, mandatory from 2026-12-07 for every offering, and renaming impact levels to certification classes. **Secondary sources only**; FedRAMP's own VDR page returned 404 to a script. No item uses FedRAMP numbers. | https://www.dwt.com/blogs/privacy--security-law-blog/2026/07/fedramp-2026-consolidated-rules ; https://www.fedramp.gov/legacy/playbook/csp/authorization/poam/ (search results, not opened) |
| 9 | Ubuntu's advisory UBUNTU-CVE-2025-32463: ecosystem `Ubuntu:24.04:LTS`, package `sudo`, fixed `1.9.15p5-3ubuntu5.24.04.1`, versions listed as affected include `1.9.15p5-3ubuntu5`; priority reason "Allows local privilege escalation". UBUNTU-CVE-2024-6387: openssh fixed in `1:9.6p1-3ubuntu13.3`. Records are CC BY-SA 4.0 (canonical/ubuntu-security-notices). | https://api.osv.dev/v1/vulns/UBUNTU-CVE-2025-32463 ; https://api.osv.dev/v1/vulns/UBUNTU-CVE-2024-6387 ; https://github.com/canonical/ubuntu-security-notices |
| 10 | **Tried:** OSV-Scanner 2.7.1 (`osv-scalibr` 0.5.3), offline, with seven records in `osv-scalibr/Ubuntu/all.zip`, against a server with the release-pocket versions: `Scanned /var/lib/dpkg/status file and found 209 packages`, `Total 5 packages affected by 7 known vulnerabilities (2 Critical, 4 High, 1 Medium, 0 Low, 0 Unknown)`, in 0.19 s; after `apt-get install --only-upgrade sudo openssh-server openssh-client openssh-sftp-server` from the local repository, the rescan listed only git, less and rsync. The scanner exits 1 when it finds vulnerabilities. | `captured/osv-vertical.txt`, `captured/osv-table.txt` |
| 11 | **Tried:** OSV-Scanner's own offline database: PyPI 37 MB; Ubuntu 805 MB and still downloading when stopped. Grype's daily v6 database is 201,260,155 bytes (2026-11-12); Grype v0.121.3 and Trivy v0.76.2 are Apache-2.0. | prototype; https://grype.anchore.io/databases/v6/latest.json |
| 12 | NCSC "Vulnerability management" (version 2.1, last reviewed 2026-05-01): update by default, respond to active exploitation, know your assets, triage and prioritise when there's no fix, "own the risk" of not updating at senior level, verify and review, start small. | https://www.ncsc.gov.uk/guidance/vulnerability-management |
| 13 | **Tried:** for CVE-2025-32462 the CNA (MITRE) score in Vulnrichment is 2.8; Ubuntu's record carries vectors for 2.8 and 8.8; OSV-Scanner printed `Severity: '8.8'`. For CVE-2025-48384 the CNA (GitHub) scored 8.1; the scanner printed 8.0 from Ubuntu's vector. | prototype; Vulnrichment JSON |

**Not confirmed:** the clouds' scanners are named only (no claims about their features or prices); NCSC's licence (likely the Open Government Licence v3.0; no licence line was visible to the fetch) is confirmed in a browser before linking.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | "Vulnerability management" (UK NCSC) | https://www.ncsc.gov.uk/guidance/vulnerability-management | reading | Crown copyright; NCSC's site terms (confirm OGL v3.0 in a browser). Linked | 5 (about 550 words) | remediate-and-track, prioritise | 2026-11-12 |
| 1 | "Exploit Prediction Scoring System (EPSS)" (FIRST) | https://www.first.org/epss/ | reading | © FIRST; data "freely and openly accessible". Linked | 6 | cvss-epss-kev | 2026-11-12 |
| 2 | "Known Exploited Vulnerabilities Catalog" (CISA), the page and its column descriptions | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | reading | US government work; data CC0 1.0. Linked | 5 | cvss-epss-kev | 2026-11-12 (the catalog JSON was read; the HTML page itself was not opened by a script: a writer confirms its sections in a browser) |
| 3 | "BOD 26-04: Prioritizing Security Updates Based on Risk" (CISA): "Required Actions" and Table 1 | https://www.cisa.gov/news-events/directives/bod-26-04-prioritizing-security-updates-based-risk | reading | US government work. Linked | 10 | prioritise, patch-slas | 2026-11-12 |
| 4 | CVSS v4.0 Specification Document (FIRST), section 2 "Base Metrics", reference | https://www.first.org/cvss/v4.0/specification-document | reference | © FIRST, free use with attribution. Linked | 10 (optional) | cvss-epss-kev | 2026-11-12 |
| 5 | "Stakeholder-Specific Vulnerability Categorization" (CISA), optional | https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc | reading | US government work. Linked | 4 | prioritise | 2026-11-12 |
| 6 | OSV-Scanner "Offline Mode", reference | https://google.github.io/osv-scanner/usage/offline-mode/ | reference | OSV-Scanner project (Apache-2.0 repository). Linked | 3 | scan-and-read | 2026-11-12 |

No video is assigned.

## 7. Practice ladder

Server labs are systemd labs `FROM lab-base-sec` (`lab: { init: systemd, restart_trial: true }`); the fill-in and the write are plain labs on Module 3's plain `RUN` line. In every server lab `OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY` is set system-wide, so the scan command is the real one: `osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status` (`--format vertical` for reading; the lesson explains each flag).

### 7.1 `example-scan-to-fix` (worked example), skills `scan-and-read`, `cvss-epss-kev`, `prioritise`, `remediate-and-track`

The payments server is internet-facing (its asset file says so: `/srv/inventory/assets.tsv`). Labelled steps:

1. **What's installed.** `dpkg -l sudo openssh-server less rsync git`.
2. **Scan.** The vertical scan (captured: seven findings in five packages). Count: `… | grep -c 'UBUNTU-CVE'`.
3. **Read one finding:** sudo's CVE-2025-32463, the installed and fixed versions, 9.3. Why the fixed version is lower than upstream's 1.9.17p1 (backport).
4. **Look it up.** `grep CVE-2025-32463 /usr/share/lab-sec/epss-2026-11-10.csv` (0.563, percentile 0.99059), `grep CVE-2025-32463 /usr/share/lab-sec/kev-2026.11.10.csv` (in KEV, added 2025-09-29), `grep CVE-2025-32463 /usr/share/lab-sec/ssvc.csv` (active, not automatable, total).
5. **Decide.** Exposed, in KEV, not automatable, total: BOD 26-04 row 3, three days and forensic triage; the clock started at the KEV listing, so it was due on 2025-10-02 (`date -d "2025-09-29 + 3 days" +%F`). Save the list of the scan's KEV entries to `~/example/kev.txt`.
6. **Patch.** `sudo apt-get update`, `sudo apt-get install --only-upgrade sudo` (the only source is the server's own patch repository).
7. **Prove it.** Rescan: sudo's two findings are gone.
8. **Old code.** `nc -w 2 127.0.0.1 22 < /dev/null` prints `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13`; upgrade openssh, and the banner changes only after `sudo systemctl restart ssh`.

Checks: `sudo-fixed` (installed version at or above the record's fix, by `dpkg --compare-versions`); `rescan-clean-for-sudo` (a fresh scan has no sudo finding); `kev-list` (`kev.txt` holds exactly the CVEs of the original scan that are in the snapshot's KEV: CVE-2025-32463 and CVE-2025-48384, computed by the check from the sealed original package list and the data); `ssh-new-code` (the banner shows the installed openssh version). Wrong fixes: `epss-guess.sh` (`kev.txt` lists the CVEs with EPSS above 0.5), `sshd-not-restarted.sh`, `upgraded-nothing.sh` (`apt-get upgrade` before `update`: from a fresh image's empty lists it installs nothing). About 25 minutes; contract about 2 minutes.

### 7.2 Recall on scanning and scores

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `count-findings` | predict_shell | scan-and-read | The captured vertical scan (`captured/osv-vertical.txt`). `grep -o "UBUNTU-CVE-[0-9-]*" scan.txt \| sort -u \| wc -l` and `grep -c 'has the following known vulnerabilities' scan.txt`. Prints `7` and `5`: findings against packages. |
| `mcq-backport` | mcq | scan-and-read | A scanner that reads upstream release notes flags `sudo 1.9.15p5-3ubuntu5.24.04.4` for a flaw "before 1.9.17p1". Right: it's a false positive: Ubuntu backported the fix, and Ubuntu's advisory lists that version as fixed. Distractors: the server is vulnerable until it runs 1.9.17p1; both are right, because the two scanners use different scores; the package is fixed only after a reboot. |
| `mcq-what-a-scanner-does` | mcq | scan-and-read | Right: compares installed versions with a database of advisories. Distractors: sends exploits at the server to see what works; reads the server's logs for attacks; checks configuration against a benchmark (that's OpenSCAP, topic 49). |
| `vector-parts` | predict_shell | cvss-epss-kev | `echo 'CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H' \| tr '/' '\n' \| grep -E '^(AV\|PR\|UI\|S):'`. Prints the four lines. The explanation reads each for sudo's CVE-2025-32463: local, no privileges, no user action, scope changed. |
| `mcq-cvss-is-severity` | mcq | cvss-epss-kev | What does a CVSS base score of 9.8 tell you? Right: how severe the flaw is in general, from its vector. Distractors: the chance it's exploited this month; that it's being exploited now; how severe it is on your server. |
| `mcq-epss-means` | mcq | cvss-epss-kev | CVE-2024-6387's EPSS is 0.995. Right: the model's probability that exploitation activity is seen in the next 30 days is 99.5%. Distractors: 99.5% of servers are vulnerable; its CVSS is 9.95; it is in the top 0.5% by severity. |
| `mcq-kev-beats-epss` | mcq | cvss-epss-kev | git's CVE-2025-48384 is in KEV with EPSS 0.044; OpenSSH's CVE-2024-6387 is not in KEV with 0.995. Which do you treat as proven exploited? Right: git's, since KEV is evidence and EPSS a prediction. Distractors: OpenSSH's, because its probability is higher; neither, until both are in KEV; whichever has the higher CVSS. |
| `mcq-whose-score` | mcq | cvss-epss-kev | The CNA scored CVE-2025-32462 at 2.8; the scanner shows 8.8. Right: the scanner's record carries more than one score and shows the highest; read the vectors to see which fits. Distractors: the scanner is out of date; 8.8 is the environmental score for this server; the CNA's 2.8 is the CVSS 4.0 score. |
| `mcq-kev-criteria` | mcq | cvss-epss-kev | What must be true before CISA adds a CVE to KEV? Right: reliable evidence of exploitation in the wild, a CVE ID and clear remediation guidance. Distractors: a CVSS score of 9.0 or more; an EPSS above 0.9; a working exploit published online. |
| `est-expected-exploited` | estimate | cvss-epss-kev | A backlog has 200 open findings, each with EPSS 0.02. How many would you expect to see exploitation activity within 30 days? Within 10%. **4** (`count * epss`). Mistakes: 0.02, 200. |

### 7.3 `fill-triage` (fill-in, plain lab), skills `cvss-epss-kev`, `prioritise`

`~/bin/triage FINDINGS EPSS KEV` prints `cve package cvss epss kev` for each finding (tab-separated), KEV entries first, then by EPSS from high to low, then by CVSS. The starter has the `awk` join with gaps: the `NR==FNR { epss[$1] = $2; next }` line for the EPSS file (the comment explains the idiom), the KEV lookup, the default when a CVE has no EPSS row (`0`), and the `sort` keys (`-k5,5r -k4,4gr -k3,3gr`). The prompt says which gaps stop `awk` and which give wrong output.

Checks make their inputs at check time: 12 to 30 findings with random CVE IDs, random CVSS and EPSS values (five decimals, the real file's format and header line, including the `#model_version` line the script must skip), and a random KEV subset; at least one tie in EPSS and one KEV entry with a lower EPSS than a non-KEV one, every run. Checks: `kev-first`, `epss-order`, `cvss-breaks-ties`, `missing-epss-is-zero`, `header-skipped`. Wrong fixes: `cvss-only-sort.sh`, `epss-only-sort.sh` (KEV ignored), `string-sort.sh` (`-k4,4r` sorts 0.9 below 0.10…: the check includes 0.0900 and 0.1000), `header-as-data.sh`. About 25 minutes; contract about 1 minute.

### 7.4 Recall on prioritising

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `bod-row` | predict_shell | prioritise | A ten-line `policy.tsv` in the table's shape (`exposed kev automatable impact days`) and `awk -v e=yes -v k=no -v a=yes -v i=total '$1==e && $2==k && $3==a && $4==i {print $5}' policy.tsv`. Prints `3`. |
| `mcq-same-flaw-two-hosts` | mcq | prioritise | CVE-2024-6387 (not KEV, not automatable, total control) on the internet-facing payments server and on an internal batch host. Right: 14 days on the payments server, "fix on system upgrade" on the batch host. Distractors: 14 days on both; 3 days on both, because the EPSS is 0.995; it depends only on CVSS, so both get the same. |
| `mcq-forensic-triage` | mcq | prioritise | Why does BOD 26-04 add forensic triage to some 3-day rows? Right: an exploited flaw giving total control on that asset may already have been used, so you look for signs before and while you patch. Distractors: to collect evidence for CISA's catalog; because patches for those flaws often fail; to measure the patch's performance impact. |
| `mcq-not-running` | mcq | prioritise | rsync's CVE-2024-12084 is in the rsync **daemon**, which isn't running on the server. Right: patch it on schedule and record that it isn't reachable today; a daemon can be started tomorrow. Distractors: close it as not applicable; ignore it until the daemon runs; uninstall rsync, since uninstalling is always the best remediation. |
| `mcq-remediation-means` | mcq | prioritise | Which counts as remediation under BOD 26-04? Right: anything that eliminates the vulnerability: a patch, decommissioning the system, or another action. Distractors: only a vendor patch; a ticket raised with the vendor; a firewall rule that logs attempts. |

### 7.5 `write-sla-due` (write, plain lab), skills `patch-slas`, `prioritise`

Prompt: write `~/bin/sla-due FINDINGS ASSETS POLICY` for the shop's policy (BOD 26-04's Table 1, given as `POLICY`, a 16-line file `exposed kev automatable impact timeline`). `FINDINGS` lines are `cve asset found kev_added automatable impact` (`kev_added` is a date or `-`); `ASSETS` lines are `asset exposed`. For each finding print `cve asset due` where `due` is the date the timeline ends, counted in calendar days from the earlier of `found` and `kev_added`, or `on-upgrade`; append ` triage` when the timeline says "& forensic triage". The prompt names `date -d "DATE + N days" +%F`, `awk`, and that ISO dates compare as text (`[[ "$a" < "$b" ]]`).

Checks make 32 findings at check time over random assets and dates, two for each of the sixteen rows, half with a KEV date earlier than `found`, and compare every line (checks `every-row`, `earlier-start`, `on-upgrade`, `triage-flag`, `exposure-from-assets`). Wrong fixes: `business-days.sh` (skips weekends), `found-only.sh` (ignores the KEV date), `impact-swapped.sh`, `upgrade-as-date.sh` (prints a date for "fix on system upgrade"), `exposed-from-name.sh` (guesses exposure from the asset's name), `no-triage.sh`. About 40 minutes; contract about 2 minutes (32 `date` calls a check).

### 7.6 Recall on SLAs and tracking (two calculation skills)

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `est-kev-due-day` | estimate | patch-slas | CISA adds a CVE to KEV on 9 November; you find it on your internet-facing server on 10 November; it gives total control and isn't automatable. On what day of November is the fix due? Exactly. **12** (`added + 3`). Mistakes: 13 (from the day you found it), 23 (the old two-week rule). |
| `est-overdue-days` | estimate | patch-slas | sudo's CVE-2025-32463 entered KEV on 29 September 2025 (3-day timeline on this server). You first scan the server on 9 November 2026. How many days overdue is it that morning? Within 1. **403** (Oct 2 2025 to Nov 9 2026: 365 + 38). Mistakes: 0 ("the clock starts when we find it"), 406 (counted from the KEV date, not the due date). |
| `est-pci-late` | estimate | patch-slas | A critical patch was released on 5 October; PCI DSS 6.3.3 gives one month. It was installed on 20 November. How many days late? Within 1. **15** (Nov 5 to Nov 20). Mistakes: 46 (days since release), 0. |
| `est-quarterly-scans` | estimate | patch-slas | PCI DSS 11.3.1 asks for internal scans at least once every three months, and a rescan after each failed one. Last year three of the quarterly scans failed once each. How many internal scans at least? Exactly. **7** (`4 + failed`). Mistakes: 4, 12 (monthly). |
| `est-mttr` | estimate | remediate-and-track | Five findings were fixed 2, 5, 9, 1 and 13 days after they were found. Mean time to remediate, in days? Exactly. **6**. Mistakes: 30 (the total), 5 (the median). |
| `est-sla-compliance` | estimate | remediate-and-track | Last quarter 40 findings were fixed, 34 of them within their SLA. SLA compliance, in percent? Exactly. **85**. Mistakes: 15, 117.6 (`40 / 34`). |
| `est-backlog-weeks` | estimate | remediate-and-track | 120 findings are open; 35 new ones arrive and 40 are fixed each week. How many weeks until the backlog is empty? Exactly. **24** (`open / (fixed - new)`). Mistakes: 3 (`open / fixed`), 1.6 (`open / (fixed + new)`). |
| `est-exception-expiry` | estimate | remediate-and-track | An exception approved on 1 March may last at most 90 days. Counting 1 March as day 0, what day of the year (January 1 = 1, a non-leap year) is its last day? Exactly. **150** (`60 + 90`). Mistakes: 90, 149. |
| `mcq-banner-old` | mcq | remediate-and-track | The package is upgraded and the scan is clean, but an outside check still sees `OpenSSH_9.6p1 Ubuntu-3ubuntu13`. Right: the SSH server hasn't been restarted, so the old code is still running. Distractors: the scanner's database is stale; the outside check caches banners; the package's version string isn't updated until a reboot. |
| `mcq-held` | mcq | remediate-and-track | `apt-get install --only-upgrade rsync` says `rsync is already the newest version` though `/srv/patches` has a newer one. Right (one of two causes the debug uses): the repository's index doesn't list it, so apt can't see it (`apt-cache policy rsync` shows the candidate). Distractors: rsync can only be upgraded with `dist-upgrade`; the new version is waiting for a reboot; apt only upgrades packages with a CVE. |
| `mcq-exception-shape` | mcq | remediate-and-track | A fix can't be applied within its 14 days. Right: a written exception with an owner, the reason, a compensating control and an expiry date. Distractors: mark it fixed and recheck next quarter; remove it from the scanner's database; extend the SLA for every finding of that severity. |
| `mcq-immutable-fix` | mcq | remediate-and-track | The servers are built from an image and replaced, never changed. Right: build a new image with the fixed package, then replace the servers. Distractors: `apt-get upgrade` on each server; patch the running servers and the image next quarter; leave it, since immutable servers can't be attacked. |

### 7.7 Ladder order for `topic.yaml`

`example-scan-to-fix`, `count-findings`, `mcq-backport`, `mcq-what-a-scanner-does`, `vector-parts`, `mcq-cvss-is-severity`, `mcq-epss-means`, `mcq-kev-beats-epss`, `mcq-kev-criteria`, `fill-triage`, `bod-row`, `mcq-same-flaw-two-hosts`, `mcq-forensic-triage`, `mcq-not-running`, `est-kev-due-day`, `est-overdue-days`, `est-pci-late`, `write-sla-due`, `est-mttr`, `est-sla-compliance`, `est-backlog-weeks`, `mcq-banner-old`, `mcq-held`. That is 21 quick items (about 32 minutes), a worked example, a fill-in and a write. Review-only: `mcq-whose-score`, `est-expected-exploited`, `mcq-remediation-means`, `est-quarterly-scans`, `est-exception-expiry`, `mcq-exception-shape`, `mcq-immutable-fix`.

**Practised before proven:**

| Skill | Practised in |
| --- | --- |
| scan-and-read | the example (steps 2 and 3), three items |
| cvss-epss-kev | the example (step 4), six items, the fill-in |
| prioritise | the example (step 5), the fill-in, four items, the write |
| patch-slas | the example's due date, three estimates, the write |
| remediate-and-track | the example (steps 6 to 8), three estimates, two items. The build's register is a new artefact: **writer's choice**, add a short labelled step to the example that writes two register lines (recommended, 5 minutes). |

## 8. Proofs

### 8.1 Build: `build-weekly-vuln-run` (systemd lab on `lab-base-sec`, 60 minutes), skills: all five

**Story.** This week's run for two machines: the internet-facing payments server, which is this lab, and the internal batch host `batch-01`, owned by the data team, whose package list arrives as a file (`/srv/inventory/batch-01/dpkg-status`, a captured copy: the scanner reads it with `-L`). `/srv/inventory/assets.tsv` gives each machine's exposure; `/srv/vuln/first-seen.tsv` the date each finding was first reported (2026-11-09 for the payments server, 2026-11-02 for batch-01); the policy is BOD 26-04's table (`/srv/vuln/policy.tsv`). The prompt asks:

1. Scan both machines and keep the register `~/vuln/register.tsv`: one line per finding, `cve asset package due status owner`, where `due` is a date or `on-upgrade` (plus ` triage` where the policy says so), `status` is `fixed` or `open`, and `owner` is `payments` or `data-team`.
2. On the payments server, fix every finding whose timeline is 14 days or shorter, from the server's patch repository, and make sure nothing still runs the old code. batch-01 isn't yours: its findings stay open, with their owner.
3. Keep the payments server's packages installed (deploys use git; staff use less) and its SSH settings and keys as they are.
4. Save this week's rescan of the payments server as `~/vuln/rescan.txt` (the vertical format).

Under the policy (facts 4 to 6) the payments server's seven findings are all 3 or 14 days except CVE-2025-32462 (60 days, fixed anyway by sudo's patch); several are overdue from their KEV dates. batch-01's (a different version set; the writer picks it so that its rows include 14 days, 60 days and `on-upgrade`) stay open.

**Checks:**

| Id | End state | Catches |
| --- | --- | --- |
| `register-complete` | the register has exactly one line per finding of the **original** scans of both machines (the check scans the sealed copy of the payments server's original package list and batch-01's file itself) | missing or invented findings |
| `due-dates-right` | each line's `due` (and `triage`) is what the policy gives, computed by the check (its own table lookup, earlier-of start date) | wrong rows, business days, `found`-only starts |
| `status-and-owner` | payments lines whose package is now fixed say `fixed`; batch-01's say `open` with `data-team` | statuses not tracked |
| `due-findings-fixed` | a fresh scan of the payments server shows no finding whose timeline is 14 days or less | CVSS-only or EPSS-only patching |
| `no-old-code` | the SSH banner shows the installed openssh version, and every process's executable is the installed one (no `(deleted)` in `/proc/*/exe` for ssh, sudo or rsync) | daemons not restarted |
| `nothing-removed` | sudo, openssh-server, less, rsync and git are installed and run (`sudo -V`, `ssh -V`, `git --version`) | uninstalling to clear findings |
| `ssh-unchanged` | `sshd -T` output and the host keys' fingerprints equal the image's | "fixing" SSH by replacing its config |
| `scanner-untouched` | the scanner, the advisory zip and the data files match their checksums | trimming the database |
| `rescan-saved` | `rescan.txt` lists exactly the findings a fresh scan lists now | an old or hand-written file |

**Wrong fixes:** `cvss-only.sh` (patches findings of CVSS 9 or more: sudo and rsync), `epss-only.sh` (patches EPSS 0.5 or more: openssh, rsync, sudo; misses git's KEV entry), `removed-git.sh`, `ssh-not-restarted.sh`, `trimmed-db.sh` (deletes records from the zip), `business-days.sh` (register only), `found-date-only.sh` (register only), `batch-marked-fixed.sh`, `old-rescan.sh` (saves the first scan as the rescan). Nine.

**CI time.** Boot 2 s; the solution about 15 s (two scans, an upgrade of five packages in about 3 s); the checks about 10 s. Eleven containers plus the restart trial: **about 5 minutes**.

**Restart trial:** tried for the mechanism (upgraded packages and `/etc` persist; the scan after a restart is the same). The banner check after a restart reads the new sshd that boot started, which is right.

### 8.2 Debug: `debug-patched-but-flagged` (systemd lab on `lab-base-sec`, 45 minutes), skills `remediate-and-track`, `scan-and-read`

**Prompt.** Monday's patch run on the payments server printed success, and the change ticket says sudo, openssh, rsync and git were all upgraded from the patch repository. This morning:

- the scan still flags rsync and git;
- the security team's outside check still sees the old OpenSSH version on port 22, though the scan says openssh is fixed.

There are three faults. Rules: patch only from the server's patch repository; keep every package installed; keep SSH's settings and host keys; don't change the scanner, its database or its data; the fix must last a reboot.

**The faults** (story at build):

1. `apt-mark hold rsync` ("held during an incident last month"). Evidence: `apt-get install --only-upgrade rsync` says it's held; `apt-mark showhold`.
2. The repository's index is stale: the newer git `.deb` is in `/srv/patches` but `Packages` was generated before it was added. Evidence: `apt-cache policy git` shows no newer candidate; `ls /srv/patches` shows the file.
3. A drop-in `/etc/systemd/system/ssh.service.d/50-keep.conf` runs a copy of the old `sshd` binary kept in `/usr/local/lib/ssh-old/` ("kept so a patch can't break logins"). Evidence: `systemctl cat ssh`, the banner, `ls -l /proc/$(pgrep -o sshd)/exe`.

**Checks:** `rsync-fixed`, `git-fixed` (installed at or above the fix; a fresh scan clean for each), `repo-index-current` (every `.deb` in `/srv/patches` is in `Packages`), `no-holds-left` (`apt-mark showhold` empty), `ssh-runs-installed-code` (banner, `/proc/PID/exe` is `/usr/sbin/sshd`, and no unit drop-in names another binary), `ssh-unchanged` and `nothing-removed` and `scanner-untouched` (as in the build), `ssh-reachable` (an SSH key login as `learner` works: the fix didn't lock anyone out).

**Wrong fixes:** `dpkg-force.sh` (installs git with `dpkg -i --force-all` and leaves the index stale), `hold-kept.sh`, `old-sshd-kept.sh`, `ssh-disabled.sh` (stops SSH to make the banner go away), `rsync-removed.sh`, `db-edited.sh`, and one "two of three" variant per fault. **Not prototyped as a lab:** the hold, the stale index and the drop-in are standard apt and systemd behaviour; the banner and `/proc/*/exe` checks were not run. Prove the contract first.

**CI time.** About 12 containers at about 25 s: **about 5 minutes**.

### 8.3 Explain

**Prompt.** "A manager reads this week's scan: 1,400 findings, 90 of them 'critical'. She asks why the team fixed a 'high' on the web servers before most of the criticals, and how you'll show the auditors you patch in time. Explain, in your own words: what a scanner does and why a distribution's own advisories matter; what CVSS, EPSS and the KEV catalog each tell you and what you do when they disagree; how the asset's exposure and the kind of access an attacker would get change the order; how you set and count due dates, and what you do when a fix can't make its date; and how you prove a finding is fixed and report progress."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `scanner` | yes | compares installed versions with an advisory database; reads the distro's own advisories because of backports; only as good as its data |
| `three-signals` | yes | CVSS is severity in general (read the vector), EPSS a 30-day likelihood, KEV evidence of exploitation; KEV first, then likelihood, with severity as a tie-breaker, never CVSS alone |
| `context` | yes | internet exposure, automatability and total against partial control change the timeline (a policy such as BOD 26-04); forensic triage where an exploited flaw may already have been used |
| `slas` | yes | calendar days from the earlier of KEV listing and discovery (PCI DSS: critical and high within a month); exceptions written with owner, reason, compensating control and expiry |
| `prove-and-track` | yes | patch, restart what runs old code (or rebuild the image), rescan; a register; MTTR, SLA compliance and backlog trend |
| `example` | no | an example with real numbers, e.g. git's KEV entry with an EPSS of 0.04 beating OpenSSH's 0.995 |

## 9. Review pool

- scan-and-read: `count-findings`, `mcq-backport`, `mcq-what-a-scanner-does`.
- cvss-epss-kev: `vector-parts`, `mcq-kev-beats-epss`, `mcq-whose-score` (review-only), `est-expected-exploited` (review-only).
- prioritise: `bod-row`, `mcq-same-flaw-two-hosts`, `mcq-remediation-means` (review-only), `write-sla-due`.
- patch-slas: `est-kev-due-day`, `est-overdue-days`, `est-pci-late`, `est-quarterly-scans` (review-only).
- remediate-and-track: `est-mttr`, `est-backlog-weeks`, `est-exception-expiry` (review-only), `mcq-banner-old`, `mcq-immutable-fix` (review-only).

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| V1 | **`lab-base-sec`** with its vulnerability parts (lab-base-sec.md, sections 2 to 4): the release-pocket pins, the patch repository, OSV-Scanner pinned, the seven records, the EPSS, KEV and SSVC extracts with `SOURCES.md`, the sealed copy of the original package list (`/usr/share/lab-sec/original-dpkg-status`, made at build), `scan-tsv`. | as designed |
| V2 | **The first lab-image downloads from GitHub that aren't a package** (OSV-Scanner's binary, and topic 49's data stream): the same rule as Module 3's step-ca, pinned by version and checksum; recorded in the devlog. | none |
| V3 | Nothing in the app. | |

## 11. Cost and time

- **Money:** none. A real-cloud extra (Amazon Inspector or Defender for Cloud on a VM) is not proposed: neither was priced this session, and Module 20 (`csa.secarch.posture`, `csa.secarch.cnapp`) owns them.
- **Learner minutes:** lesson 17, reading 26 (NCSC 5, EPSS 6, KEV 5, BOD 10), 21 quick items 32, worked example 25, fill-in 25, write 40, build 60, debug 45, explain 20: **290**. With the optional readings, 307.
- **Labs and CI:** five labs; contract minutes: example about 2, fill-in about 1, write about 2, build about 5, debug about 5: **about 15 minutes**.

## 12. Open questions, each with a recommendation

1. **OSV-Scanner rather than Trivy or Grype.** The brief named Trivy or Grype. **Recommendation:** OSV-Scanner, for the frozen, licensed, 10 KB database (lab-base-sec.md, section 2); the lesson names the others and shows Grype's EPSS and KEV columns in words.
2. **A curated database of seven real records.** A learner sees seven findings, not hundreds. **Recommendation:** keep seven (plus batch-01's) and say so; volume is taught with numbers (the explain's 1,400 findings, the estimates), judgement with the seven.
3. **BOD 26-04 as the shop's policy.** It binds only US federal agencies. **Recommendation:** use it, labelled "the shop adopts CISA's table", because it is free, current, precise and machine-checkable; PCI DSS's month is taught beside it.
4. **Overdue on day one.** The KEV dates make several findings overdue the day they're found. **Recommendation:** keep it: "found late is already overdue" is the lesson, and `est-overdue-days` asks it.
5. **App lockfiles.** OSV-Scanner reads `requirements.txt` and other lockfiles offline (tried with two GHSA records: CC BY 4.0), but the learner meets Python packaging only in Module 6. **Recommendation:** one sentence in the lesson and no lab; `csa.se.dependencies` (Module 7) runs the dependency loop.

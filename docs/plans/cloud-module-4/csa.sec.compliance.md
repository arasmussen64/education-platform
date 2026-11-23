# Writing brief: `csa.sec.compliance` (topic 49), Compliance basics

Design only; nothing here is in the repository. Sources were read on 2026-11-12 and each fact carries its URL. Lab mechanics marked **tried** ran on 2026-11-12 in Docker Desktop 29.8.2 on the owner's PC, in privileged systemd containers on `ubuntu:24.04` with OpenSCAP 1.3.9 and ComplianceAsCode 0.1.82's Ubuntu 24.04 data stream; everything started was removed afterwards. Prototype files: `prototypes/audit-vuln-compliance/comp-probe/Dockerfile`, `comp/refs.py` (the rule-to-control table), `captured/oscap-four-rules.txt` and `captured/refs-cis-l1-server.tsv` (the table, 4,159 rows). The labs run on the shared base in [lab-base-sec.md](lab-base-sec.md).

## 1. What the learner will be able to do

1. Say what each of the common frameworks is, who it applies to, who checks it and whether its text is free: SOC 2 (an attestation by a CPA against the AICPA's criteria), ISO/IEC 27001:2022 (a certifiable management system with 93 Annex A controls; sold), PCI DSS v4.0.1 (anyone handling card data; free to read under a licence), the HIPAA Security Rule (US law for health data), FedRAMP (US federal cloud; built on SP 800-53), CMMC (US defence contractors; Level 2 is SP 800-171), GDPR (EU law for personal data), CIS Benchmarks (configuration baselines) and the two free NIST documents everything maps to, the **CSF 2.0** (six functions of outcomes) and **SP 800-53 Rev. 5** (the control catalogue).
2. **Read a control**: its identifier, statement, parameters the organisation fills in ("organization-defined"), enhancements, and the discussion; tell a requirement from guidance; turn a parameter into a configuration value (30 minutes into 1800 seconds).
3. **Map a control to technical evidence**: find the automated checks that test it (OpenSCAP rules, through their published references), the configuration reading or the other tool's report where no rule exists, and save evidence that an auditor can re-run: current, complete, from the system itself, dated.
4. Use **crosswalks**: one technical setting satisfies several frameworks at once (SSH root login is CIS 5.1.20, PCI DSS 2.2.6 and NIST AC-6(2)); a mapping can be stale (the data stream maps to 800-53 **rev 4** and ISO 27001 **2013**); compliant isn't the same as secure.
5. Handle **gaps and exceptions**: a control nothing tests automatically, a rule that fails for a good reason (written exception with compensating control and expiry), a benchmark stricter or looser than the framework, evidence that went stale.

**The six-month core:**

- Frameworks say *what* must be true; evidence shows it *is* true, today, on the real system. A screenshot from March isn't evidence in November.
- NIST's CSF 2.0 has six functions (Govern, Identify, Protect, Detect, Respond, Recover) and SP 800-53 is the catalogue the others map to; both are free and public domain. ISO 27001 is bought; PCI DSS is free under a licence; CIS Benchmarks are free for non-commercial use.
- A control usually needs several checks, and a check usually serves several controls. Mappings carry the version they were written for.
- Some controls have no scanner rule (retention, patch timeliness): their evidence is a configuration reading or another tool's report, named in the evidence map.
- An exception is a decision: the reason, a compensating control, an owner and an end date. A benchmark rule silently removed is a gap nobody owns.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.sec.audit, csa.sec.vulnerabilities]`. The build uses topic 46's audit trail (retention, sealing) and topic 48's scan and patch loop as evidence; both reach topic 40 (`csa.sec.authn-authz`), whose words (authentication, least privilege, separation of duties, MFA) the control texts use. The lesson defines the frameworks; it doesn't assume the learner has met any (the owner's Azure work is not a reason to skip SOC 2 or ISO).

**Builds on (for the writer):**

| Topic | What this topic uses |
| --- | --- |
| `csa.linux.hardening` | what a CIS Benchmark is (Level 1 and 2), that OpenSCAP scans against a profile and prints `Title`/`Rule`/`Result` blocks (its `hard-oscap-failures` item reads exactly that format), before-and-after scans, exceptions with a compensating control (`mcq-prove-with-scan`), and SSH drop-ins where **the first value read wins**. This topic runs OpenSCAP for real for the first time. |
| `csa.sec.audit` | `MaxRetentionSec=`, `Storage=`, sealing, `journalctl --namespace=audit`, PCI DSS 10.5.1. |
| `csa.sec.vulnerabilities` | the offline scan, patching from the patch repository, PCI DSS 6.3.3, BOD 26-04's table. |
| `csa.linux.shell` | `awk -F'\t'` with `-v`, `grep`, `sort -u`; reading a tab-separated table. |

**Terms this topic must define itself:** framework, standard, regulation, control, control objective, requirement, guidance, parameter (organization-defined), enhancement, baseline (as in "FedRAMP Moderate baseline"), profile (OpenSCAP), rule, benchmark, scope (in scope, the cardholder data environment in one sentence), evidence, sample (an auditor tests some, not all), attestation and certification, auditor, assessor (QSA in one sentence), self-assessment, crosswalk (mapping), gap, exception (risk acceptance), compensating control, inherited control (one sentence; Module 8's `csa.cloud.models` owns shared responsibility and Module 20's `csa.secarch.compliance` the inherited-control story), continuous compliance (one sentence). OSCAL (one sentence: NIST's machine-readable format for catalogues and assessments), XCCDF and OVAL (one sentence each: the benchmark's rules and the tests behind them).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `framework-landscape` | The ten frameworks: what, for whom, who checks, how often, free or not; laws (HIPAA, GDPR) against standards and contracts (PCI DSS) against voluntary frameworks (CSF); which ones are built on which (FedRAMP on 800-53, CMMC Level 2 on 800-171). |
| `read-a-control` | The anatomy of an 800-53 control (AC-7, AU-11, IA-5(1), SI-2), PCI DSS's numbered requirements as identifiers, CSF identifiers (`PR.AA-01`); parameters; turning a requirement into a value. **A calculation skill: three estimate items.** |
| `control-to-evidence` | Finding the checks for a control (`refs.tsv`, from the benchmark's own references); running OpenSCAP for named rules; evidence kinds (a scanner rule, a configuration reading, another tool's report, a document); what makes evidence good (current, complete, reproducible, from the system, dated). |
| `crosswalks` | One setting, many controls (the references); one control, many settings; NIST's informative references between CSF and 800-53; stale mappings (800-53 rev 4 against rev 5, ISO 2013 against 2022); compliant against secure. |
| `gaps-and-exceptions` | No automated evidence; a failing rule that is right to fail here; benchmark parameters against framework parameters (CIS asks 14 characters, PCI DSS 12); written exceptions; stale evidence; coverage arithmetic. |

## 4. Lesson plan

About 2,300 words (18 minutes), around NIST's CSF 2.0 page and SP 800-53's control text.

1. **Why compliance exists (lesson only).** A customer, a regulator or a card network can't inspect your servers, so they ask you to follow a published set of controls and to prove it to an independent checker. The picture: a building inspection. The building code (the framework) says "fire exits must be marked"; the inspector (the auditor) walks a sample of floors (sample testing) and looks at signs (evidence); the certificate (attestation or certification) says "on this date, it was so". The architect's job is to make the evidence come from the building itself, not from photographs.
2. **The landscape, one table (lesson only; facts 1 to 12).** For each: what it is, who it binds, who checks, free or not. **SOC 2**: a CPA's report on a service organisation's controls against the AICPA's Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy); Type 1 (designed, at a date) and Type 2 (operating, over a period) named, with the source to confirm. **ISO/IEC 27001:2022**: a management system (the organisation runs a risk process) certified by an accredited body; Annex A lists 93 controls in four themes; the text is sold. **PCI DSS v4.0.1**: a contract obligation through the card brands for anyone storing, processing or sending card data; checked by a QSA or a self-assessment; free to read under the PCI SSC's licence. **HIPAA Security Rule**: US law (45 CFR Part 164, Subpart C) for electronic health information, e.g. §164.312(b) "Audit controls". **FedRAMP**: authorisation for clouds that sell to US federal agencies, built on SP 800-53 baselines, in transition in 2026. **CMMC**: required in US defence contracts; Phase 1 since 10 November 2025, Phase 2 (third-party assessed Level 2) from 10 November 2026. **GDPR**: EU law for personal data: Article 32 (security "appropriate to the risk"), Article 33 (tell the supervisory authority of a breach "not later than 72 hours" after becoming aware), Article 5(1)(e) (storage limitation). **CIS Benchmarks**: consensus configuration baselines per product (Module 1). **NIST CSF 2.0** (26 February 2024): outcomes in six functions, Govern, Identify, Protect, Detect, Respond, Recover, for "all organizations". **SP 800-53 Rev. 5** (release 5.2.0, 27 August 2025): the catalogue of controls in 20 families. The lesson's sorting rule: laws you must obey where they apply, contracts you sign up to, certifications you choose to earn, and catalogues everyone maps to.
3. **Reading a control (SP 800-53's AC-7, AU-11, IA-5(1), SI-2 from the OSCAL catalogue; PCI DSS numbers).** AC-7, "Unsuccessful Logon Attempts": "Enforce a limit of [Assignment: organization-defined number] consecutive invalid logon attempts by a user during a [Assignment: organization-defined time period]" (the writer quotes it from the lab's copy, which is NIST's text). The brackets are **parameters**: the framework leaves the number to you, and your policy fills it in; PCI DSS 8.3.4 fills it ("not more than 10 attempts", lockout "a minimum of 30 minutes"). A requirement is what must be true; the discussion is guidance. Turning it into a setting is arithmetic in the setting's units (`unlock_time = 1800` seconds). CSF identifiers read as function, category, subcategory (`PR.AA-01`).
4. **From control to evidence (lesson only, with the lab's own outputs).** Three kinds of evidence, in order of preference: an **automated check** that tests the system now (an OpenSCAP rule: `Rule xccdf_org.ssgproject.content_rule_sshd_disable_root_login` / `Result pass`); a **reading of the configuration** where no rule exists (`systemd-analyze cat-config systemd/journald@audit.conf` for AU-11 and PCI DSS 10.5.1, which no rule in the CIS profile tests, tried); **another tool's report** (topic 48's rescan for SI-2 and PCI DSS 6.3.3). Documents (a policy, a procedure) are evidence too, for the controls about people. Good evidence is current, complete for the scope, reproducible by the auditor and dated. Show the trap Module 1 taught: a passing rule last month can fail today because an earlier SSH drop-in says `PermitRootLogin yes` (tried: OpenSCAP's rule fails then, as `sshd -T` would).
5. **Where the mappings come from (the lab's table).** ComplianceAsCode writes, beside every rule, which controls in which frameworks it supports (tried: `sshd_disable_root_login` lists CIS Ubuntu 24.04 5.1.20, PCI DSS 4.0 2.2.6, NIST 800-53 AC-6(2), HIPAA 164.312(e)(1) and more). The lab's `refs.tsv` is that, as a table. Two cautions the lesson must supply: the mapping is to **800-53 rev 4** and **ISO 27001:2013**, not the current versions (ISO renumbered Annex A in 2022); and a mapping says a rule *supports* a control, not that the control is met: AC-7 needs both the deny count (AC-7(a)) and the unlock time (AC-7(b)), two rules. NIST publishes its own informative references between CSF 2.0 and SP 800-53 (the CSF 2.0 Tool), the "official" crosswalk for those two.
6. **Gaps and exceptions (lesson only; retrieval of Module 1).** A rule that can't pass here (`partition_for_tmp` on a server whose disk layout is fixed by its platform) becomes a written exception: control, rule, reason, compensating control, owner, expiry. A benchmark parameter that differs from the framework's: CIS asks for passwords of 14 characters, PCI DSS for 12: meet the stricter one or record which you follow. Coverage: how many controls in scope have evidence, of which kind.
7. **Compliant is not secure (lesson only).** A control set is a floor written for the average case; the threat model (topic 39) decides what this system needs beyond it. And the clouds: they hold certifications for their own controls, which you **inherit** for the parts they run; you still evidence your own. Module 20 (`csa.secarch.compliance`) builds that, with the clouds' evidence tools.

**Read now:** NIST's CSF page and the CSF 2.0 news release (the functions), the four SP 800-53 controls in the lab's copy (or the CSRC control browser), and the Module 1 OpenSCAP recall item as a reminder. Optional: the CSF 2.0 document itself (CSWP 29, 32 pages; the "CSF Core" section), the PCI SSC document library (to see PCI DSS v4.0.1 and its licence), CIS's benchmark page.

## 5. Verified facts

All read on 2026-11-12.

| # | Claim | Source |
| --- | --- | --- |
| 1 | NIST CSF 2.0 (NIST CSWP 29) released 2024-02-26; six functions Govern, Identify, Protect, Detect, Respond, Recover (Govern new); aimed at "all organizations"; 32 pages (the PDF's page count). | https://www.nist.gov/news-events/news/2024/02/nist-releases-version-20-landmark-cybersecurity-framework ; https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final |
| 2 | NIST SP 800-53 Rev. 5, release 5.2.0 of 2025-08-27 (adds controls such as SA-24); 20 families; OSCAL versions on GitHub. usnistgov/oscal-content is public domain in the US and CC0 worldwide. | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final ; https://raw.githubusercontent.com/usnistgov/oscal-content/main/LICENSE.md |
| 3 | ISO/IEC 27001:2022: Annex A has 93 controls in four themes (organizational 37, people 8, physical 14, technological 34); 2013 certificates had to move to 2022 by 2025-10-31; a 2024 amendment added climate considerations. **Secondary sources** (iso.org returned 403 to the fetch; the price was not found). | e.g. https://www.dqsglobal.com/en-us/explore/blog/new-iso-27001-2022-key-changes ; https://www.isms.online/information-security/everything-you-need-to-know-about-the-iso-27001-2022-standard-update/ |
| 4 | AICPA Trust Services Criteria (2017, revised points of focus 2022): five categories, Security, Availability, Processing Integrity, Confidentiality, Privacy; a free 554 KB PDF (an account is encouraged); SOC 2 engagements are performed by CPAs. Type 1 against Type 2 **was not confirmed** on the AICPA's pages. | https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022 ; https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2 |
| 5 | PCI DSS v4.0.1 is the PCI SSC library's current document; whether a licence agreement is required before download **was not confirmed** (the page needs a browser). Requirement texts used here are as Microsoft quotes them: 2.2.6 (system security parameters configured to prevent misuse, by its use in the data stream), 6.3.3, 8.3.4 ("Locking out the user ID after not more than 10 attempts", "lockout duration to a minimum of 30 minutes"), 8.3.6 ("A minimum length of 12 characters", "both numeric and alphabetic characters"), 10.5.1, 11.3.1. | https://www.pcisecuritystandards.org/document_library/ ; https://learn.microsoft.com/en-us/entra/standards/pci-requirement-8 (and -6, -10, -11) |
| 6 | HIPAA 45 CFR 164.312(b) "Standard: Audit controls. Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use electronic protected health information."; (c)(1) "Standard: Integrity." | https://www.law.cornell.edu/cfr/text/45/164.312 |
| 7 | GDPR: Art. 33(1) notification "without undue delay and, where feasible, not later than 72 hours after having become aware of it"; Art. 32(1) measures "to ensure a level of security appropriate to the risk"; Art. 5(1)(e) storage limitation. | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679 |
| 8 | CMMC: the DFARS rule (48 CFR parts 204, 212, 217, 252) took effect 2025-11-10, starting Phase 1 (self-assessed Level 1 and 2 in selected solicitations); Phase 2 from 2026-11-10 (third-party assessed Level 2); Phases 3 and 4 from 2027-11-10 and 2028-11-10. **Secondary sources** (DoD's CMMC page returned 403). Level 2 being SP 800-171 Rev 2's 110 requirements is from 32 CFR 170 as commonly cited, **not read this session**. | https://www.taftlaw.com/news-events/law-bulletins/are-you-cmmc-ready-dfars-phase-i-enforcement-begins-november-10-2025/ ; https://www.akingump.com/en/insights/alerts/the-cmmc-rule-is-here-what-contractors-need-to-know |
| 9 | FedRAMP: new Vulnerability Detection and Response rules mandatory from 2026-12-07; impact levels renamed to certification classes (B formerly Low, C Moderate, D High, plus A). **Secondary sources.** | https://www.dwt.com/blogs/privacy--security-law-blog/2026/07/fedramp-2026-consolidated-rules |
| 10 | CIS Benchmark PDFs are "distributed free of charge in PDF format for non-commercial use" after a registration form; the licence (often cited as CC BY-NC-SA 4.0) **was not shown** on either page; CIS's footer is "Copyright © 2026 Center for Internet Security". | https://learn.cisecurity.org/benchmarks ; https://www.cisecurity.org/cis-benchmarks |
| 11 | ComplianceAsCode (scap-security-guide) v0.1.82 (2026-09-01) ships `ssg-ubuntu2404-ds.xml` with profiles CIS Level 1 and 2 Server and Workstation and the Ubuntu 24.04 STIG V1R5; BSD-3-Clause. Ubuntu 24.04's own `ssg-debderived` is 0.1.71 with content up to Ubuntu 22.04 only. OpenSCAP is LGPL-2.1. | https://github.com/ComplianceAsCode/content/releases/tag/v0.1.82 ; repository `LICENSE`; `dpkg -c ssg-debderived_0.1.71-1_all.deb` (prototype); https://github.com/OpenSCAP/openscap |
| 12 | **Tried:** on a privileged systemd container, the CIS Level 1 Server profile (408 rules) took 2 to 5 s: with `linux-base` installed 222 pass, 110 fail, 76 notapplicable; without it 133 pass, 20 fail, 255 notapplicable (the content's "system with kernel" platform is a `dpkginfo` test for `linux-base`, and SSH, PAM and journald rules depend on it). A run of three named rules took 2.0 s. One full run of five segfaulted. | prototype |
| 13 | **Tried:** `sshd_disable_root_login` failed, then passed after `PermitRootLogin no` in `/etc/ssh/sshd_config.d/60-hardening.conf`, then failed again once `10-vendor.conf` said `PermitRootLogin yes` (the first value read wins); `accounts_password_pam_minlen` passed after `minlen = 14` in `/etc/security/pwquality.conf`; `journald_storage` passed after a `journald.conf.d` drop-in with `Storage=persistent`. | `captured/oscap-four-rules.txt`; prototype |
| 14 | **Tried:** the CIS Level 1 Server profile's references, as `refs.tsv`: 4,159 rows (ISO 27001:2013 2,607, NIST 800-53 **rev 4** 607, CIS Ubuntu 24.04 415, PCI DSS 4.0 292, HIPAA 164, NIST 800-171 74). AC-6(2): one rule (`sshd_disable_root_login`); PCI DSS 8.3.6: three (`accounts_password_pam_minlen`, `_dcredit`, `_lcredit`); PCI DSS 8.3.4: `accounts_passwords_pam_faillock_deny` and `_unlock_time`; AC-7(a) and AC-7(b) one each; PCI DSS 10.6.1: two; **PCI DSS 10.5.1, 10.3.3 and NIST AU-9, AU-11, SI-2: none**. CIS 6.1.2.4 is `journald_storage`; CIS 2.1.5 `package_dnsmasq_removed`. | `captured/refs-cis-l1-server.tsv` |
| 15 | `faillock.conf(5)` on Ubuntu 24.04: `deny=n`, `fail_interval=n` and `unlock_time=n`, in seconds; `fail_interval` defaults to 900 (15 minutes). | https://manpages.ubuntu.com/manpages/noble/man5/faillock.conf.5.html |

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | "Cybersecurity Framework" (NIST), with the CSF 2.0 release note | https://www.nist.gov/cyberframework | reading | US government work, not subject to US copyright (NIST's copyright page; the writer confirms the wording). Linked | 8 | framework-landscape, crosswalks | 2026-11-12 |
| 1 | NIST SP 800-53 Rev. 5 control browser (CPRT): AC-7, AU-11, IA-5(1), SI-2 | https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home | reference | US government work; OSCAL source CC0. Linked (the lab copies the text into its image) | 10 | read-a-control | 2026-11-12 (the catalogue page itself renders in the browser; its OSCAL source was read) |
| 2 | "The NIST Cybersecurity Framework (CSF) 2.0", CSWP 29: the "CSF Core" section, optional | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf | reading | US government work. Linked | 12 (optional) | framework-landscape | 2026-11-12 (PDF opened; its text wasn't extractable by the tools here: a writer reads the section in a browser and times it) |
| 3 | PCI SSC Document Library, optional | https://www.pcisecuritystandards.org/document_library/ | reference | © PCI SSC; download terms to confirm in a browser. Linked only | 3 | framework-landscape | 2026-11-12 |
| 4 | "CIS Benchmarks" (CIS), optional | https://www.cisecurity.org/cis-benchmarks | reading | © CIS. Linked | 3 | framework-landscape | 2026-11-12 |
| 5 | "Microsoft Entra ID and PCI-DSS Requirement 8" (Microsoft Learn): reads PCI DSS's numbered requirements beside one platform's evidence, optional | https://learn.microsoft.com/en-us/entra/standards/pci-requirement-8 | reading | CC BY 4.0. Linked | 8 | read-a-control, control-to-evidence | 2026-11-12 |

The lesson must carry the landscape table itself: no single free resource covers all ten frameworks well for a beginner (none was found this session; the writer searches once more).

## 7. Practice ladder

Server labs are systemd labs `FROM lab-base-sec` (`lab: { init: systemd, restart_trial: true }`). The lab's files: `/usr/share/lab-sec/scap/ssg-ubuntu2404-ds.xml` (the benchmark), `/usr/share/lab-sec/refs.tsv` (`rule<TAB>framework<TAB>control`), `/usr/share/lab-sec/nist-800-53r5/*.txt` (NIST's text). Prompts give the full `oscap` command once and then name it as `the scan command` (`sudo oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis_level1_server --rule xccdf_org.ssgproject.content_rule_RULE … /usr/share/lab-sec/scap/ssg-ubuntu2404-ds.xml`).

### 7.1 `example-control-to-evidence` (worked example), skills `control-to-evidence`, `crosswalks`, `read-a-control`

Labelled steps:

1. **Read the control.** `cat /usr/share/lab-sec/nist-800-53r5/AC-6.txt` and its enhancement (2), "Non-privileged Access for Nonsecurity Functions" (the writer quotes from the lab's copy).
2. **Find its checks.** `awk -F'\t' '$2 == "nist-800-53r4" && $3 == "AC-6(2)"' /usr/share/lab-sec/refs.tsv`: one rule, `sshd_disable_root_login`. Then what else that rule serves: `awk -F'\t' '$1 == "sshd_disable_root_login" {print $2, $3}' … | grep -v iso`: CIS 5.1.20, PCI DSS 2.2.6, HIPAA 164.312(e)(1)… One setting, many controls. Note the `r4`.
3. **Run it.** The scan command with that rule: `Result fail`.
4. **Fix it** the Module 1 way: a drop-in `/etc/ssh/sshd_config.d/60-hardening.conf` with `PermitRootLogin no`, `sudo sshd -t`, `sudo systemctl reload ssh`.
5. **Run it again**, and save the evidence: `sudo oscap … > ~/evidence/AC-6-2.txt` (the output carries the rule, the result and, with `date -u >> …`, the time).
6. **Watch evidence go stale.** `sudo cp /usr/share/lab-sec/examples/10-vendor.conf /etc/ssh/sshd_config.d/` (a file that says `PermitRootLogin yes`), rerun: `fail`, though the saved file says `pass`. Remove it; rerun.

Checks: `root-login-off` (the rule passes now, and an SSH login as root offering a test key is refused: the image authorises a throwaway key for root at build, as Module 1's hardening labs log in through a real `sshd`); `evidence-current` (`~/evidence/AC-6-2.txt` holds a `pass` for that rule and was written after the latest change under `/etc/ssh`); `vendor-file-gone`. Wrong fixes: `edited-main-file.sh` (`sshd_config` changed, but the vendor drop-in left: the first value wins), `evidence-before-fix.sh`, `not-reloaded.sh` (the rule passes on the files, but the running server still lets root in: the live check catches it). About 25 minutes; contract about 2 minutes.

### 7.2 Recall on the landscape

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-which-applies` | mcq | framework-landscape | A small online shop in Germany takes card payments and stores customers' addresses. Right: PCI DSS for the card data and GDPR for the personal data. Distractors: HIPAA and SOC 2; FedRAMP and CMMC; only ISO 27001, which covers both. |
| `mcq-law-or-contract` | mcq | framework-landscape | Which of these is a law, not a standard or a contract? Right: the HIPAA Security Rule. Distractors: PCI DSS; ISO/IEC 27001; the CIS Benchmarks. |
| `mcq-soc2-who` | mcq | framework-landscape | Who issues a SOC 2 report? Right: an independent CPA firm, against the AICPA's Trust Services Criteria. Distractors: the AICPA itself; a certification body accredited for ISO; the cloud provider whose services you use. |
| `mcq-free-texts` | mcq | framework-landscape | Which two can you read in full for free with no agreement? Right: NIST's CSF 2.0 and SP 800-53. Distractors: ISO 27001 and SOC 2's report; PCI DSS and ISO 27001; the CIS Benchmarks and ISO 27002. (Keep "PCI DSS free under a licence" in the explanation, as fact 5 is confirmed.) |
| `mcq-built-on` | mcq | framework-landscape | FedRAMP's controls come from: Right: NIST SP 800-53. Distractors: ISO 27001 Annex A; the CSF 2.0's subcategories; the AICPA's criteria. |
| `mcq-csf-functions` | mcq | framework-landscape | Which function did CSF 2.0 add? Right: Govern. Distractors: Identify; Recover; Detect. |
| `mcq-gdpr-72` | mcq | framework-landscape | Under GDPR, when must a breach that risks people's rights be reported to the supervisory authority? Right: without undue delay and, where feasible, within 72 hours of becoming aware of it. Distractors: within 72 hours of the breach happening; within 30 days; only once the investigation ends. |

### 7.3 Recall on reading controls (calculation skill, three estimates)

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `est-unlock-seconds` | estimate | read-a-control | PCI DSS 8.3.4 asks for a lockout of at least 30 minutes; `faillock.conf`'s `unlock_time` is in seconds. The smallest compliant value? Exactly. **1800** (`minutes * 60`). Mistakes: 30, 1.8. |
| `est-ac7-interval` | estimate | read-a-control | The shop's policy fills AC-7 as "4 invalid attempts within 15 minutes". `faillock.conf`'s `fail_interval` is in seconds: what value? Exactly. **900**. Mistakes: 15, 3600 (an hour). |
| `est-gdpr-hours-left` | estimate | read-a-control | The company became aware of a breach on Tuesday at 14:00. It's Thursday 10:00. How many hours remain to notify the supervisory authority within 72 hours? Exactly. **28** (`72 - 44`). Mistakes: 44 (hours gone), 0. |
| `parameter-filled` | predict_shell | read-a-control | NIST's AC-7 text in a file with its `[Assignment: organization-defined …]` brackets, and the shop's `policy.txt` (`ac-07_odp.01=4`, …). `grep -o '\[Assignment: [^]]*\]' ac7.txt \| wc -l` and `cut -d= -f2 policy.txt`. Prints the count of parameters and the values. Teaches that the framework leaves numbers to you. |
| `mcq-requirement-or-guidance` | mcq | read-a-control | In an 800-53 control, which part must be true for the control to be met? Right: the control statement, with its parameters filled in. Distractors: the discussion; the related controls; the references. |
| `oscap-read` | predict_shell | read-a-control | The captured four-rule output (`captured/oscap-four-rules.txt`). `awk -F'\t' '/^Rule/{r=$2} /^Result/{print $2, r}' oscap.txt \| sed 's/xccdf_org.ssgproject.content_rule_//'`. Prints four `result rule` lines. Retrieval of Module 1's report format, now real. |

### 7.4 `fill-evidence-map` (fill-in, systemd lab), skills `control-to-evidence`, `crosswalks`

`~/evidence/map.tsv` (`framework control kind source`), with gaps, for five controls in scope: `nist-800-53r4 AC-6(2)` (kind `rule`, source `...`), `pci-dss-4.0 8.3.6` (three `rule` rows, two of their sources `...`), `cis-ubuntu-24.04 6.1.2.4` (`rule`, `...`), `pci-dss-4.0 10.5.1` (kind `...`: no rule exists, so `config`, source the command that shows the effective retention), `pci-dss-4.0 6.3.3` (kind `scan`, source the scanner command). The prompt says: a `rule` row's source is a rule from `refs.tsv` mapped to that control; a `config` row's source is a command whose output shows the setting; a `scan` row's source is the scan command.

Checks: `rules-map-to-their-control` (every `rule` row's source maps to that row's framework and control in `refs.tsv`); `controls-covered` (8.3.6 has all three of its rules; AC-6(2) its one); `no-rule-where-none-exists` (10.5.1 isn't given a rule that merely mentions logs, such as `journald_storage`); `config-source-runs` (the `config` source runs and prints `MaxRetentionSec`); `scan-source-runs`. Wrong fixes: `nearby-rule.sh` (10.5.1 → `journald_storage`), `two-of-three.sh` (8.3.6 missing `_dcredit`), `substring-match.sh` (8.3.6 filled from `grep 8.3`, pulling in 8.3's other rules), `screenshot-source.sh` (`config` source `cat /home/learner/screenshot.txt`). About 25 minutes; contract about 1.5 minutes.

### 7.5 Recall on evidence and crosswalks

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-good-evidence` | mcq | control-to-evidence | Which is the strongest evidence that root can't log in over SSH? Right: today's scanner result for the rule, which the auditor can run again. Distractors: a screenshot of `sshd_config` from last quarter; the hardening runbook; an engineer's signed statement. |
| `mcq-no-rule` | mcq | control-to-evidence | No benchmark rule tests PCI DSS 10.5.1 (retention). Right: show the journal's effective retention settings (and, over time, the oldest entry kept) as configuration evidence. Distractors: mark it met because `journald_storage` passes; mark it not applicable; tailor the benchmark to add a rule that always passes. |
| `rules-for-control` | predict_shell | crosswalks | A twelve-line extract of `refs.tsv`. `awk -F'\t' '$2 == "pci-dss-4.0" && $3 == "8.3.6" {print $1}' refs.tsv \| sort`. Prints the three password rules. |
| `controls-for-rule` | predict_shell | crosswalks | The same extract. `awk -F'\t' '$1 == "sshd_disable_root_login" {print $2}' refs.tsv \| sort -u`. Prints the frameworks that one setting serves. |
| `mcq-stale-mapping` | mcq | crosswalks | The table maps a rule to "ISO 27001 A.9.4.2". Right: that's the 2013 numbering; ISO 27001:2022 renumbered Annex A, so the mapping must be translated before an auditor of the 2022 edition can use it. Distractors: A.9.4.2 is unchanged in 2022; ISO mappings never change between editions; the rule therefore doesn't apply. |
| `mcq-substring-trap` | mcq | crosswalks | `grep 8.3 refs.tsv` for PCI DSS 8.3.6's rules returns 44 lines (counted in the prototype's table; 28 of them PCI rows). Right: it also matches 8.3, 8.3.4, 8.3.9 and more (and `.` matches any character); compare the control column exactly. Distractors: 8.3.6 has 44 rules; the table has duplicates to remove; grep needs `-i`. |
| `mcq-compliant-secure` | mcq | crosswalks | Every CIS Level 1 rule passes. Right: the server meets the baseline; whether it's secure enough depends on its threats, which the baseline doesn't know. Distractors: it is secure; it is now PCI DSS compliant; Level 2 is no longer needed anywhere. |

### 7.6 `write-evidence-report` (write, systemd lab), skills `control-to-evidence`, `crosswalks`, `gaps-and-exceptions`

Prompt: write `~/bin/evidence FRAMEWORK CONTROL` (for example `evidence pci-dss-4.0 8.3.6`). It runs the scan for every rule `refs.tsv` maps to exactly that framework and control (one `oscap` run with several `--rule`), prints `rule result` for each, sorted by rule, then a last line: `met` (at least one rule passes and none fails), `not met` (any rule fails) or `no automated evidence` (no rule maps to it, or every one is `notapplicable`). The prompt names `awk -F'\t' -v`, building the `--rule` arguments in a loop, and the Module 1 report format.

Checks pick their controls at check time from `refs.tsv` and the lab's state, which the image fixes (some rules pass, some fail): one control whose rules all pass, one with a failing rule, one with no rule (a real identifier from the framework that the table lacks, such as `pci-dss-4.0 10.5.1` or `nist-800-53r4 AU-11`), one whose identifier is a prefix of another (`pci-dss-4.0 8.3` beside `8.3.6`), always across two frameworks, with at most eight rules each so a check stays under 15 s. The check computes the expected lines itself with one `oscap-rules` run (lab-base-sec.md, section 6).

Wrong fixes: `substring.sh` (`grep "$2"`), `na-is-fail.sh`, `na-is-pass.sh` (all-`notapplicable` reported `met`), `first-rule-only.sh`, `hard-coded.sh` (prints the worked example's AC-6(2) answer for anything), `unsorted.sh`. About 40 minutes; contract about 3 minutes (oscap runs of 2 s).

### 7.7 Recall on gaps and exceptions

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `mcq-exception-parts` | mcq | gaps-and-exceptions | `partition_for_tmp` fails on a server whose disks the platform fixes. Right: a written exception: the rule, why, a compensating control, an owner and an expiry. Distractors: remove the rule from the profile; pass it by creating an empty `/tmp` partition file; leave it failing without comment. |
| `mcq-stricter-benchmark` | mcq | gaps-and-exceptions | CIS asks for 14-character passwords, PCI DSS 8.3.6 for 12. The shop sets 12. Right: PCI DSS 8.3.6 is met; the CIS rule fails, and the shop records that it follows PCI DSS's value there. Distractors: both are met, since 12 is the minimum; both fail; PCI DSS fails because CIS is part of it. |
| `est-coverage` | estimate | gaps-and-exceptions | 48 controls are in scope: 30 have an automated check, 12 have configuration or document evidence, 6 have none. What percentage have evidence? Within 0.1. **87.5** (`(automated + other) / total * 100`). Mistakes: 62.5 (automated only), 12.5 (the gaps). |
| `mcq-tailoring` | mcq | gaps-and-exceptions | A colleague "tailors" the benchmark to remove the failing rules before the audit. Right: the report then hides gaps; tailoring is for rules that don't apply, recorded with reasons. Distractors: it's the standard way to reach 100%; auditors expect a 100% score; tailoring is forbidden by every framework. |

### 7.8 Ladder order for `topic.yaml`

`example-control-to-evidence`, `mcq-which-applies`, `mcq-law-or-contract`, `mcq-soc2-who`, `mcq-free-texts`, `mcq-csf-functions`, `mcq-gdpr-72`, `est-unlock-seconds`, `est-ac7-interval`, `est-gdpr-hours-left`, `parameter-filled`, `oscap-read`, `fill-evidence-map`, `mcq-good-evidence`, `mcq-no-rule`, `rules-for-control`, `controls-for-rule`, `mcq-stale-mapping`, `mcq-substring-trap`, `write-evidence-report`, `mcq-exception-parts`, `mcq-stricter-benchmark`, `est-coverage`. That is 21 quick items (about 32 minutes), a worked example, a fill-in and a write. Review-only: `mcq-built-on`, `mcq-requirement-or-guidance`, `mcq-compliant-secure`, `mcq-tailoring`.

**Practised before proven:**

| Skill | Practised in |
| --- | --- |
| framework-landscape | seven items (asked in the explain) |
| read-a-control | the example (step 1), three estimates, two shell items |
| control-to-evidence | the example, the fill-in, two items, the write |
| crosswalks | the example (step 2), the fill-in, four items, the write |
| gaps-and-exceptions | three items and an estimate; the write's `no automated evidence` |

## 8. Proofs

### 8.1 Build: `build-evidence-pack` (systemd lab on `lab-base-sec`, 60 minutes), skills: all five

**Story.** The payments server's PCI DSS assessment is next week. `/srv/compliance/scope.tsv` lists five controls and what the assessor will check, in plain words:

| Control | The assessor checks |
| --- | --- |
| `nist-800-53r4 AC-6(2)` (also PCI DSS 2.2.6) | root can't log in over SSH |
| `pci-dss-4.0 8.3.6` | passwords at least 14 characters (the shop's policy, stricter than PCI's 12) with letters and digits |
| `cis-ubuntu-24.04 6.1.2.4` | the journal is kept on disk |
| `pci-dss-4.0 10.5.1` | the audit trail is kept 365 to 400 days (topic 46's policy) |
| `pci-dss-4.0 6.3.3` | no finding past its policy timeline (topic 48's policy) |

The prompt asks: make the server meet all five; write `~/evidence/evidence.tsv` (`control kind source result file`), one row per piece of evidence, where `kind` is `rule`, `config` or `scan`, `result` is `pass`, `met` or `fail`, and `file` is the evidence file in `~/evidence/`; and record **one** exception in `~/evidence/exceptions.tsv` (`control rule reason compensating-control owner expires`) for the one CIS rule in scope that can't pass on this platform (the prompt names its control, `cis-ubuntu-24.04 1.1.2.1.1`, "/tmp on its own partition", which the platform fixes). Rules: don't change the benchmark, `refs.tsv` or the scanners; evidence files are the tools' own output.

**What the image holds:** SSH root login allowed (by a vendor drop-in, as in the example's step 6), no `pwquality.conf` settings, the default journal without a `Storage=` drop-in, the audit namespace without `MaxRetentionSec=`, the release-pocket packages (topic 48's findings), and the shop's audit writer.

**Checks:**

| Id | End state | Catches |
| --- | --- | --- |
| `ac-6-2-met` | the rule passes now, and a test root login is refused | not fixed; fixed in a file the vendor drop-in overrides |
| `passwords-met` | `accounts_password_pam_minlen`, `_dcredit` and `_lcredit` pass, and `minlen` is at least 14 | 12-character minimum; two of three |
| `journal-on-disk` | `journald_storage` passes | |
| `retention-met` | the audit namespace's effective `MaxRetentionSec` is 365 to 400 days | |
| `patches-met` | a fresh offline scan has no finding past its timeline (the check computes timelines from topic 48's policy and data) | |
| `evidence-rows-right` | each `rule` row's rule maps to its control in `refs.tsv`, every rule the control needs is there (AC-6(2) one, 8.3.6 three, 6.1.2.4 one), and no control has a `rule` row where no rule maps (10.5.1, 6.3.3) | padding with unrelated passing rules; missing rules |
| `evidence-current` | each evidence file matches a fresh run of its source now (the rules' results; the config command's output; the scan's findings) and was written after the latest change to what it measures | evidence made before the fix; hand-typed files |
| `one-exception` | exactly one exception, for `partition_for_tmp`, which does fail; every field filled; expiry at most 365 days ahead | excepting a fixable rule; open-ended exceptions |
| `benchmark-intact` | the data stream, `refs.tsv` and the scanners match their checksums, and no tailoring file is used | tailoring the failures away |

**Wrong fixes:** `vendor-file-left.sh` (fix in `sshd_config`), `minlen-12.sh`, `two-password-rules.sh`, `journald-rule-for-retention.sh` (10.5.1 evidenced by `journald_storage`), `stale-evidence.sh` (evidence saved before the fixes), `typed-evidence.sh` (files written by `echo`), `excepted-ssh.sh` (an exception for root login instead of fixing it), `no-expiry.sh`, `tailored.sh` (a tailoring file that removes failing rules), `unpatched.sh` (evidence for 6.3.3 claims `met` without patching). Ten.

**CI time.** Boot 2 s; the solution about 30 s (a patch run and five scans); the checks about 25 s (two `oscap` runs and a scan). Twelve containers and the restart trial: **about 7 minutes**. **Not prototyped end to end:** `_dcredit` and `_lcredit` passing with `dcredit = -1` and `lcredit = -1` in `pwquality.conf` (`_minlen` was tried), the test root login (needs a throwaway root key in the image), and the tailoring check. Prove the contract first.

### 8.2 Debug: `debug-audit-findings` (systemd lab on `lab-base-sec`, 45 minutes), skills `control-to-evidence`, `crosswalks`, `gaps-and-exceptions`

**Prompt.** The payments server has an evidence pack from last month (`~/evidence/`), built from the same scope as the build. The assessor's sample this morning:

- the pack says root can't log in over SSH, but the assessor logged in as root;
- the pack says the journal is kept on disk, but after the assessor's reboot test (stopping and starting the lab) the journal was empty;
- for one control, the evidence doesn't test what the control asks.

There are three faults (two in the server, one in the pack). Rules: fix the server, then regenerate the evidence for what you changed; don't change the benchmark, `refs.tsv` or the scope; evidence files are the tools' own output.

**The faults:**

1. `/etc/ssh/sshd_config.d/05-support.conf` (`PermitRootLogin yes`, "for the vendor's remote support"), added after the pack was made. Evidence: the rule now fails; `sshd -T` shows `permitrootlogin yes`.
2. `/etc/systemd/journald.conf.d/90-tmp.conf`, `Storage=volatile` ("reduce disk wear"). Evidence: `journald_storage` fails; files under `/run/log/journal`. **Untried:** that `journald_storage`'s OVAL reads drop-ins in order so a later drop-in flips it; the writer tries it first (the fallback is to plant the fault in `journald.conf` itself).
3. `evidence.tsv` evidences `pci-dss-4.0 8.3.6` with `accounts_password_pam_unix_remember` (a password-history rule, mapped to 8.3.7). Evidence: `refs.tsv`.

**Checks:** `ac-6-2-met` and `journal-on-disk` (as in the build), `evidence-rows-right`, `evidence-current`, `benchmark-intact`, `scope-intact`, `support-access-documented` (if the learner keeps vendor access, it isn't root over SSH: the check only requires root login refused). **Wrong fixes:** `evidence-only.sh` (regenerates the pack without fixing the server: `evidence-current` passes, the `met` checks fail), `server-only.sh` (fixes 1 and 2, leaves the stale pack), `deleted-the-row.sh` (removes the 8.3.6 row instead of correcting it), `fixed-main-sshd.sh` (sets `PermitRootLogin no` in `sshd_config`, which `05-support.conf` still overrides), `excepted-root.sh`, and one "two of three" per fault. About 11 containers: **about 5 minutes**.

### 8.3 Explain

**Prompt.** "Your company is preparing for its first PCI DSS assessment and also wants SOC 2 next year. A director asks: 'Can't we just pass the CIS benchmark and be done?' Explain, in your own words: what PCI DSS, SOC 2, ISO 27001 and NIST's CSF and SP 800-53 each are, who checks them and how they relate; how you'd read one control and turn it into a setting; how you'd show an assessor that a control is met, including one that no scanner rule tests; why one setting can count for several frameworks and what to watch for in a mapping; and what you'd do with a rule you can't pass. Answer the director's question."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `landscape` | yes | PCI DSS: card data, contract, QSA or self-assessment; SOC 2: a CPA's report against the Trust Services Criteria; ISO 27001: a certified management system; CSF: outcomes in six functions; 800-53: the control catalogue others (FedRAMP) build on |
| `read-and-set` | yes | statement plus parameters, filled by policy; turned into a value in the setting's units |
| `evidence` | yes | automated checks run now, configuration readings or other tools' reports where no rule exists, all current, reproducible and dated; a screenshot or a stale file isn't enough |
| `crosswalk` | yes | the benchmark's references map one rule to many controls and one control to several rules; mappings carry versions (800-53 rev 4, ISO 2013) and support rather than satisfy |
| `exceptions` | yes | a rule that can't pass gets a written exception with reason, compensating control, owner and expiry; never removed from the profile to hide it |
| `director` | yes | no: a benchmark covers configuration, not policies, people, retention, patch timeliness or the organisation's own scope; and compliant isn't the same as secure |

## 9. Review pool

- framework-landscape: `mcq-which-applies`, `mcq-free-texts`, `mcq-built-on` (review-only), `mcq-gdpr-72`.
- read-a-control: `est-unlock-seconds`, `est-gdpr-hours-left`, `parameter-filled`, `mcq-requirement-or-guidance` (review-only).
- control-to-evidence: `mcq-no-rule`, `mcq-good-evidence`, `write-evidence-report`.
- crosswalks: `controls-for-rule`, `mcq-stale-mapping`, `mcq-substring-trap`, `mcq-compliant-secure` (review-only).
- gaps-and-exceptions: `est-coverage`, `mcq-stricter-benchmark`, `mcq-tailoring` (review-only).

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| C1 | **`lab-base-sec`** with its compliance parts: OpenSCAP, `linux-base`, `libpam-pwquality`, the data stream from the pinned release zip, `refs.tsv` at build, NIST's control texts from OSCAL (public domain), `oscap-rules` with its one retry, a throwaway root key for the live root-login check | as designed in lab-base-sec.md |
| C2 | A CI spike for OpenSCAP: the example's, the write's and the build's contracts three times each on a GitHub runner before the lessons, because of the one segfault seen (lab-base-sec.md, question 2) | three runs |
| C3 | Nothing in the app. | |

## 11. Cost and time

- **Money:** none. The clouds' compliance tools (AWS Audit Manager, Microsoft Purview Compliance Manager and Defender for Cloud's regulatory compliance, Google's Security Command Center compliance) are Module 20's and were not priced.
- **Learner minutes:** lesson 18, reading 18 (NIST CSF page 8, the four controls 10), 21 quick items 32, worked example 25, fill-in 25, write 40, build 60, debug 45, explain 20: **283**. With the optional readings, 309.
- **Labs and CI:** five labs; contract minutes: example about 2, fill-in about 1.5, write about 3, build about 7, debug about 5: **about 19 minutes**.

## 12. Open questions, each with a recommendation

1. **Which frameworks to teach in depth.** Ten in one topic is a landscape, not ten lessons. **Recommendation:** the landscape for all ten (one table, seven items), depth for NIST 800-53 (free text the lab can carry) and PCI DSS (identifiers and Microsoft's quotations), and CIS through the benchmark already used in Module 1. Module 20 maps SOC 2, ISO, HIPAA, FedRAMP and CMMC to cloud services.
2. **Mappings to 800-53 rev 4.** The data stream's references are to rev 4 (fact 14), while 5.2.0 is current. **Recommendation:** use them as they are and make the staleness a taught point (`mcq-stale-mapping`); the controls used in the labs (AC-6(2), AC-7, IA-5(1)) keep their identifiers in rev 5, which the writer confirms against the OSCAL catalogue.
3. **PCI DSS's own text.** Not in the image (copyright). **Recommendation:** identifiers in the labs, Microsoft's CC BY 4.0 quotations in the lesson, and the PCI SSC library linked; the writer confirms the library's licence terms in a browser.
4. **ISO 27001's price and SOC 2's Type 1 and 2.** Neither confirmed from the publisher this session. **Recommendation:** the writer opens iso.org and the AICPA's SOC 2 page in a browser before writing those sentences; no item depends on them.
5. **CIS Benchmark licence.** Not shown on the pages read. **Recommendation:** link only, never quote; the lab uses section numbers from ComplianceAsCode (BSD-3-Clause).

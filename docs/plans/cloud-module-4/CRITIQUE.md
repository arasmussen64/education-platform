# Critique of the Module 4 briefs

By the critic, 2026-11-22. Every problem found in the fourteen briefs, what was done about it in [MODULE-4-BRIEF.md](MODULE-4-BRIEF.md), what was re-checked, and what was not.

## 0. What this review did and did not cover

Read this before trusting the rest.

- **Read in full:** `identity-lab-base.md`, `csa.m4.checkpoint.md`, `lab-base-sec.md`, `csa.sec.threat-modeling.md`, `csa.sec.authn-authz.md`.
- **Read in part** (the header, prerequisites, terms, skills, proofs, review pool, platform work, cost, open questions and unverified sections; **not** the lesson plan, the facts table, the resources table or the practice ladder): `csa.sec.strong-auth.md`, `csa.sec.crypto.md`, `csa.sec.federation.md`, `csa.sec.secrets.md`, `csa.sec.audit.md`, `csa.sec.zero-trust.md`, `csa.sec.vulnerabilities.md`, `csa.sec.compliance.md`. `csa.sec.pki.md` was read except its facts, resources and ladder. The briefs are about 900 KB of text together and the review had to fit one session without helpers.
- **So not checked:** the multiple-choice lengths of any brief's ladder; the practice items one by one; nine briefs' resources tables. Section 5's "as designed" for those ladders means "not reviewed item by item", and each topic's cold review must do that.
- **Facts re-fetched: 14, not the 55 the task asked for** (five a brief). Section 3 lists them. Two briefs (cryptography beyond IR 8547, compliance) have one or none confirmed.
- **Resources re-opened: 4** (Schneier's essay, RFC 9700, NIST SP 800-63B-4, AWS's CloudTrail page), not three a topic.
- **Incidents:** eleven chosen; six read at the source, five not (section 4).
- **Prerequisite claims:** checked by searching every Module 1 to 3 lesson for the terms the briefs lean on (section 2); the lessons were not re-read whole.
- **Experiments re-run:** two (section 5).

## 1. Problems that changed the design

| # | Problem | Where | What was done |
| --- | --- | --- | --- |
| 1 | **Two different identity bases were prototyped, and the checkpoint was built on the older one.** `identity-lab-base.md` describes today's (`idlab cert`, `timesync@M` that sets the clock right by itself, port 443). Checkpoint part 2 ran on `lab-base-idproto` of 2026-11-12 (`lab-ca issue`, `lab-secret`, `lab-clock`, a `timesync` that reads `chrony.conf`, a real `chronyd`, port 8443). The checkpoint brief says it "did not see an identity-lab base brief". Part 2's clock fault (a time server that no longer exists) cannot be built on today's design as written | base, checkpoint | The earlier time model joins the final base; part 2 moves to the final base's names and is run again there (brief 4.1, 6). The critic read the earlier files inside the image and copied them to `prototypes/critic/earlier-base-time/` |
| 2 | **Strong authentication came before the topic that teaches tokens.** Its labs read `amr` from a token, edit a realm file, use `signin`; its only prerequisite was authentication and authorization, which "never shows a token's format". Zero trust wanted both | strong-auth, federation, zero-trust | Strong authentication moves after federation, which owns the identity-lab onboarding (brief 2, 12) |
| 3 | **Two bases were both named `lab-base-sec`** (OpenBao; the payments server), and checkpoint part 3 asked "`lab-base-sec`" for git and gitleaks, which only the OpenBao one has, under the payments server's story | crypto, lab-base-sec, checkpoint | `vault` and `pay`; part 3 is on `vault` (brief 4.2, 4.3, 6) |
| 4 | **The checker cannot build a base on a base.** `build_base` builds `content/lab-bases/<name>/` and never reads its `Dockerfile`, so `id` fails on any machine without a `lab-base-net` image, which is every CI runner. Confirmed by reading `tools/labcheck.py` | base | P1, with an ADR-0018 amendment |
| 5 | **CI's limit is CPU, not memory.** Briefs worried about 3 GB for four labs; a runner has 16 GB and 4 CPUs. Keycloak's boot is CPU-bound: 16 s, 55 s and 140 s at eight, one and half a CPU (section 5). Every wrong fix is a boot | base, federation, strong-auth, zero-trust, checkpoint | A spike first (P4); a lever ready (P6); identity CI figures marked as depending on it |
| 6 | **The checkpoint checks two things no topic taught:** PCI DSS scope (one sentence in the compliance brief) and time sync (no Module 1 to 3 lesson mentions NTP, chrony or time sync: searched) | checkpoint, compliance, federation | A sixth skill `pci-scope`; clocks in federation (brief 5) |
| 7 | **The lessons were designed around assigned reading** (26 to 81 minutes a topic), which ADR-0031 no longer allows where a page can't be copied | all eleven | Brief 3.1 and each topic's "Lesson" line. PKI's and federation's lessons carry their topics alone |
| 8 | **Zero trust was never run against a real provider:** a 200-line stand-in over plain HTTP. The cookie-size problem (about 3 kB of Keycloak tokens; nginx passes one `Set-Cookie`) is open | zero-trust | An ordered list of what to try first, with Redis as the fallback (brief 5) |
| 9 | **`tm-check` exists twice in design and once on disk:** the topic's original is lost, the checkpoint's re-implementation is what survives, and its author says the two "may differ in details" | threat-modeling, checkpoint | One home (the `tm` base), starting from the surviving copy; the topic's reference and wrong models are rebuilt against it |

## 2. Cross-brief and prerequisite problems

| # | Problem | What was done |
| --- | --- | --- |
| 10 | **Most cited prototypes are gone.** Only `prototypes/checkpoint/` and `prototypes/identity-lab-base/` are on disk. `tm-zt/`, `authn-strong/`, `cps/`, `federation/`, `audit-vuln-compliance/` are not. Every "tried" in nine briefs is a report, not something a writer can re-run | Named per topic in the brief; each writer rebuilds and re-runs before the lesson |
| 11 | **Designers' Docker leftovers,** though each brief says everything was removed: `lab-base-idproto`, `lab-base-idnet`, `idlab-sso:dev`, `idlab-kcprobe` (two tags), `lab-csa.idproto-proto-sso`, `lab-csa.idproto4-sso-a` to `-d` | Not the critic's to remove; listed for the owner queue |
| 12 | PKI: "`csa.net.http-tls` names a CRL in a sentence". No Module 3 file contains "CRL" | PKI introduces the word (brief 3.5, 5) |
| 13 | PKI: `csa.net.certificates` "owns" verify codes 0, 10, 18, 19, 20, 21 and 62. Its lesson has 10, 20, 21 and 62 | The writer checks its items for 18 and 19 |
| 14 | Zero trust credits `csa.net.http-semantics` with "401 against 403". That lesson never mentions either (only a lab's stand-in app does); authentication and authorization defines them, as its own brief says | Corrected |
| 15 | Federation: "the first to have the learner run `jq`". Module 1 has `write-jq-answers`. COMMON's "jq is not in the lab images" is loose for the same reason | `jq` is in the `id` base; retrieval, not new |
| 16 | Cryptography: "none of the earlier topics teaches" MAC or HMAC. `csa.net.ipsec`'s lesson names HMAC | One sentence of retrieval |
| 17 | **PDP and PEP defined twice** (authentication and authorization; zero trust), and the glossary allows one owner | Authentication and authorization owns them |
| 18 | **"Relying party" defined three ways** (PKI, federation, strong authentication) | PKI owns one general definition |
| 19 | Workload identity, MFA, exception and compensating control, secret, token each defined in two or three briefs; four briefs settle a term "if the other brief doesn't" | Brief 3.5 settles every one |
| 20 | **Three host names** for one provider, and two company names | `login.shop.test`, `shop.test` |
| 21 | The same item id and question, `mcq-401-or-403`, in two topics | Zero trust's becomes `mcq-proxy-401-or-403` |
| 22 | The checkpoint maps the third-party-script weakness to `csa.sec.vulnerabilities/scan-and-read`, which doesn't cover it (its own note says "weak fit") | Mapped to `respond-to-risk` and `pci-scope` |
| 23 | Two designs of the resource server (the stand-in `stock-api`; mod_oauth2), and the base never ran mod_oauth2 | One rule for which lab uses which (brief 4.1) |
| 24 | `ca-whatif` asked for "in both bases, one copy built from the same file": two build contexts can't share a file | One source, one copy, a test that they match |
| 25 | Each of six briefs calls its download "the second from outside Ubuntu's archive" | Six, listed once, one pin rule |
| 26 | **Pins that break the two-week habit or disagree:** OSV-Scanner v2.7.1 was three days old when pinned (released 2026-11-09, re-read); Keycloak 26.8.1 in one brief and 26.8.2 in two; oauth2-proxy 7.15.5 in one and 7.15.6 in another | Brief 3.3's rule |
| 27 | Time: threat modeling 324, cryptography 315, federation 328, secrets 323 and zero trust 330 minutes before trims | The designers' trimmed figures, plus the two additions; writers recount once readings are optional |
| 28 | CI over the 20-minute aim: federation 34 to 38, zero trust 28 and more, strong authentication 22, checkpoint 30 | Trims named; 25 accepted for identity topics; all depend on the spike |
| 29 | The generated outlines say 240 minutes a topic and 480 for the checkpoint | Real figures in brief 2 |
| 30 | The spec's own checkpoint text names part 2's three faults, and the outline's objectives repeat them | Brief 12.2 |

## 3. Against the failure list

**Debug prompts that say what or where** (each reworded in the brief): threat modeling ("a flow from another company was never reviewed"); cryptography ("since last night's key rotation"); secrets (describes the faults' kinds, and hides a fourth required step); compliance ("two in the server, one in the pack"); zero trust ("through payroll's phone-app API"; and its prototype's check messages named a machine and a port). PKI's, federation's, strong authentication's, audit's and vulnerabilities' prompts give symptoms only. PKI's scenario says the issuing CA was re-keyed yesterday; left, as a description of the system.

**Checks a lazy or weakening fix would pass:**

| Check | The hole | Fix |
| --- | --- | --- |
| audit `still-rate-limited` ("above 0") | a burst of a million | a range tied to the stated batch |
| federation and checkpoint `api-keys-by-url` ("no `jwk`, `pem` or `pubkey` line") | a pin spelled another way | an allowlist; recorded as a reading check |
| checkpoint `no-extra-leeway` (one directive in the site's files) | the same setting in an included file | read every included file |
| compliance `evidence-current` ("written after the latest change") | depends on file times, which differ between Docker Desktop and CI | content against a fresh run |
| strong authentication `brute-force` (settings only) | fine, but cheap to prove | behaviour added |
| secrets `no-secret-zero-on-disk` (a token pattern) | wrong if the pinned OpenBao's tokens look different | confirm the format first |

**Used before taught:** time sync (problem 6); PCI scope (6); tokens in strong authentication (2); `date -d` in a `predict_shell` item would break the content README's rule (vulnerabilities: kept to labs). Found already handled by the designers: the read loop (audit teaches it), awk's two-file join (vulnerabilities), git (secrets), systemd timers (PKI).

**Restart trial and runner risks:** brief 4.5. The sealing labs depend on a workaround (`KillSignal=SIGKILL`) for a systemd fault nobody found reported; OpenSCAP crashed once in five full runs; nothing in the module has run on a runner.

**Money:** none found. One brief proposes an owner-queue item about a free Microsoft developer tenant; kept out of the open list.

**Facts re-fetched on 2026-11-22** (all supported unless noted):

| Brief | Claim | Result |
| --- | --- | --- |
| threat modeling | ATT&CK v20.1 from 13 October 2026; v19.2, v18.1 dates | supported |
| threat modeling | Schneier's $20,000, $80,000, $60,000 | supported |
| authn-authz | Access Analyzer $0.20, $0.0020, $9.00 | supported |
| strong-auth | SP 800-63B-4 on AAL2 and syncable authenticators at AAL3 | supported (first 100,000 characters of the page) |
| crypto | NIST IR 8547 final, October 2026 | supported; the 2030 and 2035 dates are not on the landing page: **not confirmed** |
| pki | AWS Private CA $400, $50, $0.75 | supported |
| federation, checkpoint | RFC 9700: date, BCP 240, exact matching, implicit and password grants | supported |
| base | Keycloak 26.8.2, 5 November | supported; the release page does not mention SCIM (the base tried it on the running server) |
| secrets | gitleaks 8.16.0 in Ubuntu 24.04 | supported; it is in universe |
| audit | CloudTrail event history, 90 days, management events only | supported |
| zero-trust, base | oauth2-proxy 7.15.5 and 7.15.6 | both exist; the briefs pin different ones |
| vulnerabilities | BOD 26-04, sixteen rows | supported from secondary reports (issued 10 June 2026; agencies follow it from 7 December 2026); the directive itself was not opened |
| lab-base-sec | OSV-Scanner v2.7.1, 9 November 2026 | supported; see problem 26 |
| compliance | CMMC phase dates | **not confirmed** (the Defense Department's page answered 403) |
| CI | a public-repository runner: 4 CPUs, 16 GB, 14 GB of disk | GitHub's docs |

## 4. The incidents for the stories

| Topic | Incident | Read at the source? |
| --- | --- | --- |
| threat modeling | Target, 2013 | No: search summaries of Krebs's report; the Senate report's PDF gave no text |
| authn-authz | Capital One, 2019 | Partly: the OCC's penalty release, which doesn't describe the role; the Justice Department's pages returned nothing |
| crypto | Adobe, 2013 | No: found by search (the Australian regulator's report, CSO Online) |
| pki | DST Root CA X3's expiry, 2021 | Yes (Let's Encrypt) |
| federation | Storm-0558, 2023 | Yes (Microsoft) |
| strong-auth | Cloudflare's phishing, 2022 | Yes (Cloudflare) |
| secrets | Uber, 2016 | Yes (FTC) |
| audit | The 2023 mailbox intrusion's detection | Yes (CISA AA23-193A) |
| zero trust | Colonial Pipeline, 2021 | Yes (the Senate committee's page) |
| vulnerabilities | Equifax, 2017 | Partly: GAO's summary page; the details are in its PDF |
| compliance | British Airways, 2018 | No: the penalty's date and amount from search; the notice's address answered 404 |

A writer who can't read a "No" at its source picks another incident.

## 5. Experiments the critic ran (Docker Desktop 29.8.2, 2026-11-22)

1. **A machine with no cable on the network base** (PKI's platform question 1). A three-machine topology with `machine root` and no `link` or `lan` for it, `FROM lab-base-net`: booted to `running` in 2 s, `root` has `lo` only, a ping from it says "Network is unreachable", `netlab verify` says `verified`. No base change needed. Files: `prototypes/critic/nocable/`.
2. **Checkpoint part 2's boot under a CPU limit.** Built from `prototypes/checkpoint/sso/` on the earlier image and started three times as `labcheck` starts a lab: no limit (8 CPUs), 16.0 s to booted, 770 MiB; `--cpus 1`, 54.5 s, 746 MiB; `--cpus 0.5 --memory 900m`, 2 min 20 s, 773 to 805 MiB, not killed. The figures are `systemd-analyze`'s. This is the **earlier** base, with two Apache machines and chrony beside Keycloak, and the critic did not check whether it sets `cache=local`. The final base boots in 9.5 s unlimited and may scale better; its image was not on this machine to try. A Docker CPU limit is also harsher than a busy shared core.

Created and removed: images `crit-nocable`, `crit-sso`; containers `crit-nocable`, `crit-sso-a`, `crit-sso-1cpu`, `crit-sso-half`, and four short-lived ones made from `lab-base-idproto` to read and copy files (`crit-ls`, `crit-ls2`, `crit-ls3`, `crit-cp`). Afterwards no container, image or network whose name begins `crit-` exists. Nothing was pruned and no image the critic did not create was changed or removed.

## 6. Open questions decided

Each is in the brief's section 10 with its reason. The ones a designer left to the critic: one host name (`login.shop.test`); `jq` (yes); rebuild the realm on apply (yes); the API's module (both, by a rule); a key-rotation check that adds a key (no); the checkpoint's third part (yes, if it keeps its contract); a check-time piece in part 1 (no); `tm-check`'s home and additions (the `tm` base, all three); Cedar or Rego (Cedar); a base for policy labs (yes); OSV-Scanner over Trivy and Grype (yes); `auditd` on paper (yes); a real-cloud lab anywhere (no); the prerequisite of secrets on federation (yes, now that federation comes first).

## 7. Still unverified

- Everything on a GitHub runner.
- The final `id` base four at once on four CPUs; mod_oauth2, a role-conditional flow in a realm file, the `amr` claim, SAML metadata at build, SCIM with a service client's token, and `signin` through oauth2-proxy, on that base.
- Checkpoint part 2 on the final base; part 3 at all; part 1's seven sibling labs.
- Zero trust against Keycloak.
- The `pay` base as one Dockerfile; the audit, vulnerability and compliance debugs as labs.
- Every contract whose prototype is no longer on disk.
- Nine briefs' ladders, facts and resources beyond the samples above; every licence called copyable; five of the eleven incidents.

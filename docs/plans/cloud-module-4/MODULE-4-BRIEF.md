# Module 4 brief: Security and identity foundations

The final plan for Module 4 of the Cloud Solutions Architect track, merged by the critic on 2026-11-22 from the eleven topic briefs of 2026-11-12, the two base designs (`lab-base-sec.md`, `identity-lab-base.md`) and the checkpoint brief of 2026-11-22. Nothing here is in the repository yet.

**How to use it.** This file decides; the designers' briefs hold the detail. Where they disagree, this file wins. Each topic section names the designer's file and lists only what changes; everything it doesn't mention stands as the designer wrote it. [CRITIQUE.md](CRITIQUE.md) lists every problem found, what was done about it, and how much of each brief the critic read and re-checked (not all of it: read that first if you rely on a brief's detail).

The owner's rule decided every judgement call: the best learning experience, then memory retention, then free or inside the $150 Azure credit. Each call is in section 10. **Nothing in Module 4 costs money:** every lab, proof and review runs locally.

The briefs name topics by the spec's numbers of 2026-11-12. This plan moves one topic (section 2), so **it names topics by id**, and writers should too.

## 1. The plan in one screen

- **Eleven topics, one moved.** Strong authentication moves from fourth to seventh, after SAML, OAuth and OIDC: its labs read a token's `amr` claim, edit a realm file and use the scripted browser, all of which the federation topic teaches first. The spec's table is reordered (section 12).
- **Five new lab bases, and one way to run an identity provider.** `id` (Keycloak 26.8 on the network base: federation, strong authentication, zero trust, checkpoint part 2), `vault` (OpenBao, PostgreSQL, git, gitleaks, podman: cryptography, secrets, checkpoint part 3), `pay` (the payments server: audit, vulnerabilities, compliance), `policy` (Cedar: authentication and authorization, one strong-authentication lab) and `tm` (the threat-model checker: threat modeling, checkpoint part 1). Two designers both called their base `lab-base-sec`; they are `vault` and `pay` now. PKI's labs need only the network base.
- **The identity base is two prototypes merged.** Today's design (`identity-lab-base.md`) is the base. Checkpoint part 2 was built on an **earlier** image of 2026-11-12 (`lab-base-idproto`, still on the owner's PC), whose time model is better: a small SNTP client that reads the machine's `chrony.conf` and a real `chronyd` that only serves. That model joins the final base (section 4).
- **`labcheck` learns to build a base on a base** (about eight lines; a fourth amendment to ADR-0018, Proposed).
- **A CI spike comes before any lab is written.** A GitHub runner has 4 CPUs, 16 GB of memory and 14 GB of disk (GitHub's docs, read 2026-11-22). Memory is not the limit: four identity labs at 0.8 GiB are 3.2 GiB. **CPU is.** The critic booted checkpoint part 2 (on the earlier image) with Docker's CPU limit: 16 s with eight CPUs, **55 s with one, 140 s with half of one** (under a 900 MiB memory cap it still booted, at 773 to 805 MiB). The spike measures the final base four at once; a ready lever (an identity lab counts as two of a machine's four jobs) is switched on only if it must be.
- **Every lesson stands on its own text** (ADR-0031), opens with a puzzle, tells one real incident, and asks its quick questions between its parts (ADR-0026, ADR-0025). Section 3.1 says how, and section 5 gives each topic its puzzle, its incident with a source, and what may be copied in.
- **Checkpoint 4 has three parts:** the threat model of a checkout with its PCI DSS scope (plain lab), the staff sign-in that fails in three ways (identity lab), and a new part 3, the leak (in `prove.more`). The compliance topic gains a sixth skill, `pci-scope`, and the federation topic teaches clocks, because the checkpoint asks for both.
- **Time:** 3,310 minutes of topics and 240 of checkpoint, about 59 hours. Labs CI grows by about 66 labs and about 3.5 hours of container time a full run (section 9).

## 2. Topic order and real prerequisites

| # | Id | Title | `prerequisites:` | Skills | Minutes | Base |
| --- | --- | --- | --- | --- | --- | --- |
| 39 | `csa.sec.threat-modeling` | Threat modeling | `csa.m3.checkpoint` | `draw-the-system`, `stride`, `rank-risks`, `respond-to-risk`, `attack-trees`, `attack-and-abuse` | 300 | `tm` |
| 40 | `csa.sec.authn-authz` | Authentication and authorization | `csa.m3.checkpoint` | `authn-or-authz`, `access-models`, `least-privilege`, `separation-of-duties`, `cloud-policy-models` | 290 | `policy` |
| 41 | `csa.sec.crypto` | Applied cryptography | `csa.sec.authn-authz` | `choose-the-primitive`, `hash-mac-signature`, `authenticated-encryption`, `envelope-encryption`, `key-strength` | 305 | `vault` |
| 42 | `csa.sec.pki` | Certificates and PKI | `csa.sec.crypto` | `run-a-ca`, `ca-hierarchy`, `revocation`, `ca-rotation`, `fix-chains` | 300 | `net` |
| 43 | `csa.sec.federation` | SAML, OAuth 2.0 and OIDC | `csa.sec.authn-authz`, `csa.sec.crypto` | `trace-oidc`, `trace-saml`, `choose-flow`, `validate-token`, `scim-provisioning` | 320 | `id` |
| 44 | `csa.sec.strong-auth` | Strong authentication and conditional access | `csa.sec.federation` | `phishing-resistance`, `authentication-strength`, `conditional-access`, `break-glass`, `rollout-without-lockout` | 300 | `id`, `policy` |
| 45 | `csa.sec.secrets` | Secrets | `csa.sec.crypto`, `csa.sec.federation` | `keep-secrets-out`, `scan-for-leaks`, `rotate-and-revoke`, `secret-zero`, `dynamic-secrets` | 310 | `vault` |
| 46 | `csa.sec.audit` | Audit logging | `csa.sec.crypto` | `what-to-log`, `retention`, `cloud-audit-trails`, `hash-chains`, `sealing-and-worm` | 295 | `pay` |
| 47 | `csa.sec.zero-trust` | Zero trust | `csa.sec.federation`, `csa.sec.strong-auth` | `zt-model`, `access-proxy`, `device-trust`, `micro-segmentation`, `continuous-verification` | 300 | `id` |
| 48 | `csa.sec.vulnerabilities` | Vulnerability management | `csa.sec.threat-modeling` | `scan-and-read`, `cvss-epss-kev`, `prioritise`, `patch-slas`, `remediate-and-track` | 290 | `pay` |
| 49 | `csa.sec.compliance` | Compliance basics | `csa.sec.audit`, `csa.sec.vulnerabilities` | `framework-landscape`, `read-a-control`, `control-to-evidence`, `crosswalks`, `gaps-and-exceptions`, **`pci-scope`** | 300 | `pay` |
| | `csa.m4.checkpoint` | Checkpoint 4: the threat model, the broken sign-in and the leak | all eleven | (draws on all) | 240 | `tm`, `id`, `vault` |

Changes from the designers' lists: strong authentication gains `csa.sec.federation` and drops `csa.sec.authn-authz` (reached through it). Nothing else changes. Module 2 is not a prerequisite of anything here: Kerberos's five-minute rule and Active Directory are "if you took Module 2" asides.

Every topic's generated outline says 240 minutes and the checkpoint's 480; no count supports either.

## 3. Rules every Module 4 item follows

Module 3's rules (its brief, section 3) stand: measured multiple choice, debug prompts, estimates, fixtures, the restart trial, fixes that last. These add to them.

### 3.1 Lessons: what ADR-0025, 0026, 0028 and 0031 ask of each topic

The eleven briefs predate these decisions. They plan a short lesson (2,100 to 3,000 words) "around" 26 to 81 minutes of assigned reading. That shape is gone. For every topic:

1. **The lesson teaches everything the items ask, in its own words.** Each brief's "Lesson plan" lists its ideas in order with what each resource was to carry; the lesson now carries all of it. Expect 3,500 to 4,500 words, shown in parts cut at its questions.
2. **`resources[0]` is brought into the page where its licence allows** (`tools/import_reading.py`, licences on the list in `tools/reading_html.py`: Creative Commons BY, BY-SA, BY-NC, BY-NC-SA, BSD, MIT, Apache, the GPL family, US government work). Section 5 names each topic's reading and whether it can be copied. A copied reading is the assigned part only (`--from`, `--to`).
3. **Everything else is `optional: true`** ("Go deeper"), left out of `estimated_minutes`, and the lesson says what each adds. This covers every RFC (the IETF Trust's licence is not on the list), AWS's documentation (© Amazon on the page), MITRE ATT&CK (its own terms), Microsoft Learn's training modules (terms of use), Schneier's essay, Smallstep's blog, LWN, jwt.io, Okta's guide, the UK NCSC (Open Government Licence), FIRST, OpenBao's docs (MPL-2.0) and the PCI SSC library. The writer reads each page's own licence on the day and records it; "copyable" below is a claim to confirm, not a fact.
4. **No video is assigned anywhere in the module:** no designer watched one. A writer who finds one checks YouTube's oEmbed answer and watches it first.
5. **One `<Puzzle>`** opens each lesson (section 5 gives a draft; 50 words, answer 150, no term the lesson hasn't taught).
6. **One `<Story>`** per lesson, from the source in section 5, read by the writer before writing, at most 200 words, in our own words. Where section 5 says "not read by the critic", the writer reads the primary document or chooses another incident and records why.
7. **Five to eight `<Check>` items** per lesson, one after each big idea, taken from the brief's practice recall items that test a single paragraph. Items that join ideas stay on the ladder. A placed item stays in `practice:`.
8. **A `glossary.yaml`** per topic. A term may be defined in one topic only, across all content, so section 3.5 names each shared term's owner.
9. **Typed items** (ADR-0027) where the skill is remembering a command or a name the learner will type for years: `openssl verify -crl_check_all`, `bao kv get`, `gitleaks detect`, `journalctl --verify`, a STRIDE letter's property, a verify code's meaning. Two or three a topic, in place of multiple choice, which also eases the "right answer longest" count.

### 3.2 Debug prompts

Purpose, symptoms, the number of faults, the rules of the fix; never what or where. Corrections to the briefs' prompts are in each topic's section (threat modeling, cryptography, secrets, compliance, zero trust). The spec's own Checkpoint 4 text names part 2's three faults; section 12 removes them.

### 3.3 Checks

- **Allowlists, not denylists, where a check must read a configuration.** "No `jwk`, `pem` or `pubkey` line" becomes "the only verify line is `jwks_uri` with the realm's HTTPS address".
- **Never file times.** Docker Desktop and a fresh CI checkout disagree about them. "Written after the fix" is proved by comparing content with a fresh run.
- **A range, not a floor, for a limit the prompt says must stay** (audit's rate limit).
- **Read every included file** when a setting can live in more than one (`apachectl -t -D DUMP_INCLUDES`, `systemd-analyze cat-config`).
- **A check that makes people or devices at the identity provider removes them in an `EXIT` trap** and never runs `kc_saved` while they exist.
- **Random values a check passes to a command go after `=`** (`--nonce="$n"`), and are hex: a random value that began with `-` failed one right answer in four parallel runs (the base's finding).
- **Pins.** Every download from outside Ubuntu's archive is the newest release at least two weeks old on the day its base is built, by version and sha256, recorded in the base's README. Module 4 has six: Keycloak, OpenBao, the Cedar CLI, OSV-Scanner, the ComplianceAsCode data stream and oauth2-proxy. (Each brief calls its own "the second after step-ca".)

### 3.4 Names used by every identity lab

Machine `idp`, Keycloak at **`https://login.shop.test`** (port 443), realm `shop`. The business is the shop of Modules 1 to 3 in every topic: zero trust's `corp.test` becomes `shop.test` (`apps.shop.test`). `office` is a staff laptop and `signin` its browser. People: `ana` (staff), `ben` (warehouse), and whoever a lab adds. A checkpoint's unfamiliarity comes from its machines and story, not from another name for the provider.

### 3.5 Terms: who defines what

| Term | Defined in (and in its `glossary.yaml`) |
| --- | --- |
| threat, trust boundary, STRIDE, risk, likelihood, impact, residual risk, control, attack tree, ATT&CK, abuse case, webhook, shared responsibility | `csa.sec.threat-modeling`. It gives MFA, authentication, authorization and signing secret one plain sentence each, with no glossary entry |
| identity, principal, credential, factor, MFA, session, token, claim, policy, default deny, least privilege, separation of duties, RBAC, ABAC, policy as code, **policy decision point, policy enforcement point**, workload identity (one sentence), `401` and `403` | `csa.sec.authn-authz`. Zero trust adds the policy engine and policy administrator and uses these |
| plaintext, ciphertext, AEAD, nonce, **hash**, **MAC, HMAC**, **signature** (in full), salt, KMS, HSM, data key, envelope encryption, key version, OpenBao and its words | `csa.sec.crypto`. Modules 1 to 3 have no glossary entry for hash, signature or HMAC (searched 2026-11-22); `csa.net.ipsec`'s lesson names HMAC, so the lesson says "you met the word in IPsec" |
| CA database, offline root, issuing CA, name constraints, **CRL**, CRL distribution point, AIA, soft and hard fail, cross-signing, systemd timer, **relying party** (anything that relies on someone else's statement about identity: a certificate here, a token later) | `csa.sec.pki`. No Module 3 file mentions a CRL (searched), so this topic introduces it; OCSP and stapling are `csa.net.http-tls`'s |
| federation, identity provider, single sign-on, front and back channel, redirect URI, OAuth's roles, grant, access, refresh and ID token, bearer token, PKCE, state, JWT, JWKS, `kid`, leeway, SAML's words, SCIM's words, realm, client, **drift**, **where a machine's time comes from (NTP, a time server, time sync)** | `csa.sec.federation`. It also owns the identity-lab onboarding (section 5) |
| phishing, adversary in the middle, TOTP, FIDO2, WebAuthn, passkey, origin, AAL, authentication strength, conditional access, report-only, break-glass account | `csa.sec.strong-auth` |
| secret, secret sprawl, git's minimum, build secret, scanner rule, rotation, secret zero, AppRole, seal, dynamic secret, lease | `csa.sec.secrets` |
| audit trail, actor, retention, tamper-evident, hash chain, WORM, legal hold, forward-secure sealing | `csa.sec.audit` |
| zero trust, policy engine, policy administrator, access proxy, ZTNA, device posture, micro-segmentation, lateral movement, exposure window | `csa.sec.zero-trust` |
| vulnerability, exploit, CVE, advisory, backport, CVSS, EPSS, KEV, SSVC, SLA, **exception, compensating control**, MTTR | `csa.sec.vulnerabilities` (`csa.linux.hardening` used "compensating control" in an item; if its glossary has it, use that one) |
| framework, control objective, parameter, evidence, attestation, crosswalk, **cardholder data environment, PCI DSS scope** | `csa.sec.compliance` |

Conditional sentences in the briefs are settled by this table: crypto defines HMAC (federation doesn't); federation defines the claims (secrets doesn't); vulnerabilities defines vulnerability and exploit (threat modeling doesn't); audit says "secret" and "token" in plain words, because secrets is not its prerequisite.

## 4. The lab bases, final

### 4.1 `content/lab-bases/id/` (`lab-base-id`, `FROM lab-base-net`)

[identity-lab-base.md](identity-lab-base.md) stands (Keycloak 26.8.2 pinned, the realm file as the configuration, `realm-apply`, `realm-saved`, `signin`, `jwt`, `idlab`, the software security key, `stock-api`, `cache=local`, one Keycloak per lab) with these decisions on its section 13 and on what the checkpoint found.

| # | The mismatch | Decision |
| --- | --- | --- |
| 1 | `kc_saved` takes a realm, not a machine | The base's: `kc_saved shop`. Every brief's `kc_saved idp` changes |
| 2 | `keycloak-apply` against `realm-apply` | `sudo realm-apply`, or `sudo systemctl reload keycloak@idp`. A reload always rebuilds; a boot rebuilds only when the file changed |
| 3 | Not built: approving a device code, `token-cases`, a SCIM token for a service client, mod_oauth2 | `signin --approve-device CODE USER` goes into the base. `token-cases` is the federation write lab's own, with a test. **The SCIM token is tried first** by the federation writer (the admin's own token got `401`); the fallback is the brief's 250-line SCIM stand-in. mod_oauth2 is installed and run on the base before a lab uses it |
| 4 | A check that adds a signing key of its own (federation's F4) | Dropped; no ADR line. Labs start with two real keys (`idlab key shop 2025 passive`, `idlab key shop 2026`). "The API gets its keys by URL" stays a reading check, written as an allowlist (3.3). Known limit, recorded |
| 5 | `realm-apply` rebuilds the realm | Accepted. What was made at run time and is not in the file goes at an apply (a registered key, SCIM-made accounts, sessions). The two labs it touches order their steps so nothing is applied afterwards, and say so |
| 6 | Where people's keys live | `/etc/idlab/keys/USER.key`, `/etc/idlab/otp/USER` |
| 7 | Not built: `kc-flows`, a throwaway person with a code or a key, the AMR mapper, `signin-watch`, the relay, `ca-whatif` | `kc-flows` and `idp-user add ... --otp|--key` go into the base. The AMR mapper goes into the base's starting realm. `signin-watch`, `relay@phish` and `attacker-replay` are strong authentication's own scenery. `ca-whatif` has one source in `content/lab-bases/policy/bin/`, a byte-identical copy in the `id` base, and a test in `tools/tests/` that fails when they differ |
| 8 | `signin` doesn't print claims | `signin --code ... \| jwt show` |
| 9 | Plain HTTP issuer in one prototype | HTTPS from the lab's CA everywhere |
| 10 | Unit ordering assumes the provider's machine is `idp` | Always `idp` |
| 11 | Three host names | `login.shop.test`, port 443 (3.4). Checkpoint part 2's `idp.shop.test:8443` and federation's `idp.shop.test` change |
| 12 | Two bases called `lab-base-sec` | `vault` and `pay` (4.2, 4.3) |
| 13 | `jq` in the image | Yes, for learners. Module 1 already has a lab that runs it (`csa.linux.shell/write-jq-answers`), so it is not new. Checks read JSON with `python3`; `predict_shell` items never use it |
| 14 | Checkpoint part 2 was designed without the base | It ran on the earlier image. Its helper names move to this base's (`idlab cert`, `idlab secret`), and its contract is run again on the final base before it is written |

**Added to the base from the earlier image** (read by the critic inside `lab-base-idproto`):

- **`timesync@M` is a small SNTP client** (106 lines of Python) that reads the `server` lines of the machine's `/etc/chrony/chrony.conf`, asks the first that answers, and steps the machine's clock (libfaketime's offset). Its journal says which server it asked and by how much it stepped. Today's design, where starting the unit sets the clock right by itself, has no cause to find; this one has (a server name that no longer resolves).
- **`chrony@M`**, real `chronyd` as a time server, with `-x` (never set a clock) fixed in the unit's `ExecStart`, never left to the lab's configuration.
- **A guarded `date`** on the lab machine that refuses `-s`: a privileged container's clock is the clock of Docker's whole machine.
- Kept from today's design: `/etc/clock/hwclock` (sealed scenery), `machine-clocks.service`, `on M clock`.
- **Which way to skew** is the lab's choice, and the README gives both with their evidence: ahead by more than the token's life (the site sees `exp` passed: `JWT expired 180 seconds ago`), or behind by more than 600 s (mod_auth_openidc's default slack: `issued more than 600 seconds in the future`). Federation's worked example uses the first, checkpoint part 2 the second.

**The API.** `stock-api` where the API is scenery (strong authentication, zero trust, federation's worked example). **mod_oauth2** where the learner builds or repairs the API (federation's build and debug, checkpoint part 2). Its finding goes in the README and federation's lesson: it answers a token it has already accepted from its cache a little past the token's expiry, so an expiry check shows a token the API has never seen.

**Still to build or try before any topic depends on it** (each is small; the owner of each is the first writer who needs it): a sign-in flow that requires a key by role, written in a realm file; the `amr` claim; SAML's NameID as the user name and metadata written at build; `signin` through oauth2-proxy and the size of its cookie; Keycloak's sign-in events in the journal as `signin-watch` reads them; a page on a second host asking for a key (the relay).

### 4.2 `content/lab-bases/vault/` (`lab-base-vault`)

The cryptography brief's section 10 (OpenBao 2.7.x from its pinned `.deb`, PostgreSQL 16, git, gitleaks 8.16 from Ubuntu's universe, age, podman with `vfs` storage, first-boot units, `gcm`, `checklib-sec.sh`), with the secrets brief's three helpers. Single-machine systemd. OpenBao and PostgreSQL are disabled until a lab enables them, which is what lets **checkpoint part 3** start from this base with neither running. Cryptography owns OpenBao's first words; secrets builds on them.

### 4.3 `content/lab-bases/pay/` (`lab-base-pay`)

[lab-base-sec.md](lab-base-sec.md) as written (the payments server: the release-pocket package pins and the local patch repository, OSV-Scanner with seven frozen records, the EPSS, KEV and SSVC extracts, OpenSCAP with the ComplianceAsCode data stream and `refs.tsv`, the journald plumbing for sealing), renamed. Build it **once as one Dockerfile** before any lab: its four layers were only ever built as two separate probes. The EPSS extract ships with attribution (FIRST states no licence; section 10).

### 4.4 `content/lab-bases/policy/` and `content/lab-bases/tm/`

Both are plain bases (Module 3's plain `RUN` line byte for byte, then one layer). `policy`: the Cedar CLI, `ask`, `access-review`, `ca-whatif`, `checklib.py`. `tm`: **`tm-check`**, the threat-model checker, its one home, with a test in `tools/tests/` that runs a reference model and its wrong models.

`tm-check` starts from the checkpoint designer's re-implementation (`prototypes/checkpoint/tm/tm-check`): the threat-modeling designer's own is not on disk. It has the topic's parts and the three additions the checkpoint needs, all accepted: the `scope ELEMENT cde|impacting|out reason` line and the `scope` part; three more control kinds (`secret-store`, `separation-of-duties`, `patch`); a reference that can narrow a weakness's allowed controls, with `controls --only N`. Topic 39's labs never write a `scope` line, so they are unaffected.

### 4.5 Kernel and runner needs

All seen on Docker Desktop 29.8.2 on the owner's PC. **Nothing in Module 4 has run on a GitHub runner.** The spike (P4) settles each row.

| Need | Who | Docker Desktop | Runner |
| --- | --- | --- | --- |
| Keycloak's boot with four labs on four CPUs | every identity lab | 9.5 s alone on the final base; 16 s, 55 s (one CPU), 140 s (half) on the earlier image | **untried; the main risk** |
| `net.ipv4.ip_unprivileged_port_start` set inside a namespace | `keycloak@idp` | works | untried |
| libfaketime's shared memory (`/dev/shm`) and preload | clocks | works for Apache, Python, `date`; not Go (oauth2-proxy) | untried |
| journald namespaces and sealing in a privileged container | audit, compliance | works with `KillSignal=SIGKILL` | untried |
| `oscap` (crashed once in five full-profile runs) | compliance | named rules only, one retry | untried; run three times |
| podman with `vfs` storage inside the lab container | secrets | works | untried |
| A machine with no cable (`machine root`, no `link` or `lan`) | PKI's offline root | **works as the base is** (critic, 2026-11-22: booted in 2 s, `lo` only, `netlab verify` says `verified`) | expected |
| Disk: the `id` image is 1.34 GB as Docker reports it | identity shards | fine | 14 GB a runner; watch a shard that holds four bases |

## 5. The topics

Each line "Lesson" gives: the draft puzzle; the incident for the story with its source and whether the critic read it; `resources[0]` and whether it can be copied in.

### `csa.sec.threat-modeling` (designer: [csa.sec.threat-modeling.md](csa.sec.threat-modeling.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `tm` base (five plain labs).
- **Prototype lost.** The brief's 72-second contract and 200-seed fuzz were run from `prototypes/tm-zt/`, which is not on disk. The writer rebuilds the build's reference and its 16 wrong models, and the write lab's generator, against the shared `tm-check`, and runs both again before the lesson.
- **Debug prompt:** "the board says a flow from another company was never reviewed" says where a fault is. It becomes "the security board's own reviewer says the review is incomplete, though the review-gap tool reports nothing missing".
- **`est-how-many-high`:** rewritten with four pairs so its `given` is short (the brief's own fallback).
- **Lesson.** Puzzle: "A shop's site uses HTTPS everywhere. A stranger who never logs in still cancels other customers' deliveries. How?" (a callback that takes any caller). Story: Target, 2013, a supplier's stolen credentials crossing into the network that held the tills. Source: Krebs on Security, "Target Hackers Broke in Via HVAC Company", https://krebsonsecurity.com/2014/02/target-hackers-broke-in-via-hvac-company/ (confirmed through search summaries on 2026-11-22; the page itself and the US Senate Commerce Committee's report were **not read by the critic**: its PDF did not yield text). `resources[0]`: OWASP's Threat Modeling Cheat Sheet, CC BY-SA 4.0, **copy in**. The Manifesto (CC BY 4.0) may be copied as a second reading. Optional: OWASP's risk rating, Schneier's "Attack Trees", ATT&CK's pages, Microsoft Learn.
- **Facts re-read by the critic:** ATT&CK v20.1 since 13 October 2026, v19.2 from 28 April, v18.1 from 28 October 2025; Schneier's $20,000, $80,000 and $60,000. Both as the brief says.
- **Minutes:** 300. **CI:** about 4.

### `csa.sec.authn-authz` (designer: [csa.sec.authn-authz.md](csa.sec.authn-authz.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `policy` base, with the designer's trims (`mcq-analyzer-by-cloud`, `mcq-gcp-deny-first` review-only).
- **Owns PDP and PEP** for the module (3.5), and `401` against `403`.
- **`est-unused-count`:** a constructed number, labelled so. It must not depend on a count read from Google's role reference on the day.
- **Fact not confirmed:** F23 (Entra Permissions Management's end of sale) was read from search summaries; the writer opens both posts or drops the dates.
- **Lesson.** Puzzle: "An API answers one caller `401 Unauthorized` and another `403 Forbidden`. Which of the two does it know?" Story: Capital One, 2019: a firewall's own cloud role could list and read the bank's storage. Source for what is confirmed: the OCC's release of 6 August 2020, https://www.occ.gov/news-issuances/news-releases/2020/nr-occ-2020-101.html (read 2026-11-22: an $80 million penalty for failing to set up effective risk assessment before moving to the public cloud). **The mechanism was not read by the critic** (the Justice Department's pages returned no text): the writer reads the court record or the department's release for the role's permissions before telling that part, or tells only what the OCC says. `resources[0]`: OWASP's Authorization Cheat Sheet, CC BY-SA 4.0, **copy in** (the introduction and first five recommendations). Cedar's docs (Apache-2.0), Azure's RBAC overview and Google's IAM overview (CC BY 4.0 as recorded; confirm) may be copied; AWS's pages are optional links.
- **Fact re-read:** IAM Access Analyzer's $0.20, $0.0020 and $9.00: as the brief says.
- **Minutes:** 290. **CI:** about 4.

### `csa.sec.crypto` (designer: [csa.sec.crypto.md](csa.sec.crypto.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `vault` base. It writes the module's glossary entries for hash, MAC, HMAC and signature.
- **Debug prompt:** "Since last night's key rotation it reports that it can't" names the cause of a fault. It becomes "Since last night it reports that it can't".
- **Prototype lost** (`prototypes/cps/`): the kept contract is rebuilt and run before the lesson.
- **Lesson.** Puzzle: "A payment file is encrypted with AES, and an attacker who can't read a byte of it changes PAY 100 into PAY 900. How?" Story: Adobe, 2013: passwords encrypted (not hashed) in a mode that made equal passwords look equal, beside readable hints. Source: the Australian Information Commissioner's investigation report, https://www.oaic.gov.au/privacy/privacy-assessments-and-decisions/privacy-decisions/investigation-reports/adobe-systems-software-ireland-ltd-own-motion-investigation-report , with CSO Online's "Adobe confirms stolen passwords were encrypted, not hashed" (both found by search on 2026-11-22; **neither page was opened**). `resources[0]`: as the brief's table has it; Nakov's book is MIT by its repository (confirm), which would make it copyable; NIST's publications are US government work.
- **Fact re-read:** NIST IR 8547 is final, October 2026 (its landing page; the 2030 and 2035 dates are in the document, which the writer opens).
- **Minutes:** 305. **CI:** about 13.

### `csa.sec.pki` (designer: [csa.sec.pki.md](csa.sec.pki.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the network base, no topic layer.
- **The split with Module 3 holds,** with two corrections from reading Module 3 as written. No Module 3 file mentions a CRL, so "topic 31 names a CRL in a sentence" is wrong and the lesson introduces the word. `csa.net.certificates`'s lesson teaches verify codes 10, 20, 21 and 62; the writer checks whether 18 and 19 are in its items before calling them retrieval. Confirmed as the brief says: `pathlen` is in `csa.net.certificates`; OCSP and an `ocsp-responder@` unit are in `csa.net.http-tls`'s labs; no earlier lesson teaches a systemd timer except as scenery, so this topic teaches it.
- **The offline root needs no base change** (4.5).
- **Lesson.** Puzzle: "A partner's certificate was revoked on Monday. On Friday the API still accepts it, and nothing is broken. Why?" Story: the expiry of the root DST Root CA X3 on 30 September 2021: old devices that never learned the new root stopped trusting sites, and a cross-signature kept old Android phones working. Source: Let's Encrypt, "DST Root CA X3 Expiration (September 2021)", https://letsencrypt.org/docs/dst-root-ca-x3-expiration-september-2021/ (**read by the critic**). `resources[0]`: the OpenSSL PKI Tutorial; its licence was not recorded where the critic read, so link it as optional unless the writer finds a licence on the list. Smallstep's article is an optional link. **This lesson carries the topic by itself.**
- **Fact re-read:** AWS Private CA's $400 and $50 a month and $0.75: as the brief says.
- **Minutes:** 300. **CI:** about 15.

### `csa.sec.federation` (designer: [csa.sec.federation.md](csa.sec.federation.md))

- **Skills, prerequisites, proofs, review pool:** as designed, on the `id` base, with section 4.1's names (`login.shop.test`, `realm-apply`, `kc_saved shop`).
- **Owns the identity-lab onboarding:** a "Before your first identity lab" note in `example-`'s prompt (what `signin` is, shown with `-v` beside the same flow by hand with `curl`; the realm file, `realm-apply`, `realm-saved` and the word drift; that a laptop needs about 0.8 GB of memory and 1.4 GB of disk).
- **Adds clocks,** because Checkpoint 4 part 2 needs them and no earlier lesson has NTP, chrony or time sync (searched; Module 2's Kerberos rule is not a prerequisite): two paragraphs (a token's times are read against the reader's clock; a machine's time comes from a time server through time sync, and how to see that it is wrong), one worked-example step (`on app clock`, `systemctl status timesync@app`, the two logs disagreeing), two come-back questions under `validate-token`, and one sentence that the lab's time sync is a stand-in because every machine shares one real clock. About 10 minutes.
- **`jq`:** the brief says this topic is the first to have the learner run it. It isn't (`csa.linux.shell/write-jq-answers`); the lesson retrieves it.
- **mod_oauth2** for the build's and debug's API; `api-keys-by-url` as an allowlist (3.3); the expiry check shows a token the API has not seen (4.1).
- **Trims,** to hold 320 minutes and the CI time: jwt.io optional; the debug's three `two-of-three` scripts become one; the worked example keeps two wrong fixes.
- **Lesson.** Puzzle: "You sign in to an app with your company account, and the app never sees your password. What does it get instead?" Story: Storm-0558, 2023: a stolen signing key for consumer accounts made tokens that the enterprise mail service accepted, because the service checked the signature and not which issuer the key was for. Source: Microsoft, "Results of Major Technical Investigations for Storm-0558 Key Acquisition" (6 September 2023), https://www.microsoft.com/en-us/msrc/blog/2023/09/results-of-major-technical-investigations-for-storm-0558-key-acquisition (**read by the critic**; the old `msrc.microsoft.com` address redirects). `resources[0]`: none can be copied (Okta, oauth.com, RFC 9700, jwt.io and OASIS are links); Keycloak's documentation is Apache-2.0 and may be copied for the client-registration part. **This lesson carries the topic by itself,** in parts, and is the module's longest.
- **Facts re-read:** RFC 9700 (January 2025, BCP 240): exact string matching, the implicit grant SHOULD NOT, the password grant MUST NOT; Keycloak 26.8.2 exists, released 5 November. As the briefs say.
- **Minutes:** 320. **CI:** about 25 once the boot is known (the brief's 38 assumed 30-second boots).

### `csa.sec.strong-auth` (designer: [csa.sec.strong-auth.md](csa.sec.strong-auth.md))

- **Skills, ladder, proofs, review pool:** as designed. **Prerequisites:** `csa.sec.federation`.
- **Its riskiest pieces were never run on the base, and are tried first:** a flow in a realm file that requires a security key by role; the `amr` mapper; the relay over HTTPS on a second host (`idlab cert phish login.shop-help.test`); `signin-watch` reading Keycloak's events; `ca-whatif --batch` and `--lint`. Its prototype (`prototypes/authn-strong/`) is not on disk.
- **A registered key is lost at the next `realm-apply`:** the worked example registers Bob's key after its last apply, and labs that need people with keys use `idlab seckey`.
- **`brute-force` check:** add behaviour to the reading (a throwaway person is locked after the stated number of failures).
- **No real Entra lab** and nothing for the owner queue's open list. The brief's note about a free Microsoft 365 developer tenant is kept for Module 10's plan.
- **Lesson.** Puzzle: "An admin types a password and a fresh six-digit code into a perfect copy of the sign-in page. Minutes later the attacker is signed in as the admin, though the code lasted 30 seconds. How?" Story: Cloudflare, July 2022: three employees typed their passwords into a phishing page, and the attackers still got nowhere, because every employee signs in with a security key bound to the real site. Source: Cloudflare, "The mechanics of a sophisticated phishing scam and how we stopped it" (9 August 2022), https://blog.cloudflare.com/2022-07-sms-phishing-attacks/ (**read by the critic**). `resources[0]`: as the brief's table; CISA's and NIST's pages are US government work and may be copied; Microsoft's and the FIDO Alliance's are confirmed on the day.
- **Fact re-read:** NIST SP 800-63B-4: verifiers "SHALL offer at least one phishing-resistant authentication option at AAL2"; "syncable authenticators SHALL NOT be used at AAL3". As the brief says.
- **Minutes:** 300. **CI:** about 22.

### `csa.sec.secrets` (designer: [csa.sec.secrets.md](csa.sec.secrets.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `vault` base, with its trims.
- **Debug prompt:** it says "three faults" and then describes their kinds, and its fix has a fourth step nobody counted (the current key leaked too). It becomes: purpose, the gateway's warning, "three faults", and the rule "a key that has leaked anywhere is no longer a secret".
- **`no-secret-zero-on-disk`:** the writer confirms the token format of the pinned OpenBao before matching it with a pattern.
- **Lesson.** Puzzle: "A key was committed by mistake and deleted in the next commit ten minutes later. Is it safe now?" Story: Uber, 2016: intruders used an access key an engineer had posted on a code-sharing site to reach cloud storage holding data on over 25 million people, and the company paid them $100,000. Source: the US Federal Trade Commission, "Uber Agrees to Expanded Settlement with FTC Related to Privacy, Security Claims" (12 April 2018), https://www.ftc.gov/news-events/news/press-releases/2018/04/uber-agrees-expanded-settlement-ftc-related-privacy-security-claims (**read by the critic**; it does not name the site). `resources[0]`: OWASP's Secrets Management Cheat Sheet, CC BY-SA 4.0, **copy in** the assigned sections. OpenBao's docs are optional links.
- **Fact re-read:** gitleaks in Ubuntu 24.04 is 8.16.0, in universe.
- **Minutes:** 310. **CI:** about 16.

### `csa.sec.audit` (designer: [csa.sec.audit.md](csa.sec.audit.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `pay` base. `auditd` stays on paper (a container can't run it).
- **`still-rate-limited`:** "above 0" passes a limit of a million. The prompt states the burst the trail must take (the settlement batch), and the check requires a burst at least that and at most ten times it.
- **Lesson.** Puzzle: "An intruder with root deletes the log lines that show the break-in. What kind of log would still give them away?" Story: the 2023 intrusion into US agencies' cloud mailboxes was found by one agency that noticed unusual `MailItemsAccessed` events in its audit log, a record that needed a paid logging tier. Source: CISA and the FBI, "Enhanced Monitoring to Detect APT Activity Targeting Outlook Online" (AA23-193A, 12 July 2023), https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-193a (**read by the critic**). It is the same incident as federation's story, seen from the log's side; the lesson says so in a sentence. `resources[0]`: OWASP's Logging Cheat Sheet, CC BY-SA 4.0, **copy in**. LWN and AWS are optional links.
- **Fact re-read:** CloudTrail's event history keeps 90 days of management events and no data events.
- **Minutes:** 295. **CI:** about 20.

### `csa.sec.zero-trust` (designer: [csa.sec.zero-trust.md](csa.sec.zero-trust.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `id` base with a topic layer (oauth2-proxy pinned; `ca-certificates`).
- **Everything here ran against a 200-line stand-in provider over plain HTTP, never Keycloak.** Before writing, in this order: `signin` through oauth2-proxy; the session cookie's size (Keycloak's three tokens are about 3 kB before encoding; nginx passes on only the first `Set-Cookie`): try `"fullScopeAllowed": false` and the fewest mappers, and if the cookie still splits, add Redis from Ubuntu's archive as the proxy's session store; refresh against a disabled person (tried on the base: refused); then the build's contract again. Its prototype (`prototypes/tm-zt/`) is not on disk.
- **Names:** `shop.test` (3.4). PDP and PEP are `csa.sec.authn-authz`'s; `401` against `403` is too (the brief credits HTTP semantics, which never taught them). Its item `mcq-401-or-403` shares an id and a question with that topic's: it becomes `mcq-proxy-401-or-403`, about the proxy's two answers.
- **Debug prompt:** "pulled salary data through payroll's phone-app API" says where. It becomes "a contractor's account pulled salary data". Check messages state end states only (the prototype's named a machine and a port).
- **Trims as designed** (eight wrong fixes in the build, one in the example).
- **Lesson.** Puzzle: "A stolen laptop joins the company VPN with a saved password. What can it reach?" Story: Colonial Pipeline, 2021: the way in was an old VPN profile nobody meant to be in use, protected by a password alone. Source: US Senate Homeland Security committee, "Portman Presses President and CEO of Colonial Pipeline on Gaps in Cybersecurity Practices" (8 June 2021), https://www.hsgac.senate.gov/media/reps/portman-presses-president-and-ceo-of-colonial-pipeline-on-gaps-in-cybersecurity-practices/ (**read by the critic**: "in the case of this particular legacy VPN, it did only have single-factor authentication"). `resources[0]`: NIST SP 800-207, US government work, **copy in** the assigned sections. CISA's maturity model may be copied; BeyondCorp's papers and the clouds' pages are optional links.
- **Fact re-read:** oauth2-proxy's newest releases are v7.15.6 (5 November) and v7.15.5 (1 October).
- **Minutes:** 300. **CI:** 25 accepted (the identity labs are this module's load balancing and IPsec).

### `csa.sec.vulnerabilities` (designer: [csa.sec.vulnerabilities.md](csa.sec.vulnerabilities.md))

- **Skills, prerequisites, ladder, proofs, review pool:** as designed, on the `pay` base. It defines vulnerability and exploit.
- **`date -d`** appears only in labs and the lesson, never in a `predict_shell` item (the content README rules `date` out of those).
- **Neither proof was built as a lab;** both contracts run before the lesson.
- **Lesson.** Puzzle: "A scan shows a critical 9.8 and a high 7.5. The team fixes the 7.5 first, and is right. Why?" Story: Equifax, 2017: a known flaw in a web framework stayed unpatched on one internet-facing system, and data on at least 145.5 million people was taken. Source: US Government Accountability Office, GAO-18-559 (30 August 2018), https://www.gao.gov/products/gao-18-559 (**the summary page was read by the critic**; the flaw's name, the patch alert that missed its owner and the expired certificate on the inspection device are in the report's PDF, which did not yield text: the writer reads it before telling those parts). `resources[0]`: CISA's KEV page and BOD 26-04, US government work, **copy in**. NCSC and FIRST are optional links.
- **Facts re-read:** BOD 26-04 was issued on 10 June 2026 with a table of 16 combinations; agencies follow its timelines from 7 December 2026 (a date that passes). OSV-Scanner v2.7.1 was released on 9 November 2026, three days before the base brief pinned it: the pin rule (3.3) applies.
- **Minutes:** 290. **CI:** about 15.

### `csa.sec.compliance` (designer: [csa.sec.compliance.md](csa.sec.compliance.md))

- **Prerequisites:** as designed. **Skills:** the five, plus **`pci-scope`**: what card data is; the cardholder data environment; in scope by storing, by connection and by impact; what segmentation does; what handing the card form to a provider changes and doesn't (the page around it, PCI DSS 6.4.3 and 11.6.1). A lesson section of about 300 words from PCI DSS v4.0.1 section 4 (the checkpoint brief's facts P1 to P9), one worked scoping of a small shop in the worked example, two practice items and three come-back questions (which of five systems are in scope; what moving the card form to the provider's frame changes; what one flat network does). Checkpoint part 1 checks it, and a proof must not teach.
- **Debug prompt:** "(two in the server, one in the pack)" says where. Removed.
- **`evidence-current`:** content compared with a fresh run; no file times (3.3).
- **PCI DSS's text** is never copied into a lab or a lesson; identifiers and short quotations only. The checkpoint designer read it from a college's copy because the PCI SSC library refused the fetch: the writer opens the official library.
- **Lesson.** Puzzle: "A company passes its security audit in the autumn and is breached before the year is out. Was the audit wrong?" Story: British Airways, 2018: a script on the airline's site sent customers' card details to an attacker for weeks, and the regulator's penalty in October 2020 was £20 million. Source: the UK Information Commissioner's penalty notice of 16 October 2020 (found by search at `ico.org.uk/media/action-weve-taken/mpns/2618421/ba-penalty-20201016.pdf`; **not read by the critic**: that address answered 404 to the tool and a mirror exists under `cy.ico.org.uk`). The writer opens the notice for the articles infringed and the number of customers. It is also the real case behind checkpoint part 1's third-party script. `resources[0]`: NIST's CSF 2.0 page and the four SP 800-53 controls, US government work, **copy in**.
- **Fact not confirmed:** the Defense Department's CMMC page refused the fetch; the phase dates are re-read on the day.
- **Minutes:** 300 (283, the scope section and its items, and the worked scoping). **CI:** about 19, after the spike's three `oscap` runs.

## 6. Checkpoint 4: the threat model, the broken sign-in and the leak (designer: [csa.m4.checkpoint.md](csa.m4.checkpoint.md))

**Prerequisites:** the eleven topics. **`estimated_minutes`: 240.** The proof block, objectives (no fault named), support and explain as designed.

**Part 1, `build-model-the-checkout`** (75 minutes, plain lab on `tm`): as designed and prototyped (a 64-line reference; each of 25 wrong models fails the part aimed at it). Decided:

- `in-pci-scope` tests `csa.sec.compliance/pci-scope`, which now exists.
- The `answered-*` check for the third-party script tests `csa.sec.threat-modeling/respond-to-risk` and `csa.sec.compliance/pci-scope` (PCI DSS 6.4.3 is taught there), not `csa.sec.vulnerabilities/scan-and-read`, which never covers someone else's script.
- Five checks with one description: the writer runs the validator; if it objects, "(1 of 5)" to "(5 of 5)".
- No piece with inputs made up at check time (the designer's question 3): three stories whose answers differ in every part, the reference outside the image and ADR-0012's fresh-version rule are what a judgement task can honestly have.
- Six weaknesses stay; if a timed run passes 75 minutes, the medium one goes first.

**Part 2, `debug-the-staff-sign-in`** (60 minutes, identity lab): the faults, checks and wrong fixes as designed and run (11 checks, 13 wrong fixes, 584 s), **on the final base**: `login.shop.test`, `kc_saved shop`, the base's helper names, mod_oauth2 from the base. Its clock fault uses section 4.1's time model, which is why that model is in the base. Its contract runs again on the final base before it is written. Add `public-client.sh` and `time-server-edited.sh`; drop `redirect-star.sh`. `no-extra-leeway` reads every included Apache file (3.3). `staff-sign-in` and `api-serves-staff` stop with "the check couldn't finish a sign-in" when the sign-in itself fails, so one fault doesn't bring back another skill.

**Part 3, `build-answer-the-leak`** (60 minutes, in `prove.more`, with `-clinic`): **accepted.** Without it no part makes the learner rotate a secret, revoke a certificate or read an audit trail, the hands-on skills of three topics. It is a systemd lab on the **`vault`** base (git, gitleaks, openssl and Python are there; OpenBao stays off). **It was never run.** It is prototyped before the checkpoint is written, in the designer's order of risk (the till refusing a revoked certificate; the pre-receive hook refusing a made-up key, with the provider's key format as a rule in the server's own configuration; rotation with two active keys). If it is too long for 60 minutes, step 5 (the exposure figures) goes first. If it cannot be made to keep its contract, the checkpoint ships with two parts and the spec's third line is not added.

**Time:** 75 + 60 + 60 + 20 = 215 minutes of work; `estimated_minutes: 240`.

## 7. Platform work, in order

| # | What | Smallest version | ADR | Blocks |
| --- | --- | --- | --- | --- |
| P0 | **The spec change** | Section 12's text, then `python -m uv run python tools/outline_cloud_track.py` | none | the outlines' order and the checkpoint's parts |
| P1 | **`labcheck` builds a base on a base** | In `build_base` (`tools/labcheck.py`): read the base's own `Dockerfile` with `base_named_in`; if it names a base, call `build_base` for that one first, refusing a base that names itself (about eight lines). The validator's "this base exists" check also reads each base's `Dockerfile`. Two tests (`id` builds `net` first; a missing parent is refused by name). Today `build_base` never looks inside a base's `Dockerfile`, so on a runner with no `lab-base-net` image the `id` build fails | **Fourth amendment to ADR-0018** (Proposed): a base may start from another base, which the checker builds first; a check may make people and devices of its own at a lab's identity provider and removes them; the module's six pinned downloads | every identity lab in CI |
| P2 | **Three edits to the network base** | `netlab` learns the services `keycloak`, `apache2`, `stock-api`, `timesync`, `chrony`; `lab-enter` gives a machine its own Apache log, state and cache folders, and preloads libfaketime for a machine that has `/etc/faketimerc` (inert for every other lab); the guarded `date`; one README line (a lab that downloads at build installs `ca-certificates` first). Changing the base reruns every Module 3 lab in Labs CI: read that run before merging | none | the `id` base |
| P3 | **The `id` base** | The prototype's `base/` as `content/lab-bases/id/`, with 4.1's decisions and additions; tests in `tools/tests/` (`jwtlib`'s verdicts, `kcapi`'s comparison, `signin`'s form reading against saved Keycloak pages, the `ca-whatif` copy) | the amendment above | federation, strong authentication, zero trust, checkpoint part 2 |
| P4 | **A CI spike** | One early pull request with the `id`, `vault` and `pay` bases and probe labs under a draft topic: the base's prototype lab four times over, checkpoint part 2 on the final base, a sealing probe, three `oscap` runs, an OpenBao first boot with a podman build and PostgreSQL. Read in the Labs job: Keycloak's boot with four at once, memory, each row of 4.5. Then put the seconds in `tools/lab-seconds.json` | none | every lab on those three bases |
| P5 | **The `vault`, `pay`, `policy` and `tm` bases** | As 4.2 to 4.4; `checklib.py`'s and `tm-check`'s tests | none | their topics |
| P6 | **An identity lab counts as two jobs** (only if P4 says so) | In `labcheck test --all --jobs N`, a lab whose base chain includes `id` takes two of the N places (a counted semaphore, about ten lines). Switch on when the spike's boot with four at once is over 45 s or a container is killed for memory. Raise the Labs shards from 8 to 10 when a shard passes 30 minutes | none | nothing unless the spike says so |
| P7 | **`content/README.md`** | "Identity labs" and "Threat-model labs" sections and the list of bases, each pointing at its base's README | none | writers |

**Not needed, so nobody builds it:** app work, a new item type, a memory budget or a longer boot wait in `labcheck` (the Keycloak unit counts as started only once the realm answers), an admin console for the learner, a real-cloud lab, a second identity provider, a headless browser for WebAuthn, the map's note on further parts (done for Checkpoint 3).

## 8. Writing waves

Every lab keeps its contract under `labcheck test`, restart trial included, before its lesson is written, and each batch gets a cold review. Section 3.5 is the contract that lets topics in one wave use each other's words.

| Wave | Topics | Waits on |
| --- | --- | --- |
| 0 | P0 to P5 | P3 waits on P1 and P2; P4 on P3 and P5's two systemd bases |
| 1 | `csa.sec.threat-modeling`, `csa.sec.authn-authz`, `csa.sec.crypto`, `csa.sec.audit`, `csa.sec.vulnerabilities` | their bases; a green spike for the last three. Cryptography owns OpenBao's words; threat modeling owns risk's |
| 2 | `csa.sec.pki`, `csa.sec.federation`, `csa.sec.secrets`, `csa.sec.compliance` | cryptography's lab patterns (secrets); audit's and vulnerabilities' built labs, which compliance's build uses as evidence; the `id` base and its backlog (federation, which owns the identity onboarding) |
| 3 | `csa.sec.strong-auth`, `csa.sec.zero-trust` | federation's onboarding and realm-file patterns; each one's untried pieces (section 5) run first |
| 4 | `csa.m4.checkpoint` | part 1: threat modeling and compliance's `pci-scope`; part 2: federation and the base's time model; part 3: secrets, PKI and audit, and its own prototype |

## 9. Cost and CI time

**Money: none.** No lab, proof or review touches a cloud account. Entra's conditional access (a P1 licence), AWS Private CA ($400 a month), Verified Access, the clouds' key services and analyzers are taught from dated documentation and priced in estimate items.

**Labs CI.** About 66 labs (eleven topics of five, the checkpoint's eleven), of which 13 boot Keycloak. Container minutes a full run, from the designers' measured and estimated contracts: threat modeling 4, authentication and authorization 4, cryptography 13, PKI 15, federation 25, strong authentication 22, secrets 16, audit 20, zero trust 25, vulnerabilities 15, compliance 19, checkpoint 30: **about 210 minutes, 3.5 hours,** on top of today's run, plus each shard's base builds (`id` about a minute after `net`; `pay` about two; `vault` about four, cold). The identity figures assume the boot the spike must confirm; at one CPU per lab they could double.

**Image sizes.** `id` 1.34 GB as Docker reports it (871 MB of files), `vault` about 570 MB, `pay` about 410 MB, `policy` about 250 MB, `tm` about 270 MB (mostly the layer every plain lab shares). A learner's laptop needs about 0.8 GB of memory for an identity lab.

## 10. Decided for the owner, and for the owner queue

**Decided under the owner's rule** (each goes under _Decided for you_ in `docs/owner-queue.md`):

1. **Strong authentication moves after SAML, OAuth and OIDC,** so tokens and the realm file are taught before a lab reads them. Free.
2. **Keycloak for every identity lab,** one provider met four times; pinned by checksum. Dex was tried and lacks SAML, SCIM, WebAuthn and flows.
3. **Five new lab bases** (`id`, `vault`, `pay`, `policy`, `tm`), and a base may start from another base (ADR-0018, fourth amendment, Proposed).
4. **Six pinned downloads from outside Ubuntu's archive** (Keycloak, OpenBao, Cedar, OSV-Scanner, the ComplianceAsCode data stream, oauth2-proxy), each the newest release at least two weeks old.
5. **The realm file is the configuration;** a change made only in the console is drift and fails a check.
6. **A machine's clock in a lab is a stand-in** (libfaketime and a small SNTP client), said once in the lesson, because a lab must never set the real clock.
7. **Checks may make and remove people and devices at the identity provider.**
8. **Cedar for policy as code here;** OPA's Rego waits for Module 18.
9. **OpenBao as the key and secrets service;** `openssl ca` as the CA; OSV-Scanner with seven frozen records, not Trivy or Grype; oauth2-proxy behind nginx for the access proxy.
10. **Checkpoint 4 has a third part, the leak,** if its prototype keeps its contract; its spec line no longer names part 2's faults.
11. **Compliance gains a sixth skill, PCI DSS scope; federation teaches clocks.**
12. **The EPSS extract ships with attribution** though FIRST states no licence; PCI DSS's, ISO's and the CIS Benchmarks' texts are never copied.
13. **No video is assigned in Module 4, and no real-cloud lab.**
14. **`auditd` is taught on paper** (a container can't run it); the sealing labs stop the audit journal "the way a crash does" because of a sealing fault in Ubuntu 24.04's systemd, said in the lesson.
15. **CI:** a spike first; an identity lab counts as two jobs only if the spike says so.

**For the owner queue's _Open_ list:** one housekeeping item, not a decision: earlier designers left images on the owner's Docker that the critic did not create and did not remove (`lab-base-idproto`, `lab-base-idnet`, `idlab-sso:dev`, `idlab-kcprobe` with two tags, and `lab-csa.idproto-proto-sso` and `lab-csa.idproto4-sso-a` to `-d`). The first held the only copy of the earlier base's time-sync client; the critic copied it, its two units, the guarded `date` and that base's helper library out to `prototypes/critic/earlier-base-time/`, so the images can go.

## 11. Look up again on the day of writing

- **The spike's answers** (4.5) before any lab that depends on a row.
- **Pins:** Keycloak (26.8.2 on 2026-11-05), OpenBao, the Cedar CLI (4.14.1 on 2026-11-02), OSV-Scanner (2.7.1 on 2026-11-09), ComplianceAsCode (0.1.82), oauth2-proxy (7.15.6 on 2026-11-05); Ubuntu 24.04's versions of gitleaks, mod_auth_openidc, mod_oauth2, libfaketime, OpenSCAP and systemd; whether systemd's sealing fault is fixed or reported.
- **Standards and catalogues that move:** ATT&CK's version and the technique IDs the items name; NIST IR 8547's dates in the document itself; SP 800-63B-4's wording; PCI DSS v4.0.1 from the official library, and SAQ A's 2025 change; BOD 26-04's table (cisa.gov) and its 7 December 2026 start; KEV's count; EPSS's model version; CMMC's phases; the CA/Browser Forum's short-lived certificate rule; FedRAMP's 2026 transition.
- **Cloud numbers:** IAM Access Analyzer's and AWS Private CA's prices; Entra's P1 and P2 split, mandatory MFA dates and Permissions Management's end; Google's role-recommendation tiers and 2-step verification phases; the clouds' audit-log defaults and KMS rotation rules; CloudTrail's 90 days.
- **Licences, on each page:** every resource section 5 calls copyable; Microsoft's two documentation repositories; Google Cloud's footer; the OpenSSL PKI Tutorial; Nakov's book; the lab packages' copyright files (the base brief's table was written from memory).
- **Incidents the critic did not read:** Target (the Senate report), Capital One's mechanism, Adobe (the regulator's report), Equifax's details (the GAO report's PDF), British Airways (the penalty notice).
- **Mechanisms nobody has run on the final bases:** section 4.1's last paragraph; zero trust against Keycloak; checkpoint part 2 on the final base and part 3 at all; the `pay` base as one Dockerfile; SCIM with a service client's token; the compliance build's password rules, test root login and tailoring check; the audit and vulnerability debugs as labs.
- **Dates that will pass:** BOD 26-04's 7 December 2026; certificate lifetimes of 100 days from 15 March 2027; Azure and Google MFA phases.

## 12. Replacement text for the spec

All in `docs/specs/cloud-solutions-architect.md`. After the change, run `python -m uv run python tools/outline_cloud_track.py`.

**12.1 The Module 4 table.** Rows 41 to 44 change order and number; every "You'll be able to…" cell but two is unchanged. In order, the eleven rows are: 39 Threat modeling, 40 Authentication and authorization, **41 Applied cryptography** (`csa.sec.crypto`), **42 Certificates and PKI** (`csa.sec.pki`), **43 SAML, OAuth 2.0 and OIDC** (`csa.sec.federation`), **44 Strong authentication and conditional access** (`csa.sec.strong-auth`), 45 Secrets, 46 Audit logging, 47 Zero trust, 48 Vulnerability management, 49 Compliance basics. Keep the column padding as the file has it. The two cells that change:

- `csa.sec.federation`: "trace a single sign-on and an OAuth flow; choose the right flow for an app: authorization code with PKCE, client credentials, or device code; validate a token, on machines whose clocks agree; provision accounts with SCIM"
- `csa.sec.compliance`: "read a control framework (SOC 2, ISO 27001, PCI DSS 4, HIPAA, FedRAMP, CMMC, GDPR, CIS Benchmarks, NIST CSF 2.0 and SP 800-53) and map a control to technical evidence; say which systems are in PCI DSS scope"

No later topic is renumbered: the module still has eleven rows.

**12.2 The checkpoint block** becomes:

```markdown
**Checkpoint 4: the threat model, the broken sign-in and the leak** (`csa.m4.checkpoint`).

1. Threat-model a web app that takes payments: its trust boundaries, its PCI DSS scope, its top risks and a control for each.
2. Fix a single sign-on, run locally with an open-source identity provider, that fails in three ways.
3. Answer a leak: find the secrets in a repository's history, rotate the key, revoke and replace the certificate, and read the audit trail for what the leaked key did.
```

If part 3's prototype fails (section 6), line 3 is left out and the title stays "the threat model and the broken sign-in". Either way line 2 stops naming the faults.

**12.3 The self-assessment table's** "Checkpoint 4" reference needs no change.

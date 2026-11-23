# Build notes: what building the lab bases found

The plan ([MODULE-4-BRIEF.md](MODULE-4-BRIEF.md)) was written before any base existed. Building them, on 2026-11-22, turned up things that differ from the briefs. **A topic's writer reads this file after the brief; where the two disagree about how a base behaves, this file and the base's own README win,** because they describe what was built and run.

Each base's README under `content/lab-bases/` is the reference for its helpers. This file only lists what a writer would otherwise get wrong.

## Every base

- **Format base scripts for Python 3.12, not the repository's 3.14.** The lab images run Ubuntu 24.04's Python 3.12. `ruff format` at the repository's target rewrote `except (A, B):` into a form 3.12 rejects, and every helper died at import. Scripts that run inside a lab are formatted with `--target-version py312`; a test parses them as 3.12.
- **`COPY --chmod=644 file /new/dir/file` makes the new directory 644 too,** so the learner can't enter it. Create the directory first.
- **A check whose test cases use fixed values lets a wrong answer pass.** A rule with fixed amounts let two wrong policies through; the cases now vary what the rule doesn't mention. Vary every input a rule is silent about.
- **Pins follow the two-week rule on the day of the build,** so some differ from the plan's versions (below).

## `vault` (keys and secrets)

- **Pinned:** OpenBao 2.7.2 (2.7.3 was three days old).
- **Image:** 885 MB, not the plan's "about 570": the plan's total left out the layers every lab shares.
- **Podman works as root only** (`sudo podman …`), with `vfs` storage and the host's network. A build step can reach `127.0.0.1`. Rootless podman fails (no `newuidmap`).
- **The `busybox` image is made at first boot** by a unit a lab enables, because `podman import` fails inside a Docker build.
- **`BAO_ADDR` comes from an `ENV` line and `/etc/environment`,** not a profile script: the checker's shells don't read profile scripts.
- **The learner's token lasts ten years** and can use only the token mount.
- **A planted secret is assembled from pieces** in the lab's seed script, so that no file in this public repository matches a secret scanner.
- **Untried:** key rotation and rewrap, AppRole, response wrapping, JWT sign-in, OpenBao Agent, gitleaks as a hook or with custom rules. A topic that uses one tries it first.

## `pay` (the payments server)

- **Pinned:** OSV-Scanner 2.7.0 (2.7.1 was 13 days old) and ComplianceAsCode 0.1.82. OSV-Scanner 2.7.0 finds nothing offline in Ubuntu's records as published (`Ubuntu:24.04:LTS`), so the build writes `Ubuntu:24.04` into the copies inside the scanner's zip. The committed records stay whole. Pinning 2.7.1 later would drop this workaround.
- **`oscap` can hang.** One whole-profile run in 28 hung for good. Named rules were fine 300 times in 300. The helper `oscap-rules` stops a run at 12 seconds and tries once more. **Labs run named rules, never the whole profile.**
- **An `openssh` upgrade restarts `sshd` by itself on this base.** The vulnerabilities brief's "the banner changes only after a restart" and its `ssh-not-restarted` wrong fixes do not hold. That debug needs a different service or a different trap.
- **`partition_for_tmp` reports "not applicable", not "fail".** The compliance build's one accepted exception needs another rule.
- **The audit service logs only to its own journal** (`LogNamespace=audit`), so its warnings are read with `journalctl --namespace audit -p warning`, not `journalctl -u shop-audit`.
- **The journal-sealing fault is still in Ubuntu 24.04's systemd** (255.4-1ubuntu8.19; upstream issue 17833 is open). The sealing labs stop the audit journal "the way a crash does", as the plan says.
- **Paths:** `/usr/share/lab-pay` and `/usr/local/lib/lab-pay` (the brief said `lab-sec`).
- **Added beyond the brief:** `sshd` runs from boot; `root-login` with a root key made at build; `base-intact`; a copy of the original package list.
- **Untried:** `auditd`'s refusal in a container (not run again), and the three topics' own labs, including the password-quality rules and the tailoring check.

## `policy` (access rules as code)

- **Pinned:** the Cedar command-line tool 4.14.1 (4.15.0 was six days old), for both `x86_64` and `aarch64`. Image 297 MB.
- **`ca-whatif`** (the conditional-access "what if" tool) models only `block`, `mfa`, `compliantDevice` and the three built-in authentication strengths by display name. It refuses any other control by name. It has not been run against a real Keycloak realm export.
- **`access-review`** counts its time window back from the log's newest line, not from now.

## `tm` (threat models)

- **`tm-check` with no reference runs six parts** (`reads`, `stride`, `ranking`, `controls`, `tree`, `abuse`), not the three the brief names: the worked example needs `controls`.
- **Added:** `controls --only rest` (for the checkpoint's "nothing left open" check); a reference model on standard input (`-`); a `none` line may not cover a letter the flow has a threat for; duplicate names are refused; an empty model fails every part.
- **The reference file's shapes** (`either`, `kept`, `no_none`) were designed by the builder, since the topic's prototype was lost. The base's README documents them.
- **Messages** give the line number and what was expected, in plain words. Keep it so when a lab adds a story.

## `id` (Keycloak)

- **Pinned:** Keycloak 26.8.2, by checksum.
- **Measured on the owner's PC** (the probe lab, full contract with the restart trial): 174 seconds alone on a quiet machine, 366 seconds each with four at once; Keycloak answers 8 to 13 seconds after boot alone, 20 to 24 seconds with four at once; about 620 MB of memory a lab. On a loaded machine a boot took up to 77 seconds. A GitHub runner has half this machine's processors, so the plan's step P6 (an identity lab counts as two of a machine's four jobs) is likely to be needed; the lab run decides.
- **Python's `time.sleep` fails under Ubuntu 24.04's libfaketime** (`OSError: [Errno 22]`) on a machine that has its own clock. The base's `timesync` runs outside libfaketime for that reason. **A lab's own Python on a machine with a shifted clock must not sleep;** the README says how to wait instead.
- **A realm is always the lab's own file.** There is no "starting realm" in the base, and no `amr` mapper: a sign-in shows `acr` and no `amr`. The strong-authentication topic's first writer adds the mapper, with the flow reference values it needs, and tries a flow written in a realm file before any lab depends on it.
- **`mod_oauth2` keeps serving a token it has already accepted after that token expires** (still `200` 46 seconds after a 20-second token ran out). A lab that teaches expiry at the API must not rely on it noticing. Two `Require` lines need `<RequireAll>`.
- **`jwtlib` checks RS256 signatures with Python's standard library,** so its tests need no extra package and no key in the repository.
- **`ca-whatif` lives in the policy base** with a byte-identical copy in this base's `bin/`. Change the policy base's and copy it over; a test fails if they differ.
- **`date -s` is refused** in every network-based lab: a lab must never set the real clock. Clocks are shifted per machine with `clock` (the README has it).
- **The probe topic holds one lab.** Nothing has yet run four identity labs at once on a GitHub runner.
- **Untried on the final base:** a flow in a realm file and `amr`; SAML's NameID and metadata made at build; a SCIM token for a service client; oauth2-proxy; the relay host for the phishing lab; Keycloak itself under a shifted clock; whether sign-in events appear without `eventsEnabled`. The topic that needs one tries it first.

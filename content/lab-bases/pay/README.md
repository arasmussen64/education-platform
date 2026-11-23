# The payments-server lab base

The labs of Audit logging, Vulnerability management and Compliance basics (the Cloud Solutions Architect track's Module 4) that boot a server start `FROM lab-base-pay`. This folder is that image: **the shop's payments server**, called `pay1` in the prompts, with an audit trail to seal, five packages to patch and a benchmark to be measured against. `tools/labcheck.py` builds it, tagged `lab-base-pay`, before it builds any lab whose `Dockerfile` says `FROM lab-base-pay` ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), third amendment). When nothing here has changed, Docker's cache makes that a second or two.

Read this before writing a lab on it. The plan behind it is `docs/plans/cloud-module-4/` (`MODULE-4-BRIEF.md`, section 4.3, and `lab-base-sec.md`, the designer's brief, which called the base `lab-base-sec`). It is one machine: these three topics are about one server and its evidence, so there is no `netlab`, no `on MACHINE` and no second machine. A lab with no server to boot (a hash-chain script, an SLA calculator) is a plain lab on Module 3's plain `RUN` line ([content/README.md](../../README.md), "Network labs"), not on this base.

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 1 | The systemd labs' first `RUN`, byte for byte | Shared with every systemd lab, so Docker builds it once. Change it only with all of them; a test compares it with the network base's. |
| 2 | From Ubuntu 24.04's archive: OpenSCAP 1.3.9 (`oscap`), `libpam-pwquality`, `linux-base`, `systemd-journal-remote`, and the story's packages **at the versions 24.04 was released with**: sudo 1.9.15p5-3ubuntu5, openssh 1:9.6p1-3ubuntu13, less 590-2ubuntu2, rsync 3.2.7-1ubuntu1, git 1:2.43.0-1ubuntu7. Then `/srv/patches`, a package repository holding the day's fixed versions of those five, which becomes the machine's **only** package source | The pins never drift (below). `linux-base` is there for the benchmark: without it most rules say `notapplicable` in a container. |
| 3 | Two downloads from outside the archive, each pinned by version and SHA-256: OSV-Scanner, and ComplianceAsCode's data stream for Ubuntu 24.04 | "Pins", below. |
| 4 | The frozen data, journald's settings, the shop, the helpers, and what is made from them at build (the scanner's database, `refs.tsv`, a copy of the package list, a throwaway root key, the checksums) | Small; rebuilt in a moment when one of these files changes. |

Not in it: `jq` (checks read JSON with `python3`), `auditd` (below), a second machine, and any way to install a package that isn't in `/srv/patches`. A topic that needs one more package can't `apt-get install` it after `FROM lab-base-pay`, because the archive's lists are gone: it adds the package to layer 2 here, for every lab on the base.

## A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { init: systemd, restart_trial: true }
├── Dockerfile         FROM lab-base-pay, then the lab's own story
├── checks.yaml  solution.sh  wrong/*.sh
```

```dockerfile
FROM lab-base-pay
COPY audit.conf /etc/shop/audit.conf
RUN mkdir -p /srv/auditors
```

Every lab on the base sets `restart_trial: true`: an audit trail, a patch and a hardening setting are all things a reboot must keep. `csa.sec.pay-probes`' one lab is the smallest example (a draft topic for the CI spike, which goes once the spike has been read).

## The shop: an audit writer and a way to make it do things

Scenery, in Python, about 250 lines with the table they share (`/usr/local/lib/shop/shop_events.py`).

- **`shop-cli EVENT [FIELD=VALUE...]`** makes the shop do something, as a customer or an admin would: `shop-cli refund order=42 amount=19.99`. A field that isn't given gets an everyday value (the person running it, `127.0.0.1`, a made-up password, session or token, new every time), as the shop itself would have one. `shop-cli events` lists the nine events and their fields; `shop-cli settle [COUNT] [FIELD=VALUE...]` is the nightly settlement batch, 1,500 refunds at once (0.05 s), numbered `order=settle-1` and up, or `order=X-1` and up when `order=X` is given. Anyone on the server may run it; no `sudo`.

  | Event | Fields |
  | --- | --- |
  | `login.ok`, `login.failed` | `user src outcome password session` |
  | `page.view`, `health.check` | `user src path` |
  | `role.change` | `actor user old new src outcome` |
  | `config.change` | `actor setting old new src outcome` |
  | `refund` | `actor order amount src outcome token` |
  | `export` | `actor table rows src outcome token` |
  | `card.update` | `user card src outcome` |

- **`shop-audit.service`** (`/usr/local/bin/shop-audit`, as the user `shop`) writes the audit trail: one line for each event that the policy says to record, with only the fields the policy names, in the policy's order. It never invents a field, and a value can't start a line of its own (a line break in a value is written `\n`, which is what stops log injection). Each line starts `time=` (UTC):

  ```text
  time=2026-11-23T00:11:55Z event=card.update user=ana card=************4242 src=127.0.0.1 outcome=ok
  ```

- **`/etc/shop/audit.conf`**, the audit policy. `audit EVENT FIELD...` records an event with those fields; `mask FIELD` writes only a field's last four characters. The image's copy audits sign-ins only (`audit login.ok user src outcome`); a lab ships its own. The writer reads it at start and at `sudo systemctl reload shop-audit`. A line it can't use is left out and reported once, as a warning: `audit.conf line 4: no such event "role.chnage"`.

The unit says `LogNamespace=audit`, so everything the writer prints goes to a journal of its own, the **`audit` journal namespace**, with its own journald (`systemd-journald@audit.service`), its own settings (`/etc/systemd/journald@audit.conf`, with `journald@audit.conf.d/` for drop-ins, which it does read: tried) and its own files (`/var/log/journal/<machine-id>.audit/`).

| To read | Command |
| --- | --- |
| the trail | `journalctl --namespace=audit -t shop-audit` (checks: `-o cat`, and keep the lines that start `time=`) |
| the writer's complaints about the policy | `journalctl --namespace=audit -u shop-audit -p warning` |
| the settings in force, drop-ins included | `systemd-analyze cat-config systemd/journald@audit.conf` |

Three things a writer should know. A unit with `LogNamespace=` has no other journal, so the policy warnings are in the audit namespace too, at warning priority (the designer's brief expected `journalctl -u shop-audit` in the default journal, which stays empty of them); `systemctl status shop-audit` shows only systemd's own lines. The namespace's journald writes a few lines of its own into it (`Journal started`), which is why the trail is read with `-t shop-audit`. And the image's `journald@audit.conf` says `Seal=no`, so that switching sealing on is something the learner does: journald's own default is `Seal=yes`, which seals as soon as keys exist.

## Sealing, and why this journal stops with a kill

Forward-secure sealing works in the namespace, and a lab can prove it with a tamper (below). Three findings shape it, all seen again on 2026-11-22 with systemd 255.4-1ubuntu8.19.

1. **A sealed journal that journald closes cleanly no longer verifies.** After a plain `systemctl restart` of a sealing journald, `journalctl --verify --verify-key=KEY` fails on the file it reopens with `Epoch sequence not continuous (13 vs 13)`, for good. After a **kill** journald finds the file unclean, starts a new one, and every seal in every file verifies: through three restarts and a `docker restart` here. systemd's issue [#17833](https://github.com/systemd/systemd/issues/17833) (open since 2020; a comment of 2026-11-14 describes this variant on systemd 262) is the report. So the base ships `/etc/systemd/system/systemd-journald@.service.d/50-lab-stop.conf`, `KillSignal=SIGKILL`: every restart of a namespace's journald is a kill. It is lab plumbing a real server shouldn't copy, and the lesson says in a sentence that the lab's audit journal stops "the way a crash does". A `docker restart` keeps the seals too (tried), so the restart trial does. Drop the file when a fixed systemd reaches 24.04: remove it, restart `systemd-journald@audit` twice with sealing on, and verify.
2. **The default journal is never sealed** (`Seal=no` in `/etc/systemd/journald.conf.d/10-lab.conf`): it is closed cleanly at every flush, so it would fail the same way. The same file sets `ReadKMsg=no`, because a privileged container reads the kernel log of Docker's whole machine and the journal would fill with other labs' messages.
3. **`journalctl --setup-keys` writes the sealing key to the default journal's folder** (`/var/log/journal/<machine-id>/fss`), and the `audit` journald loads it from there at its next start. So the learner's steps are: `sudo journalctl --setup-keys --interval=10s` (its last line is the verification key; piped, that key is all it prints on standard output), `Seal=yes` in `/etc/systemd/journald@audit.conf`, `sudo systemctl restart systemd-journald@audit`. The lab's 10 seconds stand for the default 15 minutes. `--setup-keys --force` makes new keys, and after the next restart the old verification key fails with `Tag failed verification`.

What a sealed file looks like to a check, through `seal-range` (below): `sealed FROM TO` for the real trail; `failed: Invalid hash ...` for a copy with bytes changed in place (`lab-flip`); `unsealed` for a copy rewritten entry by entry (`lab-forge-journal`), which verifies with every hash right and no validated range, because only the sealing key can make the seals. A seal covers a new entry within about 20 seconds at `--interval=10s`.

Each restart of the namespace's journald leaves an 8 MB file behind (journald sizes a new file at 8 MB), so a lab that restarts it in a loop fills the disk slowly; a contract's dozen containers don't notice.

**`auditd` can't run here.** The kernel allows audit control only from the first PID namespace, so `auditctl -s` in a container answers `Operation not permitted` (the designer's finding; not tried again). The audit topic teaches its rules on paper.

## Packages that never drift, and the patch repository

Ubuntu's release pocket keeps the versions 24.04 was released with for the life of the release, so layer 2's pins install today and in five years. `/srv/patches` holds whatever `noble-updates` had on the day the image was built (2026-11-22: sudo 1.9.15p5-3ubuntu5.24.04.4, openssh 1:9.6p1-3ubuntu13.20, less 590-2ubuntu2.1, rsync 3.2.7-1ubuntu1.5, git 1:2.43.0-1ubuntu7.4), always at or above every record's fixed version. A scan therefore finds the same seven vulnerabilities in the same five packages on every day, and a patch always clears them.

- `sudo apt-get update && sudo apt-get install --only-upgrade sudo` works offline, in about a second. Without `apt-get update` first, a fresh server has no package lists and apt installs nothing (a ready-made wrong fix).
- Nothing else can be installed, so no finding can be "fixed" from the internet and no check depends on the day's archive.
- **An upgrade restarts the service it upgrades.** Docker's image ships `/usr/sbin/policy-rc.d` to stop packages starting services; the base removes it, as the plan asked, so that the server behaves like a server. Tried: upgrading `openssh-server` restarts `ssh.service` by itself, and the banner on port 22 shows the new version at once (`SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.20`). **So "the old sshd keeps running until someone restarts it" does not happen on this base**, which the vulnerabilities brief's worked example and two of its wrong fixes assumed; that topic needs another carrier for "old code still running" (its debug's drop-in that runs a kept copy of the old binary is a candidate; untried). The upgrade also replaces an unedited `/etc/ssh/sshd_config` with the new package's.
- `/usr/share/lab-pay/original-dpkg-status` is the package list as the image was built, for checks that need the original findings after the learner has patched.

## The scanner and its frozen records

OSV-Scanner, offline, against seven Ubuntu advisories:

```text
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status
```

`--format vertical` is the one to read; it takes 0.1 s. `OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=/usr/share/lab-pay/advisories` is set for the learner's shell and for checks (the image's `ENV`) and for `sudo` (`/etc/environment`); offline mode reads `osv-scalibr/Ubuntu/all.zip` under it. The scanner exits 1 when it finds something. A package list under another name needs its kind said: `-L dpkg-status:/srv/inventory/batch-01/dpkg-status` (a bare path that isn't called `status` is refused: "could not determine extractor").

The seven: CVE-2025-32463 and CVE-2025-32462 (sudo), CVE-2024-6387 and CVE-2025-26465 (openssh), CVE-2024-32487 (less), CVE-2024-12084 (rsync), CVE-2025-48384 (git). The records are in `/usr/share/lab-pay/advisories/UBUNTU-CVE-*.json` as published; the zip is made from them at build (`lib/advisory-zip`), the same bytes every time.

**One change is made on the way into the zip.** The published records call the release `Ubuntu:24.04:LTS`. OSV-Scanner 2.7.0 reads a package list as `Ubuntu:24.04` and, offline, finds nothing in records that say otherwise (tried: "No issues found" from all seven as published; 2.7.1 finds them). So the zip's copies say `Ubuntu:24.04`, which both versions match. When the pin moves to 2.7.1 or later, `SHORTEN` in `advisory-zip` can go; the probe's scan check says at once if it can't.

Why not Trivy or Grype: neither can be given a small frozen database (the designer's brief, section 2). The lesson names them as the common choices.

Beside the records, in `/usr/share/lab-pay/` (`SOURCES.md` there, and [data/SOURCES.md](data/SOURCES.md) here, give each one's source, date and licence):

| File | What |
| --- | --- |
| `epss-2026-11-10.csv` | EPSS scores and percentiles of 2026-11-10 for the seven CVEs and 70 other real ones, with the file's `#model_version` line and header |
| `kev-2026.11.10.csv` | CISA's KEV catalog version 2026.11.10, seven columns, for the two of the seven that are in it (CVE-2025-32463, CVE-2025-48384) and 50 others |
| `ssvc.csv` | CISA's SSVC decision points: `cve,exploitation,automatable,technical_impact` |
| `nist-800-53r5/AC-6.txt`, `AC-7`, `AU-9`, `AU-11`, `IA-5`, `SI-2` | NIST's own text of six controls with their enhancements, parameters written `[Assignment: organization-defined ...]` |
| `examples/10-vendor.conf` | an SSH drop-in that says `PermitRootLogin yes` |

`snapshot.py`, in this folder, made the data files, and makes them again on the day an author wants a newer snapshot. The lessons quote these numbers (sudo's CVE-2025-32463: EPSS 0.563, added to KEV on 2025-09-29), so a new snapshot means reading the lessons again; a test pins the ones the plan quotes.

## The benchmark

OpenSCAP reads `/usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml`, ComplianceAsCode's data stream (Ubuntu's own `ssg-debderived` package has nothing for 24.04). The profile every lab uses is CIS Level 1 Server, 408 rules:

```text
sudo oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --rule xccdf_org.ssgproject.content_rule_sshd_disable_root_login \
  /usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml
```

- **Named rules only, in labs and in checks.** Three or four named rules take about a second. The whole profile takes 9 to 10 s and is not reliable on OpenSCAP 1.3.9: the designer saw one segmentation fault in five runs, and here one run in 28 **hung for good** (56 threads asleep, no CPU, in `file_groupownerships_var_log`); 300 runs of four named rules, and 100 of that rule alone, all finished (2026-11-22). `oscap-rules` stops a run after 12 seconds, or after a crash, and tries once more. A prompt that asks a learner for a whole-profile run should say what to do if it never ends.
- `oscap` exits 2 when a rule fails, and 1 when it is given a rule that doesn't exist.
- Its output puts a carriage return before each tab (`Rule\r\tNAME`). `awk -F'\t'` still reads it (the first field is `Rule\r`, the second the name), but a script that compares the first field with `Rule` exactly, or Python's text mode, doesn't.
- As the image stands the profile gives 220 `pass`, 112 `fail`, 76 `notapplicable`. `sshd_disable_root_login`, `accounts_password_pam_minlen` and `journald_storage` fail. **`partition_for_tmp` is `notapplicable`**, not `fail` as the compliance brief's exception expects: that build needs another rule for its one exception, or the brief's wording changed.
- `file_groupownerships_var_log` passes on a fresh image and fails once `journalctl --setup-keys` has made the `fss` file, so it is no rule to pin.

`/usr/share/lab-pay/refs.tsv` is the benchmark's own crosswalk, made at build by `lib/refs.py` from the data stream's references: `rule<TAB>framework<TAB>control`, 4,155 lines for the profile's rules, in six frameworks (`iso-27001-2013` 2,607, `nist-800-53r4` 603, `cis-ubuntu-24.04` 415, `pci-dss-4.0` 292, `hipaa` 164, `nist-800-171` 74). Note the `r4`: the mappings are to revision 4, the texts in `nist-800-53r5/` are revision 5. `sshd_disable_root_login` serves `nist-800-53r4 AC-6(2)`, `pci-dss-4.0 2.2.6` and `cis-ubuntu-24.04 5.1.20`; `pci-dss-4.0 8.3.6` has three rules; `grep -c 8.3 refs.tsv` says 44.

**Root over SSH.** The SSH server runs from boot (Ubuntu would start it at the first connection), with `RuntimeDirectoryPreserve=yes` so `sshd -t` always works. The image makes a throwaway key at build and authorises it for root, so a check can try a real login (`root-login`, below): a benchmark rule and `sshd -T` read the files, and a server that was never reloaded still has its old settings. As shipped, root gets in with it (`PermitRootLogin` is at its default, which allows keys).

## Check helpers

Checks run as root. These are in `/usr/local/lib/lab-pay/`, each a program that prints what a check compares; none changes the machine.

| Helper | Prints |
| --- | --- |
| `seal-range NAMESPACE KEY` | the verification of the namespace's newest journal file with a verification key: `sealed FROM TO` (UTC, as `2026-11-23T00:02:49Z`, so two compare as text and with `date -u +%FT%TZ`), `unsealed`, or `failed: MESSAGE`. Always exits 0 |
| `seal-range --file FILE KEY` | the same for one file: a copy, a tampered copy |
| `scan-tsv [FILE...]` | a fresh offline scan as `cve<TAB>package<TAB>installed<TAB>fixed<TAB>severity`, sorted, one line per finding and **source** package (`openssh`, not `openssh-server`); nothing when there are no findings. `scan-tsv dpkg-status:/usr/share/lab-pay/original-dpkg-status` is the image's seven |
| `oscap-rules RULE...` | `rule result` for each named rule, from one `oscap` run, in the order asked; `unknown` for a rule with no result. Exits 1 only then |
| `root-login` | `allowed`, `refused`, `key removed` (the throwaway key is gone from root's `authorized_keys`, so the login proves nothing) or `no answer: REASON` |
| `base-intact` | `intact`, or each sealed file that changed (and then exits 1). Sealed at build: `osv-scanner`, `oscap`, the records and their zip, the data files, the data stream, `refs.tsv`, the original package list, the shop's programs and these helpers. A lab's own scenery is not: seal that in the lab |
| `refs.py`, `advisory-zip` | run at build only |

And in `/usr/local/bin`, for learners and checks: `shop-cli`; `lab-flip FILE OLD NEW`, the careless attacker, which overwrites the first `OLD` in a file with `NEW` of the same length and touches nothing else; `lab-forge-journal IN OUT.journal [OLD NEW]`, the careful one, which reads every entry of a journal file, changes `OLD` to `NEW` in the messages, and has systemd's own `systemd-journal-remote` write a new, well-formed file.

The pure parts of all of these (what they read from a program's output) have their cases in `tools/tests/test_pay_helpers.py`, `test_pay_shop.py` and `test_pay_snapshot.py`, against outputs captured from the real programs. The programs themselves run in the probe lab's contract.

## Rules for checks and labs on the base

- **One wait per check run.** One check makes an event and waits for a seal to cover it (up to 30 s, with a `timeout:` of 60); every later check reads at once. Before waiting, read the newest file's header (`journalctl --file=... --header`, `Compatible flags:` has `SEALED`): an unsealed trail then fails at once instead of after the whole wait.
- **A check may tamper with a copy, never with the trail.** Copy the namespace's `system.journal` into a `mktemp -d` folder that an `EXIT` trap removes, and run `lab-flip` and `lab-forge-journal` on the copy. The file is being written while it is copied, so verify the copy first and take it again if it doesn't verify. The probe's `tamper-shows` is the pattern.
- **Markers are hex, and go after `=`** (`user="$marker"`), as everywhere in Module 4.
- **Never file times** for "the evidence is newer than the fix": compare content with a fresh run.
- **Read every included file** for a setting that can live in several: `systemd-analyze cat-config systemd/journald@audit.conf`, `sshd -T`.
- **The machine ID is not a secret and not per lab:** `/etc/machine-id` is written when layer 1 is built, so every lab on the same build has the same one (`2478b1c1...` on the owner's PC).
- **Don't rely on a whole-profile scan,** in a check or in a solution (above).
- **`sudo` keeps working through its own upgrade,** and a check that sudo still works asks as the learner (`su learner -c 'sudo -n true'`).
- **A wrong fix can't remove `sudo` itself:** `sudo apt-get remove -y sudo` ends in a dpkg error and sudo stays (tried). Remove one of the other four.

## Pins

The newest release at least two weeks old on the day the base was built, 2026-11-22. Each is checked against its SHA-256 in the `Dockerfile`, and a test fails if a download there has no checksum or this table falls behind.

| What | Version | Released | Licence | From | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| OSV-Scanner, `osv-scanner_linux_amd64` | 2.7.0 | 2026-10-12 | Apache-2.0 | `https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64` | `160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b` |
| ComplianceAsCode content, `scap-security-guide-0.1.82.zip` (183 MB; one file kept) | 0.1.82 | 2026-09-01 | BSD-3-Clause | `https://github.com/ComplianceAsCode/content/releases/download/v0.1.82/scap-security-guide-0.1.82.zip` | `765e84bdce7f9055f9b9c2dd0ee2b713d4255f8eec94eac6d35ea4973c28919c` |
| the file kept from it, `ssg-ubuntu2404-ds.xml` (12.6 MB) | | | | | `e311189ac70ff73be54121311fca324d6188f8c12ab53416090f595ff00e070c` |

OSV-Scanner 2.7.1 came out on 2026-11-09, thirteen days before the build, so the pin is 2.7.0 (the plan named 2.7.1). ComplianceAsCode 0.1.82 was the newest release.

From Ubuntu's archive, with each package's licence as its `copyright` file gives it: OpenSCAP 1.3.9+dfsg-1.1ubuntu2 (LGPL-2.0+ with BSD-3-Clause and Expat parts), libpam-pwquality 1.4.5-3build1 (libpwquality's BSD-style licence or GPL-2+), linux-base 4.5ubuntu9+24.04.2 (GPL-2), systemd-journal-remote 255.4-1ubuntu8.19 (LGPL-2.1+), sudo (ISC), OpenSSH (BSD-style), less (GPL-3+ or the Less licence), rsync (GPL-3), git (GPL-2).

## Kernel and runner needs

Seen on Docker Desktop 29.8.2 on the owner's PC on 2026-11-22. **Nothing here has run on a GitHub runner yet:** `csa.sec.pay-probes`' lab is what the CI spike reads, and each row gets its answer from it.

| Need | Topics | Docker Desktop | GitHub's runner |
| --- | --- | --- | --- |
| A journald namespace in a privileged container (`LogNamespace=`) | audit, compliance | works | untried (the probe's `sealed-for-auditors`) |
| Sealing that survives a restart of journald and of the container, with the kill drop-in | audit | works | untried (the probe's restart trial) |
| `systemd-journal-remote` writing a journal file | audit | works | untried (`tamper-shows`) |
| `oscap` on named rules, the same answer every time | compliance | works: 300 runs of four rules | untried (`benchmark-steady`, three runs in every container of the contract) |
| OSV-Scanner offline, one static Go program | vulnerabilities, compliance | works | untried (`sudo-patched`) |
| An SSH login to `127.0.0.1` as root with a key made at build | compliance | works | untried (`root-login-off`) |

## Files here

| File | What it is |
| --- | --- |
| `Dockerfile` | the image, four layers |
| `data/` | the frozen data and `SOURCES.md`; copied to `/usr/share/lab-pay/` |
| `snapshot.py` | makes `data/` from its public sources, on an author's machine; never run at build or in a lab |
| `journald/` | `10-lab.conf` (the default journal), `50-lab-stop.conf` (the kill), `journald@audit.conf` (the audit namespace's settings) |
| `shop/` | `shop_events.py` (the events, the policy's reader, the trail's line) and the image's `audit.conf` |
| `units/shop-audit.service` | the audit writer's unit |
| `bin/` | `shop-audit`, `shop-cli`, `lab-flip`, `lab-forge-journal` |
| `lib/` | the check helpers, and the two programs run at build |
| `.dockerignore` | keeps Python's `__pycache__` out of the image |

## Size and time

On the owner's PC (2026-11-22). Docker Desktop reports the image as 665 MB (470 MB of files inside it: the shared first layer and Ubuntu about 240 MB, layer 2 197 MB, the scanner 56 MB, the data stream 13 MB). A build from nothing takes 143 s (the first layer 48 s, layer 2 38 s, the two downloads 28 s, writing the image 17 s); with the first layer already built, 42 s; with nothing changed, about 2 s. A lab's own image on it takes a second or two.

A container boots in about a second and idles at 25 MiB of memory. The probe lab's contract (the pristine container, the solution, the restart trial and nine wrong fixes) took 157 s, 178 s, 208 s and 276 s in four runs, while other labs were being built on the same machine, and the busiest container in it used 196 MiB of memory. The seal wait is most of that time: about 20 s in each container whose trail is sealed.

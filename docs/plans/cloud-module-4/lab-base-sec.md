# Shared design: the payments-server base, `lab-base-sec` (topics 46, 48, 49)

Design only, by the `audit-vuln-compliance` designer, 2026-11-12. Nothing here is in the repository. Every mechanism marked **tried** ran on 2026-11-12 in Docker Desktop 29.8.2 (kernel 6.18.33.2-microsoft-standard-WSL2) on the owner's PC, in privileged systemd containers started the way `labcheck` starts them (`--privileged --cgroupns=host`, `/sbin/init`). Nothing has run on a GitHub runner. The prototype files are in `prototypes/audit-vuln-compliance/` (listed in its `README.md`); every container and image made was removed afterwards.

## 1. Why a base, and why not the network base

Audit logging, vulnerability management and compliance are about **one server and its evidence**: its audit trail, its packages, its configuration measured against a benchmark. None of the three topics needs several machines, so none of their labs needs `lab-base-net` (which costs 659 MB and teaches routing words these labs never use). What they do share is heavy and fiddly:

- a pinned scanner binary (OSV-Scanner, 58 MB) and a frozen, curated advisory database;
- frozen extracts of EPSS, CISA's KEV catalog and CISA's SSVC decision points;
- the OpenSCAP scanner and the ComplianceAsCode data stream for Ubuntu 24.04 (12.6 MB, taken from a 183 MB release zip), plus a rule-to-control table made from it;
- the story's packages pinned at their Ubuntu 24.04 release versions, and a local repository of today's fixed versions;
- the journald plumbing that makes forward-secure sealing reliable in a container (section 5).

Copying those into about fifteen lab folders would be the "900 copies" problem the network base solved. ADR-0018's third amendment already lets a lab say `FROM lab-base-<name>`, and `labcheck` builds `content/lab-bases/<name>/` first. So the proposal is a second base, **`content/lab-bases/sec/`**, built the same way. No new platform mechanism.

The three topics share one story: **the shop's payments server**, called `pay1` in the prompts (the container's hostname stays whatever `labcheck` gives every lab), run by the learner. Topic 46 gives it an audit trail, topic 48 keeps its packages patched, topic 49 proves both to an auditor. The compliance build draws on the other two topics' work as evidence (whole-task practice and retrieval weeks later).

## 2. The image

```dockerfile
# content/lab-bases/sec/Dockerfile (proposed)
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
# Layer 1: byte-identical to every systemd lab's first RUN (shared cache).
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop
# Layer 2: Ubuntu's archive only. OpenSCAP and PAM's password-quality
# module (compliance); linux-base, the package every Ubuntu kernel brings,
# which ComplianceAsCode's content checks to decide it is on a whole
# machine and not in a container; systemd-journal-remote, whose
# journal-remote program the worked example uses to forge an unsealed copy;
# the story's packages at their 24.04 release versions (the release pocket
# never changes), and today's fixed versions saved as a local repository,
# which becomes the machine's only package source.
RUN apt-get update \
 && apt-get install -y --no-install-recommends --allow-downgrades ca-certificates unzip \
      openscap-scanner libpam-pwquality linux-base systemd-journal-remote \
      sudo=1.9.15p5-3ubuntu5 openssh-client=1:9.6p1-3ubuntu13 openssh-server=1:9.6p1-3ubuntu13 \
      openssh-sftp-server=1:9.6p1-3ubuntu13 less=590-2ubuntu2 rsync=3.2.7-1ubuntu1 \
      git=1:2.43.0-1ubuntu7 git-man=1:2.43.0-1ubuntu7 \
 && mkdir -p /srv/patches && cd /srv/patches \
 && apt-get download sudo openssh-client openssh-server openssh-sftp-server less rsync git git-man \
 && apt-ftparchive packages . > Packages \
 && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/ubuntu.sources /usr/sbin/policy-rc.d \
 && echo 'deb [trusted=yes] file:/srv/patches ./' > /etc/apt/sources.list.d/patches.list
# Layer 3: the two downloads from outside the archive, pinned by version and
# checksum (the second and third after step-ca's in Module 3).
RUN curl -fsSL -o /usr/local/bin/osv-scanner https://github.com/google/osv-scanner/releases/download/v2.7.1/osv-scanner_linux_amd64 \
 && echo "fb7dab19a8bd9bbe5c3189f09d4b7ee1820c9553a23bac202648a56efd2f6ee8  /usr/local/bin/osv-scanner" | sha256sum -c - \
 && chmod 755 /usr/local/bin/osv-scanner \
 && curl -fsSL -o /tmp/ssg.zip https://github.com/ComplianceAsCode/content/releases/download/v0.1.82/scap-security-guide-0.1.82.zip \
 && echo "1caea418f0a5aaef7025e1655ca45a80942ea87ee832b943644ba6f9991b14a6ac5b35dddcd04b754e1fc8fbdee7b7f394507d24b123e821cca0354dc4e03cfd  /tmp/ssg.zip" | sha512sum -c - \
 && mkdir -p /usr/share/lab-sec/scap \
 && unzip -q -j /tmp/ssg.zip scap-security-guide-0.1.82/ssg-ubuntu2404-ds.xml -d /usr/share/lab-sec/scap/ \
 && echo "e311189ac70ff73be54121311fca324d6188f8c12ab53416090f595ff00e070c  /usr/share/lab-sec/scap/ssg-ubuntu2404-ds.xml" | sha256sum -c - \
 && rm /tmp/ssg.zip
# Layer 4: the lab's own small files (section 3), the journald plumbing
# (section 5) and the helpers (section 6); refs.tsv is made from the data
# stream at build time.
COPY data/ /usr/share/lab-sec/
COPY journald/10-lab.conf /etc/systemd/journald.conf.d/10-lab.conf
COPY journald/50-lab-stop.conf /etc/systemd/system/systemd-journald@.service.d/50-lab-stop.conf
COPY bin/ /usr/local/bin/
COPY lib/ /usr/local/lib/lab-sec/
RUN chmod 755 /usr/local/bin/* /usr/local/lib/lab-sec/* \
 && python3 /usr/local/lib/lab-sec/refs.py /usr/share/lab-sec/scap/ssg-ubuntu2404-ds.xml \
      xccdf_org.ssgproject.content_profile_cis_level1_server > /usr/share/lab-sec/refs.tsv
ENV OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=/usr/share/lab-sec/advisories
CMD ["/sbin/init"]
```

Every lab on it is then `FROM lab-base-sec`, its own story files, `CMD ["/sbin/init"]`, with `lab: { init: systemd, restart_trial: true }`. Labs with no server to boot (the hash-chain fill-in and write, the SLA write) are **plain labs** on Module 3's plain `RUN` line (content/README.md, "Network labs"), not on this base.

**Tried:** layers 1 and 2 (without the downloads in layer 3) built in 48 s with the first layer cached; OSV-Scanner's download and checksum in 7 s; the SSG zip in 35 s (183 MB); openscap's packages in about 26 s. Sizes from `docker history`: layer 1 153 MB (shared with every systemd lab), the story packages with OSV-Scanner 163 MB, OpenSCAP with its libraries 78 MB, the data stream 12.7 MB. **Estimate for the whole base: about 410 MB**, of which 257 MB is new. A systemd container on it booted to `running` in **1.9 s** and idled at 9 to 103 MB of memory.

**Untried as one Dockerfile:** the four layers were built as two prototypes (`comp-probe`, `vuln-probe`). Build the base once as written before any lab.

### What each package and download is, and its licence

| What | Version | From | Licence | Why |
| --- | --- | --- | --- | --- |
| openscap-scanner (`oscap`) | 1.3.9+dfsg-1.1ubuntu2 | Ubuntu archive | LGPL-2.1 (OpenSCAP repository) | the benchmark scanner Module 1 named; evidence for compliance |
| scap-security-guide (ComplianceAsCode) data stream `ssg-ubuntu2404-ds.xml` | 0.1.82 (2026-09-01) | GitHub release zip, sha512 pinned, one file kept | BSD-3-Clause (repository `LICENSE`) | Ubuntu's own `ssg-debderived` 0.1.71 has content only up to 22.04, whose platform check marks every rule "notapplicable" on 24.04 (tried) |
| linux-base | 4.5ubuntu9+24.04.2 | archive | GPL-2 (Ubuntu package) | the data stream's "system with a kernel" check (`dpkginfo` test on `linux-base`, read in the data stream): without it, SSH, PAM and journald rules are all "notapplicable" in a container (tried: 133 pass, 20 fail, 255 n/a without; 222 pass, 110 fail, 76 n/a with) |
| libpam-pwquality | archive | archive | GPL-2+/BSD (package) | password-length rules (PCI DSS 8.3.6, NIST IA-5) |
| systemd-journal-remote | 255.4-1ubuntu8.18 | archive | LGPL-2.1+ (systemd) | `journal-remote`, used once to show that an unsealed journal can be rewritten so that it still verifies |
| OSV-Scanner | v2.7.1 (2026-11-09) | GitHub release binary, sha256 pinned | Apache-2.0 | offline scanner whose database the lab can supply (section 3) |
| sudo, openssh, less, rsync, git at release versions | as in the Dockerfile | archive release pocket | each package's own (sudo ISC-style, OpenSSH BSD, less GPL-3/less licence, rsync GPL-3, git GPL-2) | the story's vulnerabilities, deterministic forever |

**Why OSV-Scanner and not Trivy or Grype** (the brief's question): both are Apache-2.0 and current (Trivy v0.76.2 of 2026-11-05, Grype v0.121.3 of 2026-11-09), but neither can be fed a small, frozen database. Grype's database is one 201 MB zstd archive per day (`grype.anchore.io/databases/v6/latest.json`, read 2026-11-12), with no documented retention for old builds; its v5 listing keeps three builds. Trivy's is an OCI artifact replaced every few hours. Either would mean a 200 MB download in every CI shard, results that change with the day's data, and a pin that may 404 next year. OSV-Scanner's offline mode reads `$OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY/osv-scalibr/<Ecosystem>/all.zip`, any zip of OSV records (tried: its own download of the full Ubuntu database was 805 MB and still growing when stopped; a hand-made zip of seven real records is 10.6 KB and scans in 0.19 s). The lesson names Trivy and Grype as the common choices (Grype's table even shows EPSS and KEV), and says why the lab freezes its own copy.

## 3. The lab's data, and its licences

All small, committed in `content/lab-bases/sec/data/`, each with a `SOURCES.md` beside it naming the source, the snapshot date and the licence.

| File (in the image) | What | Source and licence | Size |
| --- | --- | --- | --- |
| `advisories/osv-scalibr/Ubuntu/all.zip` | seven Ubuntu OSV records, copied whole: UBUNTU-CVE-2025-32463, -2025-32462 (sudo), -2024-6387, -2025-26465 (openssh), -2024-32487 (less), -2024-12084 (rsync), -2025-48384 (git) | api.osv.dev, originally canonical/ubuntu-security-notices, **CC BY-SA 4.0** (its README and LICENSE, read 2026-11-12): attribution in `SOURCES.md`, the zip itself shared alike | 10.6 KB |
| `epss-2026-11-10.csv` | EPSS scores and percentiles for the story's CVEs plus about fifty unrelated real rows, so that a lookup has to be a lookup; first line `#model_version:v2026.06.15,score_date:2026-11-10T12:00:24Z` kept | `https://epss.empiricalsecurity.com/epss_scores-2026-11-10.csv.gz` (the daily file FIRST links to). **No licence is stated** (FIRST's page says EPSS "makes the data freely and openly accessible"): a small extract with attribution; see open question 4 | about 3 KB |
| `kev-2026.11.10.csv` | the KEV columns the topic uses (`cveID,vendorProject,product,dateAdded,dueDate,knownRansomwareCampaignUse,forensicTriage`) for the story's CVEs and about fifty others | CISA's catalog version 2026.11.10 (1,779 entries), **CC0 1.0** (cisagov/kev-data `LICENSE`) | about 4 KB |
| `ssvc.csv` | `cve,exploitation,automatable,technical_impact` for the same CVEs | cisagov/vulnrichment (ADP records), **CC0 1.0** | about 2 KB |
| `refs.tsv` | `rule<TAB>framework<TAB>control`, made at build time from the data stream's `<reference>` elements for the rules of the CIS Level 1 Server profile: 4,159 rows (CIS Ubuntu 24.04 sections 415, PCI DSS 4.0 292, NIST 800-53 rev 4 607, HIPAA 164, NIST 800-171 74, ISO 27001:2013 2,607) | derived from ComplianceAsCode (BSD-3-Clause); tried, 0.25 s | 216 KB in the image, not in git |
| `nist-800-53r5/AC-7.txt` and the others the compliance labs quote | the control statements, parameters and discussion, as text | NIST SP 800-53 Rev. 5 (release 5.2.0, 2025-08-27) from usnistgov/oscal-content, **public domain in the US and CC0 worldwide** (its `LICENSE.md`) | a few KB |

What the lab may **not** carry: the text of PCI DSS (copyright PCI SSC, licence agreement), ISO 27001 (sold by ISO), the CIS Benchmark PDFs (free only for non-commercial use after registration; licence not confirmed) or the AICPA criteria. The labs use their **identifiers** (`pci-dss-4.0 8.3.4`, `cis 5.1.20`) and NIST's text; facts and identifiers are not the documents.

## 4. The vulnerable packages, the fixes, and why it never drifts

The release pocket (`noble/main`) keeps the 24.04 release versions for the life of the release, so `sudo=1.9.15p5-3ubuntu5` installs today and in five years. The fixed versions are whatever `noble-updates` holds on the day the base is built (2026-11-12: sudo 1.9.15p5-3ubuntu5.24.04.4, openssh 1:9.6p1-3ubuntu13.20, less 590-2ubuntu2.1, rsync 3.2.7-1ubuntu1.5, git 1:2.43.0-1ubuntu7.4), always at or above every record's fixed version. A scan with the frozen database therefore always finds the same seven vulnerabilities in five packages, and a patch always clears them (tried, captured in `captured/osv-vertical.txt`).

After the build the machine's only package source is `file:/srv/patches` (Ubuntu's `ubuntu.sources` is deleted), so `apt-get update && apt-get install --only-upgrade sudo` works offline in 2.8 s (tried), and nothing else can be installed: no learner can "fix" a finding by pulling an unrelated version from the internet, and checks never depend on the day's archive.

`/usr/sbin/policy-rc.d` (which the Docker image ships to stop packages starting services; it printed `policy-rc.d returned 101, not running 'restart ssh.socket'` in the trial) is removed, so an upgrade restarts services as it would on a real server. **Untried:** that removal; the writer runs an openssh upgrade with it gone.

## 5. Journald in a privileged container: three findings and the plumbing

1. **The kernel's messages are Docker's whole machine's.** A privileged container's journald reads `/dev/kmsg` of the VM, so the journal filled with other sessions' lab messages (`shopnet: port 1(office.eth0) entered disabled state`) and `Missed 381793 kernel messages` (tried). `ReadKMsg=no` in `/etc/systemd/journald.conf.d/10-lab.conf` stops it. (Module 1's and 3's systemd labs have the same exposure; worth a note to the base's owners.)
2. **The audit kernel interface is closed to containers.** `auditctl -s` in a privileged container answered `Error sending status request (Operation not permitted)` and `auditd.service` failed five times (tried). The kernel allows audit control only from the initial PID namespace (`kernel/audit.c`, `audit_netlink_ok()`: "Only support auditd and auditctl in initial pid namespace for now", read 2026-11-12). So no lab runs `auditd`; topic 46 teaches its rules from files the auditd package ships and from constructed records (topic brief, section 7). This is also why a lab can't disturb Docker's own kernel with audit rules.
3. **Forward-secure sealing breaks on a clean journald restart in systemd 255.4-1ubuntu8.18.** Tried in fresh containers, each time with a new key:
   - Sealing works: `journalctl --setup-keys --interval=10s`, `Seal=yes`, one restart, then `journalctl --verify --verify-key=KEY` prints `PASS` and `=> Validated from … to …, final 4.3s entries not sealed`.
   - After a further clean `systemctl restart` of the sealing journald, the file it reopens fails with `Epoch sequence not continuous (215 vs 215)`, and a file it creates fails with `Tag failed verification` at its first tag. Rotating first doesn't help; neither does waiting several epochs with the instance stopped. The default namespace's file created at boot by the flush fails the same way after every container restart.
   - A **kill** (SIGKILL, or `docker restart`, which ends in a kill because the images set no `STOPSIGNAL`) leaves the file marked dirty; journald then starts a new file and every seal verifies, across three restarts and a container restart (captured).

   **The plumbing:** the default namespace keeps `Seal=no`; sealing happens only in a **journald namespace** (`LogNamespace=audit` on the shop's audit writer, files in `/var/log/journal/<machine-id>.audit/`, config `/etc/systemd/journald@audit.conf`), which has no runtime-to-persistent flush and defaults to persistent storage (Ubuntu noble's `journald.conf(5)`: "Defaults to "auto" in the default journal namespace, and "persistent" in all others"); and a drop-in `/etc/systemd/system/systemd-journald@.service.d/50-lab-stop.conf` with `KillSignal=SIGKILL`, so every restart of a namespace instance is a kill. With both, sealing survived everything tried. `journalctl --setup-keys` writes the sealing key to the **default** namespace's directory (`/var/log/journal/<machine-id>/fss`) even with `--namespace=audit`, and the `audit` instance loads it from there (tried: a key moved into the `.audit` directory was ignored, and the files were unsealed). The lesson says that the lab's journal service stops "the way a crash does" because of a sealing bug in this systemd version, and the writer searches systemd's issue tracker for it on the day (no report was found by a web search on 2026-11-12; open question 1).

## 6. Helpers

In `/usr/local/bin` (for learners and checks) and `/usr/local/lib/lab-sec/` (checks only):

| Helper | Does |
| --- | --- |
| `shop-audit` and `shop-audit.service` | the shop's audit writer (Python 3, scenery): reads events from a local socket that `shop-cli` writes to, and writes the audit trail to its stdout according to `/etc/shop/audit.conf` (topic 46, section 8.1); `LogNamespace=audit` in its unit |
| `shop-cli EVENT key=value...` | makes the shop do something (log in, refund, export, change a role), as a customer or an admin would; used by learners and checks |
| `lab-flip FILE OLD NEW` | changes the first occurrence of `OLD` to `NEW` (same length) in place, byte for byte: the worked example's careless attacker (tried with `dd … conv=notrunc`: the copy then fails with `Invalid hash`) |
| `/usr/share/lab-sec/examples/10-vendor.conf` | an SSH drop-in saying `PermitRootLogin yes`, for topic 49's worked example (first value read wins) |
| `lab-forge-journal IN OUT` | the worked example's attacker: `journalctl --file IN -o export`, an edit, `systemd-journal-remote -o OUT -` (tried: the result has no `SEALED` flag and `--verify --verify-key` says `PASS` with no `Validated` line) |
| `lib/lab-sec/seal-range NS KEY` | the newest file's verification for a namespace: `sealed FROM TO`, `unsealed` or `failed: MESSAGE` |
| `lib/lab-sec/scan-tsv [FILE...]` | runs `osv-scanner … --format json` and prints `cve<TAB>package<TAB>installed<TAB>fixed<TAB>severity`, through `python3`, for checks |
| `lib/lab-sec/oscap-rules RULE...` | runs `oscap xccdf eval --profile … --rule …` once for the named rules and prints `rule result`; retries once on exit 139 (see below) |
| `lib/lab-sec/refs.py` | makes `refs.tsv` at build time |

**OpenSCAP crashed once.** One of five full-profile runs (408 rules) ended in `Segmentation fault` after 144 rules; the next four completed. Runs of two to four named rules (about 2 s each) never crashed in about twenty runs. Checks therefore run only named rules, and `oscap-rules` retries once on exit 139. Open question 2.

## 7. CI and the restart trial

- **Base build per shard:** about 2 minutes cold (the SSG zip is most of it), then cached. Only the shards that hold these topics' labs build it.
- **Restart trial:** every lab on the base sets `restart_trial: true`. A `docker restart` here is a kill (section 5), which is the case that keeps seals intact (tried), keeps installed packages and `/etc` (tried), and keeps the machine ID (tried: `/etc/machine-id` is written at first boot and survives; every privileged container on this Docker Desktop got the same ID, `2478b1c1…`, presumably from the VM's DMI product UUID: harmless here, but don't use it as a per-lab secret).
- **On a GitHub runner:** untried. Two things to watch in the first CI run: whether the runner's kernel lets journald namespaces start in a privileged container (expected: Module 1 labs run systemd there), and whether `oscap` behaves the same on the runner's kernel.

## 8. Open questions for this base (each with a recommendation)

1. **The `KillSignal=SIGKILL` workaround for sealing.** It is lab plumbing that a real server shouldn't copy. Alternatives: leave journald alone and tell learners "restart the audit journal once" (fragile: one extra restart breaks the proof, with a message that looks like tampering); or drop forward-secure sealing from the labs and teach it from captured output (loses the strongest real tamper-evidence the module has). **Recommendation:** keep the drop-in, say why in one sentence in the lesson, and record the systemd version and the reproduction in the base's README so the writer can drop it when a fixed systemd reaches 24.04.
2. **OpenSCAP's one crash.** **Recommendation:** named rules only, one retry, and the CI spike runs the compliance labs' contracts three times before they are written.
3. **A downloaded 183 MB zip for one 12.6 MB file.** Alternatives: commit the data stream (12.6 MB of XML in a public repository), or use Ubuntu's 0.1.71 content (no 24.04 profile). **Recommendation:** download as written; Docker caches it, and the checksum makes the pin exact.
4. **EPSS has no stated licence.** **Recommendation:** ship the small extract with attribution to FIRST and Empirical Security and the score date, which is how FIRST describes the data ("freely and openly accessible"); the owner queue lists it under _Decided for you_.

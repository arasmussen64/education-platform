# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Changed (CI)

- The Labs job, most of an hour of proving every lab in Docker, now runs only when a cloud topic (`content/topics/csa.*`, where every lab lives) or the tooling changes, not for a Python topic or the web app.

### Added (Step through)

- **A Step through button** beside Run in every code runner, and **Step through it** under predict-the-output questions once they're answered ([ADR-0022](docs/decisions/0022-step-through.md)). The program plays back one step at a time: the line about to run, each running call's variables, and the output so far, with First, Back, Next, Last and a slider. It reuses the last Run's input and random seed, so it shows what you just saw.
- Under the hood: `harness/tracer.py` records the run under Python's own trace hook, in the browser and in CI alike, with two new scenarios both runtimes must match; 300 steps at most, values cut at 60 characters. A Step through is saved as a `code_run` event marked `stepped`.

### Added (the placement test)

- **A placement test** at `/placement` ([ADR-0021](docs/decisions/0021-placement-test.md)), offered from Today until one is taken, and from every track's map. It walks a track's unlearned topics by halving: a few of the middle topic's own review questions, and each answer rules out half of what's left, so thirty topics take about five topics' worth of questions. It says nothing about right or wrong until the end, and ticks nothing off: the result is where to start, and the topics before it to prove in order with "Prove it now".
- **A math diagnostic**, the first _diagnostic_ (`content/diagnostics/math.yaml`): seven levels from arithmetic to the first ideas of calculus, three original questions each, walked the same way. Its result says how far up the ladder is solid and where to refresh, with a free refresher for each level, until the platform's own math refresher exists. The validator checks diagnostics like any content.
- Under the hood: answers given during a placement carry the context `placement` and a finished run is one `placement` event (a migration widens the event table's checks); progress and the follow-ups skip placement answers; the question components gain a quiet mode; Today shows each subject's latest placement in a line.

### Added (automated backups)

- **A nightly encrypted backup of the learning data** ([ADR-0020](docs/decisions/0020-automated-backups.md)). A scheduled workflow dumps the real database's data (the `public` and `auth` schemas; the schema itself comes from the migrations), encrypts it with AES-256 on the runner, shreds the plain file, and commits the encrypted dump to a private backups repository, one file a night. Until the owner adds the three secrets it needs (the session-pooler database URL, the passphrase, a token for the backups repository; `docs/setup.md` says how) it says which are missing and stops green. Every pull request's CI rehearses the restore on the throwaway local database with `tools/backup_restore_check.sh`: a learner and an event in, dumped, encrypted and decrypted, the database reset, the dump restored, the rows back.

### Added (Today across tracks)

- **Today shows where you stand on every track, and counts your practice hours per track** ([ADR-0019](docs/decisions/0019-today-across-tracks.md), the owner's ask). _Next up_ has one entry per track: its name, how many of its topics are learned, and the topic in progress or next Available. _Practice hours_ keeps one sentence for the total, then gives each track its own time and its own milestone ladder on the way to 10,000 hours, since the hours are about mastering one domain; time on a topic outside every track shows as "Other" only when there is some. Reviews and mistakes to revisit already drew on every track.

### Added (labs on your own machine)

- **The lab checker's local mode** ([ADR-0018](docs/decisions/0018-lab-checker-local-mode.md)): `tools/labcheck.py` builds a lab's container from its folder in `content/`, starts it, runs the lab's checks inside it with `docker exec`, and prints a small result to paste into the site. A lab is an exercise with `runtime: lab`: a `Dockerfile` for the scenario, `checks.yaml` for what must be true when it's done, `solution.sh` for the reference fix and `wrong/*.sh` for fixes that must fail. `labcheck test` proves that contract against real containers, and a new Labs job in CI does so for every lab on every pull request. The validator checks a lab's structure, and `--labs` runs the contract locally.
- **The lab view on the topic page.** A lab shows the three commands to run (start, check, stop) with its name filled in, lists what the checker looks for, and takes the checker's printed result: paste it, press Record, and each check gets a tick or a cross. The result is checked to be for this lab and this revision, its counts are recounted from the checks, and it's saved as a `code_check` event marked `runtime: lab`, so a passed lab build or debug counts as that proof exactly like a Python one. A worked-example lab shows its walkthrough script with labelled steps; the reference solution appears after a pass, as for Python; the tutor stays off in labs.
- **Checkpoint 1: the broken server is ready, and with it the whole of Module 1.** The module's proof, with the way through for a stuck learner that ADR-0012 asks for, all as labs: the build (_Stand up the shop's server_: run the service, a default-deny nftables firewall that keeps SSH and the API and persists, SSH hardened, the key login proved), the debug (_The broken server_: five faults at once, a full data area, a unit pointing at a binary that isn't there, a world-writable `~/.ssh`, a firewall that never opened the API's port, a worker pegging a CPU, restored without weakening security), a solved sibling (_A server stood up, start to finish_, the blog), four steps (the build with the other parts already done in the image, the last from an outline) and two fresh versions (the gateway, the ledger). Every build and debug check names the module skills it tests (`test_skills`), so a miss brings the right topic's practice back. The explain asks the learner to critique an outage "fixed" by turning the firewall off and passwords on. Fifty-five checks, twenty-six known-wrong fixes, all omissions and mistakes rather than scripted shortcuts.
- **Hardening is ready, on five labs that lock a server down and prove it, and Module 1 is now complete.** Each lab sets up `ben` with a key in an `ssh-users` group, so a real `ssh ben@localhost` is the proof and nobody gets locked out. A worked example (_Harden SSH without locking yourself out_: the effective config, the key proved first, the hardening drop-in, `sshd -t`, the login re-proved), a fill-in (_Finish the SSH hardening_: the four drop-in values), a write (_exposed-ports_: public listening ports with a verdict, SSH allowed, a `0.0.0.0:9000` debug port flagged, the loopback database skipped), the build (_Apply the baseline_: SSH hardened, a default-deny nftables firewall that keeps SSH and persists, a stray service closed) and the debug (_Hardened, and locked out_: a non-numeric `MaxAuthTries`, a wrong `AllowGroups`, `PubkeyAuthentication no`, fixed without turning passwords back on). The firewall is nftables, not `ufw`; benchmark scanners stay in the lesson and recall. Turning a protection off to make something work is a known-wrong fix in two labs. Twenty-four checks, seventeen known-wrong fixes. **All fourteen Module 1 topics are `ready`; the module checkpoint is the remaining piece.**
- **Performance triage is ready, on five labs on a slow server with real load.** The labs install `sysstat` (iostat, mpstat, pidstat, sar) and `strace` in their own tail, so the shared base and the other sixty labs don't rebuild. A worked example (_The server is slow: the first minute_: the checklist in order, ending with a written verdict, CPU is the bottleneck, `shop-worker` the culprit, memory and disk ruled out), a fill-in (_Finish the triage report_: the CPU count, the `vmstat` run-queue column, the sort key, the CPU-percent field), a write (_top-cpu_: the busiest processes by CPU), the build (_busiest-service_: sampling each service cgroup's `cpu.stat` to name the heaviest) and the debug (_The runaway that's eating a CPU_: a service burning a CPU in a storm of failing `openat` calls, found with `strace -c` and stopped at the service, since it restarts). The checks lean on the signals that are deterministic in a container, a spinner as the top process, per-cgroup CPU accounting, `strace` error counts; disks and the network stay in the lesson and recall. Twenty checks, sixteen known-wrong fixes.
- **Shell scripting is ready, on five labs where whole scripts are written and run.** The cloud track's first plain labs (no systemd): a light container with ShellCheck, where the learner writes and runs scripts. A worked example (_The habits that make a script safe_: `set -u`, `pipefail`, quoting, a cleanup trap and an idempotent append, each as a before-and-after), a fill-in (_Finish the deploy script_: the shebang interpreter, `pipefail`, the trap, a quoted path), a write (_Write backup-logs_: a nightly backup that cleans up its temp dir, keeps a filename with a space, replaces its archive instead of piling up, and exits 2 when its source is missing), the build (_Build a safe deploy script_: honest exit 2 with no version, strict mode, a trap, an atomic `ln -sfn` swap, and pruning to the three newest releases) and the debug (_Fix the fragile script_: fails the second run, drops a spaced filename via `$(ls)`, stays silent when the source is missing). ShellCheck grades three of the five. Twenty-two checks, seventeen known-wrong fixes.
- **Boot, cloud-init and instance metadata is ready, on five labs on a machine that stands in for a fresh instance.** cloud-init really runs at the container's first boot from a NoCloud seed, and three scripts stand in for the cloud console: `lab-launch` (a fresh instance, every stage runs), `lab-reboot` (the same instance, per-instance modules skipped) and `lab-imds-options` (the metadata options). A metadata-service stand-in answers at `169.254.169.254` the way EC2's does, in both the plain and the session-token protocols. A worked example (_A server configures itself on first boot_: what cloud-init did, `systemd-analyze`, and the once-per-instance rule shown with a reboot and a launch), a fill-in (_Finish the user data_: the package, the file path, a value and a `runcmd` command), a write (_Write instance-facts_: a metadata client that gets a session token first, proved by still working once tokens are required), the build (_Require session tokens for the metadata service_: turn on the requirement and keep the shop's one metadata client working through it) and the debug (_The instance came up half-configured_: a misspelled package, a config at the wrong path, and a `runcmd` writing to a directory that doesn't exist, fixed from the logs and launched fresh). Twenty-three checks, sixteen known-wrong fixes. The shared base installs `cloud-init`.
- **Networking from the host is ready, on five labs with an office on the far side of `eth1`.** The lab server has a second interface whose far end is a network namespace standing in for the office (`from-office COMMAND` runs a command there), its own name server (dnsmasq, answering for `shop.internal`), the shop's API on 8080 and its database on `127.0.0.1:5432`. A worked example (_What is this server offering?_: `ip -br addr`, `ip route`, `sudo ss -ltnp`, then from the office `dig`, `nc`, `curl` and `traceroute`, then `tcpdump` on `eth1` catching a three-way handshake and a reset), a fill-in (_Finish the network report_: the address field, the `default` route, `ss -ltn`, `dig +short`, `%{http_code}`), a write (_Write socket-report_: `ss -tan` states counted with `uniq -c` and `CLOSE-WAIT` as the verdict, against a cache that never closes its side), the build (_Build the shop server's firewall_: nftables `input` policy `drop`, `lo` and `ct state established,related` accepted, 22, 8080 and DNS from the office, everything else dropped rather than refused, and the rules in `/etc/nftables.conf` with `nftables.service` enabled) and the debug (_It works on the server, not from the office_: a stale DNS record, a firewall rule for the API's old port, and an API bound to `127.0.0.1`). Twenty-seven checks, twenty-two known-wrong fixes. The shared base installs the network tools and dnsmasq, which stays switched off unless a topic enables it.
- **How containers work is ready, on five labs that build a container from its parts.** No Docker in the lab machine, only `unshare`, `chroot`, cgroup files and overlayfs, around a root filesystem made from busybox. A worked example (_A container from its parts_: namespaces with `unshare --pid --fork --uts --mount`, `chroot`, `/proc` mounted inside, PID 1 and a hostname of its own, then a cgroup with `pids.max` 20 that a fork storm runs into), a fill-in (_Finish run-in-box_: `--fork`, `proc`, `box`), a write (_Write layers_: an overlay of image layers given bottom to top, writable layer on a tmpfs, top layer wins, copy-up), the build (_Build a container runtime in thirty lines_: overlay root thrown away afterwards, namespaces, a cgroup with pids and memory limits, cleanup) and the debug (_The container that leaks_: no `--uts` so the host gets renamed, `--pid` without `--fork`, a cgroup join written after the `exec`). Twenty-three checks, sixteen known-wrong fixes. The shared base installs `busybox-static`.
- **CPU scheduling and cgroups is ready, on five labs where the kernel does the throttling.** A worked example (_Give a program a fifth of a CPU_: `nproc`, `uptime`, a spinner in `top`, then the same spinner under `CPUQuota=20%`, `cpu.max` as `20000 100000`, and `cpu.stat`'s throttled periods climbing), a fill-in (_Finish the CPU report_: CPUs, load average, the busiest process, a service's throttled count), a write (_Write cpu-cap_: a drop-in with `CPUQuota=`, reload, restart, `cpu.max`; a second run replaces the cap), the build (_Share the CPU_: a quarter of a CPU for the batch report, three times the weight and no quota for the API) and the debug (_The API that can't get a CPU_: `CPUQuota=5%`, `Nice=19` and `CPUWeight=1` on one service). Twenty-three checks, sixteen known-wrong fixes. The checker now keeps going when one lab's file can't even be read, reporting that lab as broken.
- **Memory and the OOM killer is ready, on five labs where the kernel really kills.** A worked example (_Read the memory, then run out of it on purpose_: `free`, `/proc/meminfo`, `vmstat`, then a 200 MB hog inside a 64 MB limit with `systemd-run`, `Result=oom-kill`, signal 9, and the kernel's "Killed process" line), a fill-in (_Finish the memory report_: `MemAvailable`, swap used, the top process by RSS, OOM kills counted), a write (_Write limited-run_: any command inside a memory limit, exit 137 when killed), the build (_Contain the leak_: find the leaking service, read `memory.peak`, cap it with a drop-in and watch systemd restart it, protect the database with `OOMScoreAdjust=-900`) and the debug (_Killed, again and again_: a limit below the working set, a limit of 512 bytes, a database set to die first). Twenty-two checks, fifteen known-wrong fixes.
- **Disks and filesystems is ready, on five labs with real disks.** Each lab machine boots with image files attached as block devices (loop devices), labelled under `/dev/lab/` the way a cloud labels volumes, and lets go of them when the lab stops: the checker now runs an image's `/usr/local/lib/lab/teardown.sh` before removing a container, because a removed container leaves its loop devices attached to Docker's machine. The labs: a worked example (_A new disk, from blocks to files_: `lsblk`, `mkfs.ext4`, `mount`, `blkid`, an `fstab` line by UUID with `nofail`, proved with `mount -a`), a fill-in (_Finish the add-disk script_: XFS, UUID, `nofail`, `mount -a`), a write (_Write disk-report_: bytes and inodes used, the biggest folder, deleted files still held open), the build (_The disk is full_: rotated logs, a deleted log a running shipper holds open and must be truncated through `/proc`, an uploads volume out of inodes, and a volume grown while mounted with `resize2fs`) and the debug (_The disks that didn't come back_: an `fstab` with a wrong UUID, a wrong type and a missing mount point, each a different complaint from `mount -a`). Twenty-six checks, seventeen known-wrong fixes. The shared base now installs `xfsprogs`, `lvm2` and `lsof`.
- **Package management and patching is ready, on five labs with a package repository of their own.** The lab image builds a small `apt` repository (`make-repo.sh`: fake packages made with `dpkg-deb`, three suites with `apt-ftparchive`, a kernel stand-in whose install leaves `/run/reboot-required`, a package with a config file) and points `apt` at it alone, so `apt update`, `upgrade`, `hold`, `remove`/`purge` work offline and identically everywhere. The labs: a worked example (_Refresh the list, then look before you leap_), a fill-in (_Finish the patch script_: `update`, `--upgradable`, `hold`, `upgrade -y`), a write (_Write security-updates_: only the `noble-security` suite, `--only-upgrade`, idempotent), the build (_Patch day_: hold, upgrade, purge, install, report what still waits and whether to reboot) and the debug (_The patch script that patches nothing_: upgrade before update, the wrong package held, the reboot note looked for in `/etc`). Twenty-four checks, fifteen known-wrong fixes; the checks that run a learner's script first put the server back to a fresh night. The shared base now installs `apt-utils`.
- **Users, permissions and SSH is ready, on five labs with a real `sshd`.** A worked example (_Read the modes, then set them_: `ls -l`, `stat -c`, `chown`, `chmod`, `umask`), a fill-in (_Finish the service-account script_: `nologin`, owner, 750), a write (_Write share-folder_: a group, its folder, `usermod -aG`), the build (_Lock down the shop's server_: a secret, a deploy group, a one-command sudo rule, and Ben's key installed and tried over SSH) and the debug (_Ben can't get in_: a 644 private key, a group-writable `.ssh`, a typo in the sudo rule). Twenty-five checks, seventeen known-wrong fixes. The shared systemd lab base now installs `openssh-server`. The lesson gained `stat -c`, `getent`, `useradd --system`, `visudo -f`/`-c` and `sudo -l -U`.
- **Your place in a long topic.** Every topic page now has an outline beside the content (above it on a phone): the lesson's parts, with the one you're reading marked as you scroll; every practice item as a numbered link, marked done (after a correct answer, from your saved answers) or tried, with "x of N done" and "Next not done"; the three proof checks; and "Continue where you left off", which remembers where you were on this device. Each practice card says "Done ✓" or "Tried, not right yet" in its header, and an item you had already got right before opening the page is folded away until you ask for it, so a 24-item topic shows what's left. The outline is the same on every topic.
- **Processes and signals is ready, on five labs.** They boot systemd too, so PID 1 is the real thing: a worked example (_Stop a runaway process_: find it in the tree, `TERM` it, see its trap run), a fill-in (_Finish the report runner_: `&`, `$!`, `wait`, `$?`), a write (_Write graceful-stop_: `TERM`, wait up to five seconds, then `KILL`, proven on a polite worker and a stubborn one), the build (_The nightly runner_: three jobs at once, each one's exit status reported, all stopped on `TERM` or Ctrl-C) and the debug (_The stop script that doesn't_: a `pgrep` that matches the script itself, a `kill -9` that skips the cleanup, and a report that reads `pgrep`'s exit status backwards). Eighteen checks, sixteen known-wrong fixes. The lesson gained `pgrep`/`pkill` and the warning that a name match catches more than you meant.
- **Services and logs is ready, on five labs that boot systemd.** The lab machine is a privileged container running systemd as PID 1, which the checker now starts in its own cgroup namespace and waits for. The labs: a worked example (_Your first service_: install a unit, enable it, read the journal), a fill-in (_Finish the unit file_: four gaps), a write (_Write a unit file_ for a worker script), the build (_A service that survives a crash_: a web API that dies on request, a restart policy, a persistent journal, and a report from `journalctl -p err` and systemd's restart count) and the debug (_The service that won't start_: a misspelt section, a user that doesn't exist and a port out of range, each uncovered by fixing the one before). Thirty-one checks and eighteen known-wrong fixes. `labcheck test --jobs N` proves several labs at once; CI uses four. A lab's scenario may include a Python program; the validator now forbids only a Python exercise's files in a lab folder. ADR-0018 is accepted.
- **Shell essentials is ready, the cloud track's first learnable topic.** Its practice ladder and proofs are five labs on the same generated logs: a worked example (_Two questions about a log, answered and saved_, a five-line walkthrough with labelled steps), a fill-in (_Finish the error counter_: three gaps in a script, checked on two logs so a hard-coded answer fails), a write (_Write top-paths_: a script with two arguments, checked for two logs and two values of N), the build below, and a debug (_The report that lies_: three bugs in a report script). Fifteen checks and twelve known-wrong fixes between them, all proven in CI. Module 1's topics are now bundled into the app rather than loaded on demand, so the Today page and the follow-ups can see them.
- **The first lab:** Shell essentials' build, _A report from the shop's logs_: a container with generated access, application and CSV logs, and four files to produce with pipelines; five checks that compute the right answers from the data themselves, a reference solution, and four known-wrong fixes (counting 4xx with 5xx, a case-sensitive grep, `uniq -c` without `sort`, a header counted as a user), each of which fails a check.

### Added (content: the cloud track begins)

- **The first three topics of Module 1, Linux and the command line, as drafts:** Shell essentials, Processes and signals, and Users, permissions and SSH. Each has a lesson written for a complete beginner around freely licensed readings (MIT's Missing Semester, _The Linux Command Line_, the ArchWiki, the Linux man-pages), an explain prompt with its rubric, four to six skills, and a practice ladder of recall items: 54 between them, 31 of the new `predict_shell` kind, every one proven in real bash by the validator. They're drafts, visible on the dev server only, because their hands-on steps and proofs wait for the lab checker's local container mode ([ADR-0017](docs/decisions/0017-shell-in-the-browser.md)).
- **Three more Module 1 topics as drafts:** Services and logs (systemd unit files, `systemctl`, `journalctl`), Package management and patching (`apt` and `dnf`, security updates, holds, reboots, immutable servers) and Disks and filesystems (`lsblk` to `fstab`, ext4 and XFS, growing a cloud disk with LVM, the two ways a disk fills up, `fsync` and IOPS). 49 recall items between them, 20 of them `predict_shell` items that read real tool output (`df`, `du`, `lsblk`, `blkid`, `lsof`, `vgs`, `dpkg -l`, `apt list`, `systemctl` listings, the journal) with the text tools from Shell essentials.
- **Three more again:** Memory and the OOM killer (virtual memory and the page cache, swap and thrashing, huge pages, the OOM log and exit 137, a container's cgroup memory limit), CPU scheduling and cgroups (CFS and nice, load average and steal time, `cpu.weight` versus `cpu.max`, finding throttling in `cpu.stat`, Kubernetes requests and limits) and How containers work (namespaces, cgroups, image layers and overlayfs, the writable layer and volumes, containers versus VMs, the runtime chain). 45 recall items, 19 of them `predict_shell`. Nine of Module 1's fourteen topics are now drafted.
- **And three more:** Networking from the host (`ip`, `ss`, the TCP states and ephemeral ports, `curl`, `dig`, `nc`, `traceroute`, `tcpdump`, nftables and connection tracking, a container's network namespace), Boot, cloud-init and instance metadata (firmware to systemd, `systemd-analyze`, cloud-init's stages and user data, once-per-instance behaviour, the metadata service and IMDSv2) and Shell scripting (strict mode and its one trap, quoting and `"$@"`, exit codes, `trap … EXIT`, idempotent steps, ShellCheck). 50 recall items, 25 of them `predict_shell`; the scripting ones all run bash itself. Twelve of fourteen drafted.
- **The last two:** Performance triage (the USE method, the sixty-second checklist, reading `vmstat`, `iostat`, `pidstat`, `strace -c`, `perf report` and `sar`) and Hardening (a baseline, SSH keys only and no root login with `sshd -t` and `sshd -T`, a default-deny firewall, the `ss -ltnp` audit, least privilege, CIS Benchmarks and proving the result with OpenSCAP or Lynis before and after). 31 recall items, 14 of them `predict_shell`. **All fourteen topics of Module 1 are now drafted**; the checkpoint waits for the lab checker.

### Added (the cloud track's first question type)

- **A new kind of question for the command line, `predict_shell`** ([ADR-0017](docs/decisions/0017-shell-in-the-browser.md)): a few small files, a shell command over them, and "what will it print?". The browser runs nothing; the page shows the files and the command, and the answer is checked like a Python predict-the-output question. Every item is proven before a learner sees it: the validator runs the command in real bash (Linux in CI, Git Bash on Windows) in a temporary folder holding just those files, and the output must match exactly, with nothing written to stderr.

### Changed (AI tutor)

- **The tutor speaks to you as "you"** (instructions version 3). In the test set's first real run (25 of 25 replies fine on Claude Haiku 5.5, for $0.0044), two replies to "just give me the answer" asks said "the learner's question asks for…" to the learner themselves, and others spoke of "the author's note": the tutor was echoing the labels on the information it reads. The instructions now say to speak as "you", and the written hints are labelled as the hints you see, not an author's. Live since 2026-11-09.
- **The tutor's test set covers Modules 3 to 6 now:** five more exercises (a safe division with `try`, a CSV column total, saving numbers to a file, a shuffled copy of a list, and tests-first `clamp`), three conversations each, with a fresh attempt to get the answer out of the tutor in every one (a fake system message in a comment, "you already gave it to me", flattery, "so I can compare with mine"). Ten exercises and 24 conversations in all. The set still runs only when the owner says so, because it costs money.

### Added (the living map)

- **Memory strength on the map.** Every topic you've Learned shows how well the review scheduler predicts you remember it right now, as "Memory: 86%" with a small bar: 100% just after a review, drifting down until a review falls due at the 90% target. It's the same number the scheduler uses to decide what's due, made visible, so the spacing of reviews stops being a mystery.

### Changed (checks)

- **Every exercise is now proven in the browser's Python too.** The web tests run each ready exercise's reference solution against its tests inside Pyodide, the same way the Check button does, in a few seconds for the whole track. The validator keeps proving, under CPython, that the reference solution passes and the known-wrong ones fail.

### Added (content: Parsons problems everywhere)

- **Eighteen more Parsons problems**, so 29 of the track's 30 topics have one right after the worked example (Testing with assert is the exception: a test's `assert` lines can go in any order, so no single order would be right). Six are also in their topic's review pool. Each decoy teaches something from its topic: `"Age: " + age` without `str()`, `/` where `//` was meant, `print(age = 21)` for `==`, `and member` for `and not member`, a `print` without `end=""` in a grid, `print(total)` outside the function that owns it, `scores.sort()` assigned to a name, `copy = original` for a real copy, `student.scores` for `student["scores"]`, plain `mean` without its module, and more.

### Added (Parsons problems)

- **A new kind of practice question: put the lines in order** ([ADR-0016](docs/decisions/0016-parsons-problems.md)). A short program's lines are scrambled, with a decoy that doesn't belong, and you build the program with Add, Up, Down and Remove, then Check. It's right when the lines are exactly in the right order without the decoy; otherwise it shows the program and explains. The buttons work with a keyboard and on a phone. The scramble is the same every time an item comes back, and never the solved order.
- **Eleven Parsons problems**, one in each of these topics, right after the worked example: Programs and print, Variables, If, elif and else, While loops, For and range, Accumulator patterns, Defining functions, Lists, Dictionaries, Exceptions and Files. Three are also in their topic's review pool. The validator runs each one's lines in order and checks the decoys differ from the real lines.
- In reviews, a Parsons item counts as a code question rather than a multiple-choice one, so a session can pair it with a quick check.

### Added (web app)

- **Practice hours**, on the Today page: how much deliberate practice you've done so far and in the last 7 days, with a bar toward the next milestone on the way to 10,000 hours (1, 5, 10, 25, 50, 100, 250, 500, 1,000, 2,500, 5,000, 10,000). It adds up the time recorded on every answer, Check, explanation and review, counting at most 30 minutes per attempt, so a page left open isn't practice. Nothing new is recorded: every graded attempt has saved its duration since the event log began.

### Changed (web app)

- **A smaller first download.** The Cloud Solutions Architect track's 357 topic outlines are no longer bundled into the app's main file. They download as one piece (181 KB, 37 KB compressed) the first time the map shows that track or one of its topics opens, with a "Loading this track's map…" note meanwhile and a Try again if the download fails. The main file shrinks from 1,034 KB to 853 KB (260 KB to 221 KB compressed). The Python Foundations track's outlines stay bundled in, because the map and the Today page need them at once.

### Added (Module 6 content: Real programs)

- **Five new topics, all ready:** Exceptions, Files, CSV data, Modules and libraries, and From spec to program. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills.
  - Four are built on CS50P clips timed from CS50's subtitles: Lecture 3 for exceptions (0:28 to 26:30, the rest linked), Lecture 6 for text files (0:28 to 30:26) and for the `csv` module (1:01:35 to 1:19:02), and Lecture 4 for the standard library (0:28 to 19:13, with the own-module ending linked). From spec to program is the platform's own lesson, with Think Python's "Incremental development" section (CC BY-NC-SA 4.0) as the reading.
  - Exercise tests can create files and read what the learner's program wrote, so file work is tested for real: `with`, modes, line breaks, `FileNotFoundError`, `csv.DictReader`, totals by group.
  - Two hidden tests import the learner's file and check that importing prints nothing, which is what `if __name__ == "__main__":` is for.
- **Checkpoint 6: CSV report tool,** the track's capstone, set as a prose spec: read a sales CSV, skip and count the bad rows, total by region, write the report to a file and print it; with tests, docstrings, untouched data and `main` under the guard. A debug that crashes on a bad row, overwrites totals and loses its report file; a module-level explain. The way through: an attendance-report sibling, the build in four steps, and two fresh versions (expenses by category, rainfall by station). Every test names the skills it checks, across Modules 1 to 6.
- In all: 40 more exercises and 26 more recall items. The validator runs 910 programs over the content with no problems; 36 topics are ready: the whole Python Foundations track.

### Added (Module 5 content: Collections)

- **Five new topics, all ready:** Lists, List algorithms, References and mutation, Dictionaries, and Nested data. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills.
  - Lists, Dictionaries and Nested data are built on three more clips of CS50P Lecture 2, timed from CS50's subtitles: the list of students (34:55 to 45:36), the dictionary of houses (45:36 to 56:11), and the list of dictionaries (56:11 to 1:05:56). List algorithms is built on the Python tutorial's More on Lists and Looping Techniques. References and mutation is built around two Python Tutor programs that draw names as arrows, with Ned Batchelder's "Facts and myths about Python names and values" (the article, and his PyCon 2015 talk) as the reading and video, both linked.
  - Filtering and transforming are taught as a loop with `append`; comprehensions are named as a later shortcut. Counting with a dictionary is taught both ways: check with `in`, or `get(key, 0) + 1`.
  - Every build in the module checks that the functions leave the lists they're given unchanged, so "don't change what you were given" is tested, not just said.
- **Checkpoint 5: gradebook.** A list of student records, each with a list of scores, turned into report lines by small functions (an average, a letter grade, the best student, the lines), with a test function, docstrings, data left untouched, and `main` under the guard; a gradebook whose functions divide wrong, grade off by one, and eat the list they're given; a module-level explain. The way through: an inventory sibling, the build in four steps, and two fresh versions (team stats, weather report). Every test names the skills it checks, across Modules 1 to 5.
- In all: 39 more exercises and 27 more recall items. The validator runs 749 programs over the content with no problems; 30 topics are ready.

### Added (Module 4 content: Functions)

- **Five new topics, all ready:** Defining functions, Return values, Scope and the call stack, Decomposition, and Testing with assert. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills.
  - Three are built on CS50P clips timed from CS50's subtitles: the end of Lecture 0 for `def`, parameters, `main()` and `return` (1:26:44 to 1:45:36, in two clips), Lecture 9's global-variables section for scope (7:45 to 17:33), and Lecture 5's unit-testing section for `assert` (1:20 to 16:25). Scope also has two Python Tutor programs that draw frames and the call stack. Decomposition is the platform's own lesson, around the Python tutorial's section on docstrings.
  - From Testing with assert on, programs end with `if __name__ == "__main__":`, so a file can be loaded for its functions without running.
  - Exercises now test functions, not just whole programs: a function is loaded by name, its return value checked, and its printing checked to be absent. Tests of the learner's own tests make sure they'd fail if the function were broken.
- **Checkpoint 4: password checker.** Three rule functions, a verdict function that returns the first problem in a fixed order, a test function with asserts, docstrings throughout, and a `main` under the guard; a code-word checker with three bugs, one of them in its tests; a module-level explain. The way through: a ticket-code sibling, the build in four steps, and two fresh versions (a PIN checker and a username checker). Every test names the skills it checks, across Modules 1 to 4.
- In all: 39 more exercises and 27 more recall items. The validator runs 596 programs over the content with no problems; 24 topics are ready.

### Changed (Python harness)

- Two helpers for exercise tests, in `checks.py`: `function(name)` loads a function from the learner's file (failing with "Define a function called ..." when it's missing, swallowing anything the file prints while loading, and saying so plainly if the file asks for input), and `printed(f, *args)` returns what a call prints. A new scenario, `check-functions`, pins their behavior in both runtimes.
- The test runner keeps anything printed during a Check out of the report, so the command-line checker's output stays clean and the Check button shows results only.
- A scenario, `check-files`, pins that tests and learner programs can create and read files in the working folder, in both runtimes.

### Added (report a problem)

- **"Report a problem"** under the lesson, under every practice, proof and review item, and under the explain check (v1 spec, F15). It opens a small box for what's wrong (a wrong answer, a confusing hint, a broken link) and saves the report with the topic, the item and its revision, so the content can be fixed. Hidden when signed out.
- A new table, `problem_reports`, with its migration and database tests: learners add and read their own reports and nothing else; every report starts open, and only the owner resolves it, in the Supabase dashboard. In the live database since 2026-11-09.

### Added (the hint-only tutor)

- **"Ask the tutor"** under every fill-in and write exercise in practice, including a checkpoint's steps ([ADR-0015](docs/decisions/0015-hint-only-tutor.md), v1 spec F13). The learner can say what they're stuck on; the tutor sees the exercise, their code as it is now and their latest Check, and answers with one hint, a rung further up the ladder each time: a nudge, the idea, a closer look at their code, then the next step. Six asks per exercise. It never writes the solution: the proxy replaces any reply with more than two lines of code or copied solution lines with a safer hint. Off in proof checks and reviews, and hidden when signed out.
- **The AI proxy's second action**, `tutor_hint`, with the same checks, log and $10 monthly cap as grading, its own model and effort settings (`TUTOR_MODEL`, `TUTOR_EFFORT`), and a test set of "just give me the answer" conversations run by hand with `npm run fn:eval:tutor`. Each hint is saved as a `hint` event with `source: tutor`, its rung and the call's ID, and counts in `hints_used` alongside the written hints.
- The tutor reached the live site on 2026-11-09, when the owner deployed the proxy. Until then the box said the tutor wasn't available and the written hints carried on.

### Added (Module 3 content: Loops)

- **Five new topics, all ready:** while loops, for and range, Accumulator patterns, Strings as sequences, and Nested loops. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills, so missed questions come back.
  - Four are built on CS50P Lecture 2 (Loops), embedded in clips whose times come from CS50's own subtitles: while loops (0:28 to 16:13), for and range (to 26:47), `while True` with `break` and `continue` (to 31:34), and the Mario section for nested loops (1:05:56 to 1:19:15). Strings as sequences is built on the Text section of Python's own tutorial, with Python Tutor walking a loop along a string.
  - Accumulator patterns names the three shapes (running total, count, best so far) and makes a point of the starting value: 0 is the wrong start for a smallest-so-far.
  - Off-by-one mistakes get their own attention throughout: `range` stops before its stop value, `word[len(word)]` is one too far, and the last word of a line has no space after it.
- **Checkpoint 3: text statistics.** From a line of text: the number of words and letters, the longest word, and a bar chart of word lengths, using loops and strings only (lists and `split()` come in Module 5); a triangle-drawing program with three bugs, one of them a crash; a module-level explain about the word that ends with the text. The way through for a stuck learner: a week-of-weather sibling (sunny streaks), the build in four steps, and two fresh versions (number statistics, match results). Every test names the skills it checks, across Modules 1 to 3.
- In all: 39 more exercises and 26 more recall items. The validator runs 441 programs over the content with no problems. With this, Milestone C is complete.

### Added (interleaved practice)

- **Each practice ladder now includes one question from an earlier topic** (v1 spec, F5): a recall question from the topic's most recent prerequisite, placed after the topic's own quick checks and labelled with where it's from. It changes each day. Answering it counts for the earlier topic, so it helps keep that topic fresh.

### Added (reviews, timed to how fast you forget)

- **Reviews on the Today page** ([ADR-0009](docs/decisions/0009-reviews.md)). Each Learned topic gets a review card; its first review comes due a few days later, and each review pushes the next one further out when it goes well, or brings it closer when it doesn't. Today lists the topics due, the most forgotten first, up to 20 a day.
- **A review session** asks two items from the topic's review pool, at least one of them code or predict-the-output, choosing the ones answered longest ago. It's rated from the first attempt at each: all right is Good, some is Hard, none is Again. The result is saved as a `review` event, and the page says when the next review is.
- **Three more topic states,** on topic pages and the map: Mastered (a review went well at least a week after learning), Fading (a review is due) and Relearning (the last review went badly). A topic in any of these still unlocks what builds on it.
- **The scheduler is the platform's own code** (`web/src/reviews/fsrs.ts`): the published FSRS-4.5 formulas and default parameters, with a 90% target retention. The ML capstone will fit them to real data.

### Added (Module 2 content: Decisions and debugging)

- **Five new topics, all ready:** Booleans and comparisons, if / elif / else, Logical operators, Tracing code, and Reading errors. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills, so missed questions come back.
  - The first three are built on CS50P Lecture 1 (Conditionals), embedded in three segments whose times come from CS50's own subtitles: comparisons and `if` (0:28 to 9:55), `elif` and `else` (to 18:28), `or` and `and` (to 34:07).
  - Tracing code is built around Python Tutor; Reading errors around Python's own tutorial on errors. Both lessons are the platform's own words.
  - Logical operators makes a point of the `x == 1 or 2` trap, which is always `True`.
  - Several exercises check the code with other starting values (`run_with`), so a trace exercise can't be passed by typing the expected output in.
- **Checkpoint 2: ticket pricing.** A rules-based cinema ticket program (age bands, a weekend extra, a member discount) from a blank editor; a parking-fee program with three bugs to fix; a module-level explain. The way through for a stuck learner: a zoo-ticket sibling, the build in four steps, and two fresh versions (a swimming pool and a train fare). Every test names the skills it checks, across Modules 1 and 2.
- In all: 39 more exercises and 26 more recall items. The validator runs 292 programs over the content with no problems. Milestone B is complete.

### Added (topic states, gating and "Prove it now")

- **Every topic now has a state** for the signed-in learner, shown with an icon and a word on its page and on the map: Locked, Available, In progress, Learned (or Passed, for a checkpoint), with the date it was learned.
- **Gating is on** ([ADR-0002](docs/decisions/0002-mastery-and-gating.md)). A Locked topic, one whose prerequisites aren't learned yet, shows its lesson only, with a note saying which topics open it. Its practice and proof checks wait. A Locked checkpoint shows only what it brings together.
- **"Prove it now"** on an Available topic skips the lesson and practice and goes straight to the three checks, which can be shown again with one click. Passing them marks the topic learned, just the same.
- **"Next up" on the Today page:** the topic in progress, or else the next Available topic in track order, with its time estimate.
- Signed-out visitors see no states and no gating, because nothing of theirs is saved anyway.

### Added (more than one track, and the cloud track on the map)

- **The app shows every track.** The topic map opens on Python Foundations at `/map`, with a switcher to the others, each at `/map/<track id>`. A topic page names its track as well as its module. Tracks carry an `order`, and a module may name a **capstone**: a bigger checkpoint that ends a stage, shown after the module's own checkpoint.
- **The Cloud Solutions Architect track is on the map** as 357 `planned` outlines (324 topics, 30 checkpoints, 3 capstones), generated from its spec by `tools/outline_cloud_track.py`. Each module's topics unlock when the modules it builds on are passed, following the spec's module map. Nothing in it can be opened yet; the map says so.
- The validator checks capstones like checkpoints, and that no two tracks share an `order`. 4 new validator tests, and 4 for the generator, one of which runs the validator over generated content.

### Added (planning: a second track)

- **The Cloud Solutions Architect track is specified** in [docs/specs/cloud-solutions-architect.md](docs/specs/cloud-solutions-architect.md). It isn't built yet.
  - It runs from Linux and networking up to principal-level multi-cloud strategy, on AWS, Azure and Google Cloud.
  - It has 30 modules in 4 stages, about 320 topics, 3 capstones and a choice of specialties.
  - Every topic is proven by doing: build, explain, fix a broken version, and review. The senior stages add design reviews, game days and "Defend it".
  - **Cross-referenced with the owner's _Senior Cloud Architect Knowledge Map & Learning Roadmap_** (2026-11-08), adding everything the map had that the spec lacked and removing nothing:
    - 4 new modules: Virtualization, hardware and Windows; Software engineering literacy; Application architecture and integration; Specialized workloads. 107 new topics, 210 to 317, and many existing topics extended.
    - **The map itself** is kept in `docs/research/senior-cloud-architect-knowledge-map.md`, unchanged.
    - **An example path for an experienced learner:** the map's seven-phase, 24-month plan mapped to the track's modules, with its weekly rhythm, kill criteria and reading list. What a learner skips is decided by proofs, never by their own estimate.
    - **The track assumes nothing about the learner.** It starts from zero and teaches every topic in full, so it can serve absolute beginners. For that reason the map's depth levels (L1 to L3) were left out, at the owner's request.
    - **A 24-item self-assessment,** each item tied to the proof that covers it.
    - More certifications, with a suggested order; 6 more drills; 20 more rows in the three-cloud service table.
    - Module numbers and positional checkpoint IDs shifted because modules were inserted; nothing is built, so nothing refers to them.
- **[ADR-0014](docs/decisions/0014-cloud-labs.md), proposed,** decides how cloud skills are proven:
  - labs run in the learner's own sandboxes;
  - a local, read-only lab checker inspects the results;
  - fault modules provide break-fix exercises and game days;
  - AI grades designs;
  - CI tests the checks against recorded API responses, without touching a cloud.

### Added (explain it back, graded: part 2 of explanation grading)

- **Explain it back** works: each explain card has a box and **Check my explanation**. Claude grades it against the rubric:
  - **Passed**;
  - or **Needs work**, with up to 3 guiding questions, never the model answer;
  - or a plain message when it wasn't graded: paused for the month, unavailable, not switched on for the account, or no connection.
- Every attempt is saved as an `explain_submit` event, graded or not. A pass shows straight away in "Your proof so far", and counts toward the topic being learned.
- **The grader is Claude Haiku 5.5 at low effort.** It got all 30 samples of the test set right in two separate runs, so the bigger models weren't needed. A grading costs about $0.0002, so the $10 monthly cap covers tens of thousands.

### Added (the grading test set, part 3 of explanation grading)

- **30 sample explanations** for Module 1's six explain checks, in `supabase/functions/ai/test-set/`. Each topic has five, each with the verdict it should get:
  - a full answer and a short one, both of which should pass;
  - one missing a required idea, one with a misconception, and one that tries to talk its way to a pass, none of which should.
- **`npm run fn:eval`** runs them against Claude with the same request the proxy sends, and reports every miss and the cost. It costs money, so each run waits for the owner's go-ahead.
- A test checks every topic in the test set has an explain check and both kinds of sample. It doesn't call Claude.

### Added (the AI proxy, part 1 of explanation grading)

- **`ai_calls`**, an append-only log of every call to Claude: who, the model, the tokens and the cost. A learner can read their own rows, and only the proxy can write them. `ai_spend_this_month()` adds up the month's spending for the $10 cap. 11 database tests.
- **The AI proxy**, an Edge Function (`supabase/functions/ai/`), following [ADR-0013](docs/decisions/0013-explain-grading.md):
  - it checks, in order, that the caller is signed in, `allowed`, under the month's cap, and that a key exists;
  - it asks Claude to grade the explanation against the rubric, in a fixed JSON shape;
  - a pass means every required rubric item is met, and guiding questions that repeat the model answer are dropped.
    19 tests, none of which call the real API.
- **Deno** (2.9.6) as a pinned development tool at the repository root, with `npm run fn:test` and `npm run fn:serve`. CI has a new **Edge Functions** job.
- The explanation box (part 2) is what calls it. Both went live on 2026-11-08.

### Changed

- `supabase/README.md` says how to put the AI proxy live. Merging deploys the web app, but the function is deployed by hand.
- The first database test now looks only at its own learners, so it also passes on a local database with accounts of its own.

### Decided

- [ADR-0013](docs/decisions/0013-explain-grading.md), accepted by the owner: grading explanations with Claude, through the AI proxy. It covers the path of one explanation, what a pass means, the $10 monthly cap and its call log, how the cheapest model that passes a test set gets chosen, and what the owner sets up before it goes live.

### Added (progress tracking, part 1)

- **Your proof so far:** each topic and checkpoint page lists its three proof checks, each passed (with the date) or not yet. A Check passed on the page shows straight away.
- **Progress on the map:** for a signed-in learner, each topic they've started says "In progress", and which proof checks they've passed there.
- The rules behind it (`web/src/progress/progress.ts`), with tests for every state change in the data model: when each proof check first passed, and each topic's state. A pass on any fresh version counts as a checkpoint's build.
- Progress is worked out from the event log, so passes from before this existed count too.
- **Not yet:** topic states and gating. No topic can be Learned until explanations are graded, so gating now would lock every topic after the first. They switch on with explanation grading.

### Added (export my data)

- **Export my data** (v1 spec, F16), built early so the learning history can always be backed up. On the new account page (open it from your name in the header), "Download my data" saves everything as one JSON file: the profile and every event.
  - It reads this browser's outbox first, then the server. So an answer that hasn't reached the server yet is in the file too, and none can slip between the two. The page says how many events came from the outbox.
  - It keeps reading pages until one comes back empty, so a server that sends fewer rows than asked for can't cut the file short.
  - The browser makes the file itself: nothing is sent anywhere.
- The file's layout, with a `format` version for scripts that read it, is in the [data model](docs/specs/data-model.md#the-export-file).

### Changed

- The day helpers (`dayOf`, `addDays`) moved from the follow-up rules to `web/src/days.ts`, so a page that only needs a date doesn't load those rules too.

### Added (Checkpoint 1)

- **Checkpoint 1: receipt calculator** (`py.m1.checkpoint`), ready. That completes Module 1.
  - **Prove it:**
    - build: a restaurant receipt from a blank editor (meal, drinks and a tip percentage);
    - debug: cinema tickets, with three bugs: an unconverted input, a missing pair of parentheses, and a `print` with a comma;
    - explain: what each line of a tip calculator does, with the type of every value.
  - **The way through** ([ADR-0012](docs/decisions/0012-checkpoint-support.md)):
    - a solved sibling: a shop receipt with a discount, planned with comments;
    - the receipt in 4 fill-in steps with hints: read, work out, print, then only the plan;
    - 2 fresh versions: splitting a bill, and an electricity bill.
  - Every build and debug test names its skills, and each known-wrong answer fails only the test for its mistake.
- The content checker runs every exercise with hidden tests on an empty program. A crash there is in the tests themselves, and the page would show it.

### Changed

- The "Try it in steps" suggestion now brings the steps to the top of the screen.

### Added (getting unstuck on a checkpoint)

- [ADR-0012](docs/decisions/0012-checkpoint-support.md), accepted: every checkpoint gets four additions, and the content checker won't mark one ready without them.
  - **Find the weak skill:** every test of a checkpoint's builds and debug names the skills it checks (`test_skills`). A failed test brings them back on Today, as questions from their own topics. Like code, a test counts as missed only if no Check passed it that day.
  - **A solved sibling** to study, **the build in 3 or 4 steps** with hints, and **at least 2 fresh versions** of the build.
- The checkpoint page: an "About this checkpoint" section in place of a lesson, the three proof checks, and a "Stuck? Try it in steps" section.
  - The steps open only when asked. After 2 failing Checks on the build, the page suggests them next to it.
  - The fresh version offered is one not yet tried, or else the one tried longest ago.
- The Today page reads which tests each Check failed (`data.failing`), and loads checkpoints and the topics their tests name.
- The content checker's rules for ready checkpoints: every topic in the module ready; a solved sibling, 3 or more steps with hints, and 2 or more fresh versions; every build and debug test naming real skills of this or earlier modules.

### Added (the fifth lesson)

- **Strings and input** (`py.strings-and-input`), ready to learn. That completes Module 1's topics.
  - **Learn:** CS50P Lecture 0 from 43:23 to 45:02, on f-strings. `input()` and `int()` were already in earlier clips, so this clip covers only what's new. The `:.2f` part of the lecture (1:24:34) and the Python tutorial's section on f-strings are linked as more resources.
  - **Practice:** a worked example that asks two questions and does maths with the answers, three questions (one mixes in topic 2's "45" surprise), filling in a rectangle's area, and a price tag with `:.2f`.
  - **Prove it:** kilometres to miles from a blank editor; a shopping line with a conversion crash and a missing `f`; explaining why `age + 1` fails on typed input.
  - **Review pool:** four items. Three skills: `input-text`, `convert` and `fstrings`.

### Added (the fourth lesson)

- **Arithmetic** (`py.arithmetic`), ready to learn:
  - **Learn:** the main resource is a reading, four short sections of the free textbook _Python for Everybody_ (CC BY 4.0). CS50P's lecture only lists the operators for about 40 seconds and never covers `//` or `**`. The lecture video on the same chapter and the Python tutorial's "Numbers" section are linked as more resources.
  - **Practice:** a worked example with `/`, `//` and `%`, three questions (one mixes in topic 2's types), filling in operators for egg boxes, and Celsius to Fahrenheit.
  - **Prove it:** a pizza party from a blank editor; a bill-splitting program with a crash and a silent order-of-operations bug; explaining `/`, `//` and `%` with cookies.
  - **Review pool:** three items. Three skills: `operators`, `precedence` and `div-mod`.
- A reading used as a lesson's main resource is credited with its license once, not with its title repeated.

### Added (the third lesson)

- **Variables** (`py.variables`), ready to learn:
  - **Learn:** CS50P Lecture 0 from 15:16 to 19:54: what a variable is, `=` as assignment, and the "quotes around the name" mistake. The intro swaps the video's "container" picture for name tags, the picture that still works when lists arrive. A Python Tutor link shows `b = a`, then `a = 5`, step by step, with names drawn as arrows.
  - **Practice:** a worked example following one name, three questions (one mixes in topics 1 and 2), filling in a swap, and rotating three values.
  - **Prove it:** swap and print from a blank editor, a swap that loses a value plus a typo, and explaining why `b` stays `3`.
  - **Review pool:** four items. Three skills: `assignment`, `trace-values` and `swap`.
- `run_with` in the shared test toolkit (`harness/checks.py`). It reruns the learner's program with other starting values, so retyping the expected values can't pass. 4 unit tests, plus a scenario that both runtimes must agree on.

### Fixed

- The dev server now notices new files in `content/` and `harness/`. Before, a lesson's new questions and exercises showed as "Missing practice item" until a restart. The live site was never affected.

### Changed

- Relearning follows the research the owner asked for: a missed skill must be right on **3 different days**, coming back after 1, 3 and 7 days (successive relearning; Rawson & Dunlosky, 2011).

### Fixed

- One miss can open follow-ups for several skills, and they could all pick the same question, showing it twice on Today. Each skill now gets its own question where possible; a shared one is asked once.

### Added (a guarantee)

- A test over the real content: missing any question or exercise in any ready topic must bring back a different question on each skill it tests. New topics are covered as soon as they're ready.

### Added (mistakes come back)

- **Mistakes to revisit** on the Today page ([ADR-0011](docs/decisions/0011-mistakes-come-back.md), now accepted). The owner asked for this after missing a question in their first lesson:
  - a skill you missed comes back the next day, as a _different_ question on the same skill;
  - after a right answer it returns 3 days later, and right answers on 2 different days relearn it;
  - "Coming back later" lists what's due on other days.
- It's worked out from the event log, so misses from before this feature count too.
- Answers on Today are saved as reviews, with hints off.
- Code exercises count as missed only if they never passed that day. Failing Checks while working something out aren't mistakes.
- The Today page now loads only when visited, like the topic pages.

### Added (the second lesson)

- **Values and types** (`py.values-and-types`), ready to learn:
  - **Learn:** CS50P Lecture 0 from 59:32 to 1:07:58: what an integer is, and why a calculator prints "12" for 1 + 2. A float clip and the Python tutorial are linked as more resources.
  - **Practice:** a worked example with `type()`, three questions (one mixes in topic 1: `print` hides quotes), a fill-in and a write exercise.
  - **Prove it:** a type report (its hidden tests also check that `type()` is used), a receipt with one crashing and one silent type bug, and explaining the calculator bug.
  - **Review pool:** three items. Two skills: `identify-types` and `plus-by-type`.
- The loading test now checks every ready topic automatically.

### Added (skills)

- [ADR-0011](docs/decisions/0011-mistakes-come-back.md) (proposed): a missed question will come back as a different question on the same skill, until it's right on 2 different days. The owner asked for it, and chose fresh questions over repeats.
- Topics declare their **skills**, and every question and exercise names the skills it tests. The content checker requires every graded item to name a skill, and every skill to have at least 2 questions that can come back after a miss. Unknown skill names are caught as typos.
- Programs and print is labeled with 4 skills, and has a new review question on printing with commas.

### Fixed

- A video clip looked as long as the whole lecture, because YouTube's player always shows the full video's length (a 9-minute clip read as 1 hour 45 minutes). The page now says above the video which part to watch, how long it is, and that it stops by itself. The topic's time estimate now says it covers the whole topic. Reported by the owner.

### Added (the first lesson)

- **Programs and print** (`py.programs-and-print`), the first real topic, ready to learn:
  - **Learn:** a 9.5-minute segment of CS50P Lecture 0 (CC BY-NC-SA 4.0), with an intro on what to watch for and a recap.
  - **Practice:** a worked example, three questions (one on reading an error), a fill-in exercise and a write exercise.
  - **Prove it:** build a banner from scratch, fix a program with two bugs, and explain why an error happened.
  - **Review pool:** three items for later reviews.
    The checker runs 22 programs for it, including 12 known-wrong answers that must fail.
- A practice-hours tracker idea is on the roadmap (Phase 2).

### Changed

- Multiple-choice answers are Markdown, so they can show code.
- Code and output boxes stand out from their cards in dark mode.
- The content definition of done: while the owner is the only learner, their first pass happens on the live site.

### Added (saving progress)

- Everything a signed-in learner does on a topic page is saved to the append-only event log (F6): lesson views, answers, runs, checks and hints. Each event records the item's revision, how long the attempt took, the hints used, the study session, and the commit the app was built from.
- Events go into an outbox on the device first, then to the server in batches. Retries are always safe, because the server ignores an event it already has. Offline, nothing is lost: the app retries with growing waits and again as soon as the browser is back online.
- An event the server refuses is set aside on the device, so it can't block the others.
- A "Not saved yet" badge in the header while work is waiting on this device.
- Topic pages tell signed-out visitors that their answers won't be saved.

### Added (topic pages)

- The app reads `content/` while it's built: YAML becomes data, lessons are MDX, and exercise code is loaded as text. A topic's lesson and exercises download only when its page opens.
- **Topic pages**, in three parts:
  - **Learn:** objectives, then the lesson's intro, the main resource (a privacy-enhanced YouTube embed, cut to its start and end times, or a link) and the recap, with the source and license. Other resources are listed after it.
  - **Practice**, in order: a worked example with labeled steps to run; multiple-choice and predict-the-output questions with instant feedback; fill-in and write exercises with hints one at a time. The reference solution appears only after a pass.
  - **Prove it:** the build and debug exercises (hidden test details, no hints) and the explain prompt. Grading the explanation, and counting the proof toward mastery, arrive in Milestone B.
- Topics that aren't written yet show their outline and say so. `draft` topics show only on the dev server.
- **The map** lists every module and topic, each marked Ready, Draft or Coming soon, with an icon and a word.
- Exercises can set their own time limit (`time_limit_ms`).
- If a page fails to load, an error page with a Reload button appears inside the layout. The usual cause is the app being updated while it's open.
- The content checker requires a ready lesson to place its main resource (`<Resource index={0} />`), and no other.

### Added (content)

- `content/`: the Python Foundations track and all 36 topics from the approved list as `planned` outlines, with their prerequisites. A `status` field (`planned`, `draft`, `ready`) tracks each topic's progress.
- The content validator (`tools/validate_content.py`). It checks file formats, the topic map (tracks, prerequisites, no cycles), and the definition of done for `ready` topics. It runs every exercise through the shared harness: reference solutions must pass, starters and known-wrong solutions must fail, and predict-the-output items must print what they claim. 14 tests prove it catches each kind of mistake.
- `harness/cli.py`: runs one folder through the harness in a fresh process. Used by the validator and the scenario tests.
- A **Content** CI job.

### Added (sign-in)

- Sign-in with GitHub on the live site, and email links in local development (they land in the local test inbox). The header shows who's signed in, with Sign out.
- The Supabase client, with settings for local and production, and TypeScript types generated from the database (`npm run db:types`).

### Added (deployment)

- Cloudflare deployment config (`web/wrangler.jsonc`): the built app is served as static files, with unknown addresses falling back to the app so its pages work. Wrangler's usage statistics are turned off.
- Setup steps for connecting the repo to Cloudflare and linking the Supabase project.

### Added (database)

- Local Supabase in Docker (`supabase/`), with the Supabase CLI pinned in a root `package.json` and `db:*` scripts.
- The first migration: learner profiles, created automatically at sign-up, and the append-only event log. Row-level security on both. Learners can only add and read their own events and can't grant themselves AI access; the database refuses to edit or delete events, even for admins.
- 18 database tests (pgTAP) and a **Database** CI job that starts a throwaway database, checks the SQL, and runs them.

### Changed

- Run now asks for input like a terminal. When a program calls `input()`, you type the answer right after the prompt and press Enter; there's no separate input box any more. Re-runs use the same random seed, so random choices stay put.

### Fixed

- Cloudflare's pull-request preview builds now deploy: `wrangler preview` needed a `previews` block in `web/wrangler.jsonc`.
- Cloudflare builds no longer spend about 6 minutes installing Python. The Python version is pinned in `pyproject.toml` instead of a `.python-version` file, which Cloudflare's build reacted to.
- No more console warning when the app first opens on a page that loads on demand (it now shows "Loading…").
- Password managers no longer pop up on the program-input field. It's now an editable piece of text (`role="textbox"`) instead of an `<input>`, because NordPass ignored the opt-out markers the first fix relied on.

### Added

- Python in the browser: Pyodide runs learner code in a background Web Worker, with a CodeMirror editor, Run and Check buttons, and a 5-second time limit. A temporary Playground page lets you try it.
- The 14 harness scenarios also run under real Pyodide in the web tests, so the browser and CI are checked to give identical results.
- The Python test harness (`harness/`), shared by the browser and CI. It has 14 scenarios that both runtimes must match, and a Python CI job (uv, ruff, pytest) on Python 3.14.
- ADR-0010: a local Supabase in Docker for development, and one cloud project for real use.
- A setup guide for the owner's computer and accounts (`docs/setup.md`).
- Web app scaffold in `web/`: Vite, React, TypeScript, Tailwind CSS and React Router, with placeholder Today, Map and Topic pages. The product name is kept in a single setting.
- CI on GitHub Actions: formatting, lint, type-check, tests and build on every pull request and every push to `main`.
- v1 spec, data model and Python Foundations track plan, in `docs/specs/`.
- ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically), both accepted.
- Project documentation: vision, learning-science principles, roadmap, competitor research, devlog.
- Decision records ADR-0001 to ADR-0007: decision process, mastery and gating, AI roles, content model, free hosting, working name, tech stack.
- `CLAUDE.md` with the development process and the product rules that constrain code.
- Repository config: `.gitignore`, `.gitattributes` (LF line endings), `.editorconfig`.

### Changed

- Data model: the content validator uses the harness's own test runner instead of pytest.
- Process: Claude merges its own pull requests once CI passes, under standing permission from the owner.
- Roadmap: the "prove it" checks, topic states and gating move from Phase 2 into Phase 1.

### Fixed (lab checker)

- `labcheck test --all --jobs N` builds the first lab of each topic on its own before the parallel run, so the heavy first layer a topic's labs share is built once instead of four times at once; and a build may take up to 30 minutes instead of 15. On a busy CI runner, twelve builds had run out of time.

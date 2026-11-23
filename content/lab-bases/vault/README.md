# The vault base

The labs of two Module 4 topics of the Cloud Solutions Architect track, Applied cryptography (`csa.sec.crypto`) and Secrets (`csa.sec.secrets`), and the third part of Checkpoint 4 start `FROM lab-base-vault`. This folder is that image: one server with a key and secrets service (OpenBao), a database (PostgreSQL), git, gitleaks and podman. `tools/labcheck.py` builds it, tagged `lab-base-vault`, before it builds any lab whose `Dockerfile` says `FROM lab-base-vault` ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), third amendment). When nothing here has changed, Docker's cache makes that a second or two.

Read this before writing a lab on it. The plan behind it is section 4.2 of Module 4's brief (`docs/plans/cloud-module-4/MODULE-4-BRIEF.md`), which follows section 10 of the cryptography topic's brief and the secrets topic's. Unlike the [network base](../net/README.md), this is a single machine: an ordinary systemd lab, as in Module 1, with more installed.

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 1 | The systemd labs' first `RUN`, byte for byte | Shared with every systemd lab, so Docker builds it once. Change it only with all of them (`tools/tests/test_vault_base.py` compares it with the network base's). |
| 2 | OpenBao 2.7.2 from its release `.deb` (the one download, below), and from Ubuntu 24.04's archive: PostgreSQL 16, git 2.43, gitleaks 8.16, age 1.1, podman 4.9 (with crun), xxd, openssl 3.0, the Python cryptography library, `ca-certificates` | 644 MB. PostgreSQL's and podman's own units are switched off; OpenBao's package leaves its unit off. |
| 3 | OpenBao's configuration and first-boot units, PostgreSQL's one setting, podman's two settings, `gcm`, `lab-seal`, the check helpers | Small; rebuilt in a moment when one of these files changes. |

**Nothing runs until a lab asks for it.** A machine started from the bare base has no OpenBao, no PostgreSQL and no podman service; it boots in half a second and uses 13 MiB. That is what lets Checkpoint 4's third part start here for git, gitleaks and openssl alone. A lab's `Dockerfile` switches on what it uses:

```dockerfile
FROM lab-base-vault
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
RUN systemctl enable openbao postgresql lab-busybox-image \
 && lab-seal /srv/shop/app.py
CMD ["/sbin/init"]
```

Every lab on the base sets `lab: { init: systemd, restart_trial: true }`. `csa.sec.vault-probes`' `probe-keys-and-secrets` (a draft topic, for the CI spike) is a whole lab that uses every part below.

Not in it: `jq` (checks read JSON with `python3`, through `json` below; a learner takes one field with `bao ... -field=NAME`), `uidmap` (so podman runs with `sudo`, below), manual pages, and anything else from outside Ubuntu's archive.

## Pins

Everything is from Ubuntu 24.04's archive except one download, pinned by exact version and SHA-256 in the `Dockerfile` (the test file checks that this table and the `Dockerfile` agree). The rule (Module 4's brief, 3.3): the newest release at least two weeks old on the day the base is built.

| What | Version | Licence | From | SHA-256 |
| --- | --- | --- | --- | --- |
| OpenBao | 2.7.2, released 2026-10-26 (2.7.3, of 2026-11-19, was three days old on 2026-11-22) | MPL-2.0 | `https://github.com/openbao/openbao/releases/download/v2.7.2/openbao_2.7.2_linux_amd64.deb` | `42bd0890a8e2060e5f29410ea828ee047aa2de21028045731a0516d5a532928c` (the release's `checksums.txt`) |

The archive's packages, with the licences their `copyright` files give (read in the image, 2026-11-22): PostgreSQL 16.15, the PostgreSQL licence; git 2.43.0, GPL-2; gitleaks 8.16.0, MIT; age 1.1.1, BSD-3-Clause; podman 4.9.3 and conmon, Apache-2.0; crun 1.14.1, GPL-2+; the Python cryptography library 41.0.7, Apache-2.0 or BSD; xxd (from Vim) 9.1, the Vim licence; OpenSSL 3.0.13, Apache-2.0; busybox 1.36.1 (in layer 1), GPL-2.

gitleaks 8.16 is from 2023. It has `detect` (a repository's history, or files with `--no-git`) and `protect` (changes not yet committed); newer releases rename these to `git` and `dir`, which a lesson should say in a sentence.

## OpenBao

OpenBao is the open-source continuation of HashiCorp Vault, with the same commands (`bao` for `vault`) and the same API. A lab that uses it says `systemctl enable openbao` in its `Dockerfile`. At the machine's first boot:

1. `lab-bao-key.service` writes 32 random bytes to `/etc/openbao/unseal.key` (`root:openbao`, mode 0640), before OpenBao starts.
2. `openbao.service` (the package's unit) starts OpenBao from `/etc/openbao/openbao.hcl`: its store in `/opt/openbao/data` (pebbledb, the package's default; 2.7 has no `file` store), plain HTTP on `127.0.0.1:8200` only, the `static` seal, and an audit log in `/var/log/openbao/audit.log`.
3. `lab-bao-init.service` waits until OpenBao answers, initialises it (`bao operator init`, one recovery share), saves the root token as `/root/.bao-root-token` (mode 0600, for the checks), makes the learner an admin token in `/home/learner/.vault-token`, and runs the lab's seed scripts.

The whole of that took 1.2 s on the owner's PC, and 3 s with the probe lab's seed. The machine counts as booted only when it has finished, so a check never sees OpenBao half set up. If it fails (a seed script with a mistake), the boot ends `degraded` and `journalctl -u lab-bao-init` names the script.

**The seal.** OpenBao encrypts its store under a key it must be given at every start. The `static` seal reads that key from the file, so OpenBao unseals itself at every boot: after `docker restart` it was answering, with its keys and secrets intact, by the time the machine had booted (3 to 3.5 s). It stands in for a cloud key service's auto-unseal, and the secrets topic makes the choice its subject: whoever can read that file can open the store. `bao status` shows `Seal Type static`, `Sealed false`.

**Tokens.** The learner's token has the policy `lab-admin` (every permission on every path) and lasts ten years, so a lab left for months still works; only the token mount's maximum lifetime was raised for that (`bao auth tune ... token/`), and every other lifetime keeps OpenBao's defaults. It is a token of its own, not the root token, so the audit log tells the learner's requests (`display_name: token-learner`) from the checks'. A token of OpenBao 2.7.2 is `s.` and 24 letters and digits (26 characters); a writer who matches tokens with a pattern checks the pinned version's format again.

**`BAO_ADDR`** is `http://127.0.0.1:8200` in every shell the checker opens (an `ENV` line), for `sudo` and logins (`/etc/environment`), and in the check helpers. A unit a learner writes doesn't get it: it sets `Environment=BAO_ADDR=...` itself, as on a real server. `sudo bao` finds no token (root's home has none under the name `bao` reads), so prompts never say `sudo bao`.

**The audit log** is declared in `openbao.hcl`: OpenBao 2.7 refuses an audit device made through the API. Only OpenBao's user and root can read it, so a learner reads it with `sudo`. Each line is one request or one response as JSON, with every secret value replaced by `hmac-sha256:...`; `bao write sys/audit-hash/file input=VALUE` gives the same HMAC for a value, which is how `audit_saw` finds one.

**Seed scripts.** A lab puts `NN-name.sh` files in `/etc/lab/bao-seed.d/`. They run once, in name order, as root, with the root token in `BAO_TOKEN`, after PostgreSQL has started when the lab runs it (so a seed may create a database and connect OpenBao to it). A script that fails stops the setup, and the next boot runs every seed again from the first: write each so that a second run does no harm, or accept that a failed first boot means `start --fresh`. Passwords a seed needs are made in the seed (`openssl rand -hex 16`), never written in the repository.

**A lab that needs another OpenBao setting** ships its own `/etc/openbao/openbao.hcl`, owned by `openbao`.

Tried on the base (2026-11-22, in the probe lab): the transit engine's `datakey/wrapped`, `datakey/plaintext`, `encrypt`, `decrypt` (a wrapped data key unwraps after a restart); the database engine with the PostgreSQL plugin, `rotate-root`, a role with `default_ttl=5s`, whose account read a table, was refused more, and was dropped by OpenBao within seconds of its lease ending. Not tried on the base: the other mechanisms the two briefs list (key rotation and `rewrap`, policies per script, AppRole, response wrapping, JWT auth, OpenBao Agent). The first lab that uses each runs it first.

## PostgreSQL

PostgreSQL 16, with Ubuntu's defaults: one cluster, `16-main`, on `127.0.0.1:5432`; a local connection as the `postgres` system user needs no password (`sudo -u postgres psql`), and a connection over TCP needs one. A lab says `systemctl enable postgresql`, and makes its databases in a seed script or a unit of its own at first boot.

The base changes one setting, `recovery_init_sync_method = syncfs` (`/etc/postgresql/16/main/conf.d/lab.conf`). A lab machine is never shut down cleanly, so PostgreSQL recovers at every boot; without the setting that took 3 s at the first restart and 0.3 s at the next on Docker Desktop (the designer's prototype saw 20 s), and with it under 0.1 s. `postgresql@16-main.service` itself takes 2.3 to 2.6 s to start either way.

## podman

podman builds and runs container images with docker's commands (`podman build`, `podman history`, `podman save`, `podman run`). **It works inside the lab container on Docker Desktop, as root**: a build with two `RUN` steps took 3 s, one with a secret mount (`RUN --mount=type=secret,id=pkg ...` with `--secret id=pkg,src=FILE`) 1.8 s, and the images are still there after a restart. What it needed:

- **`vfs` storage** (`/etc/containers/storage.conf`). The lab machine's disk is an overlay filesystem, and podman's usual `overlay` driver can't stack on one. `vfs` keeps each layer as a plain folder and asks nothing of the kernel.
- **The lab machine's own network** for containers and build steps (`netns = "host"` in `/etc/containers/containers.conf`). With podman's default, each build step got a network of its own through a bridge, a veth pair and iptables rules (that worked on Docker Desktop too), and a `RUN` step could not reach a server on the lab machine at `127.0.0.1`. With the setting, podman needs none of those and the step can. A lesson says once that docker and podman on a real server give each container its own network.
- **`sudo`.** podman as the learner stops with `exec: "newuidmap": executable file not found`: running without root needs user namespaces and the `uidmap` package, which the base leaves out. Prompts say `sudo podman ...`, and say that the commands are docker's too.
- **`apparmor_profile = "unconfined"`** in `containers.conf`, for CI: see "Kernel needs".
- **An image to start from.** A lab machine has no internet and no registry. `lab-busybox-image.service`, which a lab enables, makes an image called `busybox` in podman's store at first boot (1.4 s) from Ubuntu's `busybox-static` and a few folders, with `podman import`; `FROM busybox` then resolves to it. It has `sh`, `cat`, `wget`, `ls` and busybox's other commands in `/bin`, and empty `/etc`, `/opt`, `/root`, `/tmp`, `/usr/bin` and `/var`. It can't be made while the base image is built: podman inside a Docker build has no privilege to make namespaces (`cannot clone: Operation not permitted`).

`podman history --no-trunc IMAGE` shows a build argument in every later step's line (`|1 API_KEY=... /bin/sh -c ...`), and a file a later step deleted is still in the layer that added it, with a `.wh.` file in the deleting layer; `image_has` finds both.

## git and gitleaks

Both are as Ubuntu ships them. Two things to know:

- **A check is root reading the learner's repository,** and git refuses ("detected dubious ownership"). `checklib-sec.sh` sets `safe.directory=*` in the environment of the check's own commands, which gitleaks' git inherits; nothing on the machine changes.
- **A planted secret mustn't be a secret in this repository.** A lab's seed puts a key-shaped value together from pieces (`key="AK""IA""..."`), so that the scanners that watch a public repository don't take the lab's own files for a leak. gitleaks 8.16's default rules found an AWS-shaped access key ID (`AKIA` and 16 capitals and digits) in an earlier commit, as rule `aws-access-token`, and found nothing with `--no-git` once a later commit had removed it. Its report is a JSON list with `Commit`, `File`, `RuleID`, `Secret` and more; it exits 1 when it finds something.

A seed that builds a repository gives every commit a fixed date (`GIT_AUTHOR_DATE`, `GIT_COMMITTER_DATE`), so the commits are the same in every build; a check still works the commit out from the repository (`git log -S"$key"`).

Not tried on the base: gitleaks as a server-side `pre-receive` hook, a custom rule in a `.gitleaks.toml`, and `gitleaks protect` (the secrets brief's fact S1 and Checkpoint 4's third part).

## gcm and lab-seal

`gcm seal IN OUT [--aad TEXT]` and `gcm open IN OUT [--aad TEXT]` encrypt and decrypt a file with AES-256-GCM (`openssl enc` refuses GCM). The key is 32 bytes in base64 on standard input, which is exactly what `transit/datakey/plaintext/NAME` and `transit/decrypt/NAME` of a wrapped data key print, so a key can go from OpenBao to `gcm` through a pipe and never be in a file. A sealed file is the 12-byte random nonce, the ciphertext and the 16-byte tag; `OUT` may be `-` for standard output; a new file is made with mode 0600. A changed byte, a wrong key or different `--aad` text gives `gcm: authentication failed` and exit status 1.

`lab-seal FILE...`, run in a lab's `Dockerfile`, records the checksums of scenery the learner mustn't change in `/root/lab-sums`; the checks' `sealed_ok` compares.

## Check helpers

Checks source `. /usr/local/lib/lab/checklib-sec.sh` and run as root.

| Helper | What it reads |
| --- | --- |
| `bao_root` | from here on the check's `bao` commands use the root token; false when OpenBao was never set up |
| `token_for POLICY [TTL]` | prints a new token with only that policy (and `default`), 5 minutes unless given, for trying what a policy allows |
| `caps TOKEN PATH` | what the token may do at the path, sorted on one line (`create read update`, or `deny`) |
| `audit_saw PATH VALUE` | true when the audit log holds a request to PATH that carried VALUE, sent or returned |
| `on_disk VALUE [SKIP-DIR]` | prints the files under `/home /tmp /srv /var/tmp /etc /run /var/log` that hold VALUE; true when there is one |
| `sealed_ok` | `intact`, or the sealed scenery files that changed |
| `pg SQL [DATABASE]` | the bare answer of SQL run as PostgreSQL's superuser |
| `as_user USER COMMAND...` | COMMAND as that user, with their home folder |
| `image_has IMAGE VALUE` | saves the podman image and prints every place VALUE is in it (`layer 2: tmp/deploy.token`, `history: step 4`, `config`); true when it is anywhere |
| `wait_for TRIES COMMAND...`, `json EXPRESSION` | as in the network base |

`image_has` is `podman save` and `/usr/local/lib/lab/image-search`, whose cases are `tools/tests/test_vault_base.py`. The probe lab uses `bao_root`, `on_disk`, `sealed_ok`, `pg`, `image_has`, `wait_for` and `json`; `token_for`, `caps`, `audit_saw` and `as_user` were tried by hand in that lab's container (a token with one policy got `update` on its path and `deny` on another; a decrypt's plaintext and ciphertext were both found in the audit log, by path, and a value never sent was not), but no lab's contract uses them yet, so the first check that uses one proves it with a wrong fix.

## Rules for checks and labs on the base

Module 3's rules stand (the [network base's README](../net/README.md), and `content/README.md`, "Writing a lab"). From Module 4's brief, section 3.3, and from building this base:

- **Random values a check passes to a command go after `=`** (`--username="$user"`), and are hex where the check makes them.
- **Never file times;** compare content.
- **A check that waits for an account or a lease to end** waits with `wait_for` and its own `timeout:`; the probe's, with a 5-second account, is done in under 10 s.
- **A check may ask OpenBao for a credential of its own** to see what a role gives, and may unwrap a key with the root token; it changes nothing the learner made.
- **Checks that look for a leftover secret say where they looked.** `on_disk` doesn't search `/opt` (OpenBao's store is there, encrypted), `/root` or `/usr`; a lab keeps what only checks may read under `/usr/local/lib/lab/`.
- **A fix lasts.** OpenBao's and PostgreSQL's state is on disk and survives the restart trial; a program a learner started by hand doesn't.

## Kernel needs

Seen on Docker Desktop 29.8.2 (kernel 6.18.33.2-microsoft-standard-WSL2) on 2026-11-22. **Nothing here has run on a GitHub runner yet**: `csa.sec.vault-probes` is the lab that tries it there (Module 4's brief, P4).

| Need | Who | Docker Desktop | GitHub's runner |
| --- | --- | --- | --- |
| systemd as PID 1 in a privileged container with its own cgroup tree | every lab | works | works already (every systemd lab) |
| OpenBao's unit: `ProtectSystem=full`, `PrivateTmp=`, `PrivateDevices=`, `MemorySwapMax=0` (mount namespaces and cgroup settings inside the container) | OpenBao | works | untried |
| podman with `vfs` storage: crun making mount, PID, IPC and UTS namespaces, `pivot_root`, a cgroup under the lab's systemd, and podman's seccomp filter | secrets | works | untried |
| No AppArmor profile for podman's containers | secrets | the kernel has no AppArmor | untried. A runner's kernel has AppArmor; the lab machine has no `apparmor_parser`, and `containers.conf` says `unconfined`, so podman should load nothing. If a build fails there with an AppArmor message, this is the row |
| Not needed: overlayfs, FUSE, user namespaces, a bridge, veth pairs, iptables | | | |

## Files here

| File | What it is |
| --- | --- |
| `Dockerfile` | the image, three layers |
| `openbao.hcl` | OpenBao's configuration, `/etc/openbao/openbao.hcl` |
| `units/` | `lab-bao-key.service`, `lab-bao-init.service`, `lab-busybox-image.service`, and a drop-in that gives OpenBao's unit its log folder |
| `lab-bao-key`, `lab-bao-init` | the first-boot scripts those units run |
| `make-busybox-image` | makes podman's `busybox` image |
| `storage.conf`, `containers.conf` | podman's settings |
| `postgresql-lab.conf` | PostgreSQL's one setting |
| `gcm`, `lab-seal` | helpers in `/usr/local/bin` |
| `checklib-sec.sh`, `image-search` | the check helpers, in `/usr/local/lib/lab/` |

## Size and time

On the owner's PC (2026-11-22). The image holds 812 MB of files; `docker history` adds its layers up to 885 MB (88 MB of Ubuntu, 153 MB of the shared first layer, 644 MB of layer 2), and Docker Desktop reports it as 1.2 GB. The largest parts: OpenBao's one program, 174 MB; LLVM, 118 MB, which PostgreSQL's package depends on and the labs never use; podman with its network plugins, 90 MB; PostgreSQL, 90 MB. (The plan's "about 570 MB" left the first layers out.)

Building layer 2 took 85 s both times it was built, with the first layer already in Docker's cache (a minute of downloading and installing, 20 s of writing the layer); a build with nothing changed takes about 2 s, and a lab's own image on the base a few seconds.

The bare base boots in 0.5 s and uses 13 MiB. The probe lab, with OpenBao, PostgreSQL and the busybox image, booted in 6.3 s the first time (3 s of it OpenBao's setup and seed) and 3.2 to 3.6 s after a restart, and used 79 MiB idle. Its contract run, restart trial and eight wrong fixes included, took 168 s (and 246 s in a run that also rebuilt the image, with other builds busy on the machine), and the container's memory peaked at 113 MiB as `docker stats` sampled it.

# Writing brief: `csa.sec.audit` (topic 46), Audit logging

Design only; nothing here is in the repository. Sources were read on 2026-11-12 and each fact carries its URL. Lab mechanics marked **tried** ran on 2026-11-12 in Docker Desktop 29.8.2 (kernel 6.18.33.2-microsoft-standard-WSL2) on the owner's PC, in privileged systemd containers on `ubuntu:24.04` (systemd 255.4-1ubuntu8.18), started as `labcheck` starts them; everything started was removed afterwards. Prototype files: `prototypes/audit-vuln-compliance/` (`chain/` holds the hash-chain scripts and the tamper tests; `captured/fss-verify.txt` real `journalctl --verify` output). The labs that boot a server run on the shared base designed in [lab-base-sec.md](lab-base-sec.md); read its sections 5 and 6 first.

## 1. What the learner will be able to do

1. Decide which events belong in an **audit trail** (who did what, to what, from where, when, with what outcome) and which don't; say what must never be written to one (passwords, session IDs, tokens, full card numbers) and how a field is masked or left out; recognise log injection.
2. Decide **how long** to keep audit logs from the rules that apply (PCI DSS's 12 months with three immediately available; GDPR's "no longer than is necessary"), size the storage for it, and say what each cloud keeps by default and for how long: CloudTrail's 90-day event history, Azure's 90-day activity log and 7-or-30-day Entra logs, Google Cloud's 400-day `_Required` and 30-day `_Default` buckets.
3. Name each cloud's audit trail and what it misses by default: CloudTrail management against data events; Azure's activity log (control plane) against resource logs (off until a diagnostic setting) and Entra's sign-in and audit logs; Google's Admin Activity (always on) against Data Access logs (off except BigQuery).
4. Make a log **tamper-evident**: build a hash chain in the shell and verify it, find the first broken line, and explain why a chain needs an **anchor** (or a key) to catch a cut-off tail or a full rewrite; read CloudTrail's digest files as the same idea at scale.
5. Seal a real audit trail with journald's **forward-secure sealing**, hand the verification key to someone else, verify it, and tell a sealed `PASS` from an unsealed one; say what an attacker with root can and can't change; choose **write-once storage** (S3 Object Lock compliance or governance mode, Azure immutable blob policies locked or unlocked, Cloud Storage Bucket Lock) and legal holds.

**The six-month core**, which the review pool is built around:

- An audit event answers who, what, when (UTC, from a synchronised clock), where from, and the outcome. Authentication, privilege changes, admin actions and sensitive-data access always; page views never. Secrets never; card numbers as the last four digits at most.
- Default trails are short: CloudTrail event history 90 days of management events; Azure activity log 90 days; Entra Free 7 days; Google `_Default` 30 days, `_Required` (Admin Activity) 400 days. Data-plane audit (S3 object reads, Key Vault secret reads, Google Data Access) is **off** until you turn it on. Anything that must last a year is exported.
- PCI DSS: at least 12 months, the latest three immediately available. "90 days hot" is not "three months".
- A hash chain makes an edit break exactly one link and a deletion break the next; it can't see a missing tail or a complete rewrite unless the latest hash is kept somewhere the attacker can't reach.
- Forward-secure sealing: an intruder with root can change only what came after the last seal; `PASS` without `Validated from … to …` proves nothing. Ship the logs off the box to write-once storage; compliance mode means nobody, root included, can delete before the date.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.sec.crypto]` (topic 42), which reaches `csa.sec.authn-authz` (topic 40) through its own prerequisites. Crypto owns **hash** (`sha256sum`), **MAC/HMAC** (`openssl dgst -sha256 -hmac`), **digital signature** and **key pair**, and already names "an HMAC with a secret key for a log that must not reveal card numbers" and OpenBao's HMAC'd audit log (its brief, read 2026-11-12 once it appeared beside this one); this topic uses those words in its first paragraph on tamper-evidence and never re-teaches them. Topic 40 owns **authentication**, **authorization**, **MFA**, **least privilege** and **separation of duties**, which "what to log" and "who may delete the logs" lean on. `csa.sec.secrets` (topic 45) says secrets must "never be logged" (OWASP) and shows a secret leaking into the journal; if the module's order puts topic 45 before this one, the "never log" list here is retrieval and links to it, otherwise the one-sentence definitions of secret and token are here.

**Builds on (for the writer, not `prerequisites:`):**

| Topic | What this topic uses |
| --- | --- |
| `csa.linux.services` | the journal, `journalctl -u`, `-n`, `--since`, `-o json`, persistent storage (`/var/log/journal`, `Storage=persistent`), `--vacuum-time`, drop-ins and `systemctl daemon-reload`. Its recall items read journal output; this topic never re-teaches them. |
| `csa.linux.hardening` | "logs kept past a reboot and shipped off the machine, so an intruder can't erase their tracks" (its baseline), and the drop-in precedence rule. |
| `csa.linux.scripting`, `csa.linux.shell` | `set -euo pipefail`, `tail`, `cut`, `awk`, `printf`, a script with `chmod +x`. **New here:** `while IFS= read -r line; do … done < file` (searched 2026-11-12: no Module 1 or 3 lesson teaches a read loop), taught in the worked example's step 7 and a recall item before the fill-in needs it. |
| `csa.net.certificates` | **Certificate Transparency**, "public append-only lists" of every public certificate: the lesson's first example of an append-only log. |
| `csa.net.http-tls` | signatures and certificates in one line each, for CloudTrail's signed digests. |

**Terms this topic must define itself:** audit log / audit trail (and how it differs from an application or debug log); event, field, actor (principal); source address; outcome; correlation ID (one sentence; Module 15 owns tracing); UTC and clock synchronisation (one sentence, NTP named; Module 5 `csa.ds.time` owns clocks); log injection; retention, hot and archive storage, storage limitation; control plane and data plane (one sentence each, for audit purposes; `csa.cloud.planes` owns them in Module 8); management event and data event (AWS), activity log, resource log and diagnostic setting (Azure), Admin Activity and Data Access logs, log bucket (Google); tamper-proof against tamper-evident; integrity; hash chain, genesis value, anchor; append-only; WORM, retention period, legal hold, governance and compliance mode, locked and unlocked policy; forward-secure sealing, sealing key, verification key, epoch (interval), journald namespace; `auditd`, watch rule, `auid`.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `what-to-log` | Which events (OWASP's list; PCI DSS 10.2.1's sub-requirements) and which fields (when, where, who, what, outcome; PCI DSS 10.2.2); what never to record and how to mask (last four digits) or hash (a session ID for tracking); log injection; UTC and synced clocks; the audit trail as a separate stream from operational logs; `auditd` watch rules on Linux as the OS-level version (read, not run). |
| `retention` | How long, from the rules that apply (PCI DSS 10.5.1; GDPR Art. 5(1)(e); NIST AU-11 as an organisation-defined value); hot against archive; sizing storage from event rate, size and days; journald's `MaxRetentionSec=` and the 4 GB default cap; the clouds' default windows. **A calculation skill: five estimate items.** |
| `cloud-audit-trails` | What each cloud records with no setup and what it doesn't: CloudTrail event history against trails and data events; Azure activity log, resource logs via diagnostic settings, Entra audit and sign-in logs by licence; Cloud Audit Logs' four types and two buckets; reading who-did-what in a record. |
| `hash-chains` | Chaining each record to the previous hash; what an edit, a deletion, a swap, a cut-off tail and a rewrite each look like to a verifier; the anchor; CloudTrail's hourly signed digests that chain to the previous digest; CT logs as the public version. |
| `sealing-and-worm` | journald's forward-secure sealing: keys, interval, verification, what root can and can't change, `PASS` without `Validated`; shipping off the box; write-once storage on three clouds (S3 Object Lock modes, Azure time-based retention locked or unlocked and legal hold, GCS Bucket Lock) and legal holds. |

Five skills; each is practised before a proof asks for it (section 7.9) and has at least two come-back questions (section 9).

## 4. Lesson plan

About 2,000 words (15 minutes), around the OWASP Logging Cheat Sheet as the main resource.

1. **Two kinds of log (lesson only).** An operational log helps you fix the system ("cache miss", "retrying"); an **audit trail** answers "who did what, to what, when, from where, and did it work?" for an investigator or an auditor, months later. Picture a bank's ledger beside its engineers' notebooks: the notebook can be thrown away; the ledger must be complete, unchangeable and kept for years. The two go to different places with different rules (this topic's labs give the audit trail its own journal namespace, which is what that separation looks like on one server).
2. **What to record (OWASP, "Which events to log", "Event attributes", "Data to exclude").** OWASP's always-log list (authentication successes and failures, authorization failures, session management failures, use of higher-risk functionality such as user administration, admin actions, access to sensitive data, key use; application and logging start-ups and shut-downs). PCI DSS 10.2.1 names the same for systems holding card data, including "all invalid logical access attempts" and "all changes to identification and authentication credentials" (quoted from Microsoft's PCI requirement 10 page, fact 9). Each event's fields: when (UTC, ISO 8601, from a synced clock: without it events from two servers can't be put in order; PCI DSS 10.6), where (host, service, source address), who (the user or the service's identity), what (event type, the object, the action), outcome. **Never** record a password, a session ID (a hash of it if you must track a session), an access token, a key, a full card number; a card number may appear as its last four digits. The lesson's picture: a CCTV camera on a door records who went in and when, not the PIN they typed.
3. **Log injection (OWASP, "Attacks on Logs").** A user name containing a newline can forge a second, fake line; fields are encoded (newlines and separators escaped) before they're written. One example in the lab's own format.
4. **How long (lesson only, with the sources' numbers).** Retention comes from the rules: PCI DSS 10.5.1, "Retain audit log history for at least 12 months, with at least the most recent three months immediately available for analysis"; GDPR Article 5(1)(e), personal data "kept … for no longer than is necessary", so an audit trail full of user names is deleted after its period too; NIST SP 800-53's AU-11 leaves the number to the organisation. Hot (searchable now) against archive (restored on request). Sizing: events a day × bytes an event × days. journald's own limits: `MaxRetentionSec=` deletes files older than the span (default 0, off), and `SystemMaxUse=` defaults to 10% of the filesystem **capped at 4 GB** (journald.conf(5)), so a busy server's default journal silently forgets long before a year.
5. **Tamper-evident, not tamper-proof (lesson only; the picture the resources don't give a beginner).** Anyone with root can change a file; what we can arrange is that a change can't go *unnoticed*. Start with the hash from topic 42: change one character and the hash changes completely. A **hash chain** writes, on every line, the hash of the previous line's hash plus this line's record. Draw it as a paper chain: each link is made through the one before. Edit line 7's record and line 7's link no longer fits; delete line 7 and line 8's link points at a link that's gone; swap two lines and the first of them breaks. Two things a chain can't see on its own: lines cut off the end (every remaining link still fits), and an attacker who edits line 7 and **re-makes every link after it**. Both are caught by an **anchor**: the latest hash, copied somewhere the attacker can't reach (another server, a printout, a signed message), or by a key the attacker doesn't have (an HMAC, topic 42). CloudTrail does exactly this at scale (fact 2): every hour a digest file lists each log file's SHA-256 hash, carries the previous digest's signature, and is signed with SHA-256 with RSA; validation then says whether a log file was "modified, deleted, or unchanged". Certificate Transparency's logs (topic 32) are the public, append-only version.
6. **Forward-secure sealing (LWN's "Forward secure sealing", journalctl(1) `--setup-keys` and `--verify`).** journald seals its files every interval (15 minutes by default) with a key that **changes at every interval and can't be turned back**: the machine keeps only the current sealing key, and the verification key, which can work out every past sealing key, is kept elsewhere ("The verification key should be stored externally", fact 12). So an intruder who becomes root at 14:07 can change what was written since the last seal at 14:00 and anything after, but not 13:59. `journalctl --verify --verify-key=KEY` then prints `PASS` and **`Validated from … to …, final N s entries not sealed`**. The trap the lab shows: a journal that was never sealed, or one an attacker rewrote completely, also prints `PASS`, without the `Validated` line (tried, fact 15). Read the line, not the word. Why the lab's audit trail is a **journald namespace** (`LogNamespace=audit`, `journalctl --namespace=audit`): its own files, its own settings in `/etc/systemd/journald@audit.conf`, persistent by default; and one sentence on the lab's plumbing (lab-base-sec.md, section 5): its journal service stops "the way a crash does", because a clean restart breaks the seal on this version of systemd.
7. **Off the box and write-once (the three clouds' pages).** Sealing detects; it doesn't keep the evidence from being deleted. So audit logs are shipped to a collector the server's own admins can't change, ideally into **write-once (WORM) storage**. **Where the clouds differ** (facts 18 to 20):
   - **S3 Object Lock** needs versioning; **compliance mode**: "a protected object version can't be overwritten or deleted by any user, including the root user", and the retention can't be shortened; **governance mode**: users with `s3:BypassGovernanceRetention` can. A **legal hold** has no end date until removed.
   - **Azure immutable blob storage**: time-based retention (1 day to 146,000 days) and legal holds; a policy starts **unlocked** (can be shortened or deleted, for testing), and once **locked** can be extended but never shortened or deleted; container-level or version-level.
   - **Cloud Storage Bucket Lock**: a bucket retention policy (up to 100 years) that, once locked ("an irreversible action"), can be increased but not removed or shortened; Object Retention Lock per object.
   The architect's rule of thumb: governance or unlocked while testing, compliance or locked for the real trail, and the delete permission held by nobody who administers the servers (separation of duties, topic 40).
8. **What each cloud records with no setup (the clouds' audit pages).** **Where the clouds differ** (facts 3 to 8): CloudTrail is on by default, with a 90-day "immutable record of the past 90 days of management events" per region in event history, no data events; a trail or a CloudTrail Lake store keeps more. Azure's activity log records control-plane writes for 90 days, free, and "isn't an authentication or authorization audit log" (requests rejected before an operation starts aren't in it); data-plane **resource logs** "aren't collected by default and require configuration with a diagnostic setting"; Entra keeps audit and sign-in logs 7 days on the Free licence and 30 on P1 or P2. Google writes Admin Activity, System Event and Policy Denied logs always; **Data Access** logs are off except for BigQuery; `_Required` keeps 400 days and can't be changed, `_Default` 30 days. Module 15 (`csa.ops.audit-logs`) collects all three into one place; this topic is about knowing the gaps.
9. **The OS level, briefly: auditd (lesson only).** On a Linux server the kernel's audit system, driven by `auditd`, records system calls and file access: a watch rule `-w /etc/shadow -p wa -k identity` records every write or attribute change to the password file, tagged `identity`, and each record carries `auid`, the ID the person **logged in** with, which survives `sudo`. The labs can't run it: the kernel allows audit control only from the machine's first process namespace (fact 16), so the lab reads the rule files the `auditd` package ships instead. Topic 49 will map these rules to PCI DSS requirements.

**Read now:** the OWASP Logging Cheat Sheet's sections "Which events to log", "Event attributes", "Data to exclude", "Protection" and "Attacks on Logs" (about 2,200 of its 3,500 words); LWN's "Forward secure sealing"; AWS's "Validating CloudTrail log file integrity". Optional: the Google Cloud Audit Logs overview, Azure's activity log page ("Activity log entries" and "Retention period"), S3 Object Lock.

## 5. Verified facts

All read on 2026-11-12.

| # | Claim | Source |
| --- | --- | --- |
| 1 | NIST SP 800-92, *Guide to Computer Security Log Management*, final, September 2006, is still the final version. SP 800-92 Rev. 1, *Cybersecurity Log Management Planning Guide*, is an **Initial Public Draft** of 2023-10-11 (comments closed 2023-11-29), a playbook, not yet final. | https://csrc.nist.gov/pubs/sp/800/92/final ; https://csrc.nist.gov/pubs/sp/800/92/r1/ipd |
| 2 | CloudTrail log file integrity validation uses "SHA-256 for hashing and SHA-256 with RSA for digital signing"; hourly digest files reference and hash the last hour's log files; "Each digest file also contains the digital signature of the previous digest file"; validation tells whether a log file "was modified, deleted, or unchanged". | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html |
| 3 | CloudTrail is on by default; event history is "a viewable, searchable, downloadable, and immutable record of the past 90 days of management events in an AWS Region", no charge; it "only shows management events. It does not show data events, Insights events, or network activity events"; an ongoing record needs a trail or an event data store. | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html |
| 4 | Azure activity log: control-plane operations; "Azure retains activity log events for 90 days and then deletes them. You aren't charged for entries during this time"; "Activity Log isn't an authentication or authorization audit log" (rejected requests generate no entries); resource logs (data plane) "aren't collected by default and require configuration with a diagnostic setting"; Log Analytics retention can be raised to 12 years (ms.date 2026-11-03). | https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log |
| 5 | Entra ID keeps audit logs and sign-ins 7 days on Free and 30 days on P1 and P2; longer by routing to storage through Azure Monitor (ms.date 2026-01-06). | https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-reports-data-retention |
| 6 | Cloud Audit Logs: Admin Activity "always written; you can't configure, exclude, or disable them"; System Event the same; Policy Denied generated by default and charged for storage; "Except for BigQuery, Data Access audit logs are disabled by default", and enabling them may be charged. | https://docs.cloud.google.com/logging/docs/audit |
| 7 | Log buckets: `_Required` 400 days, not configurable; `_Default` 30 days by default (configurable for projects); user-defined buckets 1 to 3,650 days. | https://docs.cloud.google.com/logging/quotas |
| 8 | OWASP Logging Cheat Sheet: events to always log (as in lesson idea 2), the when/where/who/what attributes, data to exclude (session IDs, access tokens, passwords, keys, payment card data …, a hashed session ID if tracking is needed), protection at rest ("build in tamper detection"), and log injection; licensed **CC BY-SA 4.0**. | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html |
| 9 | PCI DSS v4 text as Microsoft quotes it: 10.2.1.4 "Audit logs capture all invalid logical access attempts"; 10.2.2 the details per event (user identification, type, date and time, success or failure, origination, the affected resource); 10.3.2 audit log files "protected to prevent modifications by individuals"; 10.3.3 "promptly backed up to a secure, central, internal log server(s) or other media that is difficult to modify"; 10.3.4 file-integrity monitoring on audit logs; **10.5.1 "Retain audit log history for at least 12 months, with at least the most recent three months immediately available for analysis"**; 10.6.1 synchronised clocks. (Microsoft's page, CC BY 4.0; the PCI DSS document itself was not opened: its library page needs a browser.) | https://learn.microsoft.com/en-us/entra/standards/pci-requirement-10 |
| 10 | GDPR Article 5(1)(e): personal data "kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed". | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679 |
| 11 | OWASP Top 10:2025 lists A09 "Security Logging and Alerting Failures". | https://owasp.org/Top10/2025/ |
| 12 | `journalctl --setup-keys` generates a sealing key, "stored in the journal data directory and shall remain on the host", and a verification key that "should be stored externally"; `--interval` defaults to 15min; `--verify` checks internal consistency and, with `--verify-key`, authenticity. | https://www.freedesktop.org/software/systemd/man/latest/journalctl.html |
| 13 | journald.conf on Ubuntu 24.04 (systemd 255.4-1ubuntu8.18): `Storage=` "Defaults to "auto" in the default journal namespace, and "persistent" in all others"; `Seal=` on by default when a sealing key exists; `RateLimitIntervalSec=`/`RateLimitBurst=` default 10000 messages in 30 s per service, 0 disables; `MaxRetentionSec=` default 0 (off); `SystemMaxUse=` 10% of the filesystem capped at 4G; `ReadKMsg=` on only in the default namespace; namespace instances read `journald@NAMESPACE.conf`. | https://manpages.ubuntu.com/manpages/noble/man5/journald.conf.5.html ; https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html |
| 14 | LWN, "Forward secure sealing", Jake Edge, 2012-08-22: sealing at intervals, 15 minutes by default; the sealing key on the system, the verification key elsewhere, able to derive past sealing keys; an intruder gets only the current key; CC BY-SA 4.0. | https://lwn.net/Articles/512895/ |
| 15 | **Tried:** sealing an `audit` journald namespace: `PASS` and `=> Validated from Thu 2026-11-12 19:53:49 UTC to … 19:54:20 UTC, final 4.308091s entries not sealed.` One byte changed in a copy: `391f18: Invalid hash …`, `FAIL: … (Bad message)`. The same copy exported, edited and re-imported with `systemd-journal-remote`: `PASS` with **no** `Validated` line, with and without the key, and its header lacks `SEALED`. Without `--verify-key`, a sealed file reports `FAIL … (Required key not available)`. | prototype; `captured/fss-verify.txt` |
| 16 | **Tried:** `auditctl -s` in a privileged container: `Error sending status request (Operation not permitted)`; the kernel's `audit_netlink_ok()` returns `-EPERM` for audit control unless `task_active_pid_ns(current) == &init_pid_ns` ("Only support auditd and auditctl in initial pid namespace for now"). | https://raw.githubusercontent.com/torvalds/linux/master/kernel/audit.c (read 2026-11-12) |
| 17 | **Tried:** journald's rate limit on the `audit` namespace with `RateLimitBurst=50`: a burst of 500 lines kept 187 (the burst is scaled by free disk space), and once the interval passed the namespace logged `systemd-journald[5615]: Suppressed 343 messages from burst-test2.service`. | prototype |
| 18 | S3 Object Lock: WORM; works only with versioning; compliance mode: no user "including the root user" can overwrite or delete during retention, retention can't be shortened; governance mode: removable with `s3:BypassGovernanceRetention`; legal hold has no expiry until removed. | https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html |
| 19 | Azure immutable storage: time-based retention and legal holds; minimum 1 day, maximum 146,000 days; unlocked policies can be shortened, extended or deleted (for testing); locked ones can be extended but not shortened or deleted, at most five increases for a container-level policy; container-level and version-level WORM (ms.date 2026-08-18). | https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview |
| 20 | Cloud Storage: a retention policy blocks deletes and replacements until objects are older than it; "Locking a bucket's retention policy is an irreversible action"; locked policies can be increased only; maximum 3,155,760,000 s (100 years); Object Retention Lock per object. | https://docs.cloud.google.com/storage/docs/bucket-lock |
| 21 | Ubuntu 24.04's `auditd` package is 1:3.1.2-2.1ubuntu0.1; audit-userspace (GPL-2.0) ships sample rule files mapped to PCI DSS (`rules/30-pci-dss-v31.rules`). | `apt-cache policy auditd` (prototype); https://github.com/linux-audit/audit-userspace |

**Not confirmed:** OMB M-21-31's federal retention figures (12 months active, 18 months cold) were not read: no item uses them. The CloudTrail record's field names (`userIdentity`, `eventName`, `sourceIPAddress`, `eventTime`) are from memory: the writer reads AWS's "CloudTrail record contents" page before writing `cloudtrail-who`. The PCI DSS wording is Microsoft's quotation, not the standard opened directly.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | OWASP Logging Cheat Sheet: read "Which events to log", "Event attributes", "Data to exclude", "Protection", "Attacks on Logs" | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html | reading | CC BY-SA 4.0 (page footer). Linked | 17 (about 2,200 of 3,500 words) | what-to-log, sealing-and-worm | 2026-11-12 |
| 1 | "Forward secure sealing", Jake Edge (LWN, 2012) | https://lwn.net/Articles/512895/ | reading | © 2012 Eklektix, CC BY-SA 4.0. Linked | 7 (about 900 words) | sealing-and-worm | 2026-11-12 |
| 2 | "Validating CloudTrail log file integrity" (AWS) | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html | reading | © AWS. Linked | 5 | hash-chains | 2026-11-12 |
| 3 | "Cloud Audit Logs overview" (Google Cloud), the four log types, optional | https://docs.cloud.google.com/logging/docs/audit | reading | Google Cloud docs, CC BY 4.0 (the writer confirms the footer in a browser; the fetch showed none) | 6 | cloud-audit-trails | 2026-11-12 |
| 4 | "Activity Log in Azure Monitor": "Activity log entries" and "Retention period" only, optional | https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log | reading | Microsoft Learn, CC BY 4.0 (MicrosoftDocs). Linked | 3 | cloud-audit-trails, retention | 2026-11-12 |
| 5 | "Locking objects with Object Lock" (AWS), "Retention modes" and "Legal holds", optional | https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html | reading | © AWS. Linked | 6 | sealing-and-worm | 2026-11-12 |
| 6 | journalctl(1): `--setup-keys`, `--interval`, `--verify`, `--verify-key` entries, reference | https://www.freedesktop.org/software/systemd/man/latest/journalctl.html | reference | systemd documentation (LGPL-2.1+ with the source). Linked | 3 | sealing-and-worm | 2026-11-12 |
| 7 | "How CT works" (Certificate Transparency), optional | https://certificate.transparency.dev/howctworks/ | reading | no licence shown. Linked | 6 | hash-chains | 2026-11-12 |

No video is assigned; none was opened and timed.

## 7. Practice ladder

Labs that boot the payments server are systemd labs `FROM lab-base-sec` with `lab: { init: systemd, restart_trial: true }`. The fill-in and the write are plain labs on Module 3's plain `RUN` line (no server). Machines don't come into it: these labs are one server.

### 7.1 `example-seal-and-tamper` (worked example, systemd lab), skills `sealing-and-worm`, `hash-chains`

The shop's audit writer (`shop-audit.service`, `LogNamespace=audit`) is running with the image's `audit.conf`. Labelled steps (a "Before your first Module 4 server lab" note first: one machine, `shop-cli` makes the shop do things, the audit trail is `journalctl --namespace=audit`):

1. **See the trail.** `shop-cli refund order=42 amount=19.99`, then `journalctl --namespace=audit -n 3`. Point at who, what, where, outcome.
2. **Is it sealed?** `sudo journalctl --namespace=audit --header | grep -i flags`: no `SEALED`.
3. **Make the keys.** `sudo journalctl --setup-keys --interval=10s` (the lab's 10 seconds stands for the default 15 minutes; the prompt says so). Copy the last line, the verification key, into `~/example/verify-key.txt`, "which in real life goes to someone who doesn't run this server".
4. **Seal.** `sudo nano /etc/systemd/journald@audit.conf`, add `Seal=yes`, `sudo systemctl restart systemd-journald@audit`. Another refund; wait 15 s.
5. **Verify.** `sudo journalctl --namespace=audit --verify --verify-key="$(cat ~/example/verify-key.txt)"`: `PASS` and `Validated from … to …`. Save the output to `~/example/verify.txt`.
6. **Tamper with a copy.** `sudo cp /var/log/journal/*.audit/system.journal ~/example/copy.journal`, `sudo lab-flip ~/example/copy.journal amount=19.99 amount=91.99` (the base's helper changes those bytes, same length), verify the copy: `Invalid hash`, `FAIL`.
7. **The careful attacker, and a loop.** `sudo lab-forge-journal ~/example/copy-of-real.journal ~/example/forged.journal` rewrites a copy the way an attacker who knows the format would; verify it: `PASS`, no `Validated` line. Save to `~/example/forged.txt`. Then the read loop, which the fill-in and write need: `while IFS= read -r line; do echo "got: $line"; done < ~/example/events.txt`, with what `IFS=` and `-r` stop (trimmed spaces, eaten backslashes) shown on a line that has both.

Checks (end states): `sealed` (the key in `verify-key.txt` verifies the live namespace with a `Validated` range ending within the last 30 s, via `seal-range`); `verify-saved` (`verify.txt` contains `Validated from`); `copy-fails` (`copy.journal` fails verification with that key); `forged-unsealed` (`forged.journal`'s header has no `SEALED`, and `forged.txt` has `PASS` and no `Validated`). Wrong fixes: `key-not-saved.sh` (keys made, file empty), `old-key.sh` (keys made twice with `--force`, the first key saved: verification of the new file fails), `seal-not-restarted.sh` (file edited, journald not restarted: no seals). About 25 minutes; contract about 2 minutes (seal waits of 12 s).

### 7.2 Recall on what to log

Every multiple-choice item follows content/README.md's length rules; the brief gives the scenario, the right answer and the distractor ideas, and the writer writes each choice out in full and measures before anything else.

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-audit-or-not` | mcq | what-to-log | Which set of the shop's events belongs in the audit trail? Right: sign-ins (successful and failed), role changes and refunds. Distractors: page views, searches and errors; every request at debug level; failed requests only (OWASP logs successes too). |
| `mcq-never-in-the-trail` | mcq | what-to-log | A password reset event: which field must not be written? Right: the session ID in full. Distractors (each a field the trail needs): the user name; the source address; the outcome. The explanation adds the hashed-session-ID option and the PCI card rule. |
| `mask-card` | predict_shell | what-to-log | A captured `shop-audit` line `event=card.update user=ana card=4111111111111111 outcome=ok` and `sed -E 's/card=[0-9]{12}([0-9]{4})/card=************\1/'`. Prints the line with `card=************1111`. Pin by running in Git Bash and with Ubuntu's `sed`. |
| `mcq-log-injection` | mcq | what-to-log | A user signs up as `bob` followed by a newline and `event=role.change user=bob role=admin`. Right: the second line looks like a real event; fields must be written with newlines escaped. Distractors: the trail rejects the name; only the user's own view is affected; a sealed journal stops it (sealing proves who wrote the file, not that each field is honest). |
| `mcq-utc-clock` | mcq | what-to-log | Two servers' audit lines disagree on which refund came first. Right: their clocks aren't synchronised to the same source (PCI DSS 10.6), so their timestamps can't be compared. Distractors: one uses UTC and one local time (true problem, but the line says both are UTC); journald reorders entries; the refunds were sealed in different epochs. |
| `audit-rule-keys` | predict_shell | what-to-log | A constructed `audit.rules` in auditd's real syntax (five lines: `-w /etc/shadow -p wa -k identity`, `-w /etc/sudoers -p wa -k scope`, `-w /etc/ssh/sshd_config -p wa -k sshd`, an `-a always,exit … -S execve -F euid=0 -F auid>=1000 -F auid!=unset -k rootcmd`, and `-w /var/log/journal -p wa -k logs`). `awk '{for (i=1;i<=NF;i++) if ($i=="-k") print $(i+1)}' audit.rules \| sort -u`. Prints the five keys. Teaches the anatomy; the explanation says what `-p wa` means. |
| `mcq-auid` | mcq | what-to-log | Why do audit records carry `auid` as well as `uid`? Right: `auid` is the ID the person logged in with and stays the same through `sudo`, so root's actions trace back to a person. Distractors: `auid` is the audit daemon's own ID; it's the ID of the file's owner; it's a random ID per event. |

### 7.3 Recall on retention (calculation skill, five estimates)

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `est-trail-size` | estimate | retention | The payments service writes 60,000 audit events a day, about 300 bytes each in the journal. How many GB (1 GB = 1,000,000,000 bytes) for 395 days? Within 5%. **7.11** (`events * size * days / 1000000000`). Mistakes: 6.57 (365 days: "the year, not the year and a month the policy keeps"), 0.018 (one day). |
| `est-event-history-gap` | estimate | retention | An investigation on 12 November needs every AWS management event since 1 June (164 days). The account has no trail, only event history. How many of those days are missing? Exactly. **74** (`window - 90`). Mistakes: 90 (the history's length), 164 (thinking nothing is kept). |
| `est-entra-free` | estimate | retention | A monthly access review covers the last 30 days of Entra sign-ins. The tenant has Entra ID Free and exports nothing. How many of those days can't be seen? Exactly. **23** (`review - 7`). Mistakes: 0 (P1's 30 days), 7. |
| `est-hot-quarter` | estimate | retention | The SIEM keeps 90 days searchable and archives the rest. On 30 September an auditor asks for July to September (92 days) "immediately available". How many days of it are in the archive? Exactly. **2** (`92 - 90`). Mistakes: 0 ("90 days is three months"), 90. A deliberate knife edge, said in the explanation: PCI DSS counts months. |
| `est-journal-cap` | estimate | retention | A server's `/var` is 120 GB, and journald runs with its defaults. At 25 MB of journal a day, about how many days does it keep? Within 10%. **160** (`min(120 * 1000 * 0.10, 4000) / 25`, the 4 GB cap written as a known number). Mistakes: 480 (10% without the cap), 4800 (the whole disk). |
| `mcq-gdpr-forever` | mcq | retention | "Keep the audit trail forever, to be safe." Right: the trail holds personal data (names, addresses), so GDPR requires deleting it once its purpose and period are over. Distractors: forever is required by PCI DSS; storage is the only cost; sealed logs are exempt. |

### 7.4 Recall on the clouds' trails

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-cloudtrail-default` | mcq | cloud-audit-trails | A new AWS account, nothing configured. What's recorded? Right: 90 days of management events per region in event history. Distractors: 90 days of every API call including S3 object reads; nothing until a trail exists; management events kept indefinitely. |
| `mcq-s3-read-missing` | mcq | cloud-audit-trails | Someone downloaded objects from a bucket last week; event history shows nothing. Right: object reads are data events, which event history never shows and a trail records only when data events are selected. Distractors: the events are in another region's history; downloads by the account owner aren't logged; CloudTrail delays data events by 30 days. |
| `mcq-azure-rejected` | mcq | cloud-audit-trails | An attacker's attempts to delete a VM are refused by Azure Resource Manager's authorization. Where are they in the activity log? Right: they aren't; requests rejected before an operation starts generate no activity log entries. Distractors: as failed writes with status Forbidden; in the activity log's Security category; after the 15-minute delay. (Re-check the page's "Important" note on the day.) |
| `mcq-keyvault-reads` | mcq | cloud-audit-trails | Who read a Key Vault secret yesterday? Right: Key Vault's resource logs, which exist only if a diagnostic setting sends them somewhere. Distractors: the activity log; Entra audit logs; Key Vault keeps reads for 90 days by itself. |
| `mcq-gcp-off-by-default` | mcq | cloud-audit-trails | Which Cloud Audit Logs must you switch on? Right: Data Access logs (except BigQuery's). Distractors: Admin Activity logs; System Event logs; Policy Denied logs. |
| `cloudtrail-who` | predict_shell | cloud-audit-trails | A constructed CloudTrail record (the real field names, confirmed in AWS's record-contents page first), pretty-printed one field a line; `grep -E '"(eventName\|sourceIPAddress\|arn)"' rec.json \| cut -d'"' -f4`. Prints the ARN, the event name and the address: who, what, from where. |

### 7.5 `fill-chain-add` (fill-in, plain lab), skills `hash-chains`

`~/bin/chain-add LOG RECORD...` with gaps (the prototype's reference is `prototypes/audit-vuln-compliance/chain/chain-add`): the genesis value (`0` × 64), which line's hash to start from (`tail -n 1 "$log" | cut -d' ' -f1`), what is hashed (`printf '%s %s' "$prev" "$record"`), and the line written (`printf '%s %s\n' "$hash" "$record"`). The prompt names `sha256sum`, `cut`, `printf` and why `printf '%s'` rather than `echo` (no added newline, no `%` surprises); it says which gaps stop bash and which run wrongly, as content/README.md requires.

Checks make their inputs at check time and compute the truth independently (in `python3`'s `hashlib`, not with the learner's tools):
- `first-line`: three random records into an empty log; line 1's hash is SHA-256 of 64 zeros, a space and record 1.
- `continues-a-chain`: appends to a log of random length made by the check; the new line chains to the old last line.
- `exact-bytes`: records containing `%`, a backslash, `$`, double quotes, a tab and two spaces, every run (fixed set, random order): hashes exact.
- `format`: each line is 64 lowercase hex, one space, the record.

Wrong fixes: `echo-newline.sh` (`echo "$prev $record" \| sha256sum`), `first-line-hash.sh` (`head -n 1`), `record-only.sh` (hashes the record alone), `format-string.sh` (`printf "$prev $record"`, fails on `%`), `empty-genesis.sh` (empty previous hash). About 25 minutes; contract about 1 minute.

### 7.6 Recall on hash chains

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `chain-edited-line` | predict_shell | hash-chains | A five-line chained log, made with the reference `chain-add`, whose line 3 record was edited afterwards (hash left alone), and the reference `chain-verify` as a script file beside it. Command `bash chain-verify audit.log "$(cat anchor)"`. Prints `broken at line 3`. The explanation: an edit breaks only its own link. |
| `chain-deleted-line` | predict_shell | hash-chains | The same log with line 3 deleted. Prints `broken at line 3` (the old line 4 is now line 3, and its link points at the deleted line's hash). The explanation spells out the renumbering, which is the point. |
| `mcq-chain-blind-spot` | mcq | hash-chains | With no anchor, which change can't a verifier detect? Right: the last lines cut off the end. Distractors: one edited line in the middle; a deleted middle line; two lines swapped. |
| `mcq-rewrite-everything` | mcq | hash-chains | An intruder with root edits line 50 and recomputes every hash after it. What catches it? Right: comparing the last hash with a copy kept where the intruder couldn't reach. Distractors: running the verifier twice; the file's modification time; a longer hash such as SHA-512. |
| `mcq-cloudtrail-digest` | mcq | hash-chains | What does a CloudTrail digest file hold? Right: the SHA-256 hash of each log file delivered in the hour, and the previous digest's signature, all signed. Distractors: a copy of each log file, compressed; the hash of the bucket's contents at midnight; the list of users who read the logs. |
| `mcq-ct-append-only` | mcq | hash-chains | Retrieval of topic 32: Certificate Transparency logs are append-only; what does that let a domain owner do? Right: find a certificate for their name that they never asked for. Distractors: revoke a certificate faster; hide a certificate from the public; stop a CA from issuing one. |

### 7.7 `write-chain-verify` (write, plain lab), skills `hash-chains`

Prompt: write `~/bin/chain-verify LOG ANCHOR` for the shop's chained audit log. `ANCHOR` is the last hash as the auditors last saw it. It prints exactly one line and exits 0 for `ok N` (every line's hash is right and the last one equals the anchor; N is the number of lines), otherwise 1 with `broken at line K` (the first line whose hash isn't the SHA-256 of the previous line's hash, a space and its record; line 1's previous hash is 64 zeros) or `anchor mismatch` (every line chains, but the last hash isn't the anchor). The prompt names `while IFS= read -r line`, `${line%% *}` and `${line#* }` (the hash and the record), `sha256sum`, `cut`, and `nano ~/bin/chain-verify` with `chmod +x`.

Checks each make a random log at check time (8 to 40 records, random content, always including one record of each tricky kind: `%`, backslash, `$`, double quotes, a tab, two spaces), tamper with a copy, run the learner's script and compare with the expected verdict:

| Check | Tamper | Expect |
| --- | --- | --- |
| `intact` | none | `ok N` |
| `edited` | a random line's record changed, hash left | `broken at line K` |
| `deleted` | a random middle line removed | `broken at line K` |
| `swapped` | two neighbouring lines swapped | `broken at line K` (the first of the two) |
| `truncated` | the last 1 to 3 lines removed | `anchor mismatch` |
| `rewritten` | line K edited and every later hash recomputed | `anchor mismatch` |
| `exit-status` | one intact and one broken log | exit 0 and 1 |

**Tried** (prototype `chain/gen-and-test.sh`): the reference passed all six verdicts in three runs (logs of 9, 16 and 31 lines, 0.5 to 1.9 s a run). `w-no-anchor` failed `truncated` and `rewritten` every run; `w-echo` failed everything; **`w-no-raw` (`read line` without `IFS=` and `-r`) passed one run of three** when no backslash record happened to be drawn, which is why the tricky records are in every log, not drawn at random.

Wrong fixes: `no-anchor.sh`, `read-not-raw.sh`, `echo-hash.sh`, `last-line-only.sh` (compares only the last line's hash with the anchor), `off-by-one.sh` (reports K+1), `always-ok.sh` (prints `ok` and the line count). About 40 minutes; contract about 2 minutes.

### 7.8 Recall on sealing and write-once storage

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `mcq-root-at-1407` | mcq | sealing-and-worm | A server seals its journal every 15 minutes; an intruder becomes root at 14:07. Right: they can change entries written since the 14:00 seal and everything after, but not earlier ones. Distractors: nothing at all; everything since the last reboot; only entries in files they open. |
| `est-unsealed-window` | estimate | sealing-and-worm | Sealing every 15 minutes, the last seal at 09:45, intrusion at 09:56. How many minutes of earlier entries can be altered without a failed verification? Exactly. **11** (`intrusion - last_seal`). Mistakes: 15 (the interval), 0. |
| `verify-pass-or-sealed` | predict_shell | sealing-and-worm | Two captured verification outputs (the prototype's: a sealed file and the forged copy). `grep -c 'Validated from' sealed.txt forged.txt`. Prints `sealed.txt:1` and `forged.txt:0`. The explanation: both say `PASS`. |
| `mcq-key-where` | mcq | sealing-and-worm | Where does the verification key go? Right: off the server, with someone who doesn't administer it. Distractors: beside the journal so verification is quick; in root's home with mode 600; in the sealed journal itself. |
| `mcq-object-lock-mode` | mcq | sealing-and-worm | Audit logs in S3 must be undeletable by anyone, root included, for 400 days. Right: Object Lock in compliance mode with a 400-day retention. Distractors: governance mode (bypassable with a permission); a legal hold (no date, removable by anyone with the permission); versioning alone. |
| `mcq-azure-unlocked` | mcq | sealing-and-worm | An Azure container's time-based policy is unlocked. Right: it protects blobs but can still be shortened or deleted, so it's for testing; lock it for the real trail. Distractors: it doesn't protect anything yet; it can be extended but not shortened; it becomes locked after 24 hours by itself. |
| `mcq-legal-hold` | mcq | sealing-and-worm | Logs must be kept until a lawsuit ends, date unknown. Right: a legal hold. Distractors: a compliance-mode retention of ten years; a locked bucket retention policy; deleting nothing and hoping. |
| `mcq-gcs-lock-undo` | mcq | sealing-and-worm | A team locked a Cloud Storage bucket's retention policy at 10 years by mistake. Right: it can't be shortened or removed; the bucket can be deleted only when every object has met it. Distractors: Google support can unlock it; it can be shortened within 24 hours; deleting the project removes the lock at once. |

### 7.9 Ladder order for `topic.yaml`

`example-seal-and-tamper`, `mcq-audit-or-not`, `mcq-never-in-the-trail`, `mask-card`, `mcq-log-injection`, `audit-rule-keys`, `est-trail-size`, `est-event-history-gap`, `est-entra-free`, `mcq-cloudtrail-default`, `mcq-s3-read-missing`, `mcq-keyvault-reads`, `mcq-gcp-off-by-default`, `fill-chain-add`, `chain-edited-line`, `chain-deleted-line`, `mcq-chain-blind-spot`, `mcq-rewrite-everything`, `mcq-cloudtrail-digest`, `write-chain-verify`, `mcq-root-at-1407`, `est-unsealed-window`, `verify-pass-or-sealed`, `mcq-object-lock-mode`, `mcq-azure-unlocked`. That is 22 quick items (about 33 minutes), a worked example, a fill-in and a write. Review-only: `mcq-utc-clock`, `mcq-auid`, `est-hot-quarter`, `est-journal-cap`, `mcq-gdpr-forever`, `mcq-azure-rejected`, `cloudtrail-who`, `mcq-ct-append-only`, `mcq-key-where`, `mcq-legal-hold`, `mcq-gcs-lock-undo`.

Multiple choice: 17 in the ladder and 9 review-only. The writer measures lengths before anything else (right answer the longest in at most a third).

**Practised before proven:**

| Skill | Practised in |
| --- | --- |
| what-to-log | five ladder items; the build is the first time the learner edits `audit.conf`, so the worked example's step 1 shows the file and one `audit` line (add: "read `/etc/shop/audit.conf`" to step 1) |
| retention | three estimates; `MaxRetentionSec=` and `SystemMaxUse=` appear in the lesson's idea 4 and in `est-journal-cap`. **Writer's choice:** move `est-journal-cap` into the ladder, since the build sets both settings. Recommended. |
| cloud-audit-trails | four ladder items (asked in the explain, not in a lab) |
| hash-chains | the example's loop step, the fill-in, five items, the write |
| sealing-and-worm | the example (keys, seal, verify, tamper, forge), six items |

## 8. Proofs

### 8.1 Build: `build-payments-audit-trail` (systemd lab on `lab-base-sec`, 60 minutes), skills: all five but `cloud-audit-trails`

**Story.** The payments server's audit trail goes to the auditors next month. The prompt gives the policy and the numbers, never the settings' names beyond what the lesson taught:

1. **What's recorded.** In `/etc/shop/audit.conf`: every sign-in and failed sign-in, role change, configuration change, refund, data export and card update; never page views or health checks. Each audited event records who did it, from where, what it changed and the outcome. Never a password, a session ID or a token; a card number only as its last four digits.
2. **Sealed, and the auditors hold the key.** The trail is the `audit` journal namespace, kept on disk and sealed every 10 seconds (the lab's stand-in for 15 minutes). The verification key goes in `/srv/auditors/verify-key` (the lab's stand-in for handing it to the audit team; the prompt says so).
3. **Twelve months, then gone.** Keep the trail at least 365 days and delete it after at most 400 (PCI DSS 10.5.1 and GDPR's storage limitation). Give it room for 13 months at 60,000 events a day of about 300 bytes each.
4. Everything lasts a restart.

**`/etc/shop/audit.conf`** (the stand-in's format; the image's copy audits sign-ins only, and the worked example shows it):

```text
# audit EVENT FIELD...    record EVENT with these fields (time is always added, in UTC)
# mask FIELD              write only the last four characters of FIELD
audit login.ok user src outcome
```

`shop-cli` can make these events, each with these fields: `login.ok` and `login.failed` (user, src, outcome, password, session), `page.view` and `health.check` (user, src, path), `role.change` and `config.change` (actor, user or setting, old, new, src, outcome), `refund` and `export` (actor, order or table, amount or rows, src, outcome, token), `card.update` (user, card, src, outcome). The writer (`shop-audit`, scenery, Python) writes the fields it is told to, escaping newlines; it never invents a field. **Not prototyped:** `shop-audit` and `shop-cli` are about 120 lines of Python for the writer of the base; their interface is the one above.

**Checks** (descriptions state end states):

| Id | What it does | Catches |
| --- | --- | --- |
| `audits-what-matters` | makes one of each of the ten events with random users, addresses, orders and amounts (a fresh marker per run), waits up to 3 s, reads `journalctl --namespace=audit -o cat` since the check began: the six audited kinds are there, each with its who, where, what and outcome fields carrying the check's values; `page.view` and `health.check` are absent | missing events, missing fields, noise |
| `no-secrets` | the run's random password, session ID, token and full card number appear in no journal (`journalctl --merge -o export`) and no file under `/var/log`; the card's last four digits do appear in the `card.update` event | secrets logged, mask missing |
| `sealed-for-auditors` | waits up to 15 s; `seal-range audit "$(cat /srv/auditors/verify-key)"` says `sealed` with a range ending after the check's events were written | unsealed, wrong or regenerated key, key not handed over |
| `forgery-shows` | copies the newest audit file, rewrites it with `lab-forge-journal` (one refund amount changed), and requires the copy to verify as unsealed with the auditors' key while the original verifies as sealed: an attacker's rewrite can be told from the real trail | (with `sealed-for-auditors`) the trail not actually sealed; the tamper-at-check-time check |
| `kept-a-year` | effective `MaxRetentionSec` from `systemd-analyze cat-config systemd/journald@audit.conf` (last value wins, drop-ins included) is 365 to 400 days | 30 days, never deleted (0 or unset) |
| `room-for-13-months` | effective `SystemMaxUse` is at least 7.1 GB (60,000 × 300 × 395 bytes) | the 4 GB default cap |
| `on-disk` | the namespace's files are under `/var/log/journal/<machine-id>.audit/` and none under `/run/log/journal` | volatile storage |

The restart trial reruns all seven after `docker restart`.

**Wrong fixes:** `audits-everything.sh` (adds `page.view` and `health.check`), `password-field.sh` (records `password` on failed sign-ins "to spot guessing"), `card-unmasked.sh`, `no-who.sh` (refunds without `actor`), `unsealed.sh` (everything but `Seal=`), `key-regenerated.sh` (hands over a key, then runs `--setup-keys --force` again), `key-left-in-home.sh` (key saved to `~/verify-key`, not handed over), `retention-30-days.sh`, `kept-forever.sh` (no `MaxRetentionSec`), `default-cap.sh` (no `SystemMaxUse`), `volatile.sh` (`Storage=volatile`). Eleven, each failing only its own check (the writer confirms by running each).

**CI time.** Boot about 2 s; the solution about 20 s (it waits one seal); the checks about 25 s (one 15-s seal wait). Thirteen containers (pristine, solution, eleven wrong, plus the restart): **about 8 minutes**. To trim: drop `key-left-in-home.sh` and `no-who.sh` (other checks share their territory).

### 8.2 Debug: `debug-gaps-in-the-trail` (systemd lab on `lab-base-sec`, 45 minutes), skills `what-to-log`, `retention`, `sealing-and-worm`

**Prompt** (purpose, symptoms, count; never what or where). The payments server's audit trail is the `audit` journal namespace, sealed, with the auditors' verification key in `/srv/auditors/verify-key`; `/etc/shop/audit.conf` says what the shop records; `shop-cli` makes the shop do things and `journalctl --namespace=audit` shows the trail. Since last week the auditors report:

- of the refunds in last night's settlement batch (`shop-cli settle` replays it: 1,500 refunds in a few seconds), only a few hundred are in the trail; single refunds during the day are all there;
- after Sunday's reboot, everything before it was gone (stopping the lab and starting it again from the lab page is a reboot, as in Module 1);
- admins' role changes never appear at all, though sign-ins and refunds do.

There are three faults. Rules: keep a rate limit on the audit trail (the settlement batch is the biggest burst it must take); keep it sealed and verifiable with the auditors' key; don't remove anything from the trail; don't record anything the policy forbids; don't change the shop's programs.

**The faults** (the story, `story.sh`, at build):

1. `/etc/systemd/journald@audit.conf.d/40-quiet.conf`: `RateLimitBurst=50` ("to stop a log flood"). Evidence: `Suppressed N messages from shop-audit.service` in the trail after a batch.
2. `/etc/systemd/journald@audit.conf.d/60-disk.conf`: `Storage=volatile` ("save disk"). Evidence: the files are under `/run/log/journal/…audit/`.
3. `/etc/shop/audit.conf`: `audit role.chnage actor user old new src outcome` (a typo); `shop-audit` logs `audit.conf line 4: no such event "role.chnage"` to its own unit's journal (`journalctl -u shop-audit`) once at start.

Keys are made at build and handed over (`/srv/auditors/verify-key`); `Seal=yes` is set and stays set: sealing isn't a fault, but every fix must keep it working.

**Checks:**

| Id | End state | Fails on |
| --- | --- | --- |
| `batch-complete` | `shop-cli settle` (1,500 refunds, a fresh marker) leaves 1,500 refund events in the trail | fault 1; a burst raised too little |
| `still-rate-limited` | effective `RateLimitIntervalSec` and `RateLimitBurst` are both above 0 | turning the limit off |
| `survives-reboot` | the trail is on disk (as `on-disk` in the build, and the effective `Storage=` isn't `volatile`); when `journalctl --namespace=audit --list-boots` shows more than one boot (as it does when the restart trial reruns the checks), entries from an earlier boot are still there | fault 2 |
| `role-changes-recorded` | a `shop-cli role.change` with random values appears with actor, user, old, new, src and outcome | fault 3 |
| `noise-stays-out` | page views and health checks are absent | "fixing" 3 by auditing everything |
| `sealed-for-auditors` | as in the build | a sealing broken by a fix (keys regenerated, `Seal=no`) |
| `no-secrets` | as in the build | a policy widened to "make sure" |
| `programs-intact` | `shop-audit` and `shop-cli` match their checksums | editing the writer |

**Wrong fixes:** `limit-off.sh` (`RateLimitIntervalSec=0`), `burst-500.sh`, `volatile-kept.sh` (faults 1 and 3 only), `audit-all-events.sh` (fixes 3 by auditing every event), `new-keys.sh` (`--setup-keys --force`, key not handed over), `seal-off.sh` ("sealing slowed the batch"), `typo-left.sh` (faults 1 and 2 only), `writer-edited.sh` (a patched `shop-audit` that ignores the rate limit by batching), and one "two of three fixed" variant per fault. **Not prototyped as a lab:** each mechanism was tried (rate-limit suppression, namespace persistence, sealing across restarts); the story, the stand-ins and the contract are not. Prove the contract under `labcheck test` before writing.

**CI time.** About 12 containers; `batch-complete` takes about 5 s; **about 7 minutes**.

### 8.3 Explain

**Prompt.** "Your company's payments service is moving to the cloud, and the security lead asks you how its audit trail will work. Explain, in your own words: what the trail records and what it must never record, with a reason for each; how long it's kept, what decides that, and what the cloud keeps for you by default if you do nothing; how someone could alter or delete the trail and how each of hash chains, sealing and write-once storage makes that detectable or impossible, including what an intruder with root can still do; and who should hold the keys and the delete permission. Say one way the three clouds differ."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `what-and-not` | yes | auth successes and failures, privilege and config changes, admin actions, sensitive-data access; who, what, when (UTC, synced), where from, outcome; never passwords, session IDs, tokens, full card numbers (mask or hash); a separate stream from operational logs |
| `how-long` | yes | from the rules (PCI DSS 12 months with three immediately available; GDPR: no longer than necessary, so deleted afterwards); sized from rate × size × days; defaults are short (CloudTrail 90 days of management events, Azure activity log 90 days, Entra 7 or 30, Google `_Default` 30 and `_Required` 400) and data-plane logging is off until enabled |
| `tamper-evidence` | yes | a hash chain makes edits, deletions and reorders detectable, but a cut-off tail or a rewrite needs an anchor or a key; sealing changes keys forward so root can alter only entries since the last seal; a verification without a "validated" range proves nothing |
| `keep-it` | yes | ship off the box to write-once storage (compliance mode, locked policy, locked bucket) because sealing detects but doesn't prevent deletion; the verification key and the delete permission are held by people who don't run the servers |
| `clouds-differ` | no | for example: Google always keeps 400 days of admin activity while AWS's event history is 90 days; Azure's activity log omits requests rejected before they start; S3 has governance and compliance modes, Azure unlocked and locked policies, Google an irreversible bucket lock |

## 9. Review pool

At least two per skill; mostly produced answers on real output or numbers.

- what-to-log: `mask-card`, `audit-rule-keys`, `mcq-log-injection`, `mcq-auid` (review-only), `mcq-utc-clock` (review-only).
- retention: `est-trail-size`, `est-event-history-gap`, `est-hot-quarter` (review-only), `est-journal-cap` (review-only), `mcq-gdpr-forever` (review-only).
- cloud-audit-trails: `mcq-s3-read-missing`, `mcq-azure-rejected` (review-only), `cloudtrail-who` (review-only), `mcq-gcp-off-by-default`.
- hash-chains: `chain-deleted-line`, `mcq-rewrite-everything`, `write-chain-verify`, `mcq-ct-append-only` (review-only).
- sealing-and-worm: `est-unsealed-window`, `verify-pass-or-sealed`, `mcq-object-lock-mode`, `mcq-legal-hold` (review-only), `mcq-gcs-lock-undo` (review-only).

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| A1 | **`lab-base-sec`** (lab-base-sec.md): this topic needs its journald plumbing (`ReadKMsg=no`, `Seal=no` in the default namespace, `KillSignal=SIGKILL` for `systemd-journald@.service`), `systemd-journal-remote`, `lab-flip`, `lab-forge-journal`, `seal-range`, `shop-audit` and `shop-cli` | the base as designed; the audit pieces first, since they block the worked example |
| A2 | Nothing in the app. Estimate items exist (ADR-0024); `predict_shell` items run real `bash`, `sed`, `awk`, `grep` and `sha256sum` (Git Bash has `sha256sum`). | |

No ADR is needed: shared bases and the restart trial are ADR-0018's third amendment; the `KillSignal` drop-in is lab plumbing recorded in the base's README.

## 11. Cost and time

- **Money:** none. No cloud account is touched. A real-cloud extra (a CloudTrail trail into an S3 bucket with Object Lock in governance mode, validated with `aws cloudtrail validate-logs`) would fit AWS's free tier only partly (S3 Object Lock itself is free; the first trail of management events is free; S3 storage and requests are free-tier-limited; not checked this session) and needs the AWS CLI, which Module 6 teaches. **Not proposed;** Module 15's `csa.ops.audit-logs` builds the clouds' trails.
- **Learner minutes:** lesson 15, reading 29 (OWASP 17, LWN 7, CloudTrail 5), 22 quick items 33, worked example 25, fill-in 25, write 40, build 60, debug 45, explain 20: **292**. With the optional readings, 312.
- **Labs and CI:** five labs. Contract minutes: worked example about 2, fill-in about 1, write about 2, build about 8, debug about 7: **about 20 minutes** of container time for the topic, plus the base's first build in its shard.

## 12. Open questions, each with a recommendation

1. **`auditd` only on paper.** The labs can't run it (fact 16). Alternatives: a QEMU guest (Module 2's hypervisor labs boot one in 16 to 27 s, without hardware help) running auditd for real. **Recommendation:** paper only in this topic: rules read from real files, records constructed and labelled so. The audit system's concepts are a small part of the topic; a VM per lab would double its CI time.
2. **The sealing workaround** (lab-base-sec.md, question 1). **Recommendation:** keep it and name it.
3. **The stand-in audit policy file.** Real applications decide audit events in code; the lab's `audit.conf` is a stand-in, closer to the clouds' own switches (CloudTrail event selectors, Azure diagnostic-setting categories, Google's Data Access audit config). **Recommendation:** keep it, and say so in one sentence: the judgement (which events, which fields, what never) is the skill, and the file is how the lab checks it.
4. **No log shipping in a lab.** `systemd-journal-upload --namespace=audit` to a `systemd-journal-remote` collector worked on one machine (tried: 397 events copied, with a saved cursor), but a real "off the box" needs a second machine, the network base and its own checks. **Recommendation:** teach shipping in the lesson and items; Module 15 (`csa.ops.audit-logs`) and Module 21 (`csa.gov.logging`) build central collection.
5. **292 minutes is close to the 300 line.** **Recommendation:** keep one topic; the five skills feed one build, and the trims named in section 8 (two wrong fixes) cost nothing in learning.

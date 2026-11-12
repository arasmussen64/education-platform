# Writing brief: `csa.net.dns` (topic 30), DNS

Design only. Nothing here is in the repository. Sources were read on 2026-11-11 and each fact below carries its URL. Lab mechanics marked **tried** were run on 2026-11-11 in Docker Desktop on the owner's PC (`ubuntu:24.04`, BIND 9.18.39-0ubuntu0.24.04.9, Unbound 1.19.2-1ubuntu3.12, a privileged systemd container, `--cgroupns=host`). Everything started was removed afterwards. The prototype files are in `prototypes/dns-http/dns/` (Dockerfile, `network.sh`, the zone files, `dnssec-link.sh`, the units, `move-trial.sh`) and real captured output is in `prototypes/dns-http/captured/`.

## 1. What the learner will be able to do

1. Follow one lookup from a laptop's stub resolver through a recursive resolver to the root, the top-level domain's servers and the zone's own servers. Name each referral, the glue that came with it, and the server whose answer was authoritative, reading `dig +trace` and `dig +norecurse` output.
2. Read and write a zone file: SOA (and what its serial, refresh, expire and minimum numbers do), NS, A, AAAA, CNAME (and why one can't sit at the zone's apex), MX, TXT, CAA, PTR. Delegate a child zone with NS records and glue. Keep a secondary in step through the serial and zone transfers.
3. Work out how long an answer, or a "no such name", can stay cached: the TTL, RFC 2308's negative-caching rule and a resolver's own caps. Run a planned move as a procedure: lower the TTL, wait out the old TTL, switch, check, then raise the TTL again.
4. Give one name different answers inside and outside a network (split-horizon), and predict the classic failure: a private zone that shadows the public one, so names that exist only publicly vanish from inside. Map this onto Route 53 private hosted zones, Azure Private DNS and Cloud DNS private zones.
5. Explain DNSSEC's chain of trust (DNSKEY, RRSIG, DS, the trust anchor and the AD flag). Recognise a broken chain: SERVFAIL from a validating resolver, `dig +cd` still answering, and an Extended DNS Error naming the cause (EDE 6 "DNSSEC Bogus", EDE 7 "Signature Expired"). Fix one without switching validation off.

**The six-month core.** What should still be there half a year on, and what the review pool is built around:

- A stub asks a recursive resolver. The resolver asks the root, then the TLD's servers, then the zone's servers. Each level answers with a referral (the next servers' names, plus glue when those names sit inside the zone being delegated) until one answers with the `aa` flag.
- Caches hold an answer for its TTL, and a "no such name" for min(SOA TTL, SOA MINIMUM). Lower a TTL at least one old TTL before you change the record. Nobody can empty the caches you don't run.
- An edited zone needs a higher serial, or the secondaries never fetch it. Under BIND's inline signing, the edit isn't even loaded.
- A private zone answers every name under it. A name that is missing there gives NXDOMAIN inside the network, even when it exists publicly.
- DNSSEC: the parent's DS must match the child's key, and signatures expire. Broken means SERVFAIL for validating resolvers only. `+cd` shows the data is there, and the EDE line says why. The fix is re-signing or a correct DS, never switching validation off.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.net.transport]` (topic 28). DNS uses UDP and falls back to TCP on port 53, and this topic treats a datagram, a port and a connection as known. Topic 28's spec row teaches TCP handshakes and timeouts. If its brief doesn't define a UDP datagram and how it differs from a TCP connection, this topic adds one paragraph (section 4, idea 1). `csa.net.transport` reaches back through Module 3 to `csa.m1.checkpoint`. This topic does **not** depend on Module 2: the map runs m1 → m3, so `csa.hw.windows-ad`'s DNS words can't be assumed.

**Builds on (for the writer, not for `prerequisites:`):**

| Topic | What this topic uses from it |
| --- | --- |
| `csa.linux.net-tools` | `dig name` (answer section, TTL column, CNAME then A, `+short`), `/etc/hosts` read by `curl` but not by `dig`, dnsmasq's `host-record=` and its restart, `nc`, `tcpdump -nn port 53`, network namespaces and `from-office`. Its recall item `net-dig-answer` already reads a CNAME chain with TTLs. This topic never re-teaches those. |
| `csa.linux.services` | `systemctl restart`, `journalctl -u` (BIND's "not loaded due to errors" appears only in the journal). |
| `csa.linux.shell`, `csa.linux.scripting` | `awk`, `sort`, `grep -c`, `$(( ))`, writing and running a script, for the write lab. |
| `csa.net.layers` (topic 23) | Packets and encapsulation, if the reader wants to know why a big DNSSEC answer is truncated over UDP. |
| `csa.net.cidr` (topic 24) | Address blocks. The reverse zone `9.0.10.in-addr.arpa` is the octets of `10.0.9.0/24` written backwards, and the lesson says so in one line. |
| `csa.hw.windows-ad` (optional) | A learner who took Module 2 has met resolver, zone, SRV, PTR and conditional forwarder in Active Directory. The lesson can say "you met these with dc1" without depending on it. |

**Terms this topic must define itself.** Module 1 used `dig` but never the words below, and Module 3's earlier topics don't teach them:

- **DNS**, **name**, **label**, **fully qualified name and the trailing dot**, **domain**, **zone** (a domain minus the parts delegated away), **apex**.
- **Stub resolver**, **recursive resolver** (also called caching or full-service), **forwarder** (what Module 1's dnsmasq was), **authoritative server**, **root server**, **TLD**, **registry** and **registrar** (one sentence each).
- **Referral**, **delegation**, **glue** (RFC 9499's "in-domain" glue; the lesson avoids "bailiwick", which RFC 9499 calls historic), **the `aa`, `rd`, `ra`, `ad` and `cd` flags**, **NOERROR / NXDOMAIN / NODATA / SERVFAIL / REFUSED**.
- **Resource record**, **RRset**, **TTL**, the record types (A, AAAA, CNAME, MX, TXT, NS, SOA, PTR, CAA, SRV in one line, HTTPS/SVCB in one line), **reverse zone**.
- **SOA fields:** primary name server, the responsible person's mailbox written as a name, serial, refresh, retry, expire, minimum. Only serial, expire and minimum are worked with.
- **Primary and secondary**, **zone transfer** (AXFR and IXFR), **NOTIFY**.
- **Negative caching**, **cache cap** (Unbound's `cache-max-ttl` and `cache-max-negative-ttl`).
- **Split-horizon (split-view) DNS**, **private zone**, **shadowing**.
- **DNSSEC:** **signature (RRSIG)**, **public key (DNSKEY)**, **KSK/ZSK/CSK**, **DS**, **chain of trust**, **trust anchor**, **validating resolver**, **bogus/secure/insecure**, **NSEC** (one sentence: signed proof that a name doesn't exist), **Extended DNS Error (EDE)**.
- **Alias / ALIAS / apex alias** (provider-specific records that let the apex point at a load balancer).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `trace-resolution` | Stub, recursive and authoritative roles. Referrals, glue and the `aa` flag. Reading `dig +trace`, `dig +norecurse @server` and the header flags. Which server to ask when answers disagree. |
| `records-and-zones` | Record types and when to use each. CNAME rules (not at the apex, not beside other data) and the clouds' apex aliases. The zone file and SOA. Delegation with NS plus glue. Serial, NOTIFY and transfers. A secondary that falls behind. |
| `ttl-and-caching` | TTLs counting down in a cache. Negative caching, min(SOA TTL, MINIMUM). Resolver caps. The planned move: lower, wait at least the old TTL, switch, check, raise. Quick sums in hours and seconds. **A calculation skill: five estimate items.** |
| `split-horizon` | One name, two answers. A resolver that answers locally for a zone (Unbound's `local-zone` types `transparent` and `static`). Cloud private zones and their NXDOMAIN-shadowing rule. Forwarding rules and Azure's fallback-to-internet for Private Link zones. |
| `dnssec` | What DNSSEC proves and what it doesn't (not secrecy). DNSKEY/RRSIG/DS/trust anchor, and the AD bit. Reading a bogus answer (SERVFAIL, `+cd`, EDE 6/7/9). Re-signing and DS updates. Why switching validation off is the wrong fix. Each cloud's support (signing, and whether its resolver validates). |

Five skills. Every one is practised before either proof asks for it (section 7, last table), and every one has at least two come-back questions (section 9).

## 4. Lesson plan

The lesson is about 1,900 words (15 minutes). Each idea below names the resource section it pairs with, and the explanation the lesson must supply itself.

1. **Why names, and the shape of a name (lesson only).** A name is labels separated by dots, read right to left from an invisible root, `.`. `api.shop.test.` has the trailing dot that `dig` prints, and that dot is the root. Picture the namespace as an upside-down tree: `.` at the top, then `test.`, then `shop.test.`. A **zone** is a piece of that tree run by one set of servers. The lesson makes the "zone versus domain" distinction concrete: `shop.test` is a zone until it delegates `eu.shop.test` away, and from then on `eu.shop.test` is a zone of its own. One paragraph on UDP versus TCP if topic 28 didn't define a datagram: a DNS question and answer are usually one UDP datagram each, with no connection set up, and an answer too big for the datagram comes back with the TC flag, telling the resolver to ask again over TCP.
2. **The four players (DigitalOcean tutorial, "How DNS Works" to "What is a Resolving Name Server?").** The lesson adds a picture in words that the tutorial lacks. The laptop's stub is a receptionist who only knows one phone number, the resolver's. The resolver is a researcher with a notebook (the cache). Root, TLD and zone servers are librarians who each say "not my shelf, ask her" (a referral) until one says "this is my shelf, here it is" (the `aa` flag). Correct the tutorial's dated line "There are currently 13 root servers in operation": there are 13 root server *names*, `a` to `m`, each answered by many machines at many places (anycast, one sentence, taught properly in the routing and BGP topics). Contrast with Module 1: dnsmasq was a **forwarder**, passing questions to another resolver. Unbound is a **full recursive resolver**, doing the research itself. BIND here is **authoritative only**, with `recursion no;`. The lesson says why that last setting matters: an authoritative server that also recurses for anyone becomes an open resolver, a known source of abuse.
3. **Reading a trace (the lab's own output, tried).** Walk through `dig +trace api.shop.test` from the lab, which works with no internet: the lab has its own root (`a.root-servers.test`, 10.0.9.11), its own `test.` servers and the shop's two servers. Each block in the trace is one referral, ending in a `Received … from <server>` line. Then repeat one step by hand, `dig @10.0.9.11 +norecurse api.shop.test`. The answer section is empty, the AUTHORITY section holds `test. NS ns1.nic.test.`, ADDITIONAL holds the glue `ns1.nic.test. A 10.0.9.12`, and there's no `aa` flag. Then ask the shop's server: now `aa` is set. Header flags explained once: `rd` (please recurse), `ra` (I can), `aa` (I'm the authority), `ad` (validated). Glue: when the NS name is inside the zone being delegated (`ns1.shop.test` for `shop.test`), nobody could find its address without the parent handing it over, so the parent does.
4. **Records and zone files (DigitalOcean, "Zone Files" and "Record Types").** Read the lab's `db.shop.test` line by line. Two things the tutorial doesn't stress, which the lesson must:
   - **CNAME means "this name is that name for every type"**, so a CNAME can't share its name with any other record (RFC 2181 §10.1). The apex always has SOA and NS, so the apex can't be a CNAME. Route 53 alias records and Azure DNS alias record sets exist to point an apex at a load balancer (both pages say so; facts 18 and 19). **Where the clouds differ:** Route 53 alias answers as an A/AAAA with the target's own TTL and is free to query. Azure alias record sets track a public IP, Traffic Manager, CDN or Front Door. The lesson doesn't claim a Cloud DNS equivalent (not confirmed).
   - **The serial is a promise, not a label.** A secondary compares serials and fetches only when the primary's is higher. The lab adds a lesson nobody else teaches: with BIND's inline signing, an edit without a serial bump isn't loaded at all. `rndc reload` still prints `zone reload queued`, and the journal says `ixfr-from-differences: new serial (…) out of range … not loaded due to errors` (tried). Also, the served serial differs from the file's, because the signer bumps it on each re-sign (tried: the file said 2026111101, the server served 2026111104).
5. **Caching and TTLs (Julia Evans, "What happens when you update your DNS?").** The post is from 2020 but still right. Watch the TTL count down in the lab (tried: 586, then 584 two seconds later). **The lesson supplies what the post doesn't cover:** negative caching. An NXDOMAIN carries the zone's SOA, and its TTL is min(SOA TTL, SOA MINIMUM) (RFC 2308 §5). In the lab, SOA TTL 300 and MINIMUM 900 gave a negative TTL of 300 (tried). So querying a name *before* you create it can make it "not exist" for that long. Resolvers also cap TTLs: Unbound by default holds an answer at most 86,400 s and a negative answer at most 3,600 s (fact 4).
6. **A planned move, as a procedure (lesson only; the lab rehearses it at a small scale).** Draw it as a timeline. At T−(old TTL) or earlier, lower the TTL (bump the serial). Wait until every cache's copy with the old TTL has expired. That's the old TTL, counted from when the lowered record reached the authorities, not from when you typed it. Switch the address at T. Check through several resolvers. Afterwards, raise the TTL again (short TTLs cost queries and make an outage of the DNS host felt sooner). Tried at a small scale: old TTL 60 s, new 5 s. Waiting 62 s after lowering left the last stale answer 2.7 s after the switch. Waiting only 10 s left stale answers 30.4 s after it. Slack's DNSSEC rollback (fact 23) is the cautionary tale: a DS record cached for up to 24 hours outlived a hasty rollback, and validating resolvers returned SERVFAIL for slack.com.
7. **Split-horizon (lesson plus the cloud pages).** Same name, two answers: inside, `api.shop.test` is the private 10.0.8.41. Outside, it's the public address. The lesson builds the idea with the lab's resolver. `local-zone: "shop.test." transparent` plus one `local-data` line overrides one name and lets every other name resolve normally. `static` answers only what it holds and gives NXDOMAIN for the rest (tried: `www` became NXDOMAIN, `mail` vanished). **Where the clouds differ**, from their own pages:
   - Route 53 VPC Resolver: a matching private hosted zone with no matching record returns NXDOMAIN and never falls back to public (fact 15). A VPC Resolver forwarding rule for the same name beats the private zone. The resolver is at the VPC's base address plus two.
   - Cloud DNS: a private zone overlaps a public one, and a missing record gives NXDOMAIN "even if there's a record … defined in a public zone" (fact 17).
   - Azure Private DNS: the same by default. For Private Link zones only, a virtual network link can set `NxDomainRedirect` ("Enable fallback to internet"), and Azure's resolver then retries publicly (fact 16).

   So all three behave like Unbound's `static`, which is why "we created a private zone for our domain and half our names stopped working inside" is a classic ticket.
8. **DNSSEC (Cloudflare, "How DNSSEC works", all of it).** The lesson adds three things the page doesn't give:
   - **What DNSSEC proves:** the answer came from the zone's keyholder and wasn't altered. It's not secrecy: anyone on the path still sees the question (encrypted DNS is a different thing, named in one sentence).
   - **What broken looks like** (tried, real output). A validating resolver returns SERVFAIL with `EDE: 6 (DNSSEC Bogus): (validation failure <api.shop.test. A IN>: no keys have a DS with algorithm ECDSAP256SHA256 …)` when the parent's DS doesn't match the child's keys. It returns `EDE: 7 (Signature Expired)` when signatures have lapsed. `dig +cd` (checking disabled) returns the data anyway, which shows the records exist and only validation fails. A resolver that doesn't validate answers normally.
   - **The fixes and the anti-fixes:** re-sign, or publish the right DS. Never `val-permissive-mode`, `domain-insecure` or validation off; those make every forged answer pass too. And deleting the DS to "go insecure" has to wait out the DS's own TTL, the Slack lesson.

   **Where the clouds differ** (facts 20 to 22). Route 53 signs public hosted zones, and its VPC Resolver validates only when you switch validation on per VPC. Even then it doesn't set the AD bit or return DNSSEC records. Azure DNS signs public zones (ECDSAP256SHA256, RFC 9824 compact denial), but Azure's default resolver (168.63.129.16) "does not perform" validation. Cloud DNS manages keys and signing once enabled, and does nothing until the registrar publishes your DS.
9. **The labs (lesson only):** what each lab's machines are. `lab` runs the site's resolver (Unbound). `root`, `tld`, `ns1` and `ns2` are authoritative BIND servers in network namespaces on one bridge. `isp1` to `isp3` are other people's resolvers. `office` is a laptop. `on MACHINE COMMAND` runs a command on a machine. And the rule of the module: change only what the lab asks for.

**Read now:** the DigitalOcean tutorial, the main resource: "How DNS Works", "Zone Files" and "Record Types", about 2,800 of its 4,100 words. Then Julia Evans' post for caching, and Cloudflare's DNSSEC page. Optional: Unbound's `local-zone` reference, for the two types the labs use, and the AWS private-hosted-zone considerations page.

## 5. Verified facts

All read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | A negative answer's TTL is "the minimum of the MINIMUM field of the SOA record and the TTL of the SOA itself". One to three hours "have been found to work well", and more than a day is problematic. | https://www.rfc-editor.org/rfc/rfc2308.html (§3, §5) |
| 2 | RFC 9499 (March 2024, BCP 219) defines referral, glue ("in-domain"), delegation and authoritative server (sets AA). It calls "in-bailiwick" and "lame delegation" historic terms to avoid. | https://www.rfc-editor.org/rfc/rfc9499.html |
| 3 | A CNAME can't coexist with other data at the same name. | RFC 2181 (July 1997) §10.1, metadata from https://www.rfc-editor.org/rfc/rfc2181.json (the clause itself was not re-read this session; the Route 53 and Azure pages state the apex consequence) |
| 4 | Unbound defaults: `cache-max-ttl` 86400, `cache-max-negative-ttl` 3600, `cache-min-ttl` 0, `serve-expired` no, `ede` no, `val-log-level` 0. `trust-anchor-file` takes DS or DNSKEY in zone-file format. | https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html |
| 5 | Unbound's `static` local zone answers NODATA/NXDOMAIN for names without local data, while `transparent` resolves them normally. Its default local zones include `test.`, `invalid.`, `onion.`, `home.arpa.` and the RFC 1918 reverse zones. `nodefault` (or a local-zone of your own) undoes one, and `unblock-lan-zones` the RFC 1918 ones. | same page, second part |
| 6 | Tried: Unbound 1.19.2 answered NXDOMAIN with `aa` for everything under `test.` until `local-zone: "test." nodefault` was added. | prototype |
| 7 | `domain-insecure` ignores the chain of trust below a name. `val-permissive-mode` passes bogus data to clients. | Unbound reference, as fact 4 |
| 8 | EDE codes (RFC 8914, October 2020): 6 DNSSEC Bogus, 7 Signature Expired, 9 DNSKEY Missing, 10 RRSIGs Missing, 22 No Reachable Authority. | https://www.rfc-editor.org/rfc/rfc8914.html |
| 9 | `.test` is reserved for testing and never resolves on the public internet. | RFC 6761 §6.2 (Feb 2013), https://www.rfc-editor.org/rfc/rfc6761.html (title and date re-read from its JSON. Section 6.2 was cited by `csa.hw.windows-ad` on the same date) |
| 10 | ICANN's Board "reserves .INTERNAL from delegation in the DNS root zone permanently … for its use in private-use applications" (resolution 2024.07.29.06). | https://www.icann.org/en/board-activities-and-meetings/materials/approved-resolutions-special-meeting-of-the-icann-board-29-07-2024-en |
| 11 | Tried: BIND 9.18.39 with `dnssec-policy default; inline-signing yes;` signs a zone at first start (ECDSAP256SHA256, flags 257, one key). | prototype |
| 12 | Tried: under inline signing, an edit without a serial bump is refused. `rndc reload` prints `zone reload queued`, and the journal says `ixfr-from-differences: new serial (2026111101) out of range [2026111102 - 4173594748]` then `not loaded due to errors`. | prototype |
| 13 | Tried: `dig +trace` works with no internet when the resolver's root hints name a local root. | prototype |
| 14 | Tried: with keys replaced and the old DS left in the parent, Unbound returned SERVFAIL with `EDE: 6 (DNSSEC Bogus) … no keys have a DS with algorithm ECDSAP256SHA256 from 10.0.9.13 for key shop.test.`. A zone signed with signatures that had lapsed got `EDE: 7 (Signature Expired)`. `dig +cd` returned the address in both cases. | prototype, `captured/dns-captures.txt` |
| 15 | Route 53 VPC Resolver: a matching private hosted zone with no matching record returns NXDOMAIN and doesn't forward to public. A Resolver rule for the same name takes precedence over a private zone. The Amazon-provided DNS server is at the VPC range's base plus two. The service is now called "Route 53 VPC Resolver". | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zone-private-considerations.html |
| 16 | Azure Private DNS `resolutionPolicy: NxDomainRedirect` ("Enable fallback to internet") retries publicly after an NXDOMAIN, only for zones associated with Private Link resources (API 2024-06-01 or later). | https://learn.microsoft.com/en-us/azure/dns/private-dns-fallback (ms.date 2025-02-04) |
| 17 | Cloud DNS: "A private zone can overlap with any public zone". A missing record in an authorized private zone gives NXDOMAIN "even if there's a record … defined in a public zone". | https://docs.cloud.google.com/dns/docs/zones/zones-overview |
| 18 | Route 53 alias records can sit at the zone apex, CNAMEs can't. Alias queries to AWS resources are free. An alias to an AWS resource uses that resource's TTL. | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html |
| 19 | Azure DNS alias record sets (A, AAAA, CNAME) can point the apex at Traffic Manager, CDN, a public IP or Front Door. "The DNS protocol prevents the assignment of CNAME records at the zone apex". | https://learn.microsoft.com/en-us/azure/dns/dns-alias (ms.date 2026-10-05) |
| 20 | Route 53 VPC Resolver validates DNSSEC only when enabled per VPC. It ignores DO and CD and doesn't set AD. Enabling it "could result in an outage". | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dnssec-validation.html |
| 21 | Azure DNS signs public zones with ECDSAP256SHA256 and implements RFC 9824. "DNSSEC response validation is not performed by the default Azure-provided resolver." ZSKs roll automatically. A KSK change needs Microsoft support and a new DS. | https://learn.microsoft.com/en-us/azure/dns/dnssec (ms.date 2025-01-27, updated 2026-08-12) |
| 22 | Cloud DNS manages DNSKEY creation, rotation and signing once DNSSEC is on, but "If you cannot add a DS record through your domain registrar … enabling DNSSEC in Cloud DNS has no effect". | https://docs.cloud.google.com/dns/docs/dnssec |
| 23 | Slack, 30 September 2021: a DNSSEC rollout caused a 24-hour outage for under 1% of users. The DS had been removed at the registrar on the assumption it wasn't cached, resolvers had it cached for up to 24 hours, and validating resolvers returned SERVFAIL. | https://slack.engineering/what-happened-during-slacks-dnssec-rollout/ |
| 24 | RFC 9824 "Compact Denial of Existence in DNSSEC", September 2025. RFC 9460 (SVCB and HTTPS records), November 2023. | https://www.rfc-editor.org/rfc/rfc9824.json, …/rfc9460.json |
| 25 | Tried: negative TTL in an NXDOMAIN from the authority was 300 with SOA TTL 300 and MINIMUM 900, and it counted down in the resolver (289, 286). | prototype |
| 26 | Tried: the planned move at small scale (old TTL 60 s, new 5 s, two resolvers polled every second). Waiting 62 s after lowering left the latest stale answer 2.7 s after the switch. Waiting 10 s left 30.4 s. | prototype `move-trial.sh` |

**Where sources disagree or weren't confirmed:** the DigitalOcean tutorial (last modified 2020-11-04) still says "13 root servers in operation", and the lesson corrects it. Whether Google's VPC resolver validates DNSSEC isn't stated on the page read, so the lesson claims nothing for it. Julia Evans says some resolvers ignore TTLs: true, but this topic's arithmetic assumes they're honoured and says so.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | "An Introduction to DNS Terminology, Components, and Concepts", Justin Ellingwood (DigitalOcean): read "How DNS Works", "Zone Files", "Record Types" | https://www.digitalocean.com/community/tutorials/an-introduction-to-dns-terminology-components-and-concepts | reading | CC BY-NC-SA 4.0 (in the page's metadata). Linked, not copied | 22 of 31 (4,090 words in all; published 2014-02-19, modified 2020-11-04) | trace-resolution, records-and-zones | 2026-11-11 |
| 1 | "What happens when you update your DNS?", Julia Evans | https://jvns.ca/blog/how-updating-dns-works/ | reading | © Julia Evans (no licence stated). Linked | 13 (1,744 words; 2020-06-17) | ttl-and-caching | 2026-11-11 |
| 2 | "How does DNSSEC work?" (Cloudflare Learning Center) | https://www.cloudflare.com/learning/dns/dnssec/how-dnssec-works/ | reading | © 2026 Cloudflare, Inc. Linked | 14 (about 1,800 words of body) | dnssec | 2026-11-11 (fetched with a browser user agent; WebFetch got 403) |
| 3 | "What is recursive DNS?" (Cloudflare), optional | https://www.cloudflare.com/learning/dns/what-is-recursive-dns/ | reading | © 2026 Cloudflare. Linked | 8 | trace-resolution | 2026-11-11 |
| 4 | Unbound `unbound.conf(5)`: the `local-zone` entry only, optional | https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html | reference | BSD (NLnet Labs). Linked | 5 | split-horizon | 2026-11-11 |
| 5 | AWS, "Considerations when working with a private hosted zone", optional | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zone-private-considerations.html | reading | © AWS. Linked | 7 | split-horizon | 2026-11-11 |
| 6 | Slack Engineering, "What happened during Slack's DNSSEC rollout", optional | https://slack.engineering/what-happened-during-slacks-dnssec-rollout/ | reading | © Slack. Linked | 15 | dnssec, ttl-and-caching | 2026-11-11 |
| 7 | BIND 9.18 ARM, DNSSEC Guide, reference only (35,000 words; named for anyone who wants depth) | https://bind9.readthedocs.io/en/v9.18.39/dnssec-guide.html | reference | © 2023 ISC (BIND's documentation is MPL 2.0 with the source; the page itself shows the copyright line). Linked | not assigned | dnssec | 2026-11-11 |

No video is assigned: none was opened and timed this session. A writer who wants one opens it, times it and records its licence first.

## 7. Practice ladder

All labs boot systemd (`lab: { init: systemd }`) on the network-lab base (section 10). Each shares the topic's second `RUN` line, `apt-get install bind9 bind9-utils unbound`, which added **15.8 MB** in the prototype. Machines, the same in every lab:

| Machine | Address | Runs |
| --- | --- | --- |
| `lab` (the learner's shell) | 10.0.9.1 on bridge `br0` | the site's recursive resolver, Unbound (`resolver.service`), which `lab` and `office` use |
| `root` | 10.0.9.11, `a.root-servers.test` | BIND, the root zone, signed |
| `tld` | 10.0.9.12, `ns1.nic.test` | BIND, `test.`, signed |
| `ns1` | 10.0.9.13 | BIND primary for `shop.test` (inline-signed) |
| `ns2` | 10.0.9.14 | BIND secondary for `shop.test` |
| `isp1`, `isp2`, `isp3` | 10.0.9.21 to 23 | other people's validating resolvers (Unbound), no private zones |
| `office` | 10.0.9.30 | a laptop. `/etc/netns/office/resolv.conf` points at 10.0.9.1 |

Each BIND instance runs as `ns@<machine>.service` (`ip netns exec %i named -f -u bind -c /var/lib/lab/dns/%i/named.conf`), with its own directory, `rndc` on its own namespace's 127.0.0.1:953, and `recursion no;`. A one-time `dnssec-link.service` puts each child's DS into its parent and the root's DS into every resolver's trust anchor (tried, section 13). `on MACHINE CMD` wraps `sudo ip netns exec`. Every resolver config carries `local-zone: "test." nodefault` (fact 6), `val-log-level: 2` and `ede: yes`.

### 7.1 `example-follow-a-lookup` (worked example, lab), skills `trace-resolution`, `ttl-and-caching`

Labelled steps:

1. **The stub's view:** `cat /etc/resolv.conf`, then `dig api.shop.test`: flags `qr rd ra ad`, answer TTL 600.
2. **The whole trail:** `dig +trace api.shop.test`, with four `Received … from` lines (resolver, root, `test.`, shop).
3. **One referral by hand:** `dig @10.0.9.11 +norecurse api.shop.test`. Point at the empty answer, the AUTHORITY NS and the ADDITIONAL glue. Save the NS name the root gave to `~/example/referral.txt`.
4. **The authority:** `dig @10.0.9.13 +norecurse api.shop.test`, with `aa` set. Save the flags line to `~/example/aa.txt`.
5. **The cache counting:** two `dig api.shop.test` two seconds apart. Write the drop to `~/example/countdown.txt`.
6. **A name that doesn't exist:** `dig nope.shop.test`. Read the SOA in AUTHORITY and its TTL. Save the negative TTL the authority gives (`dig @10.0.9.13 nope.shop.test`) to `~/example/negative-ttl.txt`.
7. **Signatures:** `dig +dnssec api.shop.test` (an RRSIG line), `dig @10.0.9.12 +norecurse +dnssec shop.test DS`.

Checks: `referral.txt` equals the NS name the root returns now. `aa.txt` contains ` aa`. `countdown.txt` is a positive integer of at most 10. `negative-ttl.txt` equals the SOA TTL the authority gives for an NXDOMAIN, computed live. Wrong fixes: `asked-resolver-for-referral.sh` (step 3 run against the resolver, saving `api.shop.test`'s address), `negative-is-minimum.sh` (writes 900, the SOA MINIMUM field). About 25 minutes.

### 7.2 Recall on resolution (all real lab output, captured on the day of writing)

Every multiple-choice item here and below follows `content/README.md`'s length rules. The brief gives the scenario, the right answer and the distractor ideas, and the writer writes every choice out in full and the same shape.

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `trace-who-answered` | predict_shell | trace-resolution | A captured `dig +trace` (the prototype's, `captured/dns-captures.txt`). Command: `grep '^;; Received' trace.txt \| awk '{print $NF}' \| cut -d'(' -f2 \| tr -d ')'`. Prints the four servers in order: `127.0.0.1`, `a.root-servers.test`, `ns1.nic.test`, `ns1.shop.test`. Pin the exact output by running it. |
| `referral-sections` | predict_shell | trace-resolution | A captured `dig @10.0.9.11 +norecurse` answer. `awk '/AUTHORITY SECTION/,/^$/' ref.txt \| grep -c NS` plus the `flags:` line. Teaches an empty answer, no `aa`, and the NS in authority. |
| `mcq-glue-why` | mcq | trace-resolution | Why does `test.`'s referral for `shop.test` carry `ns1.shop.test A 10.0.9.13`? Right: the NS name is inside the zone being delegated, so nobody could look its address up without it. Distractors: it saves a round trip for every NS (true of extra data in general, not why glue is needed); the parent is authoritative for the child's addresses; the resolver asked for it. |
| `mcq-aa-flag` | mcq | trace-resolution | Two answers for the same name disagree, one from `dig` (via the resolver) and one from `dig @ns1 +norecurse` with `aa`. Which reflects the zone right now? Right: the `aa` answer, because the resolver's may be cached. Distractors: the resolver's, because it validated (AD is about authenticity, not freshness); whichever TTL is higher; both, until the serial changes. |
| `mcq-forwarder-or-recursive` | mcq | trace-resolution | Module 1's dnsmasq against this topic's Unbound: what does dnsmasq do for a name it doesn't hold? Right: it passes the question to another resolver and relays the answer. Distractors cover recursing from the root, answering NXDOMAIN, and asking the authoritative server directly. |
| `mcq-open-resolver` | mcq | trace-resolution | Why does every authoritative server in the lab say `recursion no;`? Right: so it answers only for its own zones and can't be used by strangers to look up (and amplify) anything. |

### 7.3 `fill-delegate-eu` (fill-in, lab), skills `records-and-zones`, `trace-resolution`, `dnssec`

Story: the shop opens a European site with its own name server, `ns-eu` (a ninth machine, 10.0.9.15, already running BIND with an empty config). Files with gaps (`...`):

- `/var/lib/lab/dns/ns-eu/db.eu.shop.test`: the SOA (gap: the serial, any 10-digit date-style number), the NS line (gap: `ns-eu.eu.shop.test.`), `ns-eu IN A ...` (gap) and `www IN A 10.0.9.50`.
- `/var/lib/lab/dns/ns-eu/named.conf`: `zone "eu.shop.test" { type primary; file "..."; dnssec-policy ...; inline-signing yes; key-directory "keys"; };`.
- `/var/lib/lab/dns/ns1/db.shop.test`: the delegation lines `eu IN NS ...`, the glue `ns-eu.eu IN A ...`, and the DS, which the prompt says to make with `dig @10.0.9.15 eu.shop.test DNSKEY +noall +answer | dnssec-dsfromkey -2 -f - eu.shop.test`. Then a serial gap: "the serial must go up".

The prompt gives the commands (`named-checkzone`, `on ns-eu rndc reconfig`, `on ns1 rndc reload shop.test`, `journalctl -u ns@ns1`). Checks:

- `delegated`: `dig @10.0.9.13 +norecurse www.eu.shop.test` returns NS `ns-eu.eu.shop.test.` in authority **and** glue 10.0.9.15, and so does `@10.0.9.14` (the secondary has the change too: the serial went up and NOTIFY did its job).
- `eu-authoritative`: `@10.0.9.15 +norecurse www.eu.shop.test` has `aa` and 10.0.9.50.
- `secure-through-isp`: `on isp1 dig @10.0.9.21 www.eu.shop.test` gives 10.0.9.50 **with `ad`**.
- `ds-matches`: the DS at ns1 equals `dnssec-dsfromkey` of ns-eu's current KSK (computed in the check).

Wrong fixes:
- `no-glue.sh`: the NS line without the A. The resolver can't find `ns-eu.eu.shop.test`, so `delegated` fails.
- `serial-not-bumped.sh`: ns1 refuses the edit (fact 12), so the delegation never appears.
- `no-ds.sh`: resolves without `ad`, an island of security, so `secure-through-isp` fails.
- `old-ds.sh`: a DS made before ns-eu's keys were regenerated gives SERVFAIL.

About 30 minutes. Lab total: boot 6 s, ns-eu keygen under 2 s.

### 7.4 Recall on records and zones

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `zone-serial-next` | predict_shell | records-and-zones | A zone file line `( 2026111503 3600 600 1209600 300 ) ; serial`. The command bumps it with the same awk the lab uses. Prints `2026111504`. |
| `soa-fields` | predict_shell | records-and-zones | `dig shop.test SOA +short` output. `awk '{print "expire", $7, "negative", $8}'`. Prints the expire and minimum fields. The explanation teaches expire: a secondary that can't reach its primary for that long stops answering. |
| `mcq-cname-apex` | mcq | records-and-zones | The team wants `shop.test` (the apex) to point at a load balancer's name. Right: a CNAME can't sit at the apex because SOA and NS live there; use the DNS host's apex alias (Route 53 alias, Azure alias record set) or the balancer's addresses. Distractors cover a CNAME with a short TTL, an MX record, and a TXT record pointing at the name. |
| `mcq-which-record` | mcq | records-and-zones | Restrict which CAs may issue certificates for the domain. Right: CAA. Topic 31 depends on it, so keep it. Distractors: TXT with the CA's name, MX, a DS record. |
| `mcq-secondary-stale` | mcq | records-and-zones | After an edit, `@ns1` shows the new address and `@ns2` the old one, an hour later. What is the likeliest cause? Right: the serial wasn't raised (or ns2 isn't allowed to transfer), so ns2 still has the old copy. Distractors: ns2's cache hasn't expired (authoritative servers don't cache their zone); the TTL is an hour; ns2 doesn't validate. |
| `mcq-rndc-queued` | mcq | records-and-zones | `rndc reload shop.test` printed `zone reload queued`, and the answer didn't change. Where do you look? Right: the server's journal, which says why the zone wasn't loaded. Distractors cover the resolver cache, `dig +trace`, and re-running `rndc reload`. |

### 7.5 Recall on TTLs and caching, including the estimates (calculation skill)

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `est-lower-ttl-lead` | estimate | ttl-and-caching | `api.shop.test` has TTL 86400. The move is Friday at 18:00. At the latest, how many hours before the move must the lowered TTL (300) be live on every authoritative server? Exactly. **24** (`ttl / 3600`). Mistakes: 0.08 (`300 / 3600`, the new TTL), 48 (twice the TTL). |
| `est-forgot-to-lower` | estimate | ttl-and-caching | A record with TTL 14400 is changed at 09:00 without lowering. Until what hour can a resolver that fetched it at 08:59 still hand out the old address? Answer as hours after 09:00. Within 0.1. **4** (`14400 / 3600`). Mistakes: 0 ("changes are instant"), 0.07 (minutes misread). |
| `est-negative-ttl` | estimate | ttl-and-caching | Someone looked up `sale.shop.test` a minute before it was created. The zone's SOA has TTL 3600 and MINIMUM 900. For how many seconds at most can a resolver keep saying "no such name"? Exactly. **900** (`min(soa_ttl, minimum)`). Mistakes: 3600 (the SOA's own TTL), 4500 (sum). |
| `est-negative-ttl-2` | estimate | ttl-and-caching | Other numbers: SOA TTL 300, MINIMUM 86400. Exactly. **300**. Mistakes: 86400, 300 + 86400. |
| `est-resolver-cap` | estimate | ttl-and-caching | A record has TTL 172800. Unbound runs with its defaults. For at most how many seconds will it keep that answer? Exactly. **86400** (`min(ttl, 86400)`). Mistake: 172800. The cap is a number to know (fact 4), written into `working`. |
| `est-move-window` | estimate | ttl-and-caching | TTL 3600 is lowered to 60 at 10:00 (live on both servers at once). You switch at the earliest safe moment. How many minutes after 10:00 until every honest resolver has the new address? Exactly. **61** (`old / 60 + new / 60`). Mistakes: 60, 2. |
| `mcq-flush-caches` | mcq | ttl-and-caching | Halfway through a move, someone suggests "just flush the caches". Right: only caches you run can be flushed; the world's resolvers keep their copies until the TTL ends. |
| `mcq-raise-ttl-after` | mcq | ttl-and-caching | Why raise the TTL again after the move? Right: short TTLs multiply queries, and they make an outage at the DNS host felt by everyone within minutes. |

### 7.6 Recall on split-horizon

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `split-static-or-transparent` | predict_shell | split-horizon | Two small Unbound configs, `a.conf` (`static`) and `b.conf` (`transparent`), each with one `local-data` for `api.shop.test`. The command prints each file's local-zone type with `awk`. The question asks which one makes `www.shop.test` NXDOMAIN inside. Two-part output, so it stays a reading item with a judgement in the explanation. Alternatively make it an mcq on the captured `dig` results (tried output: `transparent: api=10.0.8.41 www=NOERROR mail=10.0.9.42`, `static: api=10.0.8.41 www=NXDOMAIN mail=`). |
| `mcq-private-zone-nxdomain` | mcq | split-horizon | A Route 53 private hosted zone `shop.test` holds only `api`. From an EC2 instance, `status.shop.test` (public only) fails. Right: the VPC Resolver found a matching private zone with no record and returned NXDOMAIN without asking public DNS. Distractors cover the public record's TTL, the VPC's DNS hostnames setting, and DNSSEC validation. |
| `mcq-azure-fallback` | mcq | split-horizon | Azure: which zones can use "Enable fallback to internet"? Right: Private DNS zones for Private Link resources only. Distractors cover all private zones, public zones, and zones linked to more than one network. |
| `mcq-split-which-resolver` | mcq | split-horizon | An office laptop gets the public address for `api.shop.test` though the private zone exists. Right: the laptop asks a resolver that doesn't hold the private zone (a public resolver set by hand), not the site's. |
| `mcq-resolver-rule-wins` | mcq | split-horizon | Route 53: a private zone `shop.test` and a Resolver forwarding rule for `shop.test` on the same VPC. Who answers? Right: the forwarding rule (fact 15). |

### 7.7 Recall on DNSSEC

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `dnssec-read-ede` | predict_shell | dnssec | The captured SERVFAIL with EDE 7 (`captured/dns-captures.txt`). `grep -o 'EDE: [0-9]* ([^)]*)' out.txt`. Prints `EDE: 7 (Signature Expired)`. |
| `dnssec-cd-flag` | predict_shell | dnssec | Two captured outputs: `dig www.legacy.shop.test` (SERVFAIL) and `dig +cd …` (an A record). The command prints each status or the answer. The explanation: the data exist and only validation fails. |
| `mcq-what-dnssec-proves` | mcq | dnssec | Right: the answer was signed by the zone's key and not altered on the way. Distractors: the question and answer are encrypted; the server is the one the resolver meant to reach (true only via the chain); the record is up to date. |
| `mcq-ds-mismatch` | mcq | dnssec | After "regenerating the zone's keys", validating resolvers SERVFAIL while `dig +cd` answers. Right: the parent's DS still matches the old key. Publish the new DS (and next time, introduce the new key before removing the old one). |
| `mcq-bad-fix` | mcq | dnssec | Why is `val-permissive-mode: yes` (or `domain-insecure`) the wrong fix for one bogus zone? Right: it lets every forged answer through for that zone (or all zones), which is exactly what validation exists to stop. |
| `est-ds-ttl-wait` | estimate | dnssec | The parent's DS for `shop.test` has TTL 86400. You remove the DS at 12:00 to unsign the zone. Within how many hours can you safely stop signing? Exactly. **24**. Mistakes: 0, 1. The Slack lesson. |
| `mcq-cloud-validation` | mcq | dnssec | Which default cloud resolver validates DNSSEC without any setting? Right: none of the three is confirmed to. Azure's default resolver says it doesn't; Route 53's validates only when switched on per VPC. Keep the choices to the facts read (facts 20 to 22), and re-check on the day. |

### 7.8 `write-zone-health` (write, lab), skills `records-and-zones`, `trace-resolution`

Prompt: write `~/bin/zone-health ZONE`. It asks the parent zone's servers which name servers `ZONE` is delegated to, then asks each of them, without recursion, for `ZONE`'s SOA. It prints one line per server, sorted by name: `NAME ADDRESS serial N` when the server answers with `aa`, or `NAME ADDRESS not authoritative` otherwise. The last line is `in sync` (every server authoritative with the same serial), `out of sync` (all authoritative, serials differ) or `broken` (any server not authoritative). The prompt names `dig +norecurse`, `+short`, the `aa` flag, `sort`, and `nano ~/bin/zone-health` plus `chmod +x`.

Checks make their own inputs at check time. The image's `test.` zone already delegates `check-a.test` and `check-b.test` to 10.0.9.16 and 10.0.9.17, where nothing runs normally. Each check starts two throwaway BIND instances in scratch namespaces `chk1` and `chk2` at those addresses, with zone files it writes to `/tmp` with **serials drawn at random**, runs the learner's script and compares, then stops them and deletes the namespaces. Three checks cover the three outcomes every run, so no outcome can be missed by chance:

- `in-sync`: both servers serve `check-a.test` with the same random serial.
- `out-of-sync`: serials differ by a random 1 to 50.
- `broken`: `chk2` is started without the zone, so it answers REFUSED with no `aa`.

A fourth check runs it on `shop.test` (the real ns1 and ns2) and compares with the check's own computation.

Wrong fixes:
- `hard-coded-names.sh`: prints `ns1.shop.test`/`ns2.shop.test` for any zone.
- `asks-resolver.sh`: uses the resolver, so the cached serial and no `aa` give a wrong verdict.
- `no-aa-test.sh`: treats a REFUSED answer as authoritative with an empty serial.
- `unsorted.sh`: prints in reply order.

Timing tried in part: a BIND instance starts and serves in under a second in a fresh namespace. The check's start, stop and namespace removal stay well under its 30 s. About 35 minutes.

### 7.9 Ladder order for `topic.yaml`

`example-follow-a-lookup`, `trace-who-answered`, `referral-sections`, `mcq-glue-why`, `mcq-aa-flag`, `mcq-forwarder-or-recursive`, `mcq-open-resolver`, `zone-serial-next`, `soa-fields`, `mcq-cname-apex`, `mcq-which-record`, `mcq-secondary-stale`, `mcq-rndc-queued`, `fill-delegate-eu`, `est-lower-ttl-lead`, `est-forgot-to-lower`, `est-negative-ttl`, `est-resolver-cap`, `est-move-window`, `mcq-flush-caches`, `split-static-or-transparent`, `mcq-private-zone-nxdomain`, `mcq-azure-fallback`, `mcq-split-which-resolver`, `dnssec-read-ede`, `dnssec-cd-flag`, `mcq-what-dnssec-proves`, `mcq-ds-mismatch`, `mcq-bad-fix`, `write-zone-health`. That's 25 quick items (about 38 minutes), a worked example, a fill-in and a write. `est-negative-ttl-2`, `mcq-raise-ttl-after`, `mcq-resolver-rule-wins`, `est-ds-ttl-wait` and `mcq-cloud-validation` are review-only.

**Practised before proven:**

| Skill | Practised in |
| --- | --- |
| trace-resolution | the example, six recall items, the fill-in, the write |
| records-and-zones | six recall items, the fill-in, the write |
| ttl-and-caching | the example (countdown, negative TTL), six practice items |
| split-horizon | four practice items. Neither proof asks for anything beyond `transparent` against `static` and one `local-data` line, both shown in those items. **Writer's choice:** add a step 8 to the worked example that changes the site resolver to `transparent` with one `local-data`, so the build isn't the first time the learner edits it. Recommended (it adds 5 minutes). |
| dnssec | the example (step 7), the fill-in (DS), five recall items |

## 8. Proofs

### 8.1 Build: `build-move-the-api` (systemd lab, 60 minutes), skills: all five

**Story.** Tonight the shop's API moves from 10.0.9.41 to its new server at 10.0.9.51. The office will reach the new server on its private address, 10.0.8.51. The prompt states the procedure's rules and the end state. It never says "lower the TTL by 2 minutes", but it does state the numbers:

1. `api.shop.test`'s TTL is 60 seconds today (scaled down, so the lab takes minutes; the prompt says so). During the move it must be **5**, and nobody may be sent to the old address after the switch for longer than that.
2. Change only the shop's own servers and the site's resolver. The ISPs' resolvers aren't yours: don't touch them, restart them or empty their caches. Nothing goes into a hosts file.
3. After the move, `api.shop.test`'s TTL is **3600** again.
4. Inside the office, `api.shop.test` answers 10.0.8.51, and **every other name in the zone still resolves as it does publicly**.
5. The zone stays signed and valid. Public resolvers must still get `ad`.

**What the image holds.**
- The machines of section 7, with `api.shop.test 60 IN A 10.0.9.41`.
- A monitor, `move-watch.service`, running in the `office` namespace from boot. Every second it asks `ns1` and `ns2` directly (`+norecurse`) and `isp1` to `isp3` for `api.shop.test` and for a canary name `canary.shop.test` (TTL 3600). It appends `epoch source answer ttl` lines to `/var/lib/lab/move.log`. The story seeds the ISP resolvers' caches with **staggered phases** (it first asks `isp1` at boot, `isp2` 15 s later, `isp3` 30 s later), so whenever the learner switches, some resolver holds a copy with at least 30 s left. That makes a short wait fail by outcome as well as by rule.

**Checks** (descriptions state end states):

| Id | Command (summary) | Catches |
| --- | --- | --- |
| `new-address` | `@ns1` and `@ns2` (`+norecurse`) give `api.shop.test` 10.0.9.51 with TTL 3600. Same SOA serial on both. | not moved, TTL not raised, ns2 behind |
| `waited-old-ttl` | From `move.log`: the first second the authorities served TTL 5 (T_low), and the first second they served 10.0.9.51 (T_switch). Requires T_switch − T_low ≥ 60. **Deterministic**, read from the authorities' own answers. | switching without lowering, or without waiting |
| `nobody-sent-back` | From `move.log`: no ISP answer of 10.0.9.41 later than T_switch + 5 + 2 s. | the outcome, and mistakes the rule check might miss |
| `caches-untouched` | From `move.log`: between T_low − 5 and T_switch + 10, no ISP's canary TTL rises without a gap of more than 5 s in the log first. A gap means the whole lab rebooted, which is allowed; a rise without one means a cache was emptied. Also compares the ISP config files' checksums with the image's. | flushing, HUP, editing other people's resolvers |
| `office-private` | `on office dig api.shop.test +short` = 10.0.8.51 | no split-horizon |
| `office-sees-the-rest` | `on office dig` for `www`, `mail`, `status` and one name the check picks at random from the zone file's other names. Each equals the authority's answer. | `static` shadowing |
| `still-secure` | `on isp2 dig @10.0.9.22 api.shop.test` has `ad`. `@10.0.9.22 www.shop.test` has `ad`. | a broken signature after an edit |
| `no-hosts` | no `shop.test` name in `/etc/hosts` or `/etc/netns/office/hosts` | the hosts shortcut |

`timeout:` is not needed: every check reads files or asks DNS once.

**Wrong fixes** (each as `wrong/*.sh`):

1. `switched-without-lowering.sh`: changes the address and the TTL to 3600 at once.
2. `waited-new-ttl-only.sh`: lowers, sleeps 10 s, switches (fails `waited-old-ttl`, and `nobody-sent-back` too thanks to the stagger).
3. `flushed-the-isps.sh`: lowers, switches at once, then `unbound-control flush` on each ISP (fails `caches-untouched`).
4. `restarted-the-isps.sh`: the same, with `systemctl restart isp@…`.
5. `ttl-left-low.sh`: the right procedure, never raises the TTL (fails `new-address`).
6. `static-private-zone.sh`: the right move, the private override as `static` (fails `office-sees-the-rest`).
7. `private-address-for-everyone.sh`: puts 10.0.8.51 in the public zone (fails `new-address` and `office-private`'s twin).
8. `serial-not-bumped.sh`: edits without bumping, so ns1 refuses (fact 12), the address never changes and the log shows no switch.
9. `hosts-file.sh`: the office override as a hosts line.

**CI time.** The solution and wrong fixes 5 to 7 must wait the old TTL (about 65 s each) to prove only their own fault. The others fail fast. Estimate: boot 6 s × 11 containers, plus 4 waits of 65 s, plus checks of about 5 s each: **about 6 minutes** for this lab under `labcheck test`. To cut it, the writer may drop wrong fixes 4 and 7 (3 and 6 cover the same checks): about 4 minutes.

**Restart trial.** Tried for the DNS machinery: a restart brought every server back in 6 s, kept keys, edits and the DS chain, and validation still passed. The monitor appends after the reboot, leaving a gap the `caches-untouched` check treats as a reboot. `move.log` is on disk, so the log checks still pass. Not yet tried with the monitor itself: **prove it before writing the lesson.**

**Tamper note.** `move.log` is writable by root, and a learner could edit it. That's not the hurried shortcut this check guards against, and the lesson says the log is evidence, as a change ticket is. Recommended: no further defence.

### 8.2 Debug: `debug-half-the-lookups` (systemd lab, 45 minutes), skills `records-and-zones`, `split-horizon`, `dnssec`, `trace-resolution`

**Prompt** (what, symptoms, count; never where). The shop's zone `shop.test` has two name servers, `ns1` (the primary) and `ns2` (its secondary). Its payments site is `pay.shop.test`, a child zone that `ns1` also serves, signed. The office uses the site's resolver on `lab`, which gives `api.shop.test` its private address. Since this morning:

- customers report that the shop "works one time in two" (their resolvers are the ISPs');
- payments fail for every customer whose resolver checks signatures, though `dig +cd` shows the records;
- in the office, `status.shop.test` and the mail server don't resolve, though they do from outside.

There are three faults. Rules: the ISPs' resolvers aren't yours (change nothing on them); both name servers stay in service; `pay.shop.test` stays signed, with its DS in `shop.test`; nothing in hosts files; the office keeps its private address for `api`.

**The faults** (from the story script, `story.sh`):
1. `ns1`'s `allow-transfer` and `also-notify` name ns2's old address, 10.0.9.24. ns2 moved to .14 last week. `ns2` serves its stale copy, where `api` is still the dead 10.0.9.41.
2. The site resolver's `shop.test` override is `static`.
3. `pay.shop.test` is served from a manually signed file whose signatures ended yesterday (`dnssec-signzone -s now-31d -e now-1d -P`, made by `story.sh` at first boot, so the dates are always "yesterday" whenever the lab is built).

**Checks:**

| Id | What it proves | Fails on |
| --- | --- | --- |
| `servers-agree` | `@ns1` and `@ns2` serve the same SOA serial, and `api` = 10.0.9.51 on both | fault 1 left, or allow-transfer fixed but no retransfer (refresh is 3600 s) |
| `every-lookup-works` | 20 lookups of `api.shop.test` through each of `isp1` to `isp3` (`+tries=1`), all 10.0.9.51 | intermittence |
| `office-sees-the-rest` | as in the build | fault 2 |
| `office-keeps-private` | `on office dig api.shop.test` = 10.0.8.41 | "fixing" fault 2 by deleting the override |
| `pay-secure` | `on isp1 dig @10.0.9.21 www.pay.shop.test` has `ad` | fault 3 |
| `pay-signed-for-a-week` | the earliest RRSIG expiration on `pay.shop.test`'s SOA and A records is at least 7 days ahead | re-signing for an hour |
| `ds-in-place` | `shop.test` has a DS for `pay` matching a current KSK of `pay` | going insecure |
| `validation-still-on` | `broken.test`, a zone the image delegates from `test.` with a deliberately wrong DS, still gives SERVFAIL through all three ISPs and the site resolver. Config checksums unchanged. | validation switched off anywhere |
| `both-servers-listed` | the NS set for `shop.test` at `tld` and at `ns1` is `ns1`, `ns2` | dropping ns2 |
| `no-hosts` | as in the build | |

**Wrong fixes:**
1. `validation-off.sh`: `val-permissive-mode: yes` on the site resolver and the ISPs.
2. `domain-insecure.sh`: `domain-insecure: "pay.shop.test"`.
3. `ds-removed.sh`.
4. `resigned-for-an-hour.sh`: `-e now+3600`.
5. `ns2-dropped.sh`: removes ns2 from the NS set.
6. `transfer-fixed-not-refreshed.sh`: corrects `allow-transfer`, never triggers NOTIFY or a retransfer.
7. `static-kept.sh`: fixes faults 1 and 3 only.
8. `override-deleted.sh`: removes the private zone.
9. `hosts-entries.sh`.
10. Plus one "two of three fixed" variant per fault, to confirm each fault alone turns its own checks red.

**Proved in the prototype:** the stale secondary after a key change (tried: ns2 held the old keys and an equal serial, so it never transferred and validators fed from ns2 saw the old keys), the `static` shadowing, and SERVFAIL with EDE 7 on a zone signed with lapsed dates. **Not yet built:** the story with the wrong `allow-transfer`, and the `broken.test` zone. Prove the contract under `labcheck test` first.

### 8.3 Explain

**Prompt.** "A colleague is moving the company's main website to a new load balancer on Friday and plans to 'change the DNS on Friday afternoon'. Explain, in your own words: how a laptop finds the website's address, from its own resolver to the zone's authoritative servers, and which of them may be holding an old answer; what you'd do in the days before the move and why, with the numbers; why a name you query before creating it can stay 'missing'; what happens to internal users if the company also has a private zone for the same domain in its cloud network; and what DNSSEC adds, what a broken signature looks like to users, and why turning validation off is the wrong fix. Say one way the three clouds differ."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `resolution` | yes | stub → recursive resolver (cache) → root → TLD → authoritative, by referrals; the authority sets `aa`; old answers sit in resolvers' caches, not at the authority |
| `ttl-procedure` | yes | lower the TTL at least one old TTL before the move (with the serial raised), switch, verify through several resolvers, raise the TTL after; you can't empty other people's caches |
| `negative` | yes | NXDOMAIN is cached for min(SOA TTL, MINIMUM) |
| `split-horizon` | yes | a private zone answers every name under it; missing names give NXDOMAIN inside (Route 53 and Cloud DNS; Azure the same except Private Link fallback), so copy every needed record or scope the zone narrowly |
| `dnssec` | yes | signatures plus the DS chain prove origin and integrity; broken means SERVFAIL at validating resolvers, `+cd` shows the data; fix by re-signing or the right DS; switching validation off accepts forgeries |
| `clouds-differ` | no | for example, Azure's default resolver doesn't validate; Route 53 validates when switched on per VPC; Cloud DNS signs but needs the registrar's DS |

## 9. Review pool

At least two per skill, mostly produced answers on real output or numbers.

- trace-resolution: `trace-who-answered`, `mcq-aa-flag`, `mcq-glue-why`, `write-zone-health`.
- records-and-zones: `zone-serial-next`, `mcq-secondary-stale`, `mcq-rndc-queued`, `mcq-cname-apex`.
- ttl-and-caching: `est-lower-ttl-lead`, `est-negative-ttl-2` (review-only), `est-move-window`, `est-resolver-cap`, `mcq-raise-ttl-after` (review-only).
- split-horizon: `mcq-private-zone-nxdomain`, `mcq-resolver-rule-wins` (review-only), `split-static-or-transparent`.
- dnssec: `dnssec-read-ede`, `est-ds-ttl-wait` (review-only), `mcq-ds-mismatch`, `mcq-cloud-validation` (review-only).

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| D1 | **The network-lab base** (being designed by another designer). What these labs need from it: (a) N "machines" as network namespaces joined to one bridge on `lab` (not one veth pair), from a table of name and address; (b) `on MACHINE CMD`; (c) `/etc/netns/<m>/resolv.conf` per machine; (d) a systemd template for "a service on a machine" (`svc@machine` style, `ip netns exec %i …`); (e) rebuilt at every boot by `lab-network.service`, ordered before every machine's services; (f) Docker's `/etc/resolv.conf` unmounted and replaced on `lab`. No kernel modules beyond veth, bridge and netns. No sysctls. No IPv6 routing (AAAA records can be served without it). nftables isn't needed by this topic. | The prototype's `network.sh` (bridge `br0`, a loop over `name:octet` pairs) is a working smallest version. |
| D2 | **The DNS topic layer**: `bind9 bind9-utils unbound` as the topic's second `RUN`, with `named` and `unbound` disabled at build (`systemctl disable`) and Ubuntu's `root-auto-trust-anchor-file.conf` removed. | 15.8 MB, tried |
| D3 | `dnssec-link.service`: once, at first boot, put DS records into parents and the root's DS into every resolver's trust anchor. Keys persist under `/var/lib/lab/dns`. | tried, 2 s |
| D4 | None in the app. Estimate items exist (ADR-0024). `predict_shell` reads captured files. | |

No ADR is needed. The labs follow ADR-0018 as amended, and every check is under 30 s.

## 11. Cost and time

- **Money:** none. Everything is local. No cloud lab is proposed: the cloud behaviours are taught from their documentation and asked as judgement. An optional real-cloud extra (a Route 53 private hosted zone shadowing a public one) would cost Route 53's hosted-zone fee, which isn't free tier, so none is proposed.
- **Learner minutes:** lesson 15, reading 50 (DigitalOcean's three sections 22, Julia Evans 13, Cloudflare 14), 25 quick items 38, worked example 25, fill-in 30, write 35, build 60, debug 45, explain 20. **Total 318.** With the optional step 8 in the worked example, 323. Over Module 2's 240 to 300 range: see open question 1.
- **Labs and CI:** five labs (example, fill-in, write, build, debug). Boot 6 s each. A labcheck contract run: example about 1 min, fill-in about 2 min, write about 2 min, build about 6 min (4 if trimmed), debug about 5 min (13 containers × about 20 s). **About 16 minutes for the topic** in one Labs shard, about 4 minutes of wall time at four jobs.

## 12. Open questions, each with a recommendation

1. **318 minutes is over the 300 that Module 2 split at.** Option A: split DNSSEC into its own short topic (`csa.net.dnssec`, about 110 minutes), leaving DNS at about 230. Option B: keep one topic and trim the build's wrong fixes and the optional readings. **Recommendation: B.** DNSSEC's failure modes are explained by the TTL and delegation ideas in this topic, the debug lab mixes all three skills the way real outages do, and the overrun is 18 minutes, mostly reading. If the critic holds a hard 300-minute line, take A and move `est-ds-ttl-wait`, the EDE items and the debug's fault 3 with it.
2. **BIND, NSD or Knot for the authoritative servers.** **Recommendation: BIND** (in the prototype). It's the reference implementation, its zone files and `named-checkzone` are what most guides use, its inline signing gives the "edit without serial bump isn't loaded" lesson for free, and it is one package for all four authoritative machines. **Unbound for every resolver**, because using two programs makes "authoritative and recursive are different jobs" concrete.
3. **Scaled TTLs in the build (60 s and 5 s).** **Recommendation: yes,** stated in the prompt as scaled. The estimate items carry the real-world numbers (86400, 14400).
4. **Should the learner see the monitor's log?** **Recommendation: yes,** `cat /var/lib/lab/move.log` is how a real change is evidenced, and reading it is part of checking the move. The prompt names it.
5. **A real-cloud extra.** **Recommendation: none.** Route 53 hosted zones bill monthly, and Azure Private DNS bills per zone too (not checked this session). The behaviours are documented clearly enough to teach as judgement.

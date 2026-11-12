# Topic 36: `csa.net.troubleshooting`, Network troubleshooting

Designer's brief, 2026-11-11. The writing brief for Module 3's last topic. It has the shape of the Module 2 briefs, and Module 2's decisions stand (estimate items for calculations, captured or constructed fixtures labelled as such, the restart trial, debug prompts that give purpose, symptom and count only, targets stated and self-timed).

Prototypes, captured output and contract logs: `prototypes/troubleshooting-checkpoint/` (its `CAPTURES.md` holds every real output quoted here; `repo/content/topics/csa.m3tc-proto/exercises/t36-mechanisms/` is the prototype of this topic's debug network). Everything was built on a copy of the network-lab base (`repo/content/lab-bases/m3tc/`, the base designer's prototype unchanged) under names of my own, so no other designer's image or container was touched.

**What this topic must not be.** Every Module 3 topic already has a debug lab: a broken thing, three faults, find and fix. If topic 36 is a fourteenth of those, it teaches nothing new. What it teaches is the **method** itself, practised on purpose, and three things the other topics' debugs don't ask for: faults that come and go (an intermittent fault has to be *measured* before it can be found), naming the cause before touching anything, and a fault that isn't yours to fix (the provider's), which you prove and hand over with evidence. The practice ladder fades from a guided live diagnosis, through recorded evidence read against a clock, to two small tools that make intermittent faults measurable, and the debug is a live network whose third fault can't be fixed, only proven.

**Read with.** The other Module 3 designers' briefs existed in the shared folder on the day this was written, and I read their skills tables and debug designs to avoid repeating their faults (section 12, open question 1). Where a skill id from another topic is used, it is taken from those drafts and marked *(draft)*; the critic reconciles.

## 1. What the learner will be able to do

1. Turn "it doesn't work" into a precise symptom: from where, to what, by name or by address, which address family, which size of request, always or sometimes, since when, and what changed.
2. Choose the test that rules out about half of the remaining suspects, and read each result as "rules in" or "rules out": by address against by name, ping against TCP against HTTP, small against large, one source against another, one hop against the next, one connection's path against another's.
3. Find where along a path traffic stops: read `mtr` and `traceroute` without being fooled (a hop that rate-limits its answers, loss that doesn't carry on to the end, a return path you can't see), capture at two points and compare, ask each router which way it would send a packet (`ip route get`), and, where traffic is shared over several paths, prove the path a connection took with captures on each outgoing interface rather than trusting a tool's prediction.
4. Measure a fault that comes and goes: sample over time, count, work out the failure rate, and break the failures down by a variable (the address used, the path, the size, the server, the time window) until one value of it holds all the failures. Know how many clean samples it takes before believing a fix.
5. Read what the systems themselves recorded: a service's journal, a web server's error log and the error numbers in it, a load balancer's log line, a name server's transfer messages, a firewall rule's counter, an interface's drop counters, and line their timestamps up with the symptom.
6. Name the cause and its evidence before changing anything; change one thing; prove the symptom is gone with enough samples and that nothing else broke; write the incident note; and, when the fault is on a provider's side, write the ticket the provider needs.

**The six-month core.** Six months on, the learner should still (a) ask the scoping questions before touching anything, (b) pick the splitting test for a given set of results, (c) read an `mtr` report correctly, including the rate-limited hop, (d) do the arithmetic of intermittent faults (a share of requests failing, two faults together, the chance a fault is still there after a clean run), and (e) know which log or counter holds the evidence for a given kind of fault. The review pool (section 9) is built from those five: mostly judgement on real output and calculation with real numbers, and almost no recall of names.

## 2. Prerequisites and terms

**`prerequisites: [csa.net.load-balancing, csa.net.ipsec]`**. Topic 36 is the module's last topic and draws its cases from all the others: through these two (and their own prerequisites, per the drafts: IPsec after BGP after routing after CIDR after layers; load balancing after HTTP after DNS after transport after NAT) every Module 3 topic comes before it. *Assumption for the critic:* those chains hold. If the critic shortens them, keep at least `csa.net.dns`, `csa.net.routing`, `csa.net.transport` and `csa.net.load-balancing` direct, because the debug uses all four, and drop the IPsec case from the casebook (7.3) if IPsec no longer comes first.

**Builds on, for the writer** (taught there; this topic never re-teaches it):

| Topic | What this topic uses |
| --- | --- |
| `csa.linux.net-tools` | `ip`, `ss`, `dig`, `curl -v`, `nc -zv`, `traceroute` and `mtr` named, `tcpdump -nn -i IF FILTER`, refused (`[R.]`) against dropped (repeated SYN), nftables chains, policies, `ct state`, "a fix belongs in the file", the order "name, port, protocol" |
| `csa.linux.services`, `csa.linux.triage` | `journalctl -u UNIT`, the idea of a method (the USE method; Module 1's sixty-second checklist), "measure, change one thing, measure again" |
| `csa.linux.scripting`, `csa.linux.shell` | Bash scripts with `set -euo pipefail`, loops, `awk` and `sort | uniq -c` over logs |
| `csa.net.layers` *(draft)* | the layer model as a debugging map, ARP and `ip neigh`, ICMP types (unreachable, time exceeded, fragmentation needed), MTU and PMTUD black holes, reading Ethernet and IP headers in a capture |
| `csa.net.routing` *(draft)* | longest-prefix match, `ip route get`, FRR's `show ip route`, return paths, ECMP "in one paragraph", the black-hole symptoms (`!N`, silence) |
| `csa.net.transport` *(draft)* | TCP's timers: a refused connection answers at once, a silent host takes about two minutes on Linux by default; idle cuts |
| `csa.net.dns` *(draft)* | resolvers and authoritative servers, `dig @server`, TTLs and caching, secondaries and serials |
| `csa.net.load-balancing` *(draft)* | HAProxy's `show stat` and its log line, health checks that pass while users fail |
| `csa.net.nat`, `csa.net.ipsec`, `csa.net.bgp`, `csa.net.http-tls` *(drafts)* | their failure evidence appears as recorded cases in the casebook (7.3): `conntrack -S`, charon's log, `show bgp summary`, `openssl s_client` verify codes |

**Terms this topic must define itself:** symptom and cause; scope (who and what is affected); hypothesis; suspect; the half-split, bisection or divide and conquer (one name, used throughout: **split**); "what changed"; intermittent; sample, failure rate and failure window; correlation (failures that share a value) against cause; red herring; anti-method (Gregg's word, with the streetlight, random-change and blame-someone-else examples); ICMP rate limiting (a router answers probes at most so often, so a hop can look lossy when nothing is lost); **mtr's report columns** (`Loss%`, `Snt`, `Last`, `Avg`, `Best`, `Wrst`, `StDev`: Module 1 named mtr but never read a report); curl's exit status as evidence (6, 7, 28, 22, 35, 60) and curl's address fallback; gratuitous ARP (an announcement nobody asked for, the way failover software claims an address); egress filtering (an `output` chain with `policy drop`); a looking glass (read-only view of someone else's router: the BGP draft defines it, this topic only uses the word); escalation and the provider ticket; incident note.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `scope-it` | The scoping questions (from where, to what, by name or address, IPv4 or IPv6, small or large, always or sometimes, since when, what changed); a grid of sources against destinations and what its pattern points at; "what changed" as the first suspect |
| `split-the-suspects` | Choosing the test that rules out about half of what's left, and reading each result as rules in or rules out; the standard splits (name against address, ping against TCP against HTTP, small against large, another source, another path); curl's exit status as a layer verdict |
| `locate-on-the-path` | `mtr` and `traceroute` read correctly (loss that carries on to the end is real, loss at one hop that later hops don't show is rate limiting, the return path is invisible: test both ways); captures at two points (and on every outgoing interface where traffic is shared over several paths); `ip route get` per hop |
| `measure-intermittent` | Sampling over time; failure rate; breaking failures down by a variable until one value holds them all; the arithmetic: a share of servers or paths, two independent faults together, a page of several connections, and the chance a fault survives a clean run (estimate items) |
| `read-logs-and-counters` | Which record holds the evidence for which fault: `journalctl -u`, nginx's error log and its error numbers (110 timed out, 111 refused, 113 no route), HAProxy's log line (backend and server, status, termination state), BIND's transfer and notify lines, nftables counters, `ip -s link`, `conntrack -S`; lining timestamps up with the symptom |
| `prove-and-record` | Name the cause with its evidence before changing anything; one change at a time; prove the fix with enough samples and check nothing else broke (still a firewall, still there after a reboot); the incident note; the provider ticket (time window, source and destination, both directions' `mtr`, the first lossy hop, what you ruled out) |

Six skills, the most the house rules allow. `measure-intermittent` is the calculation skill and gets four estimate items in practice and two more in review.

## 4. Lesson plan

The lesson is short (about 15 minutes of the topic's own text) because the main resource carries the method; the lesson supplies what no resource does for a beginner: the network-specific splits, the mtr traps, the intermittent arithmetic and the cloud picture. Resources are in section 6.

1. **Why a method** (resource R2, Gregg's methodology page: the anti-methods and "Problem statement method"; 5 minutes). The streetlight anti-method (looking where it's easy, not where the fault is), random change (changing things until it works, so you never learn what was wrong and may add a fault), blame someone else. Then the alternative in one line: scope, split, locate, read the records, name it, fix one thing, prove it. This is the topic's spine; every later section is one of its steps.
2. **The method in full** (R1, the SRE book's chapter 12, "Effective Troubleshooting": its "Theory", "In Practice" and the case study; the main resource, about 38 minutes). Triage, examine, diagnose, test and treat. The lesson points out what the chapter calls "simplify and reduce" and "divide and conquer", which this topic calls **split**, and its "what touched it last", which is the scoping question "what changed".
3. **Scope first** (lesson supplies; R2's problem-statement questions as the model). *Picture in words, the symptom grid:* a small table with sources down the side (the office, the data centre, the cloud) and destinations across the top (the web page, the API, a name lookup), each cell "works", "fails" or "sometimes". One failing column points at the destination; one failing row at the source; a single failing cell at the path between them; "sometimes" anywhere means the next step is measuring, not guessing. The scoping questions, network edition: from where; to what (name or address); IPv4 or IPv6; small or large; always or sometimes, and if sometimes how often; since when; what changed.
4. **Split the suspects** (lesson supplies; Gregg's "Process of Elimination" as the idea). The standard splits, each with what it rules in and out, as a table the recap repeats:

   | Test | Works | Fails |
   | --- | --- | --- |
   | The same request by address instead of by name | the fault is in naming (resolver, name server, cache, hosts file) | naming is cleared; look below it |
   | `ping` against `nc -z` against `curl` | layer 3 works; climb | the first that fails names the layer |
   | A small response against a large one | | MTU and PMTUD (topic 23) |
   | From another source on the same network, then from another network | the fault is on the first source | the fault is on the path or the destination |
   | The same connection again from another source port | | the path is chosen per connection (ECMP, a balancer): one path or one server is bad |

   And curl's exit status as a ready-made layer verdict: 6 (no address for the name), 7 (no connection: refused, or the router said "unreachable"), 28 (out of time: dropped somewhere, or nobody at the address), 22 with `--fail` (an HTTP error), 35 and 60 (TLS). Tried in the lab (fact 9): refused gave exit 7 in a quarter of a millisecond; a firewall that drops gave exit 28 at the connect timeout.
5. **Locate on the path** (R3, Akamai's MTR guide, its sections on reading reports and on rate limiting, about 15 minutes; R7, the kernel's `icmp_ratelimit`). *What the lesson supplies:* the two rules for an mtr report, worked on a captured report (fact 12): loss that starts at a hop and carries on to the destination is real, and it starts on the link *before* the first lossy hop; loss at one hop that the next hop doesn't show is that router rate-limiting its answers (Linux answers at most one per second per destination by default, so probing a hop twice a second shows about half "lost"). Then: the return path is invisible to you, so ask for an mtr from the other end (R3 says so). Captures at two points: a packet seen at A and not at B was lost between them. `ip route get` on each router of the path. With ECMP (equal paths shared per connection), **prove the path with traffic, not with a prediction**: `ip route get ... ipproto tcp sport P dport Q` exists to say which path a connection would take, but on the kernel tried it disagreed with where forwarded connections really went (fact 15), while captures on each outgoing interface showed it at once. The lesson tells this as it happened, because it is the method's own point: a tool's opinion is a hypothesis, the packets are the evidence. **Where R3 is out of date:** its remark that loss of around 10% is "of no real concern" is too generous: TCP's throughput falls with the square root of the loss rate (topic 29's arithmetic, *draft* skill `loss-latency-math`), so the lesson says plainly that sustained loss of a few percent is worth a ticket.
6. **Faults that come and go** (lesson supplies; nothing free covers it for networks at this level). Sample, don't stare: a loop of requests with a timestamp, the address, the result and the time each took (the debug's office monitor does exactly this, and the write exercise builds one). Then break the failures down by every variable you logged; the one whose value holds all the failures is your lead. Typical variables and the cause each points at: the address (DNS round robin with a bad server, a stale record), the source port (ECMP with one bad path), the server behind a balancer (one bad backend), the size (MTU), the time (a cache's TTL, a timer, a job). The arithmetic, each with a worked example: one bad server of three fails a third of requests; two independent faults that fail a quarter and a tenth fail 1 − 0.75 × 0.9 = 32.5% together; a page that needs four connections over two paths, one bad, fails 1 − 0.5⁴ = 93.75% of the time; after a fix, 30 clean requests prove less than they seem: a fault that failed one in ten still gives 30 clean requests 0.9³⁰ ≈ 4% of the time. And one cloud lesson: a health check that passes says only that the health page works (topic 33).
7. **Read the records** (lesson supplies, with R4 and R5 for curl and R8 for nginx's log): which record for which fault, as a table the recap repeats (service journal; nginx's error log with errno 110, 111 and 113 decoded; HAProxy's log line field by field; BIND's transfer and notify lines; nftables `counter`; `ip -s link`; `conntrack -S`). Line timestamps up: when did the first error appear, and what changed just before? A log that says all is well is evidence too, but only of what that program checked.
8. **Prove it, record it, hand it over** (R1's "Test and Treat" and "Cure"; lesson supplies the notes). Name the cause and the evidence, out loud or in the notes, before changing anything: if you can't, you're guessing. Change one thing. Prove the symptom is gone with enough samples (section 6's arithmetic) and that you broke nothing (Module 1's rules: still a firewall, still there after a reboot). The incident note, five lines: symptom, cause, evidence, fix, how it was verified. The provider ticket: the time window, source and destination addresses, mtr in both directions, the first lossy hop and the link before it, what you ruled out, a capture if you have one.
9. **Where the three clouds differ** (R9 to R13; Module 11's `csa.cnet.visibility` goes deep). In a cloud you can't log in to the router, so "capture at two points" becomes the provider's tools: **AWS** Reachability Analyzer (analyses configuration, sends no packets, charged per analysis), VPC Flow Logs, Traffic Mirroring (from interfaces of supported, Nitro-based instance types); **Azure** Network Watcher (IP flow verify, next hop, connection troubleshoot, packet capture on a VM, VPN troubleshoot, flow logs; network security group flow logs retire on 2027-09-30 in favour of virtual network flow logs); **Google Cloud** Connectivity Tests (configuration analysis, plus live data-plane probes for some paths), VPC Flow Logs, Packet Mirroring (whole packets, payloads included). From a VM, `mtr`, `traceroute`, `tcpdump` and `curl` work as here, and the provider's network is the "provider" of this topic's debug: you prove the fault and open a ticket.

**Recap** (the lesson's last block): the spine (scope, split, locate, read, name, fix one thing, prove, record); the splits table; the mtr rules; the variables table for intermittent faults and the three formulas; the records table; the incident note's five lines; the ticket's contents.

## 5. Verified facts

Each read or tried on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | The SRE book's chapter 12 frames troubleshooting as the hypothetico-deductive method; its "In Practice" covers problem report, triage, examine, diagnose, test and treat, cure; it recommends "simplify and reduce" and, for large systems, bisection; it treats recent changes as a productive place to start; four common pitfalls; footer "Licensed under CC BY-NC-ND 4.0"; about 5,000 words | https://sre.google/sre-book/effective-troubleshooting/ |
| 2 | Gregg's page lists anti-methods (Blame-Someone-Else, Streetlight, Drunk Man, Random Change, Passive Benchmarking, Traffic Light) and methods including Problem Statement (six questions, among them "What has changed recently?" and "Does the problem affect other people or applications?") and Process of Elimination; no licence notice on the page (so: all rights reserved, linked only); last updated 23 January 2025 | https://www.brendangregg.com/methodology.html |
| 3 | Akamai's MTR guide: loss at a hop with 0.0% at the next is "likely ... ICMP rate limiting and not actual loss"; "always trust the reports from later hops"; loss continuing over more than one hop may be real; collect reports in both directions because the return route doesn't appear; `--report` sends 10 cycles by default, `-c` sets the count; "© 2003-2026 Akamai Technologies. All rights reserved."; updated 2018-05-10. Its line that losses of about 10% are of no real concern is contradicted by fact 4 and is not repeated | https://www.akamai.com/cloud/guides/diagnosing-network-issues-with-mtr/ (the old linode.com address redirects here) |
| 4 | TCP throughput under loss falls with the square root of the loss rate (the loss-based ceiling 1.2 × MSS ÷ (RTT × √p)) | topic 29 *(draft)*, its skill `loss-latency-math` and its sources; not re-read by me |
| 5 | Linux `icmp_ratelimit`: default 1000, "the minimal space between responses in milliseconds", 0 disables; `icmp_ratemask` default 6168 rate-limits Destination Unreachable, Source Quench, Time Exceeded and Parameter Problem (echo replies are not limited) | https://docs.kernel.org/networking/ip-sysctl.html |
| 6 | `fib_multipath_hash_policy`: 0 layer 3 (default), 1 layer 4, 2 layer 3 or inner layer 3, 3 custom | same page |
| 7 | curl exit codes: 6 "Could not resolve host", 7 "Failed to connect to host", 22 HTTP error 400 or above "only ... if --fail is used", 28 "Operation timeout", 35 "SSL connect error", 52 "The server did not reply anything", 56 "Failure in receiving network data", 60 "Peer certificate cannot be authenticated with known CA certificates"; `remote_ip` is "the remote IP address of the most recently done connection" | https://curl.se/docs/manpage.html |
| 8 | libcurl, several addresses: "When libcurl has multiple addresses left to try to connect to, and there is more than 600 millisecond left, it does at most allow half the remaining time for this attempt" | https://everything.curl.dev/transfers/conn/how.html |
| 9 | Tried: exit 6 for an unresolvable name; exit 7 in 0.0002 s for a refused port; exit 28 at exactly `--connect-timeout 2` for a port a firewall drops and for an address nobody holds; `%{remote_ip}` empty whenever no connection was made | captured, `CAPTURES.md` §2 |
| 10 | Tried: with two addresses for a name, the first unreachable, curl `--max-time 5` gave up on the first after 2.50 s and succeeded on the second (the monitor's "200 2.503") | captured, `CAPTURES.md` §1 |
| 11 | ct state RELATED: "The packet is starting a new connection, but is associated with an existing connection, such as an FTP data transfer or an ICMP error" | https://man7.org/linux/man-pages/man8/iptables-extensions.8.html |
| 12 | Tried: an mtr report with 8% loss on the provider's last link (netem) and a 2000 ms ICMP limit on an earlier router showed 37.5% at the limited hop, 0.0% at the next, 10.0% from the first hop after the lossy link to the end; with Linux's default limit on every router and `-i 0.5`, every hop showed about 33% | captured, `CAPTURES.md` §2 |
| 13 | Tried: a second machine claiming a load balancer's address and announcing it every 20 s (gratuitous ARP) made the router's ARP entry flip; `arping` showed replies from two MACs ("Received 4 response(s)" for 3 probes) and `tcpdump -e` two replies to one request; in a minute of requests 24 of 30 reached the old machine's 503 page | captured, `CAPTURES.md` §2 |
| 14 | Tried: an outbound firewall on one of three backends blocking its database gave nginx "upstream timed out (110: Connection timed out) while connecting to upstream", HAProxy `apis/api3 ... 504`, and a rising counter on the output chain, while all three backends' health checks stayed UP | captured, `CAPTURES.md` §2 |
| 15 | Tried: with two equal BGP paths and policy 1 on r2, `ip route get 10.30.0.11 from 10.10.0.10 iif eth0 ipproto tcp sport P dport 80` named tun1 for some ports and tun2 for others, but with a filter on tun2 the connections it sent to tun1 were among those dropped and some it sent to tun2 arrived: no agreement. Captures on tun1 and tun2 during 20 real connections showed the true spread (19:1, 10:10 and 5:15 in three runs) | captured, `prototypes/troubleshooting-checkpoint/CAPTURES.md` §3 and the checkpoint brief's finding 7 |
| 16 | AWS Reachability Analyzer "is a configuration analysis tool"; charged per analysis | https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html |
| 17 | Azure Network Watcher's diagnostic tools: IP flow verify, NSG diagnostics, next hop, effective security rules, connection troubleshoot, packet capture, VPN troubleshoot; flow logs; NSG flow logs retire on 2027-09-30; page dated 2026-02-25 | https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-overview |
| 18 | Google Connectivity Tests simulates the expected path from configuration and, "for some connectivity scenarios", performs live data plane analysis with probe packets | https://docs.cloud.google.com/network-intelligence-center/docs/connectivity-tests/concepts/overview |
| 19 | AWS Traffic Mirroring copies traffic from an elastic network interface to monitoring appliances; supported source instance types are listed (Nitro-based); charged per session-hour | https://docs.aws.amazon.com/vpc/latest/mirroring/what-is-traffic-mirroring.html |
| 20 | Google Packet Mirroring "clones the traffic of specified instances" and "captures all traffic and packet data, including payloads and headers" | https://docs.cloud.google.com/vpc/docs/packet-mirroring |
| 21 | BIND 9.18 (Ubuntu 24.04's) defaults `allow-transfer` to any; 9.20 changed the default to none (ISC's bind-users list, December 2025, pointing at the 9.20 release notes, not re-read) | https://lists.isc.org/pipermail/bind-users/2025-December/110390.html ; the labs set `allow-transfer` explicitly, so neither default matters to them |

Not confirmed, so not claimed: Everything curl's licence (the page shows none; the book's repository is believed to be CC BY 4.0: check before linking with a licence line); nginx's documentation licence (R8: check the footer); any free video on network troubleshooting method (none was opened; see open question 4).

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 (main) | Google SRE book, chapter 12, "Effective Troubleshooting" (Chris Jones) | https://sre.google/sre-book/effective-troubleshooting/ | reading | CC BY-NC-ND 4.0 (linked, not copied) | 38 | all six, especially `scope-it`, `split-the-suspects`, `prove-and-record` | 2026-11-11 |
| R2 | Brendan Gregg, "Performance Analysis Methodology": the anti-methods, "Problem Statement Method", "Process of Elimination" | https://www.brendangregg.com/methodology.html | reading (sections) | copyright Brendan Gregg, no licence stated (linked) | 5 | `scope-it`, `split-the-suspects` | 2026-11-11 |
| R3 | Akamai (Linode) guides, "Diagnosing Network Issues with MTR" | https://www.akamai.com/cloud/guides/diagnosing-network-issues-with-mtr/ | reading | © Akamai, all rights reserved (linked) | 15 | `locate-on-the-path` | 2026-11-11 |
| R4 | Everything curl, "How libcurl connects" (several addresses, half the remaining time) | https://everything.curl.dev/transfers/conn/how.html | reading (one page) | to confirm (see section 5) | 2 | `split-the-suspects`, `measure-intermittent` | 2026-11-11 |
| R5 | curl(1), the section "EXIT CODES" and `--write-out` | https://curl.se/docs/manpage.html | reference | curl project documentation (licence to confirm from its Copyright page) | 3 | `split-the-suspects` | 2026-11-11 |
| R6 | tcpdump(1) (Module 1's resource, reread for `-e`) | https://www.tcpdump.org/manpages/tcpdump.1.html | reference | BSD-3-Clause | 3 | `locate-on-the-path` | Module 1 |
| R7 | Linux kernel, IP sysctl: `icmp_ratelimit`, `icmp_ratemask`, `fib_multipath_hash_policy` | https://docs.kernel.org/networking/ip-sysctl.html | reference | GPL-2.0 (kernel documentation; linked) | 3 | `locate-on-the-path` | 2026-11-11 |
| R8 | nginx, `ngx_http_upstream_module` / error log (for the meaning of upstream errors) | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | reference | to confirm before linking | 3 | `read-logs-and-counters` | not opened: open before use |
| R9 | AWS, "What is Reachability Analyzer?" | https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html | reading | AWS documentation, copyright (linked) | 3 | clouds | 2026-11-11 |
| R10 | Azure, "Azure Network Watcher overview" | https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-overview | reading | Microsoft Learn, CC BY 4.0 per the docs repository (as recorded for other Microsoft Learn links in the track) | 6 | clouds | 2026-11-11 |
| R11 | Google Cloud, "Connectivity Tests overview" | https://docs.cloud.google.com/network-intelligence-center/docs/connectivity-tests/concepts/overview | reading | Google Cloud documentation, CC BY 4.0 (the spec's "Before authoring") | 4 | clouds | 2026-11-11 |
| R12 | AWS, "What is Traffic Mirroring?" | https://docs.aws.amazon.com/vpc/latest/mirroring/what-is-traffic-mirroring.html | reading | AWS documentation (linked) | 3 | clouds | 2026-11-11 |
| R13 | Google Cloud, "Packet Mirroring" | https://docs.cloud.google.com/vpc/docs/packet-mirroring | reading | CC BY 4.0 | 3 | clouds | 2026-11-11 |

The lesson assigns R1 in full (38), R2's three sections (5), R3 (15) and R4 (2): 60 minutes. R5 to R13 are "more resources", used by the labs as references.

## 7. Practice ladder

Fading: a guided **live** diagnosis, then **recorded** evidence against a clock, then a **tool** for measuring intermittent faults, then the build (a second tool, from blank) and the debug (live, unguided). The faults in this ladder are chosen so that none is a fault of the debug (section 8.2) or of Checkpoint 3's part 2: practice never gives a proof away.

Lab images: the two network labs (7.1 and 7.5) start `FROM` the network-lab base; the three recorded-evidence labs (7.3, 7.4 and the build) are **plain** labs with one shared first `RUN` (`sudo nano less procps gawk python3`), python3 being the checker's tool, not the learner's.

### 7.1 `example-follow-the-method` (worked example, network lab, 35 minutes)

**The network** is Checkpoint 3's prototype network in its first version (prototyped and passing: `debug-the-outage`), trimmed to **one** fault: r1 still carries a static route for 10.30.0.0/25 through the old VPN appliance, which no longer forwards, and being more specific than BGP's 10.30.0.0/24 it wins. The office monitor logs every load. The symptom a person sees: some page loads take two and a half seconds; most are instant.

*Why this fault:* it's a routing fault the learner met in topic 26 (whose debug has a stale blackhole route), so the example spends its effort on the **method**, not on a new mechanism, and it is not a fault of any proof in this topic or the checkpoint (whose final version no longer uses it: checkpoint brief, part 2).

**Labelled steps** (the prompt gives each command; the learner runs it and writes one line into `~/example/notes.txt`):

1. *Scope.* `tail -n 40 /var/log/shop-monitor.log`. Two kinds of line: instant, and 2.5 s with two addresses tried. `scope=some-loads-slow`.
2. *Measure.* `awk '{print $3}' /var/log/shop-monitor.log | sort | uniq -c`: the slow loads are exactly those that tried 10.30.0.11 first. `slow_share=` the share of slow loads, worked out by the next given `awk` line (the check recomputes it from the log at check time, within 5 points, because the log keeps growing).
3. *Split.* By address: `on pc curl -s -m 3 -o /dev/null -w '%{http_code}\n' -H 'Host: www.shop.test' http://10.30.0.11/health` fails, 10.20.0.11 works. By name is cleared: it's one address. `fails_by_address=10.30.0.11`.
4. *Locate.* `on pc traceroute -n 10.30.0.11` stops after r1's address and then `* * *`; `on r1 ip route get 10.30.0.11` says `via 10.0.99.2 dev old0`; `on r1 vtysh -c 'show ip route'` shows `S>* 10.30.0.0/25 ... old0` above `B>* 10.30.0.0/24`. `where=r1`.
5. *Name the cause before changing anything.* `cause=stale-more-specific-route` (from the list in the prompt) and `evidence=S>* 10.30.0.0/25`.
6. *Fix one thing.* `router r1` (or `on r1 vtysh`), `conf t`, `no ip route 10.30.0.0/25 10.0.99.2`, `end`, `write memory`.
7. *Prove it.* Twenty loads by address and by name, all instant (`for i in $(seq 20); do ...; done | sort | uniq -c`); `verified=20/20`.

**Checks:** notes complete (each key present); `slow_share` within 5 points of the log's own share; `fails_by_address`, `where`, `cause` right; r1's route to 10.30.0.11 via r2, no static route for a shop network in r1's running configuration, and saved (the base's `frr_saved`); twenty loads by address from the office each under a second. **Wrong fixes** (the example's are few, as Module 2's were): `not-saved.sh`, `kernel-route.sh` (a more specific route added with `ip route add`), `notes-guessed.sh` (the route removed but `cause=dns`). **Image:** the checkpoint prototype's, minus the DNS and firewall faults. **CI:** 5 container runs, about 2 minutes (measured 23 s per run for this network under `labcheck test`).

### 7.2 Recall: the method

Every multiple-choice item below is written out in full by the writer, each wrong choice a plausible claim of the same shape (the cores-memory topic is the model), and the right answer never more than 1.5 times the longest wrong one. The scenario and the right answer are given here; the writer adds the distractors named.

| Id | Type | Skill | Scenario and answer |
| --- | --- | --- | --- |
| `mcq-first-questions` | mcq | `scope-it` | A ticket: "the shop is down". Which first step narrows it most? Right: ask from where, to which name or address, and since when. Wrong: restart the web server; check the server's CPU; open the firewall for the shop's port. |
| `mcq-symptom-grid` | mcq | `scope-it` | Grid: from the office the site fails and the API works; from the data centre both work; from the cloud both work. Right: the fault is on the office's path to the site (or a rule that applies to the office's address). Wrong: the site's server is down; DNS is broken for everyone; the API is the cause. |
| `mcq-what-changed` | mcq | `scope-it` | Errors started at 14:02; the change log shows a firewall change at 13:58 and a certificate renewal at 09:00; the application was last deployed a week ago. Where to look first? Right: the 13:58 firewall change. Wrong: the certificate (it's the most common outage); the deploy (code changes are riskiest); the busiest server. |
| `mcq-name-or-address` | mcq | `split-the-suspects` | By name the page fails; by address (with the Host header) it loads every time. Right: the fault is in naming, so ask the name servers directly and compare. Wrong: the web server's firewall; the route to the server; the server's TLS. |
| `mcq-ping-not-tcp` | mcq | `split-the-suspects` | `ping` answers every time; `nc -zv host 443` waits and times out. Right: something drops TCP 443 on the way or at the host (a firewall or security group); layer 3 is fine. Wrong: the host is down; DNS is wrong; the route is missing. |
| `mcq-exit-28` | mcq | `split-the-suspects` | `curl` exits 28 after exactly its `--connect-timeout`. What does that rule out? Right: a refusal (that comes back at once, exit 7) and a naming failure (exit 6). Wrong: a firewall drop; nobody at the address; a slow server. (The right answer is "what it rules out"; the three wrong answers are things 28 is consistent with, so the writer frames them as "it rules out X".) |
| `mcq-another-port` | mcq | `split-the-suspects` | From one laptop, some connections to the same server work and some hang; the laptop's address and the server's never change. Which variable is left to explain it? Right: the source port, which picks a path when traffic is shared between paths (or a server behind a balancer). Wrong: the TTL; the MTU; the server's CPU. |
| `mtr-which-link` | mcq | `locate-on-the-path` | A captured mtr report (writer captures one **with numbers of its own**, not the debug's: 7 hops, 0% to hop 3, 25% at hop 4 only, 0% at hop 5, 6% from hop 6 to the end). Right: real loss starts on the link between hops 5 and 6; hop 4 rate-limits its answers. Wrong: hop 4 is losing packets; the destination is overloaded; there's no real loss because 6% is small. |
| `mcq-return-path` | mcq | `locate-on-the-path` | mtr from the office to the cloud shows 0% everywhere, yet transfers from the cloud to the office are slow and lossy. Why can the report look clean? Right: it measures the reply path only as far as each probe's answer travels; ask for an mtr from the cloud end. Wrong: mtr ignores TCP; the cloud blocks ICMP; loss below 10% doesn't show. |
| `mcq-two-captures` | mcq | `locate-on-the-path` | On r2, `tcpdump -i eth0 port 80` shows the office's SYNs; `tcpdump -i tun2 port 80` at the same moment shows none of them. Right: r2 itself drops them (its firewall or its routing). Wrong: the far end drops them; the tunnel loses them; the office never sent them. |
| `ports-and-paths` | predict_shell | `locate-on-the-path` | Files: `attempts.txt`, twenty lines `PORT RESULT` from twenty connections through a router with two equal paths and a filter on the second (captured by the writer from 7.1's network with a second link and filter added, so **not** the checkpoint's numbers), and `tun1.txt`, the source ports a capture on the first path saw leave. Command: `awk 'NR == FNR {left[$1] = 1; next} {print $2, ($1 in left ? "left-on-tun1" : "not-on-tun1")}' tun1.txt attempts.txt \| sort \| uniq -c`. Output pinned by running it: every `ok` left on tun1 and every `fail` didn't. The explanation: connections are spread per port, so one bad path fails only the connections sent its way; the failures all went the other way, which is where to look; and only a capture shows which way each went (fact 15). |
| `monitor-by-address` | predict_shell | `measure-intermittent` | File: 20 lines of the checkpoint v1 prototype's captured monitor log (CAPTURES.md §1, with the address column as the fixed monitor writes it). Command: `awk '{print $3, ($NF == "exit=0" ? "ok" : "fail")}' log \| sort \| uniq -c`. Output pinned by running it. The explanation: every failure shares one address. |
| `est-one-dead-of-three` | estimate | `measure-intermittent` | "A name has 3 addresses, handed out in turn; 1 server is dead and clients try only the first address. Of 600 requests, how many fail? Exactly." `given {addresses: 3, dead: 1, requests: 600}`, `working: requests * dead / addresses` = 200. Mistakes: 300 (`requests / 2`: "assumed it's a coin toss"), 400 (`requests * (addresses - dead) / addresses`: "counted the ones that work"). |
| `est-two-faults` | estimate | `measure-intermittent` | "Two independent faults: one fails 1 request in 4, the other 1 in 10. What percentage of requests fail? Within 1." `given {a: 4, b: 10}`, `working: 100 * (1 - (1 - 1 / a) * (1 - 1 / b))` = 32.5, `tolerance: {absolute: 1}`, unit `%`. Mistakes: 35 (`100 * (1 / a + 1 / b)`: "added them, counting twice the requests both faults hit"), 2.5 (`100 / (a * b)`: "that's the share both faults hit at once"). |
| `est-page-of-four` | estimate | `measure-intermittent` | "Traffic is shared per connection between 2 paths, and 1 drops web traffic. A page needs 4 separate connections. What percentage of page loads hit at least one dropped connection? Within 1." `working: 100 * (1 - (1 - dead / paths) ** connections)` with `given {paths: 2, dead: 1, connections: 4}` = 93.75. Mistakes: 50 ("that's one connection, not a page"), 6.25 (`100 * (dead / paths) ** connections`: "that's all four failing"). |
| `est-clean-run` | estimate | `measure-intermittent` | "A fault failed 1 request in 10. After your fix, 30 requests in a row succeed. If the fault were still there, what is the chance (in %) of 30 clean requests in a row? Within 0.5." `working: 100 * (1 - 1 / rate) ** run` with `given {rate: 10, run: 30}` = 4.24. Mistakes: 90 (`100 * (1 - 1 / rate)`: "that's one clean request"), 0 (`100 * (1 / rate) ** run`: "that's 30 failures in a row"). |
| `mcq-errno` | mcq | `read-logs-and-counters` | nginx's error log: `connect() failed (111: Connection refused) while connecting to upstream ... upstream: "http://127.0.0.1:9001/"`. Right: nothing listens on 9001 on that machine (the application is down or on another port). Wrong: a firewall drops the connection (that's 110, timed out); no route to the upstream (113); the client gave up. |
| `mcq-transfer-denied` | mcq | `read-logs-and-counters` | Captured (CAPTURES.md §1): ns1's `zone transfer 'shop.test/AXFR/IN' denied` for 10.30.0.200 and ns2's `Transfer status: REFUSED`. Right: ns1 doesn't allow ns2's address to copy the zone, so ns2 serves its old copy. Wrong: ns2 is down; the zone's serial is too low; the network drops TCP 53. (This is topic 30's debug fault, used here as a recorded case: retrieval, not a spoiler; it's no longer a checkpoint fault.) |
| `nft-counter-rose` | predict_shell | `read-logs-and-counters` | Two files, `before.txt` and `after.txt`, each `nft list chain` output with four rules and their `counter packets N`; command: `paste` of the counter columns and an `awk` printing the rule whose count rose. Output: the drop rule's line. Constructed (labelled), in nft's real format. |
| `mcq-healthy-but-failing` | mcq | `read-logs-and-counters` | HAProxy shows all three servers UP; one request in three returns 502. Where do you look next? Right: the log line of a failing request, which names the server, and that server's own error log. Wrong: the health check's interval; the balancer's CPU; the network between client and balancer. |
| `mcq-two-changes` | mcq | `prove-and-record` | You suspect the firewall and the route; you change both, and the symptom goes. What have you lost? Right: knowing which was the cause (and whether the other change was needed or harmful). Wrong: nothing, it works; the change log; the ability to roll back. |
| `mcq-provider-ticket` | mcq | `prove-and-record` | Loss starts on the provider's link. What belongs in the ticket? Right: the time window, source and destination, mtr reports from both ends, and the first lossy hop with the one before it. Wrong: a screenshot of the error page; the server's CPU graph; "the internet is slow since Tuesday". |
| `mcq-name-first` | mcq | `prove-and-record` | Why write the cause and its evidence down before changing anything? Right: if you can't, you're guessing, and a guess that happens to work hides the real cause. Wrong: auditors require it; it speeds up the fix; tickets need a cause field. |

That is 23 recall items: 16 multiple choice, 3 `predict_shell`, 4 estimate. The writer checks the topic-level length rule for the 16 multiple-choice items (the right answer the longest in at most half of them), and can move up to five of them to review-only to bring the topic's time down (section 11).

### 7.3 `fill-triage-casebook` (fill-in, plain lab, 30 minutes, timed)

**What it trains:** the recognition step of the method at speed, across the whole module: which evidence points at which layer and cause, read from real output against a stated clock (the spec's "Standards, not just correctness").

**The lab:** `/srv/cases/case-1/` to `case-6/`, each a `ticket.txt` (the symptom in a user's words, the machines involved) and evidence files (`monitor.log`, `mtr.txt`, `capture.txt` as `tcpdump -nn -r` printed it, `dig-*.txt`, `journal-*.txt`, `routes-*.txt`, `nft-*.txt`, `conntrack-S.txt`), the same file names in every folder where possible so the list gives nothing away. `~/triage.txt` holds one block per case with gaps:

```
[case-3]
layer = ...        # link, network, transport, application, naming, security
where = ...        # the machine where the cause is, as the ticket names it
cause = ...        # from /srv/cases/causes.txt
evidence = ...     # FILE:LINE, the one line that shows it
```

Cases 1 and 2 are filled in as examples. **The six cases** (each from a different topic's failure, captured from that topic's lab when it's built; until then, the three marked "captured" exist today):

| Case | Ticket (substance) | Cause (truth) | Evidence | Source of the fixture |
| --- | --- | --- | --- | --- |
| 1 (example) | "The shop fails for half a minute now and then" | `stale-secondary` | ns1's `zone transfer ... denied` | captured, checkpoint v1 prototype |
| 2 (example) | "Some pages take two and a half seconds" | `stale-more-specific-route` | `S>* 10.30.0.0/25` | captured, checkpoint v1 prototype |
| 3 | "The price list download never finishes; pages load" | `pmtu-black-hole` | a capture with repeated full-size segments and the server's firewall counter on ICMP | topic 23's debug lab (layers designer captured it, `prototypes/layers-cidr-ipv6/d23/`) |
| 4 | "At lunchtime new connections to the payment API time out; existing ones are fine" | `nat-ports-exhausted` | `conntrack -S` with `insert_failed` rising, the SNAT rule's 10-port range | topic 27's NAT prototype (its finding 11) |
| 5 | "The VPN to the cloud is down since the provider's change" | `ike-proposal-mismatch` | charon's `NO_PROPOSAL_CHOSEN` | topic 35's IPsec prototype (eight failure modes captured) |
| 6 | "Customers get 'No server is available' for a few seconds every minute" | `deep-health-check` | HAProxy's `Server web/... is DOWN, reason: Layer7 wrong status` for all three at once, every minute | topic 33's LB prototype |

`causes.txt` lists 14 causes (the six truths plus eight plausible neighbours: `dns-cache-ttl`, `asymmetric-return-path`, `idle-timeout-cut`, `certificate-chain-incomplete`, `bgp-policy-missing`, `mtu-mismatch-on-link`, `server-down`, `firewall-port-closed`).

**Checks** (one per case and field, so a failure points at one case): `case-N-cause`, `case-N-where`, `case-N-evidence` (the named line exists and contains the case's key token, a list the check holds), `evidence-untouched` (checksum of `/srv/cases`). **Wrong fixes:** `all-firewall.sh` (every cause `firewall-port-closed`), `layer-only.sh` (layers right, causes wrong), `evidence-wrong-file.sh`, `copied-examples.sh` (cases 3 to 6 copied from 1 and 2), `edited-evidence.sh`. **Time:** "a triage desk does six of these in 30 minutes; time yourself" (stated, not enforced, Module 2 decision 8).

**Skills:** `split-the-suspects`, `locate-on-the-path`, `read-logs-and-counters`.

### 7.4 `write-probe` (write, network lab, 30 minutes)

**The tool:** `~/bin/probe URL [COUNT]` makes COUNT requests (default 20), each with `curl -s -o /dev/null --max-time 2`, and prints one line per attempt, `N RESULT SECONDS`, where RESULT is `ok` (exit 0 and a status under 400), `http-NNN` (a status of 400 or more), `no-address` (exit 6), `no-connection` (exit 7), `timeout` (exit 28) or `other-E`; then a summary line per RESULT, `RESULT COUNT/TOTAL`, largest first, and a last line `failure-rate PCT` (a whole number, rounded half up). From a blank file, created as `nano ~/bin/probe` and `chmod +x ~/bin/probe`, both given in full.

**The network:** the base with an office machine and a `targets` machine (scenery) that holds addresses the scenery's firewall drops (10.99.0.0/24 is routed to it and dropped), a closed port, and a small web server. **Checks make their own inputs** (README rule, house rule 2): each check starts a throwaway HTTP server of its own on `targets` at a random high port that answers 503 to every k-th request (k chosen at check time from 2 to 6) and 200 otherwise, runs `probe` with a COUNT chosen at check time (12 to 30), and compares the summary with the exact counts it works out; a second check probes a random nonexistent name under `shop.test` (all `no-address`), a closed port (all `no-connection`) and a dropped address with COUNT 3 (all `timeout`, about 6 s); a third checks the per-attempt lines' count and numbering. A hard-coded summary fails because k and COUNT change every run; a wrong classifier fails the second check. **Wrong fixes:** `status-ignored.sh` (503 counted ok), `exit-only.sh` (no http-NNN), `timeout-as-refused.sh`, `hardcoded.sh` (prints a fixed summary), `rate-truncated.sh` (rounds down: chosen counts make the rounding differ in at least one of two runs the check does). Timeouts: the dropped-address check `timeout: 30`, the others 30 by default.

**Skills:** `split-the-suspects` (curl's exit status as the layer), `measure-intermittent`.

### 7.5 Where the live practice is

The worked example (7.1) is live and guided; the casebook (7.3) is recorded and unguided; the probe (7.4) is live and builds the measuring instrument; the build (8.1) analyses the evidence a monitor leaves. That is every skill practised before the debug asks for it: `scope-it` (7.1, 7.2), `split-the-suspects` (7.1, 7.2, 7.3, 7.4), `locate-on-the-path` (7.1, 7.2, 7.3), `measure-intermittent` (7.1, 7.2, 7.4), `read-logs-and-counters` (7.2, 7.3), `prove-and-record` (7.1, 7.2).

## 8. Proofs

### 8.1 Build: `build-outage-report` (plain lab, 45 minutes)

**The prompt (substance).** The office's monitor writes one line per load, as in the worked example: `TIME PAGE ADDRESSES STATUS SECONDS exit=N` (ADDRESSES the addresses curl tried, comma-separated, `-` when none). Build `~/bin/outage-report LOG` that prints exactly:

```
loads N
failed F (P%)
slow S                    # succeeded, but took 1 second or more
by-address A1 ok=X fail=Y slow=Z     # one line per first address tried, sorted by address
longest-outage START LENGTH          # the longest run of consecutive failed loads: its first TIME and how many loads
verdict ADDRESS|time|none            # the first address that holds every failure and every slow load, else "time" if every failure is in the longest run, else "none"
```

Percentages rounded half up to a whole number. The learner may use any tools; the lesson's `awk` and `sort | uniq -c` are enough, and the prompt says so.

**Checks make their own inputs.** Each check writes a fresh log of its own (300 to 600 lines, seed taken from the time) in the monitor's format, from one of three shapes chosen at check time: one bad address (failures and slow loads all share it), one outage window (a run of 10 to 20 failures at a random place, with scattered slow loads on several addresses), or neither; it runs the learner's script on it and compares every line with its own answer. Three checks, one per shape, so a script that only handles one shape fails the others; a fourth runs it on the real monitor log of the image (a captured log from the checkpoint's v1 prototype) and compares with the answer computed by the check's reference awk.

**Wrong fixes:** `slow-counted-as-failed.sh`, `last-address-not-first.sh` (attributes a load to the address that answered, not the first tried), `longest-run-off-by-one.sh`, `verdict-always-address.sh`, `rounding-down.sh`, `hardcoded-sample.sh` (prints the sample log's answer).

**Skills (for `test_skills`-style mapping in reviews):** `measure-intermittent`, `scope-it`.

### 8.2 Debug: `debug-branch-api` (network lab, 50 minutes): mechanisms prototyped

**The network** (prototyped as `t36-mechanisms`, every mechanism below seen working on 2026-11-11, CAPTURES.md §2):

```
branch 10.40.0.0/24          provider (ISP)                          data centre 10.20.0.0/24
client .10 -- br1 -- isp1 -- isp2 -- dc1 -- lb .79 (own) .80 (service), api1 .11, api2 .12, api3 .13, db .50
                                                   lbold .81 (the old load balancer, still running)
```

`br1` (the branch router) and `dc1` (the data centre's router) are the shop's; `isp1` and `isp2` are the provider's, sealed (`netlab seal`) and the prompt says they aren't the learner's. `lb` runs HAProxy (round robin over api1 to api3, health check `GET /health` every 2 s, backend connections from its own address .79); the APIs are nginx proxying `/api/` to the data service on `db:5000` (scenery, a small Python server); `api3` came from a new image with an outbound firewall.

**The three faults** (each in a file a boot reads, so each survives a restart until fixed):

1. **Provider loss, with a red herring.** `netem isp2 eth2 loss 8%` (the provider's last link toward the data centre) and `net.ipv4.icmp_ratelimit=2000` on isp1; every other router at 0. Symptom: API calls from the branch are slow now and then (TCP retransmits). Evidence: mtr shows 37.5% at isp1 only and 10% from dc1 to the end (fact 12). **Not fixable by the learner.** Deliverable: `~/ticket/provider.txt` with `last_clean_hop=` and `first_lossy_hop=`.
2. **A duplicate service address.** `old-lb.service` on lbold (a unit on the lab machine that runs in lbold's namespace, enabled) claims 10.20.0.80 and announces it every 20 s, and answers with a 503 maintenance page; the real lb announces every 30 s (scenery, as failover software does). Symptom: windows of 503s from the branch that HAProxy's log never shows (fact 13). Evidence: `arping` from dc1 gets two MACs; `tcpdump -e` shows two replies to one request; `ip neigh` on dc1 changes. Fix: stop and disable `old-lb` (and nothing else on lbold).
3. **A backend that can't reach its database.** api3's `nftables.conf` output chain is `policy drop` with DNS, 80 and 443 allowed, and not the data service's port 5000. Symptom: one API call in three (while the real lb holds the address) returns 504 after 2 s. Evidence: HAProxy's log names api3 with 504; api3's nginx error log says `upstream timed out (110: Connection timed out) while connecting to upstream` for `10.20.0.50:5000`; the output chain's counter rises; all three servers stay UP (fact 14). Fix: allow TCP to 10.20.0.50 port 5000 in api3's file (not "accept all output").

They interact: while lbold holds the address, the branch never reaches HAProxy, so fault 3 hides; while the real lb holds it, fault 3 fails a third of calls; fault 1 slows everything a little all the time and mtr's isp1 line tempts the learner to blame the wrong hop.

**Prompt (substance, house rule 5).** The shop's branch office calls the shop's API at `http://10.20.0.80/api/stock` (the load balancer, three API servers, the data service), over a provider's network between br1 and dc1. Since Tuesday the branch reports that the API is "slow, and sometimes fails: sometimes an error page, sometimes a maintenance page". **There are three faults.** Find each one, and before you change anything for a fault, write its cause and the line of evidence into `~/ticket/notes.txt` (the format is in the prompt: `fault-1 cause = ...`, `evidence = ...`). Fix the faults on the shop's machines at their causes. isp1 and isp2 are the provider's: change nothing on them; if a fault is on the provider's side, write in `~/ticket/provider.txt` the address of the last hop before the trouble starts and the first hop where it shows. The rules of the fix: every machine keeps its firewall; fixes last a reboot; the load balancer and the three API servers stay in service with their health checks. **Time yourself: 50 minutes.**

`notes.txt` is checked for the two fixable faults' causes from a published list (as in Checkpoint 2's part 2), not for the order of writing: the prompt asks for it first, and the method is taught that way, but nothing can tell when a file was written, so no check pretends to (open question 3).

**Checks** (descriptions are end states; the page lists them only after a first try, #235):

| id | End state | How | Skill |
| --- | --- | --- | --- |
| `calls-succeed` | 30 calls from the branch, every one 200 with the data service's body, each within 5 s (`timeout: 60`) | `on client curl` in a loop | `measure-intermittent` |
| `one-owner` | Only one machine answers ARP for 10.20.0.80, and it is lb | `on dc1 arping -c 3 -I eth1 10.20.0.80`: every reply from lb's MAC | `locate-on-the-path` |
| `old-lb-gone-for-good` | old-lb is stopped and disabled, lbold keeps its own address 10.20.0.81 | `systemctl is-active`, `is-enabled`, `on lbold ip -br addr` | `prove-and-record` |
| `api3-reaches-db` | api3's API calls succeed directly (`on api3 curl http://127.0.0.1/api/stock` 200) | | `read-logs-and-counters` |
| `api3-still-guarded` | api3's output policy is drop and it still can't open a connection to a port it has no use for (the check starts a listener of its own on db:2525 and api3 gets nothing from it) | timing, as Module 1's firewall checks | `prove-and-record` |
| `api3-saved` | api3's file loads the rules it runs (scratch-namespace comparison); `nftables@api3` enabled | | `prove-and-record` |
| `balancer-intact` | HAProxy runs the configuration it was given (checksum) with api1 to api3 all UP | `show stat` | `prove-and-record` |
| `provider-untouched` | isp1 and isp2 and the topology as they were | `netlab intact` | `prove-and-record` |
| `ticket-right` | `provider.txt` names 192.0.2.2 as the last clean hop and 198.51.100.2 as the first lossy one (computed by the check from the topology's `netem` line and the path) | | `locate-on-the-path` |
| `notes-right` | `notes.txt` gives the two fixable faults' causes from the list (`duplicate-address`, `egress-filter-blocks-dependency`) | | `scope-it`, `split-the-suspects` |

**Wrong fixes:** `old-lb-stopped-not-disabled.sh` (back at boot: `old-lb-gone-for-good`), `vip-deleted-by-hand.sh` (`ip addr del` on lbold; the service re-adds it: `one-owner` after its next announcement, so the check waits 25 s, `timeout: 40`), `api3-output-accept.sh` (`api3-still-guarded`), `api3-runtime-only.sh` (`api3-saved`), `netem-removed.sh` (`provider-untouched`), `ticket-blames-isp1.sh` (`ticket-right`), `ticket-first-hop-only.sh` (names dc1 as both: `ticket-right`), `health-check-deepened.sh` (the learner points the health check at `/api/stock`, which takes api3 out instead of fixing it: `balancer-intact`), `two-of-three-a.sh`, `two-of-three-b.sh`. Ten, each failing a check of its own.

**Not yet proved:** the whole lab under `labcheck test` (the prototype proved each mechanism and captured its evidence; its checks and wrong fixes are designed, not run). The ARP flip's timing depends on the two announcement periods; the deterministic checks (`one-owner`, `old-lb-gone-for-good`) don't depend on it, only the symptom does. `calls-succeed` with 8% loss: 30 calls each within 5 s passed in the prototype's runs (each call took under 1 s even with retransmits), but must be watched on CI.

### 8.3 Explain (20 minutes)

**Prompt.** "A colleague says: 'When the network acts up, I restart the router, and if that doesn't work I open the firewall for a minute to see if it helps.' The network now has an intermittent problem: about one request in five fails, at no particular time. In your own words: what's wrong with your colleague's approach; how you would scope the problem and what you'd measure first; which tests would split the possible causes and what each result would rule out; how you would find where on the path the trouble is, including what can make a hop in `mtr` look lossy when it isn't; which records you'd read; how many clean results you'd want before believing a fix, and why; what you would do if the cause turned out to be in your provider's network; and one way finding a fault in a cloud differs from finding it on your own routers."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `anti-methods` | yes | Restarting and opening the firewall are guesses (random change); they can hide the cause, add a security hole, and teach nothing; a restart also destroys evidence (caches, counters, logs in memory). |
| `scope` | yes | From where, to what, by name or address, which family and size, always or sometimes and how often, since when, what changed; and for an intermittent fault, sample it over time before guessing. |
| `split` | yes | Tests that halve the suspects, with what each rules out: by address against by name (naming), ping against TCP against HTTP (layer), small against large (MTU), another source or path (the path); curl's exit status as a quick verdict. |
| `locate` | yes | mtr or traceroute; loss that carries on to the end is real and starts on the link before the first lossy hop; loss at one hop only is rate limiting; the return path is invisible, so test from both ends; captures at two points. |
| `intermittent` | yes | Break the failures down by a variable (address, path or source port, server, size, time) until one value holds them all; one in five suggests one bad member of five or two faults together. |
| `prove` | yes | Name the cause and evidence first; change one thing; enough clean samples (a one-in-five fault survives ten clean tries about 11% of the time, so ten isn't enough; say why); check nothing else broke. |
| `provider` | yes | Prove it and hand it over: time window, addresses, mtr from both ends, the first lossy hop and the one before it, what's been ruled out. |
| `clouds` | no | In a cloud you can't log in to the router: Reachability Analyzer or Network Watcher or Connectivity Tests analyse configuration; flow logs and traffic or packet mirroring stand in for captures. |

**Model answer:** the writer drafts it from the rubric, in the learner's voice, about 300 words, as Module 2's explains are.

## 9. Review pool

At least two come-back items for every skill, mostly judgement on real output and calculation; ● marks items already in practice, ○ items that appear only in review.

| Skill | Items |
| --- | --- |
| `scope-it` | ● `mcq-symptom-grid`, ● `mcq-what-changed`, ○ `mcq-symptom-grid-v6` (a grid where only IPv6 fails from one network: the fault is that network's IPv6 path, not the server) |
| `split-the-suspects` | ● `mcq-name-or-address`, ● `mcq-another-port`, ○ `mcq-exit-7-fast` (exit 7 in a millisecond: something answered with a refusal, so the host is up and reachable) |
| `locate-on-the-path` | ● `mtr-which-link`, ● `ports-and-paths`, ○ `mtr-rate-limited-only` (a report whose only loss is at one middle hop: no real loss) |
| `measure-intermittent` | ● `est-two-faults`, ● `est-clean-run`, ○ `est-one-bad-of-five` (5 backends round robin, one returns 502: of 250 calls, 50 fail; mistakes 125 and 200), ○ `est-clean-run-twenty` (1 in 5, 20 clean in a row: 1.15%; mistakes 80 and 0) |
| `read-logs-and-counters` | ● `mcq-errno`, ● `nft-counter-rose`, ○ `mcq-haproxy-termination` (a log line with `sD--` and `504` after 5 s: the server took too long; distractors from the other termination states) |
| `prove-and-record` | ● `mcq-two-changes`, ● `mcq-provider-ticket` |

Eighteen review items, six of which produce their answer (two `predict_shell`, four estimate), which meets the review-pool rule; `measure-intermittent` has six estimate items in all (four in practice, two review-only).

## 10. Platform work needed first

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| T1 | The network-lab base and labcheck's shared bases | as the base brief specifies (its N1 to N3); nothing extra for this topic | 7.1, 7.4, 8.2 |
| T2 | Answer to the base's open question 5 ("where does a learner's lasting kernel setting live?") | **None needed for this topic**: every fix here lives in a file a service reads (FRR, nftables, a systemd unit's enablement), so `netlab` needs no new word | none |
| T3 | Machine-level units that aren't one of the base's services | the debug's `old-lb.service`, `lb-garp.service` and `db-api.service` are ordinary units on the lab machine that run `ip netns exec M lab-enter M PROGRAM`, exactly like the base's per-machine units; no base change, but the base README should show the pattern once | 8.2 |
| T4 | A check may hold a listener or a server of its own on a lab machine for its duration | already allowed (README: "it may start a throwaway process of its own"); used by 7.4 and 8.2 | none |

No new item types: recall items are `mcq`, `predict_shell` and `estimate` (ADR-0024).

**What the labs need from the kernel, and where it was seen working** (house rule 4):

| Need | Used by | Docker Desktop 29.8.2, WSL 2 kernel (2026-11-11) | GitHub's runners |
| --- | --- | --- | --- |
| `sch_netem` loss on one interface | 8.2 (provider loss) | works (fact 12); the base brief confirms netem loads on demand and delays egress only, which is why the loss sits on isp2's interface toward the data centre | **not tried**: the base brief's CI spike (its N3) must include one netem lab; if netem is missing there, the debug's fault 1 can't run in CI and the contract would need a stand-in (open question 6) |
| `net.ipv4.icmp_ratelimit` per namespace | 8.2 (the red herring) | works: set by a `sysctl` line in the topology, seen in mtr | per-namespace sysctl; expected to work, not tried |
| Gratuitous ARP (`arping -U`) updating a router's neighbour entry | 8.2 (fault 2) | works (fact 13) | expected (no module), not tried |
| nftables `output` chain, counters, `ct state` | 8.2 (fault 3), 7.4 | works | works in CI today (Module 1's firewall labs) |
| `fib_multipath_hash_policy` per namespace, captures on each tunnel | 7.2's `ports-and-paths` fixture | works (checkpoint prototype); `ip route get` with ports does not predict the path (fact 15) | expected, not tried |
| A dropped address range for `timeout` results | 7.4 | nftables drop rule in scenery | works in CI today |

## 11. Cost and time

**Money:** none. Everything is local. The cloud tools of section 4.9 are taught from their documentation; none is used (Reachability Analyzer and Traffic Mirroring charge, fact 16 and 19).

**Learner time (`estimated_minutes`):** lesson 15; reading 60 (R1 38, R2 5, R3 15, R4 2); 23 recall items 35; worked example 35; casebook 30; probe 30; build 45; debug 50; explain 20: **320**. That is over Module 2's 300 split line. Two ways down, in order of preference: (a) assign only R1's "Theory", "In Practice" and case study (about 28 minutes instead of 38) and move five multiple-choice items to review-only (`mcq-first-questions`, `mcq-return-path`, `mcq-exit-28`, `mcq-healthy-but-failing`, `mcq-name-first`), leaving 18 recall items in practice (27 minutes): **about 302, written as 300**; (b) split the topic (open question 2). Recommendation: (a).

**CI time** (measured: 23 s per container run for a ten-machine network lab under `labcheck test` on the owner's PC; a plain lab about 3 s):

| Lab | Container runs | Estimate |
| --- | --- | --- |
| `example-follow-the-method` | 5 | 2 min |
| `fill-triage-casebook` | 7 | 0.5 min |
| `write-probe` | 7 (the dropped-address check takes 6 s) | 3 min |
| `build-outage-report` | 8 | 0.5 min |
| `debug-branch-api` | 12 (`vip-deleted-by-hand` waits 25 s) | 6 min |
| **Topic** | 39 | **about 12 minutes of runner time** |

Images: the network labs add a few kilobytes of scenery each to the base; the plain labs share one small layer (python3 is the only addition to a Module 2 plain lab's first `RUN`, about 30 MB).

## 12. Open questions, each with a recommendation under the owner's rule

1. **The topic designers' drafts were readable on the day.** I used them to keep this topic's (and the checkpoint's) faults off theirs. *Recommendation:* the critic re-checks section 7's and 8.2's faults against the final topic briefs; if one has become a topic's debug fault, swap it for another from this list, each prototyped here or in a draft: an outbound filter on one of two ECMP tunnels (checkpoint v2, prototyped), a resolver's stale forwarder for one domain, a port the edge forwards for one service and not another.
2. **320 minutes.** *Recommendation:* trim as in section 11 (a), not split: the method is one idea, and splitting it would put the scoping and the proving in different topics, which is the opposite of what retention needs (whole-task practice, 4C/ID).
3. **"Name it before you fix it" can't be enforced.** A check can't tell when a file was written relative to a fix (the learner has `sudo`). *Recommendation:* ask for it in the prompt, check the content (the causes), and grade the habit in the explain (rubric `prove`). Don't build a "commit your diagnosis" command: it would be a ritual, not evidence, and it adds platform work.
4. **No video.** None of the free videos on troubleshooting method was opened on the day. *Recommendation:* keep R1 as the main resource (reading, CC BY-NC-ND 4.0); a writer who finds and watches a good free talk adds it as R0 only after checking its licence and length.
5. **The provider ticket asks for two addresses, not a loss figure.** A measured loss percentage would vary run to run (8% configured, 10.0% measured in 40 probes). *Recommendation:* keep it to the two hops, which are deterministic; the explain asks what else goes in a ticket.
6. **`calls-succeed` and 8% loss on CI.** *Recommendation:* run the debug's contract three times on CI in the network labs' first pull request (the base's CI spike, its N3); if `calls-succeed` ever fails for the solution, lower the loss to 5% (mtr still shows it clearly in 40 probes) rather than loosen the check.

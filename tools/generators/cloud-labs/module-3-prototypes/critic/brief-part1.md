# Module 3 brief: Networking

The final plan for Module 3 of the Cloud Solutions Architect track, merged from the seven designers' briefs in this folder by the critic on 2026-11-11. Nothing here is in the repository yet.

**How to use it.** This file decides; the designers' briefs hold the detail. Where they disagree, this file wins. Each topic section names the designer's file and lists only what changes; everything it doesn't mention stands as the designer wrote it. [CRITIQUE.md](CRITIQUE.md) lists every problem found and what was done about it. [network-lab-base.md](network-lab-base.md) is the base's design; section 4 below is its final form and wins where they differ.

The owner's rule for open questions (2026-11-11) decided every judgement call here: the best learning experience first, then memory retention, then free or inside the $150 Azure credit. Each such call is listed in section 10, for the owner queue's _Decided for you_. Nothing in Module 3 costs money: every lab, proof and review runs locally.

## 1. The plan in one screen

- **Sixteen topics, not fourteen.** Topic 34 (BGP, about 365 minutes as one topic with six skills) splits into `csa.net.bgp` and `csa.net.bgp-steering` along its designer's seam, and topic 31 (HTTP and TLS, 332 minutes) splits into `csa.net.http-tls` (the protocol on the wire and how a server is set up for it) and `csa.net.certificates` (chains, ACME rotation and mutual TLS). Shorter topics reach their proofs and first reviews sooner, and the TLS handshake gets proofs of its own (in the one-topic design neither proof tested it). The spec changes (section 12).
- **One way to build a network.** Every network lab starts `FROM lab-base-net`: each machine is a network namespace with its own `/etc`, built at boot by `netlab` from a topology file, with each daemon a systemd unit per machine (`frr@r1`, `nginx@web`). Six designers prototyped their own variants (the container's main namespace as a router, gateway or server; `router`, `on-dc`, `cloud-enter`, `ns@`); all move to the base. The lab machine is on no lab network. The base gains a per-machine sysctl folder, a per-machine network file, `radvd`, a fresh-build check and the helpers the designers needed (section 4).
- **The route-based VPN is a VTI after all.** The base designer found strongSwan with VTI dropping every packet; the IPsec designer had it working. The critic reproduced both and found the cause: the base's `libstrongswan-extra-plugins` loads strongSwan's `forecast` plugin, which breaks VTI. Without it, BGP over a VTI-based IPsec tunnel works between two base machines (`prototypes/critic/vti/RESULT.md`). GRE inside IPsec stays as the documented fallback.
- **Everything is proven locally, at no cost.** FRR for routing and BGP, strongSwan for IPsec, BIND and Unbound for DNS, nginx, HAProxy, Caddy and step-ca for the web topics, nftables for NAT and firewalls, netem for distance and loss, captures for the truth on the wire. The clouds' behaviour is taught from their dated documentation and, where it decides a lab, modelled in a router's configuration and labelled "modelled on".
- **No new item types, no new app work.** Estimate items (ADR-0024), `predict_shell`, the per-check `timeout:` and `prove.more` exist, and the map already lists a checkpoint's further parts. The platform work is the base, a 29-line `labcheck` change, an opt-in restart trial in the contract, a CI spike and a ten-line validator fix (section 7).
- **Checkpoint 3 has three parts:** the address plan (plain lab), the intermittent outage (three faults no topic's debug uses), and a new part 3, the cloud link (a circuit and a backup IPsec VPN with BGP), in `prove.more`.
- **Time:** 4,640 minutes of topics and 240 of checkpoint, about 81 hours. Labs CI grows by about 7.5 hours of container time a full run: raise the Labs shards from 4 to 8.

## 2. Topic order and real prerequisites

Every Module 3 topic depends on `csa.m1.checkpoint`, directly or through another Module 3 topic (the spec's map runs Module 1 to Module 3; Module 2 is **not** a prerequisite). Two briefs got this wrong: the transport brief asked for a `csa.m2.checkpoint` gate, and the IPv6 brief and the base brief leaned on `csa.hw.windows-ad` for the words DNS, resolver, zone and record. A Module 3 learner may never have met dc1, so those words are defined where section 3.7 says.

| # | Id | Title | `prerequisites:` | Skills | Minutes |
| --- | --- | --- | --- | --- | --- |
| 23 | `csa.net.layers` | Layers and packets | `csa.m1.checkpoint` | `layer-model`, `read-headers`, `arp-neighbours`, `icmp-messages`, `encapsulation-mtu`, `pmtud-blackholes` | 310 |
| 24 | `csa.net.cidr` | IPv4 and CIDR | `csa.net.layers` | `binary-and-masks`, `block-math`, `split-and-summarise`, `overlaps`, `private-and-reserved` | 295 |
| 25 | `csa.net.ipv6` | IPv6 | `csa.net.cidr` | `v6-notation`, `v6-address-types`, `v6-plan`, `slaac-dual-stack`, `v6-egress` | 300 |
| 26 | `csa.net.routing` | Routing | `csa.net.cidr` | `longest-prefix-match`, `static-routes`, `static-or-dynamic`, `return-path`, `find-the-black-hole` | 300 |
| 27 | `csa.net.nat` | NAT | `csa.net.routing`, `csa.net.ipv6` | `snat-and-dnat`, `nat-rules`, `nat-sizing`, `port-exhaustion`, `avoid-nat` | 290 |
| 28 | `csa.net.transport` | TCP and UDP | `csa.net.nat` | `read-a-capture`, `window-math`, `tcp-timers`, `idle-cuts`, `udp-behaviour` | 300 |
| 29 | `csa.net.congestion` | Congestion control and QUIC | `csa.net.transport` | `loss-based-cc`, `bbr-model`, `loss-latency-math`, `quic-changes`, `http3-in-practice` | 300 |
| 30 | `csa.net.dns` | DNS | `csa.net.transport` | `trace-resolution`, `records-and-zones`, `ttl-and-caching`, `split-horizon`, `dnssec` | 315 |
| 31 | `csa.net.http-tls` | HTTP and TLS | `csa.net.dns`, `csa.net.congestion` | `http-versions`, `tls-handshake`, `tls-server-config` | 175 |
| 32 | `csa.net.certificates` | Certificates and mutual TLS | `csa.net.http-tls` | `cert-chains`, `acme-and-rotation`, `mutual-tls` | 230 |
| 33 | `csa.net.http-semantics` | HTTP semantics | `csa.net.http-tls` | `caching`, `cors`, `methods-and-status`, `api-styles` | 315 |
| 34 | `csa.net.load-balancing` | Load balancing | `csa.net.http-semantics` | `choose-the-balancer`, `health-checks`, `failover-math`, `drain-and-stick`, `read-the-balancer` | 315 |
| 35 | `csa.net.bgp` | BGP sessions and policy | `csa.net.routing` | `bgp-sessions`, `announce-and-filter`, `best-path`, `local-preference` | 285 |
| 36 | `csa.net.bgp-steering` | Steering traffic and cloud circuits | `csa.net.bgp` | `inbound-steering`, `route-reflection`, `failure-detection`, `cloud-circuits` | 295 |
| 37 | `csa.net.ipsec` | VPNs and IPsec | `csa.net.bgp`, `csa.net.http-tls` | `ipsec-building-blocks`, `route-based-tunnel`, `bgp-over-tunnel`, `read-ike-logs`, `tunnel-mtu` | 310 |
| 38 | `csa.net.troubleshooting` | Network troubleshooting | `csa.net.load-balancing`, `csa.net.ipsec` | `scope-it`, `split-the-suspects`, `locate-on-the-path`, `measure-intermittent`, `read-logs-and-counters`, `prove-and-record` | 300 |
| | `csa.m3.checkpoint` | Checkpoint 3: the address plan, the outage and the cloud link | all sixteen | (draws on all) | 240 |

Changes from the designers' lists: load balancing drops `csa.net.nat` (reached through HTTP semantics, HTTP and TLS, DNS and transport); IPsec drops `csa.net.layers` and `csa.net.nat` (reached through BGP and through HTTP and TLS) and keeps `csa.net.http-tls` for the cryptography words its lesson builds on. Routing and BGP can be taken straight after CIDR; DNS straight after transport. The numbering is the suggested path.

Topics over 300 minutes (layers, DNS, HTTP semantics, load balancing, IPsec) were each trimmed by their designers as far as is sensible and stay single topics, because each one's debug is a whole task across its skills. Layers carries the module's lab onboarding (10 minutes); the others overrun by 10 to 15 minutes of reading.

## 3. Rules every Module 3 item follows

Module 2's rules (its brief, section 3) stand. These add to them or correct the briefs.

### 3.1 Multiple choice

- The validator's lines: right answer at most 1.5 times the longest wrong one; right answer the longest in no more than half of a topic's items (four or more items). Aim for 1.3 and a third.
- Only the transport and congestion designers **measured** their choices (right longest in 3 of 14 and 3 of 13; largest ratio 1.04 and 1.03): they are the model. Every other brief gives the right answer and suggests the distractors; the writer writes every choice out in full, in one shape, and measures before anything else. The briefs flag three items whose choices are lists ("AWS …; Azure …; Google …": routing's `mcq-cloud-forwarding-flag`, NAT's `mcq-cloud-exhaustion-metric`, load balancing's `mcq-fail-open`); write each as four lists of the same shape or turn it into an item per cloud.
- IPsec has 18 multiple-choice items and the troubleshooting topic 16: the most exposed to the "longest in half" rule. Both designers named items that may move to review-only; move them if the count needs it.

### 3.2 Debug prompts

Purpose, symptoms, the number of faults, the rules of the fix; never what or where. The prompts in the briefs meet this, with two corrections: topic 23's "each machine's settings are in its files (the base's location)" becomes "each machine keeps its settings in its own `/etc`" (no file named), and topic 25's "r1's sysctl file" never appears in a prompt (the brief names it only in the faults). Check descriptions are listed only after a first try (#235) and state end states. A debug whose faults uncover each other (routing, the domain-style "one after another" of certificates and IPsec) says "fixing one can change what you see" and nothing more.

### 3.3 Numbers

- Every calculation skill has at least three estimate items with different numbers and stories (all briefs meet this; counted in each topic's review table).
- **Dotted quads.** Until the validator reads `10.20.30.77` as four numbers (platform work P3), an estimate prompt restates the octet it gives ("its last number is 77").
- **No knife edges.** Checkpoint part 1's numbers clear the next size by at least 11%; CIDR's build makes the reserved addresses decide exactly one subnet on purpose. Throughput checks are thresholds in the middle of a measured gap (congestion: 25 Mbit/s between CUBIC's 1.4 to 7.4 and BBR's 41 to 46), never values.
- **Scaled time is said.** Idle timers (10 to 20 s for 350 s), TTLs (60 s and 5 s for hours), BGP timers (3 and 9 for 60 and 180), certificate lifetimes (24 hours) and the prefix limit (5 for 100) are scaled in labs; every prompt gives the real figure beside the lab's. Estimate items use the real figures.

### 3.4 Fixtures

Captured (real output, named machine and date) or constructed (a real format with made-up numbers), never mixed, as in Module 2. Every `predict_shell` output is pinned by running it in Git Bash **and** with CI's `awk` (Ubuntu's mawk unless the image installs gawk; no lab image adds gawk, and no item uses `strtonum`, `and()` or other gawk-only functions). Commands that print `\n` from `sed` are checked in both.

### 3.5 Labs

- **One base.** Section 4. Prompts give a machine's files by their path inside it (`on r1 nano /etc/frr/frr.conf`), never `/etc/netns/r1/...`. Services are `name@machine`: `sudo systemctl restart frr@r2`, `systemctl reload nginx@web`, `journalctl -u haproxy@lb`.
- **The restart trial is in the contract.** Every Module 3 lab sets `lab: { restart_trial: true }` (platform work P1): after the solution passes, `labcheck test` restarts the container and runs every check again.
- **Fixes last.** A check that a fix lasts reads the lasting place, never only the live state: FRR's running equals saved (`frr_saved`), nftables' file loaded in a scratch namespace equals the running rules (`nft_saved`), a sysctl's live value equals what the machine's `/etc/sysctl.d` sets (`sysctl_saved`), and for a machine's network file, `netlab verify` (section 4.3). A `wrong/*.sh` that makes the fix live only proves each.
- **No hand-made routes.** `ip -j route` leaves out `protocol` for a route typed with `ip route add` and shows `"protocol":"boot"` only with `-d` (the critic's probe, 2026-11-11). Checks use `ip -d -j route` and reject `boot` (the FRR brief's recipe R3, as written, would have passed a hand-made route).
- **One wait per check run.** One check waits for convergence (30 s for BGP, 15 s for IPsec, 60 s for DNS after boot); every later check reads at once. Seeded timers are fast (`timers bgp 3 9`, `timers connect 5`, OSPF hello 1 dead 4) and the lesson says what the defaults are.
- **No ties decided by time.** Every BGP lab makes the default winner deterministic (`bgp bestpath compare-routerid` and addresses chosen so the wrong path wins without the learner's change).
- **Never compare whole interface lists.** Loading tunnel modules adds placeholder devices (`gre0`, `ip_vti0` …) to every new namespace on the same Docker machine, which differs between the owner's PC and a runner and from day to day. Checks name the interface they read.
- **Seed files written by FRR.** Every FRR seed is generated with `write memory` at authoring time, or `frr_saved` fails a pristine router (checkpoint finding 5).
- **A resolver in front of servers that boot later** sets `infra-host-ttl: 60` (Unbound's default 900 s hid a fault for 15 minutes; checkpoint finding 3). Every resolver config also has `local-zone: "test." nodefault`.
- **Source ports a check chooses** come from above `ip_local_port_range` (61000 and up), moving with the clock, never reused in a run (TIME-WAIT, exit 45; checkpoint finding 6).
- **A path is proved by traffic.** `ip route get … ipproto tcp sport P dport Q` did not predict the ECMP path of forwarded connections on this kernel; checks capture on each outgoing interface (checkpoint finding 7).
- **Plain labs with Python.** Module 3's plain labs (CIDR's fill, write and build, IPv6's and routing's and NAT's and transport's writes, HTTP semantics' write, the certificate report, IPsec's log write, the troubleshooting casebook and build, checkpoint part 1) share one first `RUN`: Module 1's plain line plus `python3 ipcalc sipcalc openssl curl`. Python is the checks' tool, never the learner's. Throwaway servers in plain labs listen on 127.0.0.1 (no namespaces without privilege).

### 3.6 Clouds

Every cloud fact is dated and sourced in the designer's facts table; the lesson carries the three clouds side by side where they differ. A lab never pretends to be a provider: a modelled cloud router says "modelled on AWS Direct Connect's documented behaviour" and quotes it. No Module 3 lab touches a cloud account.

### 3.7 Terms: who defines what

Module 1 taught `ip`, `ss`, `dig` with A and CNAME and the TTL column, `curl`, `nc`, `traceroute`, `tcpdump`, nftables, conntrack, namespaces and veth pairs, and named NAT and the ARP table. It never used `sysctl` (searched: no `csa.*` file mentions it). Owners, so no topic assumes a word no earlier topic taught:

| Term | Defined in |
| --- | --- |
| machine, switch, topology file, scenery, `on`, `netlab show`, `name@machine` services, placeholder interfaces, a machine's `/etc/network/up` and `sudo netlab restart` | `csa.net.layers` (the first network lab's note and worked example) |
| layer, header, frame/packet/segment/datagram, hex, MAC, ARP states, TTL, ICMP types, MTU, MSS, DF, PMTUD, tunnel, GRE, VXLAN | `csa.net.layers` |
| `sysctl`, `/etc/sysctl.d/` (name order, later files win), `net.ipv4.ip_forward`, `rp_filter`, ECMP | `csa.net.routing` (it is the first topic that needs a kernel setting; transport, NAT and congestion build on it) |
| DNS record, AAAA record (one sentence each) | `csa.net.ipv6`; DNS's full vocabulary in `csa.net.dns` |
| egress-only gateway | `csa.net.ipv6` |
| load balancer, security group, connection pool (one sentence each) | `csa.net.transport` |
| QUIC, stream, head-of-line blocking, 0-RTT, Alt-Svc | `csa.net.congestion` |
| symmetric and public-key encryption, key exchange, forward secrecy, cipher suite, handshake | `csa.net.http-tls` (IPsec builds on them) |
| certificate, chain, SAN, CA, ACME | `csa.net.certificates` (`csa.net.http-tls` names "certificate" in one sentence) |
| cookie | `csa.net.http-semantics` (its labs send cookies; load balancing uses the word) |
| autonomous system, eBGP/iBGP, prefix list, route map, looking glass | `csa.net.bgp` |
| AS-path prepending, communities, route reflector, BFD | `csa.net.bgp-steering` |
| mtr's report columns, ICMP rate limiting, curl exit codes | `csa.net.troubleshooting` |


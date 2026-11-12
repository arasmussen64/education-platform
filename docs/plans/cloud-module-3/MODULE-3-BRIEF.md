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
- **Time:** 4,635 minutes of topics and 240 of checkpoint, about 81 hours. Labs CI grows by about 7.5 hours of container time a full run: raise the Labs shards from 4 to 8.

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

## 4. The network-lab base, final

The design is [network-lab-base.md](network-lab-base.md) and its prototype (`prototypes/network-lab-base/repo/content/lab-bases/net/`), which kept two contracts under the real `labcheck`. Everything there stands except what this section changes.

### 4.1 What stands

- `content/lab-bases/net/`, `FROM ubuntu:24.04`, first layer byte-identical to the systemd labs' first `RUN`; a lab's Dockerfile is `FROM lab-base-net`, `COPY topology`, `COPY machines/ /etc/netns/`, `RUN netlab enable && netlab seal …`.
- A machine is a network namespace with its own `/etc/<program>` (through `/etc/netns/<m>/`), `/run`, state folders and hostname; `on MACHINE [COMMAND]` makes the learner root on it; the lab machine is the console and on no lab network; switches live in a `switches` namespace; no machine reaches the real internet.
- The topology file's ten words (`machine`, `link`, `lan`, `route`, `dns`, `sysctl`, `netem`, `mtu`, `tunnel`, `run`); `netlab up` sets every kernel setting explicitly in every namespace (`ip_forward` first, then `rp_filter` 0, redirects off, `accept_dad` 0, `accept_ra` off on routers, the ephemeral range, CUBIC).
- Per-machine units `frr@`, `strongswan@`, `named@`, `unbound@`, `nginx@`, `haproxy@`, `nftables@`, all after `netlab.service`; the plain units of those daemons **masked** on the lab machine (N4).
- Check helpers in `checklib.sh`: `frr`, `json`, `wait_for`, `tcp_state`, `pcap`/`capture`, `frr_saved`, `intact`.
- Addresses from RFC 5737 and `2001:db8::/32`, sites in `10.0.0.0/8`, tunnel inside addresses as `/30`s from `169.254.0.0/16`, names under `.test`, private ASNs.
- FRR 8.4.4, strongSwan 5.9.13, BIND 9.18, Unbound 1.19, nginx 1.24, HAProxy 2.8 from Ubuntu's archive (no third-party sources in the base). `tshark` stays in the base (about 125 MB once, cached): learners use it once, in topic 23's worked example, to see a header dissected in words; checks read `tcpdump` text or JSON, never tshark output, whose format changes between versions.

### 4.2 What changes

| # | Change | Why | Who needs it |
| --- | --- | --- | --- |
| B1 | **strongSwan without the extra plugins.** Layer 2 installs `strongswan-swanctl charon-systemd libstrongswan-standard-plugins strongswan-pki` (not `libstrongswan-extra-plugins`), ships the IPsec designer's `/etc/strongswan.d/swanctl.conf` plugin list (it silences the "plugin failed to load" lines the extra package was added for) and `charon { plugins { forecast { load = no } } }` as a guard. Each machine running strongSwan gets `install_routes = no` | The extra package's `forecast` plugin makes VTI drop every inbound packet (`XfrmInTmplMismatch`); found and fixed by the critic on the base prototype | `csa.net.ipsec`, checkpoint part 3 |
| B2 | **Per-machine `/etc/sysctl.d/`.** `netlab up` applies each machine's `/etc/netns/<m>/sysctl.d/*.conf` in name order after its defaults and the topology's `sysctl` words, **only keys under `net.`** (anything else is refused with a line in the journal). Never `sysctl --system` inside a machine: it also applies `/usr/lib/sysctl.d`, whose `kernel.*` and `fs.*` keys belong to Docker's whole machine. Helper `sysctl_saved M KEY` compares the live value with the files' final value | Kernel settings a learner fixes must last (forwarding on a NAT gateway, keepalive times, BBR, IPv6 forwarding); the base had no home for them (its open question 5) | routing, NAT, IPv6, transport, congestion |
| B3 | **Per-machine network file `/etc/network/up`** (`/etc/netns/<m>/network/up` on the lab machine): `ip` commands `netlab up` runs inside the machine after the topology and sysctls, before its services. The topology stays scenery (sealed); the network file is the machine's own configuration, which a lab may give the learner. `sudo netlab restart` rebuilds the network as a reboot would (every machine's services are `PartOf=netlab.service`) | Faults and fixes that live in a machine's addresses, neighbours, link states, tunnels and routes (a pinned MAC, a link set down, a misaligned prefix, the VPN's `vti0`); proved in topic 23's and 25's debug prototypes | layers, CIDR, IPv6, IPsec |
| B4 | **`netlab verify`**: builds a throwaway copy of every machine (`chk-<m>`) from its files without services, compares normalised state (link up or down and MTU; configured addresses, not link-local or advertised; routes without local, broadcast and anycast entries, advertised routes or the PMTU cache; permanent neighbours; `nft -s list ruleset`; forwarding sysctls), lets the check probe inside the copy, then removes it. The layers designer's `netlab-state` (24 lines) is the comparison | "The fix lasts" for anything in a network file, including pins of something that changes at every boot, which no reading of the files can show | layers, CIDR, IPv6, IPsec |
| B5 | **`radvd@M`** (`radvd` package, 149 KB; `run M radvd`; config `/etc/radvd.conf` in the machine) | The IPv6 labs teach and fault `radvd.conf`; FRR's router advertisements would need the topic re-prototyped and teach a less readable file | IPv6 |
| B6 | **`netlab link M IF down\|up\|silent\|restore`** (the FRR brief's `lab-link`): `silent` drops everything arriving over the link in the far machine while carrier stays up | Teaching loud against silent failures; checks that prove a backup by cutting the primary (section 4.4) | routing, BGP steering, checkpoint part 3 |
| B7 | **Helpers in `/usr/local/bin`:** `looking-glass M 'show …'` (read-only `vtysh`), `holdconns N HOST PORT` (parallel, one 3-second deadline) and `holdserver PORT…`, `web-svc` (dual-stack test server: 8080 echoes the caller's address, 9000 counts bytes). **In `checklib.sh`:** `bgp-best M PREFIX`, `nft_saved M`, `sysctl_saved M KEY`, and `cors-verdict` (the Fetch standard's CORS check and preflight rules, about 40 lines of Python, with its own table of cases run by `tools/tests/`) | Each was needed by two or more topics, and inline Python in checks is unreadable | BGP, NAT, IPv6, HTTP semantics |
| B8 | **Packages added to layer 2:** `radvd ipcalc sipcalc`. Already there: `iperf3`, `mtr-tiny`, `iputils-tracepath`, `iputils-arping`, `socat`, `openssl`, `ndisc6`, `nginx`, `haproxy`, `bind9`, `unbound` | The CIDR topic teaches `ipcalc` and `sipcalc` as checking tools | CIDR, IPv6, checkpoint |
| B9 | **Machine-level custom units documented:** a lab's own program on a machine is an ordinary unit whose `ExecStart` is `ip netns exec M lab-enter M PROGRAM` (`shop-api@app`, `move-watch` on `office`, `certbot@web.timer`, `caddy@shop`, `step-ca@ca`, `old-lb` on `lbold`) | Several topics run stand-in services and timers on machines | most topics |
| B10 | **Hostnames and domain names.** Each machine's UTS namespace sets its hostname **and** a domain name of `(none)` | Otherwise FRR writes `domainname localdomain` into saved configurations (checkpoint finding 5) | every FRR lab |
| B11 | **MAC addresses are not fixed;** a new veth pair's random MAC is kept | Topic 23's pinned-MAC fault and its wrong fix depend on MACs changing at every boot | layers |

Topic-only layers (a second `RUN` after `FROM lab-base-net`, identical within the topic): DNS adds nothing (BIND and Unbound are in the base); congestion adds `caddy python3-aioquic ngtcp2-client` (63 MB, with `h3get` and `wan-set` as scenery); certificates adds `certbot faketime` and step-ca 0.30.2 plus step-cli 0.31.0 from their pinned GitHub release `.deb`s, checked by sha256 in the same `RUN` (the first lab download from outside Ubuntu's archive, decided in section 10); HTTP semantics adds `python3-websockets`.

### 4.3 What no lab does any more

The six designers' own topologies go: the container's main namespace as a router or server (NAT's gateway, transport's `lab`, congestion's Caddy server, DNS's resolver host, HTTP's `lab`, load balancing's HAProxy, IPsec's gateway), hand-written `network.sh` per lab, `router NAME`, `on-dc`/`cloud-enter`/`on-cloud`/`on-nat`, `ns@` units with configs under `/var/lib/lab/dns`, `NetworkNamespacePath=` units that see the container's `/etc` instead of the machine's. Each becomes a named machine on the base (`gw`, `app`, `shop`, `resolver`, `web`, `origin`, `lb`, `vpn`), reached with `on`. A machine's firewall persists through `nftables@M` and its `/etc/nftables.conf`, exactly as Module 1 taught for one server; `systemctl enable nftables@gw` replaces `systemctl enable nftables`.

### 4.4 Rules for checks on the base

- A check may cut and restore a link to prove a backup (the FRR brief's R5): `netlab link` with the restore in an `EXIT` trap, waiting for the primary to return before it exits, last in `checks.yaml`, with `timeout:` 60 to 90. It changes nothing the learner made and leaves the lab as it found it. The ADR-0018 amendment records this exception to "checks only read" (platform work P0).
- A check may start throwaway servers, listeners, BIND instances or namespaces of its own (`chk-…`), and removes them.
- Scenery the learner mustn't change (an ISP, the cloud, the other side of a VPN, an edge cache) is sealed and checked with `intact`; a scenery daemon changed live is caught by its behaviour or by `frr_saved` on it.

### 4.5 Kernel needs, and where they were seen

All seen on Docker Desktop 29.8.2 (kernel 6.18.33.2-microsoft-standard-WSL2) on 2026-11-11. **Nothing has run on a GitHub runner** (`ubuntu-24.04`, kernel 7.0.0-1017-azure): the CI spike (P2) settles each row.

| Need | Topics | Docker Desktop | Runner, and the fallback |
| --- | --- | --- | --- |
| veth, bridges, namespaces, per-namespace `ip_forward` and `rp_filter` | all | works | expected (Module 1 and 2 labs use namespaces in CI today) |
| nftables NAT (`nf_nat`, `nft_chain_nat`, masquerade) | NAT, IPv6, transport | works | likely (Docker's own port publishing loads NAT on the host); if not, a `labs.yml` step `sudo modprobe -a nf_nat nft_chain_nat` |
| `ip_gre` | layers | works | modules on demand untried; fallback: the narrow link becomes a plain veth with MTU 1400 and the debug's ICMP fault is unchanged |
| `xfrm_user`, `esp4`, `ip_vti` | IPsec, checkpoint part 3 | works (with B1) | modules are in the runner's standard package; fallback: `sudo modprobe -a esp4 ip_vti xfrm_user` in `labs.yml`; last resort, GRE inside IPsec (the base's proven design) |
| `sch_netem` | transport, congestion, troubleshooting, base `netem` word | works, delays egress only | may live in `linux-modules-extra`; fallback: install it and `modprobe` in `labs.yml` |
| `tcp_bbr` | congestion | works, autoloads from `/etc/sysctl.d` | fallback as netem; if thresholds overlap on a busy runner, check `bbr` in `ss -tni` and lower the threshold |
| nftables `reset tcp option window` | transport | works | untried |
| IPv6 in namespaces, forwarding, SLAAC | IPv6, NAT | works | Docker may disable IPv6 in the container's own namespace; new namespaces should take kernel defaults |
| `fib_multipath_hash_policy` per namespace | routing, checkpoint part 2 | works | expected |

Workflow-file changes merge only from a branch that already holds `main`'s version of the file (the owner's `gh` token lacks the workflow scope).

## 5. The topics

### 23. `csa.net.layers` (designer: [csa.net.layers.md](csa.net.layers.md))

- **Skills, prerequisites:** as designed (six; `csa.m1.checkpoint`).
- **Owns the module's lab onboarding:** a "Before your first network lab" note at the top of `example-follow-a-request`'s prompt, and the base's layout steps in its first labelled steps (`netlab show`, the topology, `on`, `systemctl status frr@r1`, a machine's `/etc/network/up`). Terms as section 3.7.
- **Practice ladder:** as designed, 25 items. `fill-tunnel-up`'s starter is r1's `/etc/network/up`, applied with `sudo netlab restart`. `est-mss-from-mtu`'s third mistake (1500) gets a working (`"1500"`). `hdr-two-sides`: the writer simplifies the command once its output is pinned. Recall items and labs use the captured fixtures listed in the facts table.
- **Proofs:** build `build-branch-tunnel` as designed, its `fixes-last` check through `netlab verify`. Debug `debug-big-downloads-hang` as prototyped (contract kept, restart trial passed), with the faults in r2's `/etc/network/up` and web's `/etc/nftables.conf`, the prompt reworded as 3.2 says, and `two-of-three.sh` added. Explain as designed.
- **Review pool:** as designed.
- **Resources:** as designed, main Beej ch. 4 (re-opened by the critic 2026-11-11: sections 4.1 to 4.5, about 2,000 words with the glossary). Required video Ben Eater's "Hop-by-hop routing" (watch before writing; it becomes `resources[0]` only if it shows the two-sided view). Cloudflare's "What is MTU?" refuses automated fetches (the critic's tool got HTTP 403; the designer used a browser user agent): a writer opens it in a browser before linking it; if it can't be confirmed, Majkowski's blog post and the three clouds' MTU pages carry the section. Facts re-read by the critic: AWS 9001 and the 1500/8500 limits, Google 1460 (1300 to 8896, no fragmentation, MSS clamping only outside the VPC), Azure blocking GRE, Google supporting GRE version 0: all as the brief says.
- **Minutes:** 310 (the designer's 300 after trims, plus 10 for the lab onboarding).

### 24. `csa.net.cidr` (designer: [csa.net.cidr.md](csa.net.cidr.md))

- **Skills, prerequisites:** as designed (five; `csa.net.layers`). "In code" is bash `$(( ))`, as decided there; topic 26's write lab accepts bash or awk.
- **Facts now confirmed** (critic, 2026-11-11): Google's VPC Network Peering refuses overlapping subnet ranges ("No subnet IP range can exactly match, contain, or fit within another subnet IP range in a peered VPC network"), so the lesson names all three clouds (the brief's F8); AWS's default VPC is `172.31.0.0/16` with a `/20` default subnet per zone (F9).
- **Practice ladder:** as designed (26 items). `est-binary-octet`'s given becomes the octet itself (`given: {octet: 10110100}`, working `128 + 32 + 16 + 4`) instead of the contrived "4 of them are ones". The fill-in, write and build are plain labs on the shared plain `RUN` (3.5).
- **Proofs:** build `build-address-plan` as designed. Debug `debug-new-warehouse` as designed, its hosts' and routers' addresses in their `/etc/network/up`, the plan in `/etc/netlab/plan.txt`; **its contract and restart trial run before the lesson is written** (only its mechanisms were captured). Explain as designed.
- **Review pool, resources:** as designed (re-opened: Beej ch. 17, about 1,900 words, sections as listed; AWS's subnet page, five reserved addresses as listed).
- **Minutes:** 295.

### 25. `csa.net.ipv6` (designer: [csa.net.ipv6.md](csa.net.ipv6.md))

- **Skills, prerequisites:** as designed (five; `csa.net.cidr`). Drop the "builds on `csa.hw.windows-ad`" row: this topic defines a DNS record and the AAAA record in one sentence each.
- **Labs on the base:** radvd through `radvd@r1` (B5), r1's forwarding in its `/etc/sysctl.d/` (B2), r1's LAN address in its `/etc/network/up` (B3), DAD turned on for the worked example's hosts with the topology's `sysctl` word, `web-svc` from the base (B7), "hosts untouched" by `netlab seal` on h1's and h2's files.
- **Practice ladder:** as designed, with the designer's trims (`mcq-ula-use` and `mcq-rs-ra-order` to review-only). **`mcq-azure-ipv6`'s right answer is narrowed:** "Outbound IPv6 through a NAT gateway or a load balancer's outbound rules leaves from translated public addresses". Microsoft's IPv6 overview (re-read 2026-11-11) calls an instance-level public IP "IPv6 Internet connectivity directly to individual VMs" and doesn't say it is translated; the NAT Gateway page confirms StandardV2's IPv6 public addresses and NAT64. The lesson says the same.
- **Proofs:** build `build-dual-stack-branch` and debug `debug-ipv6-half-works` (prototyped, contract and restart trial kept) as designed. Explain as designed; its `clouds-differ` row uses the narrowed Azure wording.
- **Review pool, resources:** as designed. The spec's row changes (section 12).
- **Minutes:** 300.

### 26. `csa.net.routing` (designer: [csa.net.routing.md](csa.net.routing.md); shared: [frr-labs-common.md](frr-labs-common.md))

- **Skills, prerequisites:** as designed (five; `csa.net.cidr`).
- **Adds, for the module:** the definition of `sysctl` and `/etc/sysctl.d/` (one paragraph in lesson section 9, with `net.ipv4.ip_forward` and `rp_filter`, and why a live `sysctl -w` is gone at the next boot), one recall item on it (`sysctl-forwarding-file`, `predict_shell` over two `sysctl.d` files: which value wins), and one ECMP item (`mcq-ecmp-one-dead-path`, `find-the-black-hole`: some connections from one laptop fail and others don't; both next hops in `ip route`), because checkpoint part 2 rests on ECMP and nothing else in the module practises it before topic 38.
- **Labs on the base:** `router NAME` becomes `on NAME vtysh`; `lab-link` becomes `netlab link`; a router's files are `/etc/frr/frr.conf` inside it; recipe R3 reads `ip -d -j route` (3.5).
- **Debug fault 2, corrected:** a static default route via a next hop on a connected subnet that no longer exists (198.51.100.254) **is** installed by FRR (it resolves through the connected `/24`; the critic's probe showed it resolved, not inactive); the symptom is the same, but the evidence is r1's `ip neigh` showing 198.51.100.254 `FAILED` or `INCOMPLETE`, not a missing route. The lesson's "how packets vanish" table gains that row ("the next hop doesn't answer ARP"), which retrieves topic 23. The writer captures the real outputs.
- **Review pool:** as designed; `est-loop-crossings-ttl128` reworded "how many times in all does it cross a link between two of the looping routers" (127; mistakes 128 and 42).
- **Resources:** as designed (re-read: FRR 8.4's distance table with 255 never installed; AWS's priority list; Azure's "preferred, even if BGP routes are more specific"; Google's subnet routes first and no ECMP across categories; the Systems Approach page has both sections).
- **Minutes:** 300 (295 plus the sysctl paragraph and two items).

### 27. `csa.net.nat` (designer: [csa.net.nat.md](csa.net.nat.md))

- **Skills, prerequisites:** as designed (five; `csa.net.routing`, `csa.net.ipv6`).
- **The gateway is a machine, `gw`, not the container's main namespace.** Its rules are gw's `/etc/nftables.conf` (`nftables@gw`), its forwarding a file in gw's `/etc/sysctl.d/` (B2); Module 1's saved-file check works inside it. The brief's claim that `csa.linux.hardening` taught `/etc/sysctl.d/` is wrong (no Module 1 file mentions sysctl); topic 26 teaches it.
- **Debug fault 2 changed.** As designed, a masquerade rule without `oifname` would also translate the office's outgoing traffic, so fault 3 (the office's stale `10.1.1.0/24` rule) could never show. Fault 2 becomes `iifname "wan" masquerade` (the in-and-out confusion: it rewrites only traffic arriving from the internet, so customers reach the app as 10.1.0.1 while the office's traffic still depends on its own, stale rule). The worked example keeps the "no `oifname`" demonstration; the wrong fixes and checks are unchanged. The writer re-runs the three faults together before writing the prompt.
- **Labs:** `holdconns` and `holdserver` from the base (B7); the CI spike runs this topic's worked example first.
- **Practice ladder, proofs, review pool, resources:** as designed (re-read: AWS 55,000 per address per unique destination, up to 8 addresses, ports 1024 to 65535; regional gateways 32 per zone; Google 64,512 ports, defaults 64 and 32, 1,008 VMs; AWS's Ohio example $0.045 an hour and per GB, gateway endpoints free; Azure's default route table dropping `100.64.0.0/10`).
- **Minutes:** 290.

### 28. `csa.net.transport` (designer: [csa.net.transport.md](csa.net.transport.md))

- **Skills:** as designed (five). **Prerequisites:** `csa.net.nat` (not a Module 2 gate).
- **Labs on the base:** topology A is `app` (shop-api as `shop-api@app`, its config `/etc/shop/api.conf` inside app) — `nat` — `db`/`supplier`; topology B is `app` — `edge` — `wan` (netem) — `dr`. The keepalive override fault is two files in app's `/etc/sysctl.d/`; checks compare with `sysctl_saved` (B2), not `systemd-sysctl --cat-config` (which reads the global `/usr/lib/sysctl.d` too). The fast clock stays, said in every prompt.
- **Practice ladder, proofs:** as designed. `write-syn-check`'s hidden pairs need three nftables option rewrites nobody has tried (`sack-perm`, `timestamp`, `maxseg size set`): try them first, or replace a pair as the designer proposes.
- **Review pool, resources:** as designed (re-read: the kernel's 131 s, keepalive 2 h/9/75 s, 924.6 s; NLB 350 s, TLS listeners fixed, the Nitro v6 350-s warning; Cloud NAT 30/30/1,200/30 s; HPBN's sections and CC BY-NC-ND 4.0; Cloudflare's 2019 post and its four sections).
- **Minutes:** 300.

### 29. `csa.net.congestion` (designer: [csa.net.congestion.md](csa.net.congestion.md))

- **Skills, prerequisites:** as designed (five; `csa.net.transport`).
- **Owns QUIC and HTTP/3 in practice:** QUIC's handshake and streams, Alt-Svc and HTTPS-record discovery, the silent fallback when UDP 443 is blocked, the firewall rule, and the clouds' HTTP/3. Topic 31 doesn't repeat them (section 5, topic 31).
- **Labs on the base:** the Caddy server is machine `shop` (`caddy@shop`, B9) with its firewall in `nftables@shop`; the sender is `shop` too; the office is a machine. Topic layer as section 4.2. Every Caddyfile has `skip_install_trust`; a boot step trusts Caddy's local root for every machine (`/etc/ssl` is shared).
- **Practice ladder, proofs, review pool:** as designed (lengths measured: right longest in 3 of 13). The 25 Mbit/s threshold waits on the CI spike.
- **Resources:** as designed (re-read: `tcp_bbr.c`'s header, "does not react directly to packet losses or delays", no version named; draft-ietf-ccwg-bbr-07 of 2 November 2026 specifies BBRv3, Experimental; RFC 9438's β 0.7, C 0.4 and the three stacks; nginx's QUIC since 1.25.0; HTTP/3 explained CC BY 4.0).
- **Spec row:** "choose and set a sender's congestion control" added (section 12).
- **Minutes:** 300.

### 30. `csa.net.dns` (designer: [csa.net.dns.md](csa.net.dns.md))

- **Skills, prerequisites:** as designed (five; `csa.net.transport`).
- **Labs on the base:** machines `resolver` (`unbound@resolver`, the office's resolver), `root`, `tld`, `ns1`, `ns2`, `ns-eu` (`named@`, configs in each machine's `/etc/bind`), `isp1` to `isp3` (`unbound@`), `office`; `dnssec-link` as a one-time topic boot unit; `move-watch` as a machine-level unit on `office` (B9). Every resolver: `local-zone: "test." nodefault`, `infra-host-ttl: 60`.
- **Practice ladder:** as designed (30 entries), with the worked example's step 8 (`transparent` with one `local-data`) added, as the designer recommends, so the build isn't the first edit of the resolver; `mcq-open-resolver`, `mcq-azure-fallback` and `mcq-split-which-resolver` move to review-only to hold the time. `est-forgot-to-lower` says "a resolver that fetched it just before the change" (fetched at 08:59 the exact answer is 3.98).
- **Proofs:** build `build-move-the-api` and debug `debug-half-the-lookups` as designed; **neither was built end to end** (the monitor, the staggered caches, `broken.test`, the wrong `allow-transfer`): prove both under `labcheck test`, with the restart trial, before the lesson. Explain as designed.
- **Review pool:** as designed.
- **Resources:** as designed. The DigitalOcean tutorial renders its text in the browser: the critic's fetch saw only its navigation, so the writer confirms the three sections and the "13 root servers" line in a browser. Cloudflare's "How DNSSEC works" refuses automated fetches (as in topic 23): confirm in a browser or replace it. Re-read by the critic: Route 53's private-zone NXDOMAIN rule and the Resolver rule precedence, the Slack outage (2021-09-30, 24 hours, under 1% of users, a DS cached for 24 h), Unbound's defaults (86,400, 3,600, `infra-host-ttl` 900, round robin on), Julia Evans' post (2020-06-17).
- **Minutes:** 315.

### 31. `csa.net.http-tls`, HTTP and TLS (new scope; designer material: [csa.net.http-tls.md](csa.net.http-tls.md), the HTTP-versions and handshake parts)

- **Title:** HTTP and TLS. **Prerequisites:** `csa.net.dns`, `csa.net.congestion`.
- **Skills:** `http-versions` (HTTP/1.1 against HTTP/2: connections, multiplexing, HPACK, ALPN; HTTP/3 named as topic 29's; the round-trip sums, three estimates: `est-rtt-tls12`, `est-rtt-tls13`, `est-hundred-connections`), `tls-handshake` (reading 1.2 and 1.3 in `s_client -trace`, what an observer sees, SNI in clear and ECH), `tls-server-config` (new: which versions to allow, SNI and a default server that refuses unknown names, HTTP/2 on, OCSP stapling set up and read with `-status`).
- **Removed, because topic 29 owns them:** lesson idea 2 (how a client finds HTTP/3) and the HTTP/3 cloud list, the worked example's Caddy step, `alt-svc-parse`, `mcq-h3-udp-blocked`, `mcq-when-h3-helps` (the same id and question as topic 29's) and `est-h3-saving` (topic 29's `est-rtt-saved` with the same 150 ms). The lesson says "HTTP/3 runs on QUIC, topic 29" in one sentence. No Caddy or `ngtcp2-client` in this topic's labs.
- **Practice ladder:** `example-two-handshakes` (the designer's example steps 1, 3 and 4, plus a stapling step against the lab's OCSP responder and an SNI step comparing two names' certificates); recall: `alpn-from-curl-v`, `mcq-h2-hol`, `est-rtt-tls12`, `est-rtt-tls13`, `trace-13-messages`, `trace-12-in-clear`, `mcq-what-observer-sees`, `mcq-sni-why`, `mcq-tls-versions`, `stapling-status`, `mcq-first-handshake-no-staple`, `mcq-ocsp-today`; **`fill-nginx-tls`** (new: gaps for `ssl_protocols`, the `http2` flag on `listen` (nginx 1.24), `ssl_stapling on` with its `resolver`, and the second site's `server_name`; checks read the live server with `openssl s_client` and `curl -w %{http_version}`; wrong fixes `tls11-allowed`, `no-http2`, `stapling-without-resolver`, `wrong-server-name`); **`write-handshake-report`** (new, from the designer's `write-cert-report`: `~/bin/handshake-report HOST PORT [NAME]` prints `protocol`, `alpn`, `certificate-name` (the leaf's first SAN for that SNI) and `stapled yes|no`, against throwaway `openssl s_server` processes the checks start on 127.0.0.1 with random names and settings; plain lab).
- **Proofs (new, designed here, not prototyped):** build **`build-two-sites-one-address`**: on `web`, `www.shop.test` and `api.shop.test` on one address, each with its own certificate (given as files from the lab CA), chosen by SNI; TLS 1.2 and 1.3 only; HTTP/2; OCSP stapling for www against the lab's responder (`openssl ocsp`, scenery, as the designer's prototype ran on port 8888); an unknown name refused (`ssl_reject_handshake on` in a default server) rather than given another site's certificate; HTTP redirected to HTTPS; saved and `nginx@web` enabled. Checks: `sni-each`, `unknown-name-refused`, `versions`, `h2`, `stapled` (second handshake), `full-chain`, `redirect`, `lasts`. Wrong fixes: `one-cert-for-both`, `tls11-allowed`, `no-http2`, `no-stapling`, `unknown-gets-www`, `not-reloaded`. Debug **`debug-handshake-failures`**: the shop's partner integration (an old client limited to TLS 1.2, scenery) fails, a monitoring probe that sends no SNI reports a name mismatch, and stapling never appears; three faults (versions limited to 1.3, the default server is api's, the stapling resolver missing), each found from `s_client` output and nginx's error log. Rules: keep 1.0 and 1.1 off, don't hand the probe another site's certificate, no client told to skip verification. Explain: the designer's prompt without the certificate and ACME clauses, plus "what SNI is for and what an observer still sees". Both labs are proved under `labcheck test` before writing (they reuse mechanisms the designer tried: verify codes, `-trace`, stapling from the second handshake).
- **Review pool:** `est-rtt-tls13`, `est-hundred-connections` (review-only), `trace-12-in-clear`, `keylog-decrypted` (review-only), `mcq-what-observer-sees`, `mcq-first-handshake-no-staple`, `mcq-tls-versions`.
- **Resources:** MDN "Evolution of HTTP", The Illustrated TLS 1.3 Connection (MIT), Cloudflare's "What happens in a TLS handshake?", the nginx SSL module. Cloudflare's page refuses automated fetches (critic, 2026-11-11, HTTP 403): the writer confirms it in a browser; if it can't, The Illustrated TLS 1.3 Connection becomes `resources[0]`. Facts re-read: TLS 1.3 is RFC 9846 (July 2026, Proposed Standard, obsoleting RFC 8446 and 5246 among others); ECH is RFC 9849 (March 2026).
- **Minutes:** 175.

### 32. `csa.net.certificates`, Certificates and mutual TLS (new topic; designer material: [csa.net.http-tls.md](csa.net.http-tls.md), the chain, ACME and mTLS parts)

- **Prerequisites:** `csa.net.http-tls`. **Skills:** `cert-chains`, `acme-and-rotation`, `mutual-tls` (as designed; `acme-and-rotation` keeps its four estimates).
- **Practice ladder:** `example-issue-and-rotate` (the designer's example steps 5 to 7, plus reading the chain served); the chain, ACME and mTLS recall rows of sections 7.5 to 7.7; `fill-local-ca` and `write-cert-report` (its `protocol` line dropped: topic 31's report has it) as designed.
- **Proofs:** build `build-shop-tls` and debug `debug-padlock-trouble` as designed (its `versions` and `h2` checks stay as retrieval of topic 31). Neither was built end to end; the untried pieces (the TLS 1.1 refusal check, nginx rejecting a client certificate without `clientAuth`, an already-expired certificate made with `faketime`, the certbot drop-in for `REQUESTS_CA_BUNDLE`) are tried first, each with the designer's fallback.
- **Labs on the base:** `web` (nginx@web), `ca` (step-ca as `step-ca@ca`, its files in ca's state folder), `office`, `partner`. certbot runs **inside `web`**: `certbot@web.service` and `certbot@web.timer` (B9), so its `/etc/letsencrypt` is web's and its deploy hook is `systemctl reload nginx@web`. The prompts say so; the masked plain `nginx` unit refuses the habit-typed `systemctl reload nginx` with a clear message.
- **Review pool:** the designer's chain, ACME and mTLS rows.
- **Resources:** Let's Encrypt's "How It Works", "Challenge Types" and "Ending OCSP Support in 2025" (re-read: Must-Staple failing from 2025-01-30, OCSP URLs dropped 2025-05-07, responders off 2025-08-06, for privacy), "From 90 to 45" optional, Cloudflare's mTLS page (confirm in a browser). The CA/Browser Forum schedule: 200 days from 2026-03-15, 100 from 2027-03-15, 47 from 2029-03-15 (BR v2.3.1 as the designer read it; the ballot's page confirms "398 days to 47 days", March 2026 to March 2029).
- **Minutes:** 230.

### 33. `csa.net.http-semantics` (designer: [csa.net.http-semantics.md](csa.net.http-semantics.md))

- **Skills:** as designed (four). **Prerequisites:** `csa.net.http-tls`.
- **Owns the cookie** (one sentence, in the CORS credentials paragraph), which topic 34 uses.
- **Labs on the base:** `origin` (nginx@origin, the learner's `/etc/nginx/sites-available/shop` inside it; `shop-app` and `order-board` as machine-level units), `edge` (nginx@edge, sealed scenery), `office`. `cors-verdict` lives in the base's `checklib.sh` with its test table (B7). The write lab is a plain lab whose throwaway servers listen on 127.0.0.1.
- **Practice ladder, proofs:** as designed; the debug's WebSocket fault is scaled down (board ping 45 s, faulty timeout 30 s, check 75 s with `timeout: 100`), as the designer recommends. `est-ping-interval` is written as a deliberate retrieval of topic 28's rule (the smallest timer on the path wins), in a new story.
- **Review pool, resources:** as designed (re-read: MDN caching's sections and its `no-cache` sentence; `Access-Control-Max-Age` 5 s default, Firefox 86,400, Chromium 7,200 since v76; RFC 9111 §5.2.2.4, §5.2.2.7 and the 10% heuristic; nginx's WebSocket page, `proxy_http_version` "before version 1.29.7", 60 s; grpc.io's four RPC kinds and deadlines).
- **Minutes:** 315 (the designer's 321 with RFC 6455 §1 moved to the recap and `mcq-idempotency-key` already review-only).

### 34. `csa.net.load-balancing` (designer: [csa.net.load-balancing.md](csa.net.load-balancing.md))

- **Skills:** as designed (five). **Prerequisites:** `csa.net.http-semantics`.
- **Labs on the base:** `lb` (haproxy@lb, `/etc/haproxy/haproxy.cfg` inside it, the stats socket at lb's `/run/haproxy/admin.sock`), `web1` to `web3`, `api1`, `api2`, `stock1`, `stock2`, `db` with their stand-ins as machine-level units, `office`. Commands become `on lb socat …`, `systemctl reload haproxy@lb`, `journalctl -u haproxy@lb`.
- **Practice ladder, proofs, review pool:** as designed, with the designer's trims (R6 to R8 to "More resources"; `mcq-azure-http-probe` and `mcq-tls-stays-with-payments` review-only). Untried pieces tried first: the hiccup as a fast 503, the `stock-sync` stand-in, the API backend, and which of `show info`'s `Uptime_sec` or the worker's `/proc` start time resets at a reload in 2.8. Google's "all backends unhealthy" row is worded from the page as it is (re-read 2026-11-11): Application Load Balancers answer 503 (classic 502); passthrough Network Load Balancers may drop all traffic if their failover policy says so, otherwise send to unhealthy backends as a last resort, and the global external type fails over to the next region.
- **Resources:** as designed (re-read: HAProxy's Starter Guide section 2; Yanacek's article and its correlated-failure sentence; ALB defaults 30/5/5/2 and fail-open; Google's 5/5/2/2; nginx's active checks commercial only).
- **Minutes:** 315.

### 35. `csa.net.bgp` (designer: [csa.net.bgp.md](csa.net.bgp.md); shared: [frr-labs-common.md](frr-labs-common.md))

- **The split is accepted;** this is the first half. **Skills, prerequisites:** as designed (four; `csa.net.routing`).
- **Labs on the base:** `edge`, `ispa`, `ispb`, `transit`, `cloud`, `office`, `shopweb`, `web`; `looking-glass` and `bgp-best` from the base; the far routers sealed and checked with `intact` and `frr_saved` (R6).
- **Practice ladder, proofs, review pool, resources:** as designed (re-read: FRR 8.4's "enabled by default for the traditional configuration", the MED wording "received from the same AS", the import check "for versions 7.4 and beyond").
- **Minutes:** 285.

### 36. `csa.net.bgp-steering` (new id; designer: [csa.net.bgp-steering.md](csa.net.bgp-steering.md))

- **Skills, prerequisites:** as designed (four; `csa.net.bgp`). `route-reflection` and `failure-detection` are calculation skills with three and four estimates.
- **Labs:** as designed, on the base, with BFD through `bfdd=yes` and `netlab link … silent` for the silent cut.
- **Practice ladder, proofs, review pool, resources:** as designed (re-read: Direct Connect's `7224:7100/7200/7300` "evaluated before any AS_PATH attribute", the associated-Region medium preference, "AWS does not recommend using MED"; the 100-route default per private or transit VIF, raisable to 1,000, the session going idle; hold 90 s, keepalive 30 s, BFD 300 ms × 3, graceful restart not with BFD).
- **Minutes:** 295.

### 37. `csa.net.ipsec` (designer: [csa.net.ipsec.md](csa.net.ipsec.md))

- **Skills:** as designed (five). **Prerequisites:** `csa.net.bgp`, `csa.net.http-tls`.
- **The tunnel is a VTI,** as the designer built it; the base gets the `forecast` fix (B1), which the critic confirmed makes VTI work between two base machines. The fallback, if a runner refuses `ip_vti`, is the base designer's GRE inside a tunnel-mode SA (its contract kept), switched by the topology's `tunnel` lines and the `children` block.
- **Labs on the base:** the learner's gateway is machine `vpn` (`strongswan@vpn`, `frr@vpn`, `nftables@vpn`); the provider is `cloud` (sealed; `strongswan@cloud`, `frr@cloud`, ordered to start before `vpn`'s); `internet` and `office` are machines. `vti0` lasts in vpn's `/etc/network/up` (B3), so the fill-in's gaps move from `vti0.service` to that file, and the build's `comes-back-at-boot` check reads it through `netlab verify`. `cloud-vpn-status` and `cloud-vpn-log` stay as read-only wrappers for the provider's view.
- **Practice ladder, proofs:** as designed; `keyingtries = 0` in every learner connection (the critic's restart trial failed without it, as the designer's first did). ECP-384 untried: the writer runs it first and falls back to `modp3072`.
- **Review pool, resources:** as designed. strongSwan's documentation is CC BY 4.0 (its page footer, re-read 2026-11-11), not "not stated" as the base brief has it. Re-read: AWS's MTU table (AES-GCM 1446/1406, with NAT-T 1438/1398, AES-CBC SHA1/SHA2-256 1438/1398), the virtual private gateway's default ASN 64512 fixed after creation, the inside `/30` from `169.254.0.0/16` and default `0.0.0.0/0` selectors.
- **Minutes:** 310.

### 38. `csa.net.troubleshooting` (designer: [csa.net.troubleshooting.md](csa.net.troubleshooting.md))

- **Skills, prerequisites:** as designed (six; `csa.net.load-balancing`, `csa.net.ipsec`).
- **Faults checked against the final topic briefs** (the designer's open question 1): the debug's three (provider loss with a rate-limited hop, a duplicate service address announced by gratuitous ARP, a backend's egress filter blocking its database) appear in no topic's debug; topic 23's pinned-MAC fault is a neighbour of the duplicate address but a different mechanism. The worked example's stale more-specific static route resembles routing's stale blackhole (debug fault 3): it is practice, chosen so the example spends its effort on the method, and the prompt says it is a routing fault met before. The casebook uses other topics' debug faults as recorded cases on purpose (retrieval after those proofs).
- **Practice ladder, proofs, review pool:** as designed, with the designer's trim (a): R1's core sections only and five multiple-choice items to review-only. The debug's checks and wrong fixes are run under `labcheck test` before writing; `calls-succeed` with 8% loss runs three times in the CI spike, and drops to 5% loss if it ever fails for the solution. The casebook's plain `RUN` is the shared Module 3 plain line (3.5), without `gawk`.
- **Resources:** as designed (re-read: the SRE chapter's CC BY-NC-ND 4.0 and its sections; Gregg's anti-methods and problem-statement questions, no licence stated; Akamai's guide, including the "small amounts of loss in the neighborhood of 10%, there is no cause for real concern" line the lesson corrects). Everything curl's and nginx's documentation licences are confirmed before they are listed.
- **Minutes:** 300.

## 6. Checkpoint 3: the address plan, the outage and the cloud link (designer: [csa.m3.checkpoint.md](csa.m3.checkpoint.md))

**Prerequisites:** the sixteen topics. **`estimated_minutes`: 240.** Objectives as designed (no cause of part 2 named). The proof block as designed:

```yaml
prove:
  build: build-the-address-plan              # part 1, plain lab
  debug: debug-the-outage                    # part 2, network lab
  more:
    - id: build-the-cloud-link               # part 3, network lab
      versions: [build-the-cloud-link-clinic]
  explain: ...                               # opens once part 1 passes
unstuck:
  example: example-address-plan-print-shop
  steps: [step-size-the-blocks, step-place-and-summarise, step-the-ipv6-plan, step-the-whole-plan]
  versions: [build-the-address-plan-clinic, build-the-address-plan-bakery]
```

**Part 1, `build-the-address-plan`** (60 minutes): as designed and prototyped (the checker passes the reference plan and each of 14 wrong plans fails only its own check, identically under Python 3.14 and Ubuntu's 3.12). Its rules are the CIDR and IPv6 topics' builds' rules, so it brings in nothing new; the cloud facts it uses were re-read (AWS and Azure reserve 5, Google 4; Azure IPv6 subnets exactly /64; Google's `fd20::/20` with a /48 per network; RIPE-690's /48 for businesses and nibble boundaries). The image uses the shared plain `RUN`.

**Part 2, `debug-the-outage`, version 2** (60 minutes): as designed (nine machines; the zone edited without a new serial, a filter on one of two ECMP tunnels, an app firewall that only knows the old network). Version 1 isn't used: its three faults repeat topics 30, 23 and 26's debugs, and a checkpoint's debug is unfamiliar work. Fault 1 shares its symptom (a stale secondary) with topic 30's debug but not its cause or evidence (the same serial and different answers, and "zone is up to date" in ns2's log, against a refused transfer); the primary is unsigned, so unlike topic 30's inline-signed primary it loads the edit. `test_skills` corrections: `both-tunnels` names `csa.net.troubleshooting/locate-on-the-path` and `csa.net.routing/find-the-black-hole` (where topic 26's new ECMP item lives). **Before writing:** a full contract run with the two redesigned checks (`both-tunnels-carry`, the office half of `app2-web-for-the-shop`) and the restart trial.

**Part 3, `build-the-cloud-link`** (60 minutes, in `prove.more`), with fresh version `-clinic`: as designed, with **a VTI** for the tunnel (the base's B1), so the machines and checks follow topic 37's. It retrieves CIDR (the summary), BGP (sessions, filters, local preference), BGP steering (prepending, failover) and IPsec (the sheet, PFS, a private key) in one task weeks after the topics. It overlaps topic 36's build (circuits and a VPN backup) and topic 37's (a tunnel from a sheet), deliberately, in a new story with new numbers, and with the scenery's cloud comparing AS paths so prepending (not communities) is the tool. **Not prototyped end to end:** build it first from the critic's VTI variant of the base's `proto-bgp-over-ipsec` plus a `dx` link and a second session, and time `fails-over` on the CI spike's runner with four labs at once.

**The explain** (20 minutes): as designed.

**Support:** solved sibling, four steps and two fresh versions for part 1 as designed; one fresh version for part 3 (a build part needs one); none for part 2. The map already lists a checkpoint's further parts (`MapPage.tsx` reads `partsPassed`), so the designer's C5 is done.

**Time:** 60 + 60 + 60 + 20 = 200 minutes of work; with three labs' starts and the slower checks, `estimated_minutes: 240`.

## 7. Platform work, in order

| # | What | Smallest version | ADR | Blocks |
| --- | --- | --- | --- | --- |
| P0 | **The network-lab base and shared lab bases** | `content/lab-bases/net/` from the base prototype with section 4.2's changes B1 to B11; the 29-line `tools/labcheck.py` change (build `content/lab-bases/<name>` before a lab whose Dockerfile says `FROM lab-base-<name>`; diff in `prototypes/network-lab-base/labcheck-shared-base.diff`) with tests for `base_of` and `build_base`; the validator checks a named base exists; `cors-verdict`'s case table in `tools/tests/`; `.github/workflows/labs.yml` adds `content/lab-bases/**` to its paths (the branch must hold `main`'s version of the workflow file first); `content/README.md` gains a "network lab" section (sections 2, 7 and 9 of the base brief, section 3.5 and 4.4 of this one, and the Module 3 plain `RUN` line) | **Amendment to ADR-0018** (Proposed): a lab may start from a shared base in `content/lab-bases/<name>/`, which the checker builds first (still built locally from the content folder); a check may cut and restore a link to prove a backup, restoring it before it exits | every Module 3 network lab |
| P1 | **The restart trial in the contract** | opt-in `lab: { restart_trial: true }` (`content_model.LabOptions`); `labcheck test`, after the solution passes, runs `docker restart`, waits for the boot and runs every check again, all of which must pass; about 15 to 20 s a lab | the same amendment | nothing; every Module 3 lab opts in |
| P2 | **A CI spike** | one early pull request with the base and five probe labs under a draft topic: the base's BGP-over-IPsec lab **switched to VTI** (the critic's variant in `prototypes/critic/vti/lab`, with `keyingtries = 0`), topic 23's debug (GRE, PMTU), topic 25's debug (IPv6, radvd), topic 27's worked example (nftables NAT) and a congestion probe (netem, BBR, the 25 Mbit/s threshold three times over). Read in the Labs job: every contract, the timings with four labs at once, which modules loaded, `reset tcp option window`, IPv6 in namespaces. Add the `labs.yml` `modprobe` step only for what fails (section 4.5). Then raise the Labs shards from 4 to 8 | none | IPsec, layers, IPv6, NAT, transport, congestion, troubleshooting, the checkpoint, and the shard count |
| P3 | **Estimate items read dotted quads** | before the general number pattern in `numbers_in()` (`tools/validate_content.py`), match `\b\d{1,3}(?:\.\d{1,3}){3}\b` and add each octet; one test | none (makes ADR-0024's rule see the numbers) | cleaner prompts in CIDR, IPv6 and the checkpoint; nothing waits on it |
| P4 | **The spec change** | section 12's text, then `python -m uv run python tools/outline_cloud_track.py` (creates the outlines for `csa.net.bgp-steering` and `csa.net.certificates`, renames topic 31's) | none | the two new topics' folders |

Decided against, so nobody builds them: a per-lab `network.sh` (the base replaces it); FRR from FRR's own repository; Pebble (its root changes at every start, so it can't pass the restart trial); a downloaded static `curl` with HTTP/3 (not from the archive); a "commit your diagnosis" command for topic 38 (a ritual, not evidence); a headless browser for CORS (`cors-verdict` applies the Fetch standard's rules to real answers); a real-cloud lab anywhere in Module 3.

## 8. Writing waves

Every lab is proved under `labcheck test`, restart trial included, before its lesson is written, and each batch gets a cold review (the writing process Module 2 used). Topics in one wave can be written in parallel; section 3.7 is the contract that lets them use each other's words before those lessons exist.

| Wave | Topics | Waits on |
| --- | --- | --- |
| 0 | P4 (spec), P0, P1, P2, P3 | nothing; P2 waits on P0 |
| 1 | `csa.net.layers`, `csa.net.cidr`, `csa.net.routing`, `csa.net.dns`, `csa.net.http-semantics`, `csa.net.bgp` | the base and a green spike. Layers owns the onboarding note the others' first labs link to; routing owns `sysctl` |
| 2 | `csa.net.ipv6`, `csa.net.nat`, `csa.net.transport`, `csa.net.http-tls`, `csa.net.load-balancing`, `csa.net.bgp-steering` | layers' network-file and `netlab verify` patterns (IPv6); the spike's NAT row (NAT, transport); BGP's dual-homed shop and helpers (steering) |
| 3 | `csa.net.congestion`, `csa.net.certificates`, `csa.net.ipsec` | transport's topology B and fast-clock wording (congestion); HTTP and TLS's `web` machine and nginx patterns (certificates); BGP's FRR patterns and the spike's VTI row (IPsec) |
| 4 | `csa.net.troubleshooting`, `csa.m3.checkpoint` | captures for the casebook from the built layers, NAT, IPsec and load-balancing labs; part 1 reuses CIDR's and IPv6's check code; part 3 waits on IPsec and BGP steering |

## 9. Cost and CI time

**Money: none.** No lab, proof or review touches a cloud account; circuits, VPN gateways, NAT gateways and load balancers are taught from dated documentation and modelled locally (the spec's "stand-ins for what one person can't buy").

**Labs CI.** About 91 labs (sixteen topics of five, the checkpoint's eleven). From the designers' measured and estimated contract times (minutes of container time for a full run): layers 12, CIDR 8, IPv6 13, routing 15, NAT 14, transport 33, congestion 30, DNS 16, HTTP and TLS 10, certificates 15, HTTP semantics 20, load balancing 110, BGP 18, BGP steering 22, IPsec 83, troubleshooting 12, checkpoint 35: about 470 minutes, plus about 30 for the restart trials, so **about 8.3 hours** a full run, on top of today's 130 labs (four shards of about 20 minutes at four labs each, about 5.3 hours). With **eight shards** that is about 26 minutes a shard if balanced; shards go by topic, so watch for one over 30 and move to ten. Load balancing (29 wrong fixes, 20-to-60-second windows) and IPsec (31 wrong fixes, rekeys and maintenance restarts) are the heavy ones: their writers keep every wrong fix to what a check needs and share traffic generators between checks. Public-repository runners are free.

**Image sizes.** The base is about 520 MB on disk (Docker Desktop reports 688 MB), built once per CI shard in under a minute and cached on a learner's machine after the first Module 3 lab; each lab adds kilobytes; topic layers add 63 MB (congestion), about 120 MB (certificates, step-ca included) and a few MB (HTTP semantics).

## 10. Decided for the owner, and for the owner queue

**Decided under the owner's rule** (each goes under _Decided for you_ in `docs/owner-queue.md`, overturnable in a line):

1. **Sixteen topics:** split BGP into `csa.net.bgp` and `csa.net.bgp-steering`, and HTTP and TLS into `csa.net.http-tls` and `csa.net.certificates`. Shorter topics reach proofs and reviews sooner, and the TLS handshake gets proofs of its own; free.
2. Module 3's topics gate on `csa.m1.checkpoint` (directly or through each other), not on Module 2, as the spec's map has it.
3. **One network-lab base** for every network lab, built by `labcheck` from `content/lab-bases/net/` (ADR-0018 amendment, Proposed), with the restart trial run in CI for every Module 3 lab.
4. **The route-based VPN is a VTI,** with strongSwan's extra plugins left out of the base; GRE inside IPsec is the fallback if a runner refuses VTI.
5. **Tools:** Ubuntu's FRR 8.4.4; BIND for authority and Unbound for recursion; HAProxy for load balancing and nginx for web servers; Caddy 2.6.2 for HTTP/3 with ngtcp2's `gtlsclient` and a 40-line aioquic client (Ubuntu's curl has no HTTP/3); certbot with step-ca for ACME. step-ca's and step-cli's `.deb`s come from their GitHub releases, pinned by version and sha256: **the first lab image to download from outside Ubuntu's archive** (recorded in the devlog). `tshark` stays in the base.
6. A machine's lasting kernel settings live in its own `/etc/sysctl.d/`, and its addresses, tunnels and neighbours in its own `/etc/network/up`; only `net.` keys are applied.
7. A check may cut and restore a link to prove a backup route works.
8. Labs run on a fast clock (idle timers, TTLs, BGP timers, certificate lifetimes, prefix limits scaled and said); items use the real numbers.
9. Where a cloud's documented behaviour decides a lab, a router models it, labelled "modelled on" and quoted.
10. **Checkpoint 3 has a third part,** the cloud link (BGP over IPsec with a circuit), in `prove.more`; part 2 is the version whose faults no topic's debug uses.
11. The spec's rows for topics 25, 29 and 38 change wording (Azure translates IPv6 egress anyway; choosing a sender's congestion control; measuring intermittent faults and proving a provider's).
12. The Labs CI job's shards go from 4 to 8 when Module 3's labs land.
13. No real-cloud run in Module 3: every cloud claim is from dated documentation, and Module 11 is where the clouds' own networks are built.
14. Topic 38's "name it before you fix it" is asked in the prompt and graded in the explain, not enforced by a check.
15. CIDR "in code" is bash arithmetic; the spec's Subnetting drill runs as estimate questions.

**For the owner queue's _Open_ list:** nothing. Module 3 spends no money, touches no live service and needs no account.

## 11. Look up again on the day of writing

- **The CI spike's answers** (section 4.5's last column) before any lab that depends on a row.
- **Cloud numbers that move:** AWS NAT gateway prices (the Ohio example) and the regional gateway's limits; Azure NAT Gateway StandardV2 (regions, IPv6, its known issue with load-balancer outbound rules); Cloud NAT's TIME_WAIT default (30 s for gateways created after late September 2026); ALB, NLB, Azure Load Balancer, Application Gateway and Google health-check defaults; Nitro v6's 350-s connection tracking; Direct Connect quotas and BGP timers; ExpressRoute's limits and community rule; Azure VPN Gateway's defaults (ASN 65515, 4,000 prefixes, 60/180 timers, DH group 2 first); AWS's VPN MTU table; HTTP/3 on CloudFront, Front Door, Application Gateway (preview) and Google's load balancers; NLB's QUIC passthrough; Azure's IPv6 limitations (ICMPv6 in NSGs, IPv6-only VMs).
- **Standards and software that move:** cite RFC 9846 for TLS 1.3 (re-read its §1.2 and §2.3; the briefs quote RFC 8446); Let's Encrypt's lifetimes and profiles; the CA/Browser Forum schedule; whether mainline Linux's BBR is still version 1 (`tcp_bbr.c`'s header, the bbr-dev list) and the BBRv3 draft's number; BIND 9.20's `allow-transfer` default (the labs set it explicitly); Ubuntu 24.04's package versions (FRR 8.4.4, strongSwan 5.9.13, BIND 9.18.39, Unbound 1.19.2, nginx 1.24.0, HAProxy 2.8.30, Caddy 2.6.2, ngtcp2-client 0.12.1, python3-aioquic 0.9.25, curl 8.5.0) and step-ca's release checksums.
- **Resources a person must open:** Cloudflare's Learning Center pages (MTU, DNSSEC, TLS handshake, mTLS) refuse automated fetches; the DigitalOcean DNS tutorial renders in the browser; every YouTube video (Ben Eater, Practical Networking, Kurose, Computerphile, NSRC, LearnCantrill) is watched once before it is assigned; the licences of Everything curl, the curl manual and nginx's documentation; Google Cloud pages' CC BY 4.0 footers.
- **Mechanisms nobody has run yet** (each brief lists its own): nftables' `sack-perm`, `timestamp` and `maxseg` rewrites; a TLS 1.1 refusal check; nginx and a client certificate without `clientAuth`; an expired certificate made with `faketime`; certbot's `REQUESTS_CA_BUNDLE` drop-in; HAProxy's reload and `Uptime_sec`; the fast-503 hiccup; ECP-384; topic 30's monitor and `broken.test`; topic 24's debug; topic 38's debug checks; checkpoint part 2's redesigned checks and part 3 end to end; `sipcalc`'s IPv6 output and tcpdump's RS/RA wording (capture before writing items).
- **Dates that will pass:** Azure NSG flow logs retire 2027-09-30; certificate lifetimes drop to 100 days on 2027-03-15; Let's Encrypt's 45-day default from 2028-02-16.

## 12. Replacement text for the spec

All in `docs/specs/cloud-solutions-architect.md`. After the change, run `python -m uv run python tools/outline_cloud_track.py`.

**12.1 The Module 3 section** (from `### Module 3: Networking` to the line before `### Module 4:`) becomes:

```markdown
### Module 3: Networking

Networking and DNS sit under every cloud service, and they're behind many outages and most breaches. This module goes deep. Its labs run in local containers, several machines to a lab, with real routing software (FRRouting), VPN software (strongSwan), DNS servers (BIND and Unbound), web servers and load balancers (nginx, HAProxy, Caddy).

| #   | Topic                               | ID                        | You'll be able to…                                                                                                                                                                                                                      |
| --- | ----------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 23  | Layers and packets                  | `csa.net.layers`          | follow a request down and up the network layers, using the OSI and TCP/IP models as debugging tools; explain ARP and ICMP; explain encapsulation and MTU, and spot MTU problems                                                         |
| 24  | IPv4 and CIDR                       | `csa.net.cidr`            | split and summarize address blocks and check them for overlaps, by hand and in code; do CIDR math on sight; use variable-length masks and the RFC 1918 private ranges                                                                   |
| 25  | IPv6                                | `csa.net.ipv6`            | plan IPv6 addressing; run dual stack; explain why IPv6 egress needs no NAT, and where a cloud translates anyway                                                                                                                         |
| 26  | Routing                             | `csa.net.routing`         | predict the next hop with longest-prefix match; compare static and dynamic routing; spot asymmetric routes and black holes                                                                                                              |
| 27  | NAT                                 | `csa.net.nat`             | explain source and destination NAT; size NAT for connection counts; diagnose port exhaustion; say when to avoid NAT entirely                                                                                                            |
| 28  | TCP and UDP                         | `csa.net.transport`       | read a TCP handshake and teardown in a capture; explain window scaling, timeouts and keepalives, and why idle connections get cut                                                                                                       |
| 29  | Congestion control and QUIC         | `csa.net.congestion`      | explain CUBIC and BBR, and how loss and latency interact; choose and set a sender's congestion control; explain what QUIC and HTTP/3 change, and when they help                                                                         |
| 30  | DNS                                 | `csa.net.dns`             | trace a lookup end to end, from recursion to authority; use record types, TTLs, negative caching and split-horizon DNS; explain DNSSEC; lower TTLs ahead of a move                                                                      |
| 31  | HTTP and TLS                        | `csa.net.http-tls`        | explain what HTTP/1.1, 2 and 3 change; read a TLS 1.2 and 1.3 handshake, including SNI and OCSP stapling; serve several sites on one address with the right protocol versions                                                          |
| 32  | Certificates and mutual TLS         | `csa.net.certificates`    | build and read certificate chains; issue and rotate certificates automatically with ACME; set up mutual TLS                                                                                                                             |
| 33  | HTTP semantics                      | `csa.net.http-semantics`  | use caching headers correctly; explain CORS; choose between REST, WebSockets and gRPC over HTTP/2 for a given flow                                                                                                                      |
| 34  | Load balancing                      | `csa.net.load-balancing`  | choose between layer 4 and layer 7; design health checks, draining and stickiness; explain how a bad health check takes down a fleet, and how failover flapping happens                                                                 |
| 35  | BGP sessions and policy             | `csa.net.bgp`             | bring up BGP sessions and read their state; announce your own prefixes and filter what you send and accept, so you never leak routes or accept a hijack; predict which path BGP chooses and choose your exit with local preference      |
| 36  | Steering traffic and cloud circuits | `csa.net.bgp-steering`    | steer incoming traffic with more-specific prefixes, AS-path prepending, MED and communities; explain route reflection; detect failures fast with BFD; make one circuit primary in both directions on Direct Connect, ExpressRoute and Cloud Interconnect, and plan the backup |
| 37  | VPNs and IPsec                      | `csa.net.ipsec`           | build a route-based IPsec tunnel with BGP over it; debug phase 1 and phase 2 failures                                                                                                                                                   |
| 38  | Network troubleshooting             | `csa.net.troubleshooting` | find a fault from its symptoms with a repeatable method, using captures, traceroute, DNS lookups and logs; measure a fault that comes and goes; prove a fault that's on a provider's side                                               |

**Checkpoint 3: the address plan, the outage and the cloud link** (`csa.m3.checkpoint`).

1. Build an IPv4 and IPv6 address plan for three clouds, four regions in each and two data centres, with room for five years' growth. Code checks it for overlaps, block sizes and summarization.
2. Fix a local network of routers, name servers and an app. It has an intermittent outage caused by three faults.
3. Connect a data centre to a cloud over a private circuit and a backup IPsec VPN with BGP: advertise only the summary, prefer the circuit both ways, and fail over by itself.
```

Keep the table's column padding as the rest of the file has it (re-pad by hand if a formatter disagrees; the topic 36 row is long, as some Module 11 rows are).

**12.2 Renumber every later topic.** Two rows were added, so every topic row after Module 3's table moves up by two (Module 4's first topic, now 37, becomes 39, and so on to the end). From the repository root, in Git Bash:

```bash
awk '/^### Module 4:/ {s = 2} s && /^\| [0-9]+ +\|/ {match($0, /[0-9]+/); n = substr($0, RSTART, RLENGTH) + s; w = RLENGTH; $0 = substr($0, 1, RSTART - 1) sprintf("%-" w "d", n) substr($0, RSTART + RLENGTH)} {print}' docs/specs/cloud-solutions-architect.md > /tmp/spec.md && mv /tmp/spec.md docs/specs/cloud-solutions-architect.md
```

Then check one table by eye: a two-digit number that becomes three digits needs one more space of padding. The designers' briefs name later topics by their old numbers (the IPsec brief's "topic 41 (PKI)", now 43); they are plans, kept as written.

**12.3 The drills table's Subnetting row,** "Runs in" cell: "The browser (Python)" becomes "The browser (estimate questions)", as Module 2's brief asked Module 3 to settle.

**12.4 The Stage 1 opening paragraph** needs no change (it already says Stage 1's practice runs locally).

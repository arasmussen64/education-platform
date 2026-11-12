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

Then check one table by eye: a two-digit number that becomes three digits needs one more space of padding. Text elsewhere that names a later topic by number (Module 2's brief's mention of "topic 41 (PKI)" in the IPsec brief, for instance) is in plans, not the spec, and needs no change.

**12.3 The drills table's Subnetting row,** "Runs in" cell: "The browser (Python)" becomes "The browser (estimate questions)", as Module 2's brief asked Module 3 to settle.

**12.4 The Stage 1 opening paragraph** needs no change (it already says Stage 1's practice runs locally).

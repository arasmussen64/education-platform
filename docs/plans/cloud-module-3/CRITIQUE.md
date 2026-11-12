# Module 3 critique

What the critic found in the seven designers' briefs on 2026-11-11, and what [MODULE-3-BRIEF.md](MODULE-3-BRIEF.md) does about each. Read every brief and `frr-labs-common.md` in full, the prototypes' READMEs, captures and key files, the spec's Module 3 and its rules, `content/README.md`, ADR-0012, ADR-0018 and ADR-0024, Module 1's networking topic, and Module 2's brief. Re-fetched about 75 facts and 25 resources from their sources (section 4), and ran three probes in Docker (section 3).

## 1. Problems across briefs

| # | Problem | What was done |
| --- | --- | --- |
| X1 | **Seven ways to build a network.** The base designer built one engine (`netlab`, machines as namespaces with their own `/etc`, per-machine units); five other designers prototyped their own: the container's main namespace as NAT gateway (NAT), app server (transport), Caddy server and sender (congestion), resolver host (DNS), web server (HTTP and TLS, HTTP semantics), HAProxy (load balancing) and VPN gateway (IPsec); `router NAME` with `/etc/frr/NAME` (routing, NAT, BGP); `cloud-enter`/`on-cloud` (IPsec); `ns@` units under `/var/lib/lab/dns` (DNS); `NetworkNamespacePath=` units (transport, load balancing). | Every network lab moves to the base; the lab machine stays on no lab network; each former main-namespace role becomes a named machine (brief, section 4.3). |
| X2 | **The base had no home for a learner's lasting kernel setting or a machine's own network configuration** (its open question 5, answered "don't invent"), while NAT, transport, congestion and IPv6 need lasting sysctls, and layers, CIDR, IPv6 and IPsec need lasting addresses, tunnels, neighbours and link states. Transport's workaround (`ip netns exec M sysctl --system`) would also apply `/usr/lib/sysctl.d`'s `kernel.*` and `fs.*` keys to Docker's whole machine. | Base changes B2 (per-machine `/etc/sysctl.d/`, `net.` keys only) and B3 (per-machine `/etc/network/up`), plus B4 (`netlab verify`) for "the fix lasts". |
| X3 | **VTI: two designers, opposite results.** The base designer found strongSwan with VTI dropping every packet (`XfrmInTmplMismatch`) and chose GRE inside IPsec; the IPsec designer had VTI working end to end. The checkpoint designer asked the critic to settle it. | The critic reproduced both (section 3) and found the cause: the base's `libstrongswan-extra-plugins` loads the `forecast` plugin. Without it VTI works between two base machines. Decision: VTI, GRE as fallback (B1). |
| X4 | **HTTP/3 taught twice.** Congestion (29) and HTTP and TLS (31) both teach discovery by Alt-Svc, the silent fallback when UDP 443 is blocked, the clouds' HTTP/3 support and the round trip saved; both labs install Caddy and `ngtcp2-client`; both have an item called `mcq-when-h3-helps`; 31's `est-h3-saving` is 29's `est-rtt-saved` with the same 150 ms. | Topic 29 owns QUIC and HTTP/3 in practice; the duplicates leave topic 31 (brief, topic 31). |
| X5 | **Module 2 assumed as a prerequisite.** The transport brief asked for a `csa.m2.checkpoint` gate; the IPv6 brief "builds on `csa.hw.windows-ad`" for DNS, resolver and record; the base brief cites windows-ad for resolver and zone. The spec's map runs Module 1 to Module 3; the outlines' prerequisites are `csa.m1.checkpoint`. | Gate on Module 1; a term-owner table (brief, 3.7) gives every word an earlier Module 3 owner. |
| X6 | **`sysctl` used and never taught.** No Module 1 or 2 file mentions it (searched). NAT says `csa.linux.hardening` taught `/etc/sysctl.d/` (false); transport offered to teach it if routing didn't. | Routing (26) owns it: a paragraph and an item. |
| X7 | **Four designers specified FRR differently.** FRR brief: `frr@NAME` with the package's pathspace unit, a UTS drop-in, `router`, `lab-link`, `looking-glass`, routers without hyphens. Base: its own `frr@M` running FRR inside the machine (hyphens fine, UTS per machine). IPsec: the default `frr.service` in the main namespace. Checkpoint: the base's. | The base's form wins; the FRR brief's helpers (`looking-glass`, `bgp-best`, `holdconns`, `holdserver`, `netlab link`) join the base (B6, B7); the domain-name noise is fixed (B10). |
| X8 | **`tshark` in or out.** Base: keep (six topics read captures). DNS and HTTP: leave it out (147 MB). Layers: once in the worked example, never in checks. | Keep in the base (cached once); learners use it in topic 23; checks don't parse its output. |
| X9 | **radvd or FRR for router advertisements.** Base: FRR sends RAs, radvd not installed. IPv6: radvd, its debug fault is in `radvd.conf`. | radvd joins the base (B5): the IPv6 labs are prototyped with it and its file is the clearer one to teach. |
| X10 | **nginx installed three times.** HTTP and TLS, HTTP semantics and the base each asked for an nginx line; the HTTP semantics brief asked the critic to align them. | nginx is in the base; topic layers carry only what's new. |
| X11 | **Checkpoint fault overlap.** The checkpoint designer replaced version 1's faults when they turned out to repeat topics 23, 26 and 30's debugs. Version 2's name-server fault still shares its symptom with topic 30's debug. | Kept: same symptom, different cause and evidence (an unsigned primary that loaded the edit; "zone is up to date"). The brief says so. |
| X12 | **Checkpoint part 2 rests on ECMP,** which only topic 38 practises (and routing mentions in one paragraph). | A routing recall item on ECMP; `test_skills` point at it. |
| X13 | **Split proposals in two briefs, numbering in a third.** BGP split (365 minutes), HTTP and TLS split (332), and IPsec's brief renumbering itself. | Both splits accepted; one renumbering for the spec (section 12). |
| X14 | **CI cost estimates on different bases.** Load balancing (110 minutes of container time) and IPsec (83) dwarf the others (8 to 33). | Totalled at about 8.3 hours a full run; eight shards recommended; the two heavy topics told to keep wrong fixes to what checks need. |
| X15 | **Plain labs need Python** (CIDR, IPv6, routing, NAT and transport writes, HTTP semantics write, certificate report, IPsec log write, troubleshooting casebook and build, checkpoint part 1) but Module 1's plain line has none; troubleshooting added `gawk`, which would change what `awk` means in its images. | One shared Module 3 plain `RUN`: Module 1's line plus `python3 ipcalc sipcalc openssl curl`, no `gawk`. |
| X16 | **Terms shuffled between topics** (cookie in load balancing or HTTP semantics; datagram in layers or transport; AEAD in IPsec or HTTP and TLS). | Owners fixed in the brief's 3.7. |

## 2. Problems within briefs

### Network-lab base (`network-lab-base.md`)

- **VTI "fails on this kernel"** is the `forecast` plugin, not the kernel (X3). B1.
- **No lasting home for sysctls or machine settings** (X2). B2, B3.
- strongSwan's documentation licence is **CC BY 4.0** (its page footer), not "not stated". Corrected in topic 37's section.
- Open questions decided: restart trial in CI (yes), tshark (keep), FRR 8.4.4 (Ubuntu's), 8 shards (yes), mask the plain units (yes), lasting kernel settings (B2, B3).

### Layers (`csa.net.layers.md`)

- The base's onboarding steps (+10 minutes) weren't counted. 310 minutes.
- `est-mss-from-mtu`'s third mistake has no working. Added.
- The debug prompt's "(the base's location)" points at the files. Reworded (brief, 3.2).
- Cloudflare's MTU page (resource 4) refuses automated fetches; the designer fetched it by sending a browser's user agent. A person confirms it in a browser before it is linked; fallbacks named.

### CIDR (`csa.net.cidr.md`)

- F8 (Google peering refuses overlaps) and F9 (AWS's default VPC 172.31.0.0/16) were unconfirmed. **Both confirmed** by the critic (section 4).
- `est-binary-octet`'s given ("4 of them are ones") is contrived. The octet becomes the given.
- The debug's contract hasn't run. Must run before writing.

### IPv6 (`csa.net.ipv6.md`)

- Leans on `csa.hw.windows-ad` (X5). Defines record and AAAA itself.
- `mcq-azure-ipv6`'s right answer ("VMs reach the IPv6 internet through translated public addresses") claims more than Microsoft's pages say: translation is stated for a StandardV2 NAT gateway and load-balancer outbound rules; the IPv6 overview calls instance-level public IPs "direct". Narrowed.
- Needs radvd, a per-machine sysctl file and a network file from the base (X2, X9).

### Routing (`csa.net.routing.md`) and the shared FRR brief (`frr-labs-common.md`)

- **Recipe R3 would pass a hand-made route.** It rejects routes whose `protocol` is `boot`, but `ip -j route` without `-d` leaves `protocol` out for such a route (the critic's probe). Checks use `ip -d -j route`.
- **Debug fault 2's evidence is wrong.** A static default via a missing next hop on a connected subnet is installed by FRR (it resolves through the connected route; the critic's probe showed it resolved, not inactive). The learner will see a `FAILED` neighbour, not a missing route. Corrected; the lesson gains the row.
- `est-loop-crossings-ttl128` ("crossings of any loop link") is ambiguous. Reworded.
- Owns `sysctl` (X6) and gains an ECMP item (X12).

### NAT (`csa.net.nat.md`)

- **The debug's faults can't all show.** A masquerade rule without `oifname` also translates the office's outgoing traffic, so the office's stale-prefix rule (fault 3) never matters. Fault 2 becomes `iifname "wan" masquerade`; the writer re-runs the three together.
- "`csa.linux.hardening`: forwarding in `/etc/sysctl.d/`" is false (X6).
- Gateway in the main namespace (X1). Machine `gw`.

### Transport (`csa.net.transport.md`)

- `csa.m2.checkpoint` gate (X5); `sysctl --system` in a namespace (X2); `systemd-sysctl --cat-config` checks read global files too. Replaced by `sysctl_saved`.
- `write-syn-check` relies on three untried nftables rewrites. Try first.
- Strong otherwise: the only brief (with congestion) that measured its multiple-choice lengths.

### Congestion (`csa.net.congestion.md`)

- HTTP/3 overlap (X4): kept here.
- Main-namespace server (X1). Machine `shop` with `caddy@shop`.
- Throughput thresholds unproven on a runner. In the CI spike.

### DNS (`csa.net.dns.md`)

- `est-forgot-to-lower`: "fetched it at 08:59" makes the exact answer 3.98, not 4. Reworded.
- 318 minutes (323 with the recommended step 8). Step 8 added, three items to review-only: 315.
- Build and debug not built end to end. Must run first.
- The DigitalOcean main resource renders in the browser (the critic's fetch saw only navigation); Cloudflare's DNSSEC page refuses automated fetches. A person confirms both.

### HTTP and TLS (`csa.net.http-tls.md`)

- HTTP/3 duplicated (X4). Removed.
- **Split accepted,** but the designer's split left the protocol half with only two skills (house rules ask 3 to 6) and no proofs. The brief adds `tls-server-config`, a new fill-in, write, build and debug for `csa.net.http-tls`, all designed but not prototyped (mechanisms the designer tried).
- Untried: the TLS 1.1 refusal check, `clientAuth` rejection, `faketime`, the certbot drop-in. Try first.
- certbot's timer and deploy hook would run in the wrong namespace on the base. `certbot@web` units and `systemctl reload nginx@web`.
- Cloudflare's main resource refuses automated fetches; fallback named.

### HTTP semantics (`csa.net.http-semantics.md`)

- 331 minutes; trimmed to 315 with the designer's own reading cut.
- `est-ping-interval` repeats transport's `est-smallest-idle` idea. Kept as a deliberate retrieval in a new story.
- `cors-verdict` placement left open. In the base's check library with its own tests.

### Load balancing (`csa.net.load-balancing.md`)

- Google's "all backends unhealthy" behaviour for passthrough Network Load Balancers is more nuanced on the page than the brief's fact 9 (a failover policy may drop all traffic; the global type fails over to another region). Worded from the page.
- Untried pieces (fast-503 hiccup, stock-sync, which uptime resets at a reload). Try first.
- 337 minutes trimmed to 315 by the designer's own cuts; the heaviest CI topic (X14).

### BGP and BGP steering (`csa.net.bgp.md`, `csa.net.bgp-steering.md`)

- Sound; facts sampled all held. Adapted to the base's tools (X7). Split accepted.

### IPsec (`csa.net.ipsec.md`)

- VTI confirmed (X3). The gateway becomes machine `vpn`; `vti0` lasts in its network file, so the fill-in's gaps and the build's boot check move there.
- Restart needs `keyingtries = 0` (the critic's VTI restart trial failed without it, as the designer's first did).
- 18 multiple-choice items: watch the length rules. ECP-384 untried.

### Troubleshooting (`csa.net.troubleshooting.md`)

- Faults checked against the final briefs (its open question 1): no clash. The worked example's fault resembles routing's debug fault 3; acceptable for practice, said in the prompt.
- `gawk` in its plain line (X15). Removed.
- Debug checks never run. Must run first.

### Checkpoint (`csa.m3.checkpoint.md`)

- Part 3 designed for GRE or VTI "as the critic decides". VTI.
- Part 2's redesigned checks not contract-run; part 3 not prototyped; version 2 not restart-tried. All before writing.
- `both-tunnels`' `test_skills` named a BGP skill for an ECMP behaviour. Repointed.
- C5 (the map lists further parts) is already done (`MapPage.tsx` reads `partsPassed`).

## 3. What the critic ran (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, 2026-11-11)

1. **The IPsec designer's VTI prototype**, rebuilt and its solution applied: the office downloaded the 303,030-byte report through the tunnel; `XfrmInTmplMismatch` 0.
2. **The base's BGP-over-IPsec lab switched to VTI** (`prototypes/critic/vti/lab`): SAs up, no traffic, `XfrmInTmplMismatch` rising (the base designer's result). `swanctl --stats` showed the base's charon loading `forecast`, `farp`, `connmark` and others from the extra plugin packages. With `forecast` set to `load = no`: ping 3/3, BGP Established over the VTI, the route learned by BGP on `vti0`. After `docker restart` the tunnel didn't return by itself (`keyingtries` default 1 and both charons starting together); `swanctl --initiate` brought it up at once. Written up in `prototypes/critic/vti/RESULT.md`.
3. **A route probe** in a throwaway container from the base image: a route added with `ip route add` has no `protocol` in `ip -j route` and `"protocol":"boot"` in `ip -d -j route`; FRR's static default via an on-link address nobody holds showed as resolved through the interface.

Containers `m3critic-vti`, `m3critic-lbipsec`, `m3critic-probe` and images `m3critic-vti`, `m3critic-lbipsec`, `m3critic-netbase` were removed; no prune; nothing else touched. Loaded kernel modules stay until Docker Desktop restarts.

## 4. Facts re-fetched (all 2026-11-11)

Each held as the brief states unless the last column says otherwise.

| Brief | Claims checked | Source | Result |
| --- | --- | --- | --- |
| Base | FRR `ebgp-requires-policy` default; nginx active checks commercial; AWS inside `/30` from 169.254.0.0/16 and default `0.0.0.0/0` selectors; strongSwan's VTI instructions; Unbound's cache defaults | FRR 8.4 BGP page; nginx hc module; AWS "Get started with Site-to-Site VPN"; strongSwan route-based VPN; unbound.conf | held; strongSwan's docs are CC BY 4.0, not "not stated" |
| Layers | AWS 9001 and the 1500/8500 limits and type 3 code 4; Google 1460, 1300 to 8896, no fragmentation, MSS clamping outside only; Azure blocks GRE; Google supports GRE v0, not on Cloud NAT or Application LBs | AWS EC2 MTU; Google VPC MTU; Azure VNet FAQ; Google VPC overview | held |
| CIDR | AWS /16 to /28, the five reserved, canonical form; Google's four reserved, /29, /4 with /8 advice; Azure's five, /29 to /2; **F8** Google peering; **F9** AWS default VPC | AWS subnet sizing; Google subnets; Azure FAQ; Google VPC peering; AWS default VPC components | held; F8 and F9 now confirmed |
| IPv6 | Azure /64 only, no IPv6-only VMs, no ICMPv6 in NSGs, Azure Firewall no IPv6; StandardV2 IPv6 and NAT64; egress-only gateway IPv6 only, stateful, free; Google /96 per interface and `fd20::/20` | Azure IPv6 overview; Azure NAT overview; AWS egress-only gateway; Google subnets | held; "translated" not stated for instance-level IPs (narrowed) |
| Routing | FRR distances and 255; AWS priority order; Azure UDR order and the VNet-route exception; Azure "None" for 100.64.0.0/10; Google's order and ECMP within categories | FRR 8.4 zebra; AWS route priority; Azure UDR overview; Google routes | held |
| NAT | 55,000 per address per unique destination, 8 addresses, ports 1024 to 65535; regional 32 per zone; Google 64,512, defaults 64/32, 1,008 VMs; Ohio $0.045 and gateway endpoints free; Azure TCP idle 4 min, UDP 4 min fixed, UDP hold-down 65 s | AWS NAT basics; AWS regional NAT; Google ports and addresses; AWS VPC pricing; Azure NAT overview | held |
| Transport | `tcp_syn_retries` 131 s; keepalive 2 h, 9, 75 s; 924.6 s; NLB 350 s, TLS fixed, Nitro v6 350 s; Cloud NAT 30/30/1,200/30 and 30-or-120 TIME_WAIT | kernel ip-sysctl; NLB idle timeout; Cloud NAT tuning | held |
| Congestion | BBR header (loss sentence, 10 round trips, 10 s, four states, internal pacing, no version); BBRv3 draft-07 of 2 November 2026, Experimental; RFC 9438's 0.7, 0.4, three stacks; nginx QUIC since 1.25.0; HTTP/3 explained CC BY 4.0 | `tcp_bbr.c`; datatracker; RFC 9438; nginx QUIC; the repository's LICENSE | held |
| DNS | Route 53 private-zone NXDOMAIN and Resolver-rule precedence; Slack (2021-09-30, 24 h, under 1%, DS cached 24 h); Unbound `cache-max-ttl` 86,400, `cache-max-negative-ttl` 3,600, `infra-host-ttl` 900, `rrset-roundrobin` yes | AWS private hosted zones; Slack Engineering; unbound.conf | held |
| HTTP and TLS | RFC 9846 (TLS 1.3, July 2026, obsoleting 8446 and 5246 among others); RFC 9849 (ECH, March 2026); Let's Encrypt's OCSP dates and reason; the CA/B schedule (the ballot page confirms 398 to 47 days, March 2026 to March 2029; the 200/100 steps from BR v2.3.1 as the designer read it) | rfc-editor JSON; Let's Encrypt; CA/B Forum | held |
| HTTP semantics | MDN caching's sections and `no-cache`; Max-Age 5 s, 86,400, 7,200 since v76; RFC 9111's `no-cache`, `private`, 10%; nginx WebSocket hop-by-hop, "before version 1.29.7", 60 s; gRPC's four kinds and deadlines | MDN; RFC 9111; nginx; grpc.io | held |
| Load balancing | ALB 30/5/5/2 and fail-open; Google 5/5/2/2, 503 (classic 502); passthrough NLB behaviour; Yanacek's sentence; HAProxy's two kinds of balancer; nginx active checks commercial | AWS ALB health checks; Google health checks; builder.aws.com; HAProxy intro; nginx | held; passthrough behaviour more nuanced than fact 9 |
| IPsec | AWS MTU/MSS table; VGW default ASN 64512, fixed; strongSwan XFRM since 5.8.0 and kernel 4.19, VTI instructions; inside `/30`; AWS route priority and no ECMP on a VGW | AWS customer gateway best practices; AWS "How Site-to-Site VPN works"; strongSwan; AWS VPN route priority | held |
| BGP | `ebgp-requires-policy` defaults; MED "received from the same AS"; import check from 7.4; private ASN ranges | FRR 8.4 BGP; AWS Direct Connect | held |
| BGP steering | `7224:7100/7200/7300` before AS_PATH; associated-Region medium preference; MED "not recommended"; 100 routes per private VIF (to 1,000), session idle, 1,000 on public; hold 90, keepalive 30, BFD 300 × 3, graceful restart not with BFD | AWS Direct Connect routing; quotas; BGP settings | held |
| Troubleshooting | SRE chapter CC BY-NC-ND 4.0 and its sections; Gregg's anti-methods and "What has changed recently?", no licence; Akamai's rate-limiting sentence, the 10% line and both directions; `icmp_ratelimit` 1000 | sre.google; brendangregg.com; Akamai; kernel ip-sysctl | held |
| Checkpoint | RIPE-690's /48 and /56 and nibble boundaries; AWS VGW route priority, AS path then MED, no ECMP on a VGW; reserved addresses; Google `fd20::/20`; Unbound `infra-host-ttl` 900 | RIPE; AWS VPN route priority; AWS, Azure, Google subnet pages; unbound.conf | held; AWS advises against AS-path prepending for devices that support asymmetric routing (consistent with IPsec's MED item) |

Could not be checked by the critic: the curl manual's exit codes (the page is longer than the fetch reached), RFC 9293 §3.8.4 (same), anything on Microsoft's ExpressRoute and VPN FAQ pages beyond what other briefs cross-confirm.

## 5. Resources re-opened

Opened and matching the briefs: Beej ch. 4 and ch. 17; AWS, Google and Azure MTU, subnet and routing pages; the Systems Approach's 3.3.4 and 3.3.5; APNIC's Neighbor Discovery post (2019-10-18, about 1,000 words, no licence stated); HPBN ch. 2 (CC BY-NC-ND 4.0); Cloudflare's "When TCP sockets refuse to die" (2019-09-20, about 3,000 words); Julia Evans' DNS post; MDN caching; grpc.io core concepts; nginx WebSocket proxying; the HAProxy Starter Guide; Yanacek's article; strongSwan's route-based VPN page; the SRE chapter; Gregg's methodology page; Akamai's MTR guide; HTTP/3 explained's licence.

Could not be opened by the critic's tools: **Cloudflare's Learning Center pages** (TLS handshake, MTU, DNSSEC, mTLS) answer HTTP 403 to automated fetches; the designers fetched them by sending a browser's user agent, which the critic declined to do. **DigitalOcean's DNS tutorial** returned only its navigation. YouTube videos were not watched by anyone. Each is marked "a person confirms it in a browser" in the brief, with a fallback where it is a main resource.

## 6. Prerequisite and term checks

Every "builds on" row was checked against the topic it names. Module 1's networking lesson teaches `ip`, `ss`, `dig` (A, CNAME, TTL), `curl`, `nc`, `traceroute`, `tcpdump` and the handshake flags, nftables hooks and `ct state`, conntrack, namespaces and veth pairs, and names NAT, DNAT and the ARP table: the layers, routing, NAT and transport briefs' claims hold. The umask item CIDR builds on (`$((0666 & ~0022))`, `csa.linux.permissions/perm-umask`) exists. Wrong: Module 2 as a source of DNS words (X5) and Module 1 as a source of `sysctl` (X6). Cross-Module-3 assumptions ("`csa.net.layers` defines TTL and ICMP", "`csa.net.transport` defines MSS", "`csa.net.http-tls` defines forward secrecy", "`csa.net.ipv6` names the egress-only gateway") were each confirmed in the briefs named, and fixed as owners in the brief's 3.7.

## 7. Still unverified

- **Everything on a GitHub runner** (P2's spike): modules on demand (`ip_gre`, `esp4`, `ip_vti`, `xfrm_user`, `sch_netem`, `tcp_bbr`, NAT), IPv6 in namespaces, `reset tcp option window`, throughput thresholds with four labs at once, and timings.
- **VTI after a restart in the base** with `keyingtries = 0` and the cloud ordered first (the fix is the IPsec designer's and is expected to work; the critic only re-initiated by hand).
- Labs whose contracts never ran: CIDR's debug, DNS's build and debug, HTTP and TLS's new build and debug, certificates' build and debug, troubleshooting's debug, checkpoint part 2's redesigned checks and restart trial, checkpoint part 3, and every lab not marked "prototyped" in its brief.
- Cloudflare's Learning Center pages, the DigitalOcean tutorial and every video (section 5).
- The CI time totals are the designers' estimates added up, not measurements.

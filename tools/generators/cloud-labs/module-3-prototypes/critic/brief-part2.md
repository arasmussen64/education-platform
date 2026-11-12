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


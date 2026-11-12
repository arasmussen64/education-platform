# Writing brief: `csa.net.ipsec` (topic 35), VPNs and IPsec

Design only. Nothing here is in the repository. Sources were read on 2026-11-11, each with its date below. Lab mechanics marked **tried** were run in Docker on the owner's PC (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, cgroup v2) on 2026-11-11; the prototype, its exact commands, timings and every captured log are in `prototypes/lb-ipsec/README.md` and `prototypes/lb-ipsec/ipsec/` beside this file, and everything started was removed.

**The answer to "does IPsec work in a lab container at all?"** Yes, on Docker Desktop, tried end to end: strongSwan 5.9.13 (swanctl, charon-systemd) negotiates IKEv2 between the lab machine and a "cloud" network namespace, the kernel carries ESP (AES-GCM), and FRR 8.4.4 runs BGP over the tunnel; the office reaches the cloud's app through it, and it all survives `docker restart`. One limit decides the design: **Docker Desktop's kernel has no XFRM interfaces** (`CONFIG_XFRM_INTERFACE` is not set; `ip link add ... type xfrm` answers `Unknown device type`), so the route-based tunnel is a **VTI** (`ip link add vti0 type vti ... key 42`, matched by `mark_in`/`mark_out` in swanctl), which works; strongSwan's own documentation calls XFRM interfaces the better choice on kernels from 4.19, and the lesson says so and says why the lab doesn't use them. GitHub's `ubuntu-24.04` runner (kernel 7.0.0-1017-azure) ships `esp4`, `ip_vti`, `xfrm_user` and `xfrm_interface` in its standard module package (the file list, read 2026-11-11); whether a privileged container there loads them on demand, as Docker Desktop does, has not been run. Section 10 has the CI test, the smallest workaround and the honest fallback, and what each proves.

## 1. What the learner will be able to do

1. Say what IKE and ESP each do, what phase 1 (the IKE SA) and phase 2 (the CHILD SA, the IPsec SA) agree, and what crosses the wire: UDP 500, UDP 4500, ESP as IP protocol 50, the inside addresses hidden.
2. Build a route-based IPsec tunnel with strongSwan from a provider's configuration sheet: a VTI, `0.0.0.0/0` traffic selectors, strong proposals with perfect forward secrecy, the pre-shared key kept private; and run BGP over it with FRR, sending only the office's prefix and accepting only the cloud's.
3. Make it last: it comes back after a reboot and after the provider restarts its end for maintenance.
4. Debug a tunnel from the logs of both ends: tell a phase 1 proposal mismatch from a wrong pre-shared key or identity, a phase 2 proposal or traffic-selector mismatch, a peer that never answers, and a rekey that fails an hour in; and find the tunnel MTU problem behind "small pages load, big downloads hang", then fix it with MSS clamping in both directions.
5. Say how AWS, Azure and Google Cloud's VPNs differ in the things that bite: tunnels per connection and maintenance, default proposals, BGP numbers and limits, MTU and MSS.

**The six-month core:**

- IKE (UDP 500, then 4500) agrees keys; ESP (protocol 50) carries the traffic. Phase 1 builds the IKE SA; phase 2 builds the CHILD SA. A firewall in front of a VPN gateway allows UDP 500, UDP 4500 and ESP.
- Route-based: `0.0.0.0/0` selectors, a tunnel interface, routing (best, BGP) decides what goes in. Policy-based: the selectors decide. Narrow selectors on a route-based tunnel leave BGP's own addresses out, so the tunnel is "up" and nothing works.
- Read the error, then read the other end's log: `NO_PROPOSAL_CHOSEN` in IKE_SA_INIT is phase 1, in a CHILD_SA exchange phase 2; `AUTHENTICATION_FAILED` is the PSK or the identity, and only the responder can say which; `TS_UNACCEPTABLE` is selectors; retransmits with no reply is the path; "rekeying failed" an hour in is the PFS group.
- ESP costs about 50 to 60 bytes a packet; when ICMP is blocked, big TCP segments vanish. Clamp the MSS on the tunnel interface, both directions: largest TCP payload = link MTU − ESP overhead − 40.
- A provider restarts its end; your end must start again (`close_action`, `keyingtries = 0`, DPD), and AWS gives you two tunnels for exactly this.

## 2. Prerequisites and terms

**`prerequisites:`** `[csa.net.layers, csa.net.nat, csa.net.http-tls, csa.net.bgp]`. The Module 3 rows below are what this brief **assumes** those topics teach (they're being designed at the same time); the critic should check them.

| Topic | What this topic uses from it |
| --- | --- |
| `csa.linux.net-tools` | `ip addr`, `ip route`, `tcpdump` with filters, nftables in `/etc/nftables.conf`, network namespaces and veths, `from-office`. |
| `csa.linux.services`, `csa.linux.permissions` | Writing and enabling a unit (a oneshot that makes `vti0`), `journalctl -u`, file modes (the PSK file must not be world-readable). |
| `csa.linux.scripting` | The write lab's script: arguments, `grep`, `case` or `if`, exit codes. |
| `csa.net.layers` (assumed) | Encapsulation, MTU, DF and "fragmentation needed", the path-MTU black hole. This topic applies them to ESP. |
| `csa.net.transport` (through `bgp`; checked against `csa.net.transport.md`) | The TCP handshake; MSS, which that brief defines ("the largest payload this side will accept in one segment ... the link's MTU minus 40 bytes") and reads in the SYN's options. |
| `csa.net.nat` (assumed) | Source NAT and why a NAT breaks a protocol with no ports (ESP), the motive for NAT traversal on UDP 4500. |
| `csa.net.http-tls` (checked against `csa.net.http-tls.md`) | That brief defines symmetric against public-key encryption (a paragraph), key exchange (ECDHE) and forward secrecy (a sentence each), cipher suite and handshake. This topic builds on them: Diffie-Hellman by its IKE "group" numbers, PFS for rekeyed CHILD SAs, and AES-GCM as encryption with integrity in one (define "AEAD" here if 31 doesn't). Module 4's cryptography topic (40) comes later; nothing here may lean on it. |
| `csa.net.bgp` (checked against `csa.net.bgp.md` and `frr-labs-common.md` in this folder, 2026-11-11) | FRR 8.4 (Ubuntu's): `vtysh`, `frr.conf`, `write memory`; `router bgp`, `neighbor ... remote-as`, `network` and its import check, prefix lists with `le`, route maps in and out, RFC 8212 and FRR's `bgp ebgp-requires-policy` (`(Policy)` in `show bgp summary`), keepalive and hold timers, local preference and "MED only between paths from one neighbour AS" (its `best-path` skill), `ip route show proto bgp`. The BGP designer proposes splitting topic 34 into `csa.net.bgp` and `csa.net.bgp-steering` (MED steering, communities, BFD, cloud circuits); if that happens this topic becomes 36 and still needs only `csa.net.bgp`: its one MED item (`mcq-two-tunnels-med`) rests on the decision order `csa.net.bgp` teaches. |

**Terms this topic must define itself:** VPN (site-to-site, against remote access in one sentence); IPsec; IKE and IKEv2; ESP (and AH in one clause: integrity only, rarely used, doesn't survive NAT); security association (SA), SPI; IKE SA (phase 1) and CHILD SA (phase 2, "IPsec SA" in the clouds' words; IKEv1's main and quick mode in one sentence, because Azure's page still uses them); the four exchanges by name (IKE_SA_INIT, IKE_AUTH, CREATE_CHILD_SA, INFORMATIONAL); proposal (an encryption, an integrity or PRF algorithm and a DH group); DH group by its numbers (group 2 MODP 1024, 14 MODP 2048, 20 ECP 384) and perfect forward secrecy (PFS); pre-shared key (PSK) and identity (ID); traffic selectors; tunnel and transport mode; policy-based and route-based VPN; VTI, mark, XFRM interface (by name); lifetime, rekey; dead peer detection (DPD); NAT traversal and MOBIKE (why IKE moves to port 4500 even without NAT, which every learner will see in the lab); MSS clamping; the inside tunnel addresses (169.254.0.0/16, link-local; Azure calls them APIPA); customer gateway, virtual private gateway and transit gateway (AWS), VPN gateway and local network gateway (Azure), HA VPN gateway and Cloud Router (Google).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `ipsec-building-blocks` | IKE and ESP and what each carries; phase 1 and phase 2; SAs and SPIs; proposals, DH groups and PFS (and why a PFS group isn't negotiated with the first CHILD SA); PSK and identities; lifetimes and rekeying; UDP 500, UDP 4500, protocol 50; NAT-T and MOBIKE; reading `swanctl --list-sas` |
| `route-based-tunnel` | Policy-based against route-based; the VTI and its key and marks (XFRM interfaces by name); `0.0.0.0/0` selectors and why `charon.install_routes = no`; the inside /30 and link-local addresses; building it with swanctl and making it last a reboot and a provider restart |
| `bgp-over-tunnel` | BGP between the inside addresses; what to send and what to accept (prefix filters in and out); learning routes rather than typing them; two tunnels, MED and local preference during a provider's maintenance; each cloud's ASN, timers and prefix limits |
| `read-ike-logs` | Phase 1 and phase 2 failures from strongSwan's log on each end: proposal mismatches, PSK against identity, traffic selectors (unacceptable or narrowed), no answer, rekey failure; which end's log can tell you what |
| `tunnel-mtu` | ESP's overhead and the inner MTU, MSS from MTU, what NAT-T adds, the black hole when ICMP is blocked, MSS clamping in both directions on the tunnel interface, each cloud's MTU and MSS numbers |

Five skills; each has at least four questions that can come back (section 9). `tunnel-mtu` is the calculation skill and has five estimate items.

## 4. Lesson plan

**4.1 Why a VPN** (strongSwan, "Introduction to strongSwan", the sections "Securing a Network" and "IKE and IPsec Basics"). Supply the picture the labs use: the office (192.168.10.0/24) behind the lab machine, the lab's outside address 198.51.100.10, "the internet" in between, the cloud's VPN gateway at 203.0.113.10 and its network 10.20.0.0/16 behind it. A site-to-site VPN makes the two private networks reach each other across the internet as if wired, encrypted. In the cloud this is the cheap, quick connection; the dedicated circuits (Direct Connect, ExpressRoute, Cloud Interconnect) are topic 34's and Module 11's, and the spec's "stand-in for what one person can't buy" is exactly a VPN with BGP.

**4.2 The two protocols and the two phases** (strongSwan, "IPsec Protocol": ESP, tunnel mode, the packet structure, the IKEv2 exchanges, NAT traversal). The lesson draws in words the one picture every later step needs:

- IKE talks first, on UDP 500. IKE_SA_INIT agrees the IKE proposal and does a Diffie-Hellman exchange (phase 1 begins); IKE_AUTH proves who each end is (PSK or certificate) and, in the same exchange, creates the first CHILD SA (phase 2). CREATE_CHILD_SA makes more CHILD SAs and rekeys them later; INFORMATIONAL carries deletes and DPD.
- ESP then carries the office's packets, each wrapped in a new IP header between the two outside addresses, protocol 50, numbered with an SPI. On the wire you see only ESP between 198.51.100.10 and 203.0.113.10 (**tried**: `tcpdump -nn -i eth1 esp`).
- IKE moves to UDP 4500 in IKE_AUTH. With a NAT in the way that's NAT traversal (ESP is then wrapped in UDP 4500 too); without one, strongSwan still moves, because RFC 4555 (MOBIKE) says implementations that support it and NAT traversal MUST change to 4500 "even if no NAT was detected". The lab shows `[4500]` with no NAT; without this sentence the learner will think something is wrong.
- A firewall in front of a VPN gateway therefore allows UDP 500, UDP 4500 and ESP.

**4.3 Proposals, keys and lifetimes** (strongSwan "Introduction", "Authentication Basics"; swanctl.conf reference, `esp_proposals`). A proposal is a set: encryption, integrity (or AEAD such as AES-GCM, which does both), PRF, DH group. Both ends must share one; the provider usually accepts several and **which one you get depends on what you propose** (AWS: its endpoints "evaluate proposals ... starting with the lowest configured value"; Azure's default route-based IKE policy starts with DH group 2, 1,024-bit). PFS: a DH group in the ESP proposal gives each rekeyed CHILD SA fresh keys. The lesson supplies the gotcha the swanctl reference states and the prototype showed: the first CHILD SA takes its keys from IKE_AUTH and negotiates no DH group, so a PFS mismatch establishes and fails at the first rekey (strongSwan's default: rekey after an hour, hard expiry 10% later, so the tunnel dies at about 66 minutes). PSK and identity: each end sends an ID (here its outside address) and the responder looks up the matching configuration and secret.

**4.4 Policy-based and route-based** (strongSwan "Introduction", "Routing"; "Route-based VPN", the VTI section and the first paragraph on XFRM interfaces). Policy-based: the traffic selectors say what is encrypted. Route-based: selectors `0.0.0.0/0` both ways and a tunnel interface; whatever is *routed* into `vti0` is encrypted, and routing decides, so BGP can decide. The VTI: `ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42`, the `mark_in`/`mark_out` of 42 in swanctl, `net.ipv4.conf.vti0.disable_policy=1`, and `charon.install_routes = no` (strongSwan's page: route installation "must be disabled"), which the lab ships as scenery. XFRM interfaces: the better mechanism on newer kernels; not in the lab because Docker Desktop's kernel lacks them. The inside addresses: AWS gives each tunnel a /30 from 169.254.0.0/16 (the customer end .2, AWS .1); Azure's custom APIPA BGP addresses come from 169.254.21.0 to 169.254.22.255; link-local addresses are never routed beyond a link, so they can't clash with anyone's networks.

**Where the clouds differ (4.3 and 4.4):** a table the lesson must build, because no single page does:

| | AWS Site-to-Site VPN | Azure VPN Gateway | Google Cloud HA VPN |
| --- | --- | --- | --- |
| Tunnels | two per connection, each in its own zone; configure both | several connections in active-active, failing over by BGP (the BGP overview's diagram); the details of active-active gateways weren't read for this brief | two interfaces; a single-interface setup has no SLA; configure two tunnels |
| Who starts IKE | your device, unless "startup action: start" (IKEv2 only) | the gateway has offer lists "as initiator" and "as responder", so either end | not checked for this brief |
| Default proposals | many accepted; restrict them with `modify-vpn-connection-options` | route-based default: DH group 2, AES256/SHA1 first; set a custom IPsec/IKE policy | IKEv1 and IKEv2 ciphers listed on its page |
| BGP | Amazon-side ASN 64512 by default; inside /30 from 169.254.0.0/16 | default ASN 65515 (65515, 65517 to 65520 reserved); keepalive 60 s, hold 180 s, fixed; up to 4,000 prefixes, more drops the session | dynamic routing only (BGP via Cloud Router), link-local addresses |
| MTU and MSS | tunnel MTU 1446, MSS 1406 for AES-GCM without NAT-T (AWS's table by algorithm) | the gateway clamps MSS in both directions, 1,360 bytes over the internet (IPv4) | gateway MTU 1460; prefragment on your side; payload MTU 1406 for AEAD ciphers (IPv4) |
| Maintenance | one tunnel at a time; AWS lowers the MED on the other tunnel; keep your weights and local preference equal | — | — |

**4.5 BGP over the tunnel** (topic 34's material, applied; AWS "Routing during VPN tunnel endpoint updates"). BGP runs between the inside addresses, so the CHILD SA's selectors must include them (they do with `0.0.0.0/0`). Send only the office's prefix (`network 192.168.10.0/24` with a route-map out); accept only what you expect (a route-map in that refuses a default route and anything outside the cloud's space): a cloud that sends you `0.0.0.0/0` would otherwise take the office's internet traffic into the tunnel. Learn routes; don't type static ones. With two tunnels, BGP moves the traffic when one goes down, and AWS steers with MED during its maintenance.

**4.6 Making it last** (swanctl.conf reference: `start_action`, `close_action`, `dpd_action`, `keyingtries`; AWS "tunnel initiation options"). Three things go wrong after the tunnel first works, all three seen in the prototype: at a reboot, `vti0` isn't there unless something makes it (a oneshot unit); when the provider restarts its end it sends a delete, and without `close_action = start` your end never starts again (**tried**: not back within 45 s; with it, back in 4 to 6 s); and at boot, if the first attempt meets a peer that isn't ready, `keyingtries = 1` (the default) gives up (strongSwan retries with `keyingtries = 0`, though not after a "permanent" error such as `NO_PROPOSAL_CHOSEN`). AWS's own side retries forever only if you set its startup action to start, and by default your device must bring the tunnel up.

**4.7 Reading the logs** (the lab's own captured logs; this is the lesson's biggest original contribution, because no free resource lays the failures side by side). A table of each failure, what the initiator (lab) logs and what the responder (cloud) logs, from the prototype's captures:

| Failure | Lab (initiator) | Cloud (responder) |
| --- | --- | --- |
| IKE proposal mismatch (phase 1) | `parsed IKE_SA_INIT response 0 [ N(NO_PROP) ]`, `received NO_PROPOSAL_CHOSEN notify error` | `received proposals: IKE:AES_CBC_128/HMAC_SHA1_96/PRF_HMAC_SHA1/MODP_1024`, `configured proposals: ...`, `received proposals unacceptable` |
| Wrong PSK (phase 1, IKE_AUTH) | `parsed IKE_AUTH response 1 [ N(AUTH_FAILED) ]`, `received AUTHENTICATION_FAILED notify error` | `tried 1 shared key for '203.0.113.10' - '198.51.100.10', but MAC mismatched` |
| Wrong identity (phase 1, IKE_AUTH) | the same two lines as a wrong PSK | `looking for peer configs matching ...198.51.100.10[branch.shop.test]`, `no matching peer config found` |
| ESP proposal mismatch (phase 2) | `IKE_SA cloud[7] established ...`, then `received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built` | `received proposals: ESP:AES_CBC_256/HMAC_SHA1_96/NO_EXT_SEQ`, `no acceptable proposal found` |
| Selectors the peer won't accept (phase 2) | `received TS_UNACCEPTABLE notify, no CHILD_SA built` | `traffic selectors 10.20.0.0/16 === 192.168.20.0/24 unacceptable` |
| Selectors narrowed on a route-based tunnel | `CHILD_SA cloud-vti{13} established ... TS 192.168.10.0/24 === 10.20.0.0/16`; then BGP stays `Active` | `CHILD_SA branch-vti{9} established ... TS 10.20.0.0/16 === 192.168.10.0/24` |
| No answer (UDP 4500 dropped on the path) | `sending packet: from 198.51.100.10[4500] ...`, `retransmit 1 of request with message ID 1`, 2, 3 ... | nothing after IKE_SA_INIT |
| PFS group mismatch | established at first; at the rekey `received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built`, `CHILD_SA rekeying failed, trying again in 14 seconds` | `received proposals: ESP:AES_GCM_16_256/NO_EXT_SEQ`, `configured proposals: ESP:AES_GCM_16_256/MODP_2048/NO_EXT_SEQ, ...` |

The rules to take away: the notify's name and the exchange it came in say the phase; a wrong PSK and a wrong identity look the same from your side; only the responder knows which. In the cloud you get the responder's view from its VPN logs (AWS Site-to-Site VPN tunnel logs, Azure's gateway diagnostics), and in the lab from `cloud-vpn-log`.

**4.8 The tunnel's MTU** (AWS "Best practices for your customer gateway device", the MTU and MSS table; Google "MTU considerations"). ESP in tunnel mode adds an outer IP header (20), the ESP header (8), an IV (8 for GCM), the trailer (2 plus padding) and the integrity check (16): 54 bytes with AES-GCM, so a 1,500-byte link carries a 1,446-byte inner packet, AWS's number. TCP's largest payload is the MTU less 40. If a link on the path is smaller and ICMP is blocked, a big segment with DF set vanishes, small ones pass: pages load and downloads hang (**tried**, both directions). The fix on your side is MSS clamping on the tunnel interface for SYNs in **both** directions (one direction fixes downloads only, **tried**), with a value from the arithmetic: a 1,400-byte line under AES-GCM allows 1,400 − 54 − 40 = 1,306. Azure clamps on its side (1,360); AWS and Google publish numbers for you to set.

**Recap** bullets: the six-month core, then the commands: `swanctl --list-sas`, `--list-conns`, `--load-all`, `--initiate --child`, `--terminate --ike`, `--rekey --child`; `journalctl -u strongswan`; `ip -s xfrm state`, `ip xfrm policy`; `tcpdump -nn -i eth1 'esp or udp port 500 or udp port 4500'`; `vtysh -c 'show bgp summary'`; the nftables clamp line.

## 5. Verified facts

Each read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | strongSwan supports XFRM interfaces from 5.8.0, the kernel from 4.19 (iproute2 5.1.0); on newer kernels they "provide a better solution than VTI devices"; for a VTI, route installation by the IKE daemon "must be disabled" (`charon.install_routes = 0`), `disable_policy=1` is recommended, the mark must match the VTI's key, and `0.0.0.0/0` selectors can be negotiated | https://docs.strongswan.org/docs/5.9/features/routeBasedVpn.html (CC BY 4.0) |
| 2 | swanctl defaults: `keyingtries` 1 (0 retries until success or a permanent error); `start_action` none; `close_action` none ("does not provide any guarantee that the CHILD_SA is kept alive"); `dpd_action` clear; `dpd_delay` 0s; CHILD `rekey_time` 1h; IKE `rekey_time` 4h; `mobike` yes; a DH group in `esp_proposals` applies only when the CHILD SA is rekeyed or created by CREATE_CHILD_SA, and "a proposal mismatch might therefore not immediately be noticed" | https://docs.strongswan.org/docs/5.9/swanctl/swanctlConf.html |
| 3 | `life_time` of a CHILD SA defaults to 110% of `rekey_time` | same (rekey_time: "If life_time is set explicitly, it defaults to 10% less than that"; the 66-minute figure assumes the default 1h rekey and 10% margin, as the tried log's "expires in 3953s" after "rekeying in 3389s" shows) |
| 4 | IKE listens on UDP 500 and may use 4500; notify types NO_PROPOSAL_CHOSEN 14, AUTHENTICATION_FAILED 24, TS_UNACCEPTABLE 38 | RFC 7296, sections 2.23 and 3.10.1: https://www.rfc-editor.org/rfc/rfc7296.html |
| 5 | The header before ESP carries protocol value 50 | RFC 4303, section 2: https://www.rfc-editor.org/rfc/rfc4303.html |
| 6 | Implementations supporting MOBIKE and NAT traversal "MUST change to port 4500 if the correspondent also supports both, even if no NAT was detected" | RFC 4555, section 3.3: https://www.rfc-editor.org/rfc/rfc4555.html |
| 7 | AWS: two tunnels per Site-to-Site VPN connection, "It is important to configure both tunnels"; endpoints evaluate proposals "starting with the lowest configured value from the list"; standard bandwidth up to 1.25 Gbps per tunnel | https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNTunnels.html |
| 8 | AWS: by default your customer gateway must bring the tunnel up; startup action "start" makes AWS initiate (IKEv2 only) and retry continuously; DPD timeout action default: the IKE session stops, the tunnel goes down, routes are removed | https://docs.aws.amazon.com/vpn/latest/s2svpn/initiate-vpn-tunnels.html |
| 9 | AWS: during tunnel endpoint updates AWS sets a lower outbound MED on the other tunnel; keep the same weight and local preference on both tunnels | https://docs.aws.amazon.com/vpn/latest/s2svpn/routing-vpn-tunnel-updates.html |
| 10 | AWS: virtual private gateway default ASN 64512, fixed after creation | https://docs.aws.amazon.com/vpn/latest/s2svpn/how_it_works.html |
| 11 | AWS: maximum MTU 1446 and MSS 1406; by algorithm: AES-GCM-16 without NAT-T 1446/1406, with NAT-T 1438/1398; AES-CBC with SHA1 or SHA2-256 without NAT-T 1438/1398, with NAT-T 1422/1382; use IKEv2; fragment before encryption | https://docs.aws.amazon.com/vpn/latest/s2svpn/cgw-best-practice.html |
| 12 | AWS: inside tunnel CIDR is a /30 from 169.254.0.0/16; DPD timeout default is given as 40 s in translated pages and the console guidance and 30 s in the API reference | search results of 2026-11-11 pointing at the API reference and the German and Italian VPNTunnels pages; **not confirmed on the English page**, which no longer lists the options inline. Don't put a DPD default in an item. |
| 13 | Azure: PolicyBased = static routing, RouteBased = dynamic; route-based default Phase 1: IKEv1 and IKEv2, DH group 2 (1024 bit), AES256/SHA1 first, lifetime 28,800 s; Phase 2 lifetime 27,000 s (route-based), PFS per the offer list; "MSS clamping is done bidirectionally on the Azure VPN Gateway": 1,360 bytes (IPv4) over the internet; recommended algorithms IKE AES256/SHA256/DH2, IPsec AES256GCM (page dated 2025-03-31, updated 2026-10-13) | https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-devices |
| 14 | Azure: default ASN 65515; reserved 65515, 65517, 65518, 65519, 65520; up to 4,000 prefixes, "The BGP session is dropped if the number of prefixes exceeds the limit"; BGP keepalive 60 s and hold 180 s, fixed (FAQ dated 2026-06-04) | https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-vpn-faq |
| 15 | Azure: custom APIPA BGP addresses from 169.254.21.0 through 169.254.22.255 (dated 2026-08-27) | https://learn.microsoft.com/en-us/azure/vpn-gateway/bgp-howto |
| 16 | Google: Cloud VPN gateway MTU 1460 (HA VPN over Interconnect 1440); enable prefragmentation on the peer; Cloud VPN doesn't fragment after encapsulation and uses MSS clamping; payload MTU 1406 (IPv4) for AEAD ciphers | https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/mtu-considerations (no date shown) |
| 17 | Google: HA VPN "Provides 99.99% SLA for most topologies"; a single-interface setup has no availability SLA; HA VPN supports only dynamic routing (BGP); IKEv1 and IKEv2 with a PSK; IPv6 in HA VPN needs IKEv2 | https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/overview |
| 18 | Ubuntu 24.04: strongswan-swanctl and charon-systemd 5.9.13-2ubuntu4.24.04.5, frr 8.4.4-1.1ubuntu6.8, wireguard-tools 1.0.20210914 | `apt-cache policy` in `ubuntu:24.04`, tried |
| 19 | Docker Desktop's kernel: `CONFIG_XFRM_USER=m`, `CONFIG_INET_ESP=m`, `CONFIG_NET_IPVTI=m`, `CONFIG_CRYPTO_GCM=y`, `CONFIG_WIREGUARD=m`; `CONFIG_XFRM_INTERFACE` not set | `/proc/config.gz`, tried |
| 20 | The runner image `ubuntu-24.04` 20261101.360.1 has kernel 7.0.0-1017-azure, whose `linux-modules` package lists `esp4`, `ip_vti`, `tunnel4`, `xfrm_user`, `xfrm_algo`, `xfrm_interface` | https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md; https://packages.ubuntu.com/noble-updates/amd64/linux-modules-7.0.0-1017-azure/filelist |
| 21 | Tried: every log line in 4.7; tunnel and BGP in 7 to 8 s from the solution; restart trial back in 11 s; a cloud restart recovered in 4 to 6 s only with `close_action = start`; the MTU table in 4.8 | `prototypes/lb-ipsec/README.md` |

Not confirmed, so not used: AWS's maximum number of BGP routes a customer gateway may advertise (I didn't open the quotas page); the DPD default (fact 12); WireGuard on the runner (no `wireguard.ko` in the standard module list: built in or in the extra package, unknown).

## 6. Resources

Fetched on 2026-11-11.

| # | Title (as the topic should list it) | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 (main) | strongSwan documentation, "IPsec Protocol": ESP, tunnel and transport mode, the IKEv2 exchanges, NAT traversal | https://docs.strongswan.org/docs/5.9/howtos/ipsecProtocol.html | reading | CC BY 4.0 (the strongSwan Team); linked, not copied | 12 (about 1,250 words with diagrams) | ipsec-building-blocks | 2026-11-11 |
| R2 | strongSwan documentation, "Introduction to strongSwan": read "Securing a Network", "IKE and IPsec Basics", "Authentication Basics", "Routing" and "Site-to-Site Configurations" | https://docs.strongswan.org/docs/5.9/howtos/introduction.html | reading | CC BY 4.0 | 15 (about 2,000 of its 4,000 words) | ipsec-building-blocks, route-based-tunnel | 2026-11-11 |
| R3 | strongSwan documentation, "Route-based VPN": the VTI section and the opening of the XFRM section | https://docs.strongswan.org/docs/5.9/features/routeBasedVpn.html | reading | CC BY 4.0 | 8 | route-based-tunnel | 2026-11-11 |
| R4 | AWS, "Best practices for an AWS Site-to-Site VPN customer gateway device" (the MTU and MSS table) | https://docs.aws.amazon.com/vpn/latest/s2svpn/cgw-best-practice.html | reading | © AWS; linked | 5 | tunnel-mtu | 2026-11-11 |
| R5 | AWS, "AWS Site-to-Site VPN tunnel initiation options" and "Routing during VPN tunnel endpoint updates" | https://docs.aws.amazon.com/vpn/latest/s2svpn/initiate-vpn-tunnels.html, https://docs.aws.amazon.com/vpn/latest/s2svpn/routing-vpn-tunnel-updates.html | reading | © AWS; linked | 5 | route-based-tunnel, bgp-over-tunnel | 2026-11-11 |
| R6 | Azure, "About VPN devices": the default IPsec/IKE parameter tables and "TCP MSS Clamping" (more resources) | https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-devices | reading | CC BY 4.0 (MicrosoftDocs/azure-docs); linked | 6 | ipsec-building-blocks, tunnel-mtu | 2026-11-11 |
| R7 | Azure, "About BGP with VPN Gateway" and the FAQ's BGP section (more resources) | https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-bgp-overview, https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-vpn-faq | reading | CC BY 4.0; linked | 8 | bgp-over-tunnel | 2026-11-11 |
| R8 | Google Cloud, "MTU considerations" for Cloud VPN, and the HA VPN part of "Cloud VPN overview" (more resources) | https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/mtu-considerations, https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/overview | reading | CC BY 4.0 (Google Cloud documentation; confirm the footer on the day); linked | 8 | tunnel-mtu, bgp-over-tunnel | 2026-11-11 |
| R9 | swanctl.conf reference (lookup during labs) | https://docs.strongswan.org/docs/5.9/swanctl/swanctlConf.html | reference | CC BY 4.0 | lookup | all | 2026-11-11 |
| R10 | RFC 7296, IKEv2: sections 1 to 1.3, optional, for the exchanges exactly | https://www.rfc-editor.org/rfc/rfc7296.html | reading | IETF Trust Legal Provisions; linked | 20 | ipsec-building-blocks | 2026-11-11 |

Assigned before the labs: R1 to R5, 45 minutes. R6 to R8 are "More resources": the lesson's comparison table carries their numbers, so nobody has to read three clouds' pages to answer a question. Considered and dropped: Cloudflare's "What is IPsec?" (HTTP 403 from here); Steve Friedl's "An Illustrated Guide to IPsec" (reachable over plain HTTP only, IKEv1-era, licence not confirmed); no free video was found and opened that covers IKEv2 well enough to recommend.

## 7. Practice ladder

All systemd labs but one share **the VPN scenery** (section 10 says what the base must provide), **tried** as the prototype:

```
office 192.168.10.10 -- lan0 192.168.10.1 [lab] eth1 198.51.100.10 -- 198.51.100.1 [internet] 203.0.113.1 -- 203.0.113.10 [cloud] vpc0 10.20.1.10/16
```

`lab` is the learner's VPN gateway (the root namespace of the container). `internet` is a router namespace (its link MTUs and an ICMP filter are the debug's ISP line). `cloud` is the provider's VPN gateway with its network behind it: its own strongSwan (charon-systemd in the cloud namespace and a mount namespace that binds `/srv/cloud/swanctl` and `/srv/cloud/strongswan.conf` into place, the `dc-enter` pattern), its own FRR (FRR's pathspace, `/etc/frr/cloud/`, `watchfrr --netns`, `vtysh -N cloud`; in the module's shared FRR pattern this is simply the router `cloud`, `frr@cloud.service`, readable by the learner through `looking-glass cloud 'show ...'`, `frr-labs-common.md` N4 to N9), its own `vti0` and an app on 10.20.1.10:80 (`index.html` and a 303,030-byte `report.txt`) plus an upload sink that checks start on port 9000. The learner's read-only views of the provider: `/srv/provider/vpn-config.txt` (the configuration sheet, in the shape of AWS's downloadable one: outside addresses, PSK, IKE version, proposals, inside /30, ASNs, the customer gateway's identity), `cloud-vpn-status` (the cloud's `swanctl --list-sas`) and `cloud-vpn-log` (the cloud's charon log), standing in for a provider's console and VPN logs. The scenery ships `/etc/strongswan.d/charon-lab.conf` (`charon { install_routes = no }`) and `/etc/strongswan.d/swanctl.conf` (the plugin list that silences 13 lines of noise), and orders the cloud's units `Before=strongswan.service frr.service`.

### 7.1 `example-first-tunnel` (worked example, systemd lab), skills all five

Parameters (the sheet): outside 203.0.113.10, PSK given, IKEv2, IKE `aes256-sha256-modp2048`, ESP `aes256gcm16-modp2048`, inside 169.254.21.0/30 (cloud .1, lab .2), cloud ASN 64512, office ASN 65010, key/mark 42. About 40 minutes. Steps:

1. **Read the sheet.** `cat /srv/provider/vpn-config.txt`; what each line will become.
2. **The tunnel interface.** `sudo ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42`, the address, `up`, `mtu 1436`, `disable_policy`; `ip -d link show vti0`. The note explains key and marks.
3. **The connection.** `sudo nano /etc/swanctl/conf.d/cloud.conf` with the whole file given, each block explained (connections, local and remote, children, `local_ts`/`remote_ts = 0.0.0.0/0`, proposals, `mark_in`/`mark_out`, the `secrets` block); `sudo chmod 600` it; `sudo systemctl enable --now strongswan`; `sudo swanctl --list-sas`.
4. **On the wire.** `sudo tcpdump -nn -i eth1 -c 6 'esp or udp port 500 or udp port 4500'` while the office pings 10.20.1.10 (after step 6 the ping works; here it shows the IKE packets on a re-initiate and the note explains the move to 4500 without NAT, MOBIKE).
5. **A failure on purpose.** Change one character of the PSK, `sudo swanctl --load-all`, `sudo swanctl --terminate --ike cloud`, `sudo swanctl --initiate --child cloud-vti`: read `AUTHENTICATION_FAILED`; `cloud-vpn-log | tail` shows `MAC mismatched`; put it back. The note: from your side a wrong identity looks the same; the provider's log tells them apart.
6. **BGP over it.** `/etc/frr/daemons` `bgpd=yes`; `frr.conf` given in full (prefix-lists and route-maps in and out, `network 192.168.10.0/24`, `neighbor 169.254.21.1 remote-as 64512`); `sudo systemctl enable --now frr`; `sudo vtysh -c 'show bgp summary'`; `ip route show proto bgp`.
7. **Through the tunnel.** `from-office curl -s http://10.20.1.10/`; `sudo ip -s xfrm state` (the byte counters rose).
8. **Make it last.** The oneshot unit `vti0.service` (given in full, ordered `Before=strongswan.service frr.service`); `keyingtries = 0`, `close_action = start`, `dpd_action = restart` in the connection; `sudo systemctl daemon-reload`, `enable vti0`. Then the provider's maintenance, on purpose: `sudo systemctl restart lab-cloud` and watch `swanctl --list-sas` come back.
9. **Write down what you saw** into `~/example/`: `ike.txt` (the IKE algorithms line from `--list-sas`), `auth-error.txt` (the line the cloud logged for the wrong PSK), `learned.txt` (`ip route show proto bgp`).

Checks: the tunnel is up with `0.0.0.0/0` selectors; BGP established and `10.20.0.0/16` learned by BGP on `vti0`; the office reaches the app; `vti0.service` enabled; `strongswan` and `frr` enabled; `ike.txt` holds `MODP_2048`; `auth-error.txt` holds `MAC mismatched`; `learned.txt` holds `10.20.0.0/16`. Wrong fixes: `psk-left-wrong.sh`, `not-enabled.sh`.

### 7.2 Recall on the building blocks and the route-based tunnel

As for every topic, each multiple-choice item is written out in full, in one shape, within about 1.3 times in length, the right answer not the longest in more than a third of the topic's items; wrong choices are real, plausible claims (suggested in brackets).

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-ike-or-esp` | mcq | ipsec-building-blocks | Which carries the office's packets to the cloud? Right: ESP, IP protocol 50, between the two outside addresses. [Wrong: IKE on UDP 500; IKE on UDP 4500 without NAT; TCP 179.] |
| `mcq-firewall-for-vpn` | mcq | ipsec-building-blocks | What must the edge firewall allow from the provider's address to the VPN gateway? Right: UDP 500, UDP 4500 and ESP (protocol 50). [Wrong sets: TCP 500 and 4500; UDP 500 and TCP 443; UDP 500 and AH.] |
| `mcq-why-4500` | mcq | ipsec-building-blocks | No NAT anywhere, yet `swanctl --list-sas` shows port 4500. Right: with MOBIKE, both ends move to 4500 in IKE_AUTH whether or not there's a NAT. |
| `predict-list-sas` | predict_shell | ipsec-building-blocks | File and command in 7.6. |
| `mcq-pfs-first-child` | mcq | ipsec-building-blocks | The ESP proposal's DH group was wrong, yet the tunnel came up. Right: the first CHILD SA takes its keys from IKE_AUTH and negotiates no DH group; it will fail at the first rekey. |
| `est-pfs-drop` | estimate | ipsec-building-blocks | CHILD SA rekey every 60 minutes, hard lifetime 10% longer; the rekey fails every time. After how many minutes does traffic stop? Exactly. **66**. Mistakes: 60 (the rekey time), 240 (the IKE SA's rekey). |
| `mcq-route-or-policy` | mcq | route-based-tunnel | Which describes a route-based tunnel? Right: selectors `0.0.0.0/0` both ways, and whatever is routed into the tunnel interface is encrypted. |
| `mcq-narrow-selectors` | mcq | route-based-tunnel | The tunnel shows INSTALLED with `192.168.10.0/24 === 10.20.0.0/16`, but BGP stays `Active`. Right: the BGP peers' inside addresses (169.254.21.x) aren't in the selectors, so BGP's packets are never encrypted. |
| `mcq-vti-mark` | mcq | route-based-tunnel | The tunnel is up, `vti0` exists, but nothing goes through and `ip -s link show vti0` counts errors. Right: the VTI's key and the connection's marks differ, so no IPsec policy matches what is routed into `vti0`. |
| `mcq-install-routes` | mcq | route-based-tunnel | Why does the lab set `charon.install_routes = no`? Right: with `0.0.0.0/0` selectors charon would install a route for everything; with a VTI, routing (BGP) decides instead. |
| `mcq-inside-addresses` | mcq | route-based-tunnel | Why are tunnel inside addresses 169.254.x.x? Right: link-local addresses never leave the link, so they can't clash with either side's networks. |
| `mcq-gone-after-maintenance` | mcq | route-based-tunnel | Every time the provider restarts its end, the tunnel stays down until someone types `swanctl --initiate`. Right: nothing restarts the CHILD SA when the peer deletes it: set `close_action = start` (and `keyingtries = 0`). |

### 7.3 `fill-make-it-last` (fill-in, systemd lab), skills `route-based-tunnel`, `bgp-over-tunnel`

Scenery: the example's tunnel, built by hand by a colleague (the story): `vti0` made with `ip link` and nothing else, the connection without `keyingtries`, `close_action` or `dpd_action`, `strongswan` and `frr` running but not enabled. In `~/tunnel/` the learner gets `vti0.service` and `cloud.conf` with gaps, and a prompt that says to copy them into place and enable everything. Gaps: in `vti0.service`, the `type vti local ... remote ... key ...` and the address line and `WantedBy=`; in `cloud.conf`, `keyingtries`, `close_action`, `dpd_action`, `mark_in`, `mark_out`. About 25 minutes.

Checks: `vti0.service` enabled and active, its `ExecStart` makes a VTI with key 42 (`systemctl show vti0 -p ExecStart`); `strongswan` and `frr` enabled; the loaded connection matches the file (`swanctl --list-conns` shows it, and `/etc/swanctl/conf.d/cloud.conf` holds `keyingtries = 0`, `close_action = start`, `dpd_action = restart`: a fill-in may check its gaps' words); `survives-maintenance` (`timeout: 60`: the check restarts `lab-cloud` and passes if the office reaches the app again within 30 s); `office-reaches-cloud`. Wrong fixes: `not-enabled.sh`, `no-close-action.sh`, `marks-differ.sh` (marks 43: the tunnel is up, the office's traffic dies), `unit-not-wanted.sh` (no `WantedBy=`, so `enable` does nothing).

### 7.4 `write-ike-diagnose` (write, plain lab), skill `read-ike-logs`

A **plain lab** (no systemd, no tunnel), so it is quick in CI. From a blank file, `~/bin/ike-diagnose LOGFILE` reads one strongSwan log of one connection attempt (journal lines, with their date, host and `charon-systemd[pid]:` prefix) and prints exactly one line:

| Output | When the log shows |
| --- | --- |
| `phase 1: no proposal chosen` | `received NO_PROPOSAL_CHOSEN notify error` |
| `phase 1: authentication failed` | `received AUTHENTICATION_FAILED notify error` |
| `phase 2: no proposal chosen` | `received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built` with no `rekeying failed` |
| `phase 2: traffic selectors unacceptable` | `received TS_UNACCEPTABLE notify, no CHILD_SA built` |
| `phase 2: rekey failed` | `CHILD_SA rekeying failed` |
| `no answer from the peer` | `retransmit` lines and nothing established |
| `up` | a CHILD_SA `established` and none of the above |

The prompt gives the table (it is the skill's vocabulary, learned in 4.7, and the lab tests applying it to unseen logs). About 30 minutes.

**The check makes its inputs at check time**: a generator in the image (Python, standard library) builds each log from the prototype's captured lines for that case (`prototypes/lb-ipsec/ipsec/log-*.txt`, lab side), with random documentation addresses, SPIs, connection names, pids and times, and with 3 to 8 harmless lines inserted at random (`flags changed for fe80::...`, `vici client 3 connected`, `loaded IKE shared key with id ...`). Checks:

1. `each-case-right` (`timeout: 30`): one fresh log per case (7), each answer exact.
2. `twenty-random` : 20 more, cases drawn so each appears at least twice; all right. (With 7 cases a constant answer is right at most 4 times in 20, never all; a script that confuses two cases fails each time either appears.)
3. `ignores-the-prefix` : the same 7 cases with the journal prefix in `short-iso` format (`2026-11-12T02:08:27+00:00 lab charon-systemd[146]: ...`).
4. `missing-file` : a missing file exits non-zero with a message on stderr.

Wrong fixes: `no-phase.sh` (prints `no proposal chosen` without the phase), `auth-as-phase-2.sh`, `rekey-as-up.sh` (sees `established` and stops), `first-match.sh` (reads only the first notify, so the PFS log, established first, reads `up`), `constant.sh` (always `up`), `exit-zero-on-missing.sh`.

### 7.5 Recall on BGP over the tunnel, the logs and the MTU

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-filter-what-you-accept` | mcq | bgp-over-tunnel | Why a route-map in that refuses `0.0.0.0/0` from the cloud? Right: a default route from the cloud would send the office's internet traffic into the tunnel. |
| `mcq-two-tunnels-med` | mcq | bgp-over-tunnel | AWS maintenance on tunnel 1; your router prefers tunnel 1 by local preference; traffic drops. Right: AWS lowers the MED on tunnel 2, but local preference beats MED, so keep weight and local preference equal on both tunnels. |
| `mcq-azure-timers` | mcq | bgp-over-tunnel | Azure's BGP uses keepalive 60 s and hold 180 s, fixed. Right: match them; a silent failure can take up to 180 s to move traffic. |
| `mcq-azure-prefixes` | mcq | bgp-over-tunnel | The data centre advertises 4,200 prefixes to an Azure VPN gateway. Right: Azure drops the BGP session (limit 4,000); summarise. |
| `predict-cloud-proposals` | predict_shell | read-ike-logs | File and command in 7.6. |
| `mcq-psk-or-identity` | mcq | read-ike-logs | The lab logs `AUTHENTICATION_FAILED`; the provider's log says `no matching peer config found`. Right: the identity the lab sent isn't the one the provider expects; the PSK was never tried. |
| `mcq-retransmits` | mcq | read-ike-logs | `retransmit 3 of request with message ID 1` from port 4500, IKE_SA_INIT fine. Right: something on the path drops UDP 4500 (or the reply); it isn't a proposal or key problem. |
| `predict-which-exchange` | predict_shell | read-ike-logs | File and command in 7.6. |
| `mcq-hangs-at-big-pages` | mcq | tunnel-mtu | Through the tunnel the order page loads, the 300 KB report never finishes. Right: big segments are dropped on a smaller link whose ICMP is blocked; clamp the MSS on the tunnel interface. |
| `mcq-clamp-direction` | mcq | tunnel-mtu | After clamping SYNs leaving `vti0`, downloads work and uploads still hang. Right: the cloud's SYN-ACK comes in through `vti0` unclamped, so the office still sends big segments; clamp SYNs arriving from `vti0` too. |
| `est-gcm-inner-mtu` | estimate | tunnel-mtu | Link 1500; outer IP header 20, ESP header 8, IV 8, trailer 2, integrity check 16, no padding needed. Largest inner packet? Exactly. **1446**. Mistakes: 1480 (only the outer header), 1406 (the MSS, one step too far). |
| `est-mss-with-nat-t` | estimate | tunnel-mtu | The same, with NAT traversal's 8-byte UDP header added. Largest TCP payload (MSS)? Exactly. **1398**. Mistakes: 1406 (forgot UDP), 1438 (the inner MTU, not the MSS). |
| `est-clamp-value` | estimate | tunnel-mtu | The office's new line has an MTU of 1400; the tunnel uses AES-GCM without NAT-T (54 bytes of ESP overhead, no padding at this size). Largest MSS to clamp to? Exactly. **1306**. Mistakes: 1360 (forgot ESP), 1406 (AWS's figure for a 1500 link). |

### 7.6 The predict-the-output items, pinned

Run on 2026-11-11 in Git Bash. Each file is captured output from the prototype (lab or cloud side), cut to the lines shown; the files are in `prototypes/lb-ipsec/predict/ip1` to `ip3`.

**`predict-list-sas`** (`ipsec-building-blocks`): `sas.txt` is the captured `swanctl --list-sas` (the healthy tunnel, 11 lines). Command: `grep -oE '^ *[a-z-]+: #[0-9]+, (reqid [0-9]+, )?[A-Z]+' sas.txt | awk '{print $1, $NF}'; awk '$1 == "local" || $1 == "remote" {if ($2 ~ /\//) print $1, $2}' sas.txt`. Output:

```
cloud: ESTABLISHED
cloud-vti: INSTALLED
local 0.0.0.0/0
remote 0.0.0.0/0
```

Explanation: the IKE SA (phase 1) is established, the CHILD SA (phase 2) installed, and its selectors are everything both ways: a route-based tunnel.

**`predict-which-exchange`** (`read-ike-logs`): `lab.log` is 11 captured lines of the wrong-PSK attempt (the lines with `NATD` were left out of the capture). Command: `grep -oE 'parsed [A-Z_]+ response|N\((NO_PROP|AUTH_FAILED|TS_UNACCEPT)\)' lab.log`. Output: `parsed IKE_AUTH response` then `N(AUTH_FAILED)`. Explanation: the error came in IKE_AUTH, where identities and keys are checked: phase 1's second exchange; a PSK or an identity, and the provider's log decides which.

**`predict-cloud-proposals`** (`read-ike-logs`, `ipsec-building-blocks`): `cloud.log` is five captured lines from the cloud during the ESP mismatch. Command: `awk -F': ' '/proposals:/ {print $1 " -> " $2}' cloud.log | sed 's/, /\n    /'`. Output:

```
received proposals -> ESP:AES_CBC_256/HMAC_SHA1_96/NO_EXT_SEQ
configured proposals -> ESP:AES_GCM_16_256/MODP_2048/NO_EXT_SEQ
    ESP:AES_GCM_16_128/MODP_2048/NO_EXT_SEQ
```

Explanation: an `ESP:` proposal is phase 2; the lab offered AES-CBC with SHA-1, the provider takes only AES-GCM. (The writer checks `sed`'s `\n` in Git Bash's sed, which printed it correctly here, and in CI.)

### 7.7 Ladder order for `topic.yaml`

`example-first-tunnel`, `mcq-ike-or-esp`, `mcq-firewall-for-vpn`, `mcq-why-4500`, `predict-list-sas`, `mcq-pfs-first-child`, `est-pfs-drop`, `mcq-route-or-policy`, `mcq-narrow-selectors`, `mcq-vti-mark`, `mcq-install-routes`, `mcq-inside-addresses`, `mcq-gone-after-maintenance`, `fill-make-it-last`, `mcq-filter-what-you-accept`, `mcq-two-tunnels-med`, `mcq-azure-timers`, `mcq-azure-prefixes`, `predict-cloud-proposals`, `mcq-psk-or-identity`, `mcq-retransmits`, `predict-which-exchange`, `mcq-hangs-at-big-pages`, `mcq-clamp-direction`, `est-gcm-inner-mtu`, `est-mss-with-nat-t`, `est-clamp-value`, `write-ike-diagnose`. That is 25 quick items (18 multiple choice, 3 predicts, 4 estimates; one more estimate is review-only) and three labs. Eighteen multiple-choice items is a lot for the length rules: the writer checks "longest in more than half" across them all, and may turn `mcq-inside-addresses` and `mcq-install-routes` into review-only items if the topic runs long (open question 1).

## 8. Proofs

### 8.1 Build: `build-tunnel-to-the-cloud` (systemd lab, 60 minutes), skills `route-based-tunnel`, `bgp-over-tunnel`, `ipsec-building-blocks`

**Different numbers from the example** (so the build is not a copy): the sheet says outside 203.0.113.10, a new PSK, IKEv2, IKE `aes256-sha384-ecp384`, ESP `aes256gcm16-ecp384` (PFS group 20), inside 169.254.44.0/30 (cloud .1, lab .2), cloud ASN 64600, office ASN 65010, the cloud's network 10.30.0.0/16 with the app at 10.30.1.10. The provider **also accepts** an old weak pair (`aes128-sha1-modp1024` for IKE and ESP), as real providers do; the prompt's policy says "use the sheet's proposals; nothing weaker". (ECP_384 is listed by charon's `swanctl --list-algs` with the openssl plugin, **tried**; an end-to-end ECP-384 tunnel has not been run: the writer confirms it first, or uses `modp3072`.)

**Prompt (substance).** Build the office's tunnel to the cloud from the sheet: route-based (a VTI), with BGP over it; send only the office's 192.168.10.0/24; accept from the cloud only prefixes inside 10.0.0.0/8 no longer than /24 (never a default route); the tunnel and BGP must come back by themselves after a reboot and after the provider restarts its end; the PSK may be read only by root. The prompt names the commands (`swanctl`, `vtysh`, `systemctl`, `cloud-vpn-status`, `cloud-vpn-log`) and the files (`/etc/swanctl/conf.d/`, `/etc/frr/frr.conf`, `/etc/frr/daemons`, `/etc/systemd/system/`).

**Checks** (`test_skills` in parentheses):

1. `tunnel-up-route-based` (route-based-tunnel): in `cloud-vpn-status`, the IKE SA established with 198.51.100.10 and a CHILD SA installed with `0.0.0.0/0 === 0.0.0.0/0`.
2. `the-sheets-proposals` (ipsec-building-blocks): the IKE SA's algorithms are `AES_CBC-256/HMAC_SHA2_384_192/PRF_HMAC_SHA2_384/ECP_384` and the CHILD SA's `ESP:AES_GCM_16-256` (read from the provider's side, so a lab config that only *lists* strong proposals behind a weak one fails too).
3. `survives-a-rekey` (ipsec-building-blocks, `timeout: 30`): the check rekeys the CHILD SA from the provider's side (`swanctl --rekey --child` in the cloud); within 10 s a new CHILD SA is installed and shows `/ECP_384`, and the office still reaches the app.
4. `bgp-up` (bgp-over-tunnel): the lab's FRR neighbour 169.254.44.1 is `Established`.
5. `learns-by-bgp` (bgp-over-tunnel, `timeout: 45`): the check advertises from the cloud a fresh `10.R1.R2.0/24` (R1 from 31 to 229, R2 from 0 to 255, chosen now), a fresh `172.16.R2.0/24` and `0.0.0.0/0`; within 15 s the lab's kernel has the first by `proto bgp` on `vti0` and neither of the others; the check withdraws all three. (**Tried**: 0.3 s to arrive.)
6. `sends-only-the-office` (bgp-over-tunnel): the cloud has received from the lab exactly `192.168.10.0/24` (the scenery's cloud accepts anything, so the check sees what the lab sends).
7. `office-through-the-tunnel` (route-based-tunnel): the office downloads the app's page and the ESP byte counters (`ip -s xfrm state`, outbound) rose during the request.
8. `survives-maintenance` (route-based-tunnel, `timeout: 60`): the check restarts the provider's gateway (`systemctl restart lab-cloud`, scenery); within 30 s the tunnel, the BGP route and the office's request are all back.
9. `comes-back-at-boot` (route-based-tunnel): `strongswan` and `frr` enabled; an enabled unit whose `ExecStart` creates `vti0` as a VTI with the connection's key, or a systemd-networkd `.netdev` of `Kind=vti` with networkd enabled; FRR's running configuration is saved (the shared recipe R2, `frr-reload.py --test /etc/frr/frr.conf` printing nothing, here for the main namespace's default instance, so without `--pathspace`; needs `frr-pythontools`); the loaded swanctl connection comes from a file under `/etc/swanctl/conf.d/`.
10. `psk-private` (ipsec-building-blocks): every file under `/etc/swanctl/` that contains the PSK is owned by root and not readable by group or others.

**Wrong fixes**: `weak-proposals.sh` (the old template's `aes128-sha1-modp1024`: check 2), `no-pfs.sh` (`esp_proposals = aes256gcm16`: check 3), `policy-based.sh` (selectors `192.168.10.0/24` and `10.30.0.0/16`: checks 1 and 4), `static-route.sh` (no BGP, `ip route 10.30.0.0/16 dev vti0` in the unit: checks 4 and 5), `no-in-filter.sh` (accepts everything: check 5), `redistribute-connected.sh` (sends the lab's connected networks: check 6), `no-close-action.sh` (check 8), `vti-by-hand.sh` (no unit: check 9), `marks-differ.sh` (check 7), `psk-world-readable.sh` (mode 644: check 10). Ten, four of them shortcuts the prompt forbids (weak crypto, static routes, accepting everything, a world-readable key).

**Restart trial**: apply `solution.sh`, `docker restart`, run the checks. **Tried** with the prototype's equivalent: booted in 6 to 7 s, BGP route back 11 s after the restart command. The first attempt failed (section 4.6) until the scenery was ordered before `strongswan` and the solution set `keyingtries = 0`; the writer keeps both.

### 8.2 Debug: `debug-tunnel-down` (systemd lab, 45 minutes), skills `read-ike-logs`, `tunnel-mtu`, `ipsec-building-blocks`

**The story.** The office's tunnel worked on the example's sheet (IKE `aes256-sha256-modp2048`, ESP `aes256gcm16-modp2048`, identities the outside addresses). Last night two things happened: someone "tidied" the strongSwan configuration from an old template, and the ISP moved the office to a new line. Three faults, found one after another, each from the evidence the last fix uncovers:

1. **Phase 1, identity.** The lab sends `id = branch.shop.test`; the provider expects 198.51.100.10. Lab: `AUTHENTICATION_FAILED`; `cloud-vpn-log`: `no matching peer config found`; the sheet names the identity.
2. **Phase 2, proposal.** `esp_proposals = aes256-sha1` (the old template); the provider takes only `aes256gcm16-modp2048` and has no weak fallback in this lab. Lab: `IKE_SA ... established`, then `received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built`; cloud: received and configured proposals.
3. **The tunnel's MTU.** The new line's links are 1,400 bytes and its router drops ICMP "destination unreachable" (scenery in the `internet` namespace); the lab's `/etc/nftables.conf` clamps the MSS only on `oifname "eth1"`, left from the days of a policy-based tunnel, so it never matches traffic that now leaves through `vti0`. Small pages load; the report download and a 400 KB upload hang.

**Prompt (to rule 5).** What the system is (office, lab gateway, the ISP's line, the provider's gateway and app; the sheet; the provider's views `cloud-vpn-status` and `cloud-vpn-log`); the symptom ("since last night nothing from the office reaches the cloud app at 10.20.1.10"); three faults; the rules of the fix: the provider's side, the ISP's line and the office laptops are not yours to change; keep the tunnel route-based with BGP (no static routes); keep the sheet's proposals; every fix must last a reboot. Done when, from the office, `curl -s -o /dev/null -w '%{size_download}\n' http://10.20.1.10/report.txt` prints 303030 and the upload command given (to port 9000) completes. Check descriptions show only after a first try (#235).

**Checks** (`test_skills`):

1. `tunnel-up` (read-ike-logs): in `cloud-vpn-status`, IKE SA established, CHILD SA installed, `0.0.0.0/0` both ways.
2. `survives-a-rekey` (ipsec-building-blocks, `timeout: 30`): as the build's, `/MODP_2048` after a provider-side rekey (catches a phase 2 fix without PFS).
3. `routes-by-bgp` (read-ike-logs, `timeout: 45`): a fresh prefix from the cloud reaches the lab by BGP (catches a static-route workaround).
4. `big-download` (tunnel-mtu, `timeout: 30`): 303,030 bytes in under 10 s from the office.
5. `big-upload` (tunnel-mtu, `timeout: 30`): 400,000 bytes from the office to a listener the check starts in the cloud, all received in under 10 s.
6. `clamp-lasts` (tunnel-mtu): `/etc/nftables.conf` loaded into a scratch namespace gives the running ruleset (Module 1's `firewall-survives-reboot` check, which handles interface names), and `nftables` is enabled.
7. `others-untouched` : the office's `eth0` MTU is 1500; the `internet` namespace's links are 1400 and its ICMP rule is present; `/srv/cloud/**` and the cloud's loaded connection (`swanctl --list-conns` in the cloud, hashed) equal the story's.
8. `config-lasts` (ipsec-building-blocks): the loaded connection's local identity is 198.51.100.10 and comes from `/etc/swanctl/conf.d/`; `strongswan` enabled.

**Wrong fixes**: `still-fqdn.sh`, `esp-still-cbc.sh`, `no-pfs.sh` (`aes256gcm16` alone: check 2), `clamp-one-way.sh` (check 5), `clamp-1460.sh` (checks 4 and 5), `clamp-runtime-only.sh` (`nft add rule`, file unchanged: check 6), `office-mtu-lowered.sh` (check 7), `isp-icmp-opened.sh` (deletes the ISP's ICMP rule: check 7), `changed-the-provider.sh` (edits `/srv/cloud` to accept the FQDN and CBC: check 7). Nine, five of them shortcuts the rules forbid. Confirm on CI that each fault alone turns only its own checks red.

### 8.3 Explain

**Prompt.** "A company connects its office to a cloud network with a site-to-site IPsec VPN, BGP over it. Explain, in your own words: what IKE and ESP each do, and what phase 1 and phase 2 agree; why a route-based tunnel with BGP is the usual choice with the clouds, and one way a policy-based habit breaks it; how you would tell from the logs of both ends a proposal mismatch in phase 1, a wrong pre-shared key or identity, and a phase 2 failure; why big downloads can hang over a tunnel when small pages work, and the fix, with the arithmetic; what makes the tunnel come back after a reboot and after the provider's maintenance; and two ways AWS, Azure or Google Cloud's VPNs differ."

**Rubric** (required unless noted):

- `ike-esp`: IKE (UDP 500, then 4500) authenticates the ends and agrees keys; ESP (protocol 50) encrypts and carries the traffic; phase 1 builds the IKE SA (proposal, Diffie-Hellman, authentication), phase 2 the CHILD SA (ESP proposal, selectors, optional PFS group); a firewall must allow UDP 500, UDP 4500 and ESP.
- `route-based`: `0.0.0.0/0` selectors and a tunnel interface let routing (BGP) decide what goes in, add prefixes without renegotiating, and fail over between tunnels; narrow, policy-based selectors leave out the BGP peers' inside addresses (or new prefixes), so the tunnel is up and BGP isn't.
- `reading-logs`: `NO_PROPOSAL_CHOSEN` in IKE_SA_INIT is phase 1, in IKE_AUTH or CREATE_CHILD_SA (after "IKE_SA established") phase 2; `AUTHENTICATION_FAILED` is a PSK or identity problem, told apart only on the responder (a MAC mismatch against no matching peer configuration); retransmits without an answer are the path; a failure an hour in is a rekey (PFS group).
- `mtu`: ESP adds about 54 bytes with AES-GCM (more with NAT-T or CBC); big TCP segments with DF set are dropped silently where ICMP is blocked; clamp the MSS on the tunnel interface in both directions to link MTU − overhead − 40 (1,306 on a 1,400 line), or follow the provider's MSS table.
- `lasting`: the tunnel interface made at boot by a unit, the services enabled; `close_action = start`, `keyingtries = 0`, DPD restart so a provider restart or a dead peer brings it back; two tunnels where offered.
- `clouds`: any two correct, e.g. AWS two tunnels per connection, MED lowered on the other during maintenance; Azure's route-based defaults start with DH group 2, BGP timers 60/180 fixed, 4,000 prefixes, MSS clamped to 1,360 on its side; Google HA VPN 99.99% only with two tunnels, BGP only, gateway MTU 1460.
- `vti-or-xfrm` (optional): the lab used a VTI with marks; XFRM interfaces do the same job better on newer kernels.

## 9. Review pool

● marks items in the practice ladder.

| Skill | Items |
| --- | --- |
| `ipsec-building-blocks` | ● `mcq-firewall-for-vpn`, ● `predict-list-sas`, ● `mcq-pfs-first-child`, ● `est-pfs-drop`, review-only `mcq-weak-default-accepted` (the tunnel came up with `MODP_1024` because the provider accepts it and the config listed it; the provider accepting a proposal doesn't make it a good one) |
| `route-based-tunnel` | ● `mcq-narrow-selectors`, ● `mcq-vti-mark`, ● `mcq-gone-after-maintenance`, review-only `mcq-xfrm-or-vti` (on a kernel from 4.19, XFRM interfaces; VTI on older kernels or, as in the lab, where XFRM interfaces aren't built) |
| `bgp-over-tunnel` | ● `mcq-filter-what-you-accept`, ● `mcq-two-tunnels-med`, ● `mcq-azure-prefixes`, review-only `mcq-static-or-bgp` (a static route to the cloud's /16 works today and silently misses the next subnet the cloud adds) |
| `read-ike-logs` | ● `mcq-psk-or-identity`, ● `mcq-retransmits`, ● `predict-which-exchange`, ● `predict-cloud-proposals`, review-only `mcq-ts-unacceptable` (`TS_UNACCEPTABLE`: the provider is configured with specific selectors that don't match yours) |
| `tunnel-mtu` | ● `est-gcm-inner-mtu`, ● `est-mss-with-nat-t`, ● `est-clamp-value`, ● `mcq-clamp-direction`, review-only `est-cbc-inner-mtu` (AES-CBC with HMAC-SHA2-256: link 1500, outer 20, ESP header 8, IV 16, integrity 16; the encrypted part (payload, padding and the 2-byte trailer) must be a multiple of 16: largest inner packet **1438**, AWS's figure; working `floor((1500 - 20 - 8 - 16 - 16) / 16) * 16 - 2`; mistakes 1440 (forgot the trailer), 1446 (the GCM figure)) |

`review_pool:` (16): `mcq-firewall-for-vpn`, `predict-list-sas`, `est-pfs-drop`, `mcq-weak-default-accepted`, `mcq-narrow-selectors`, `mcq-gone-after-maintenance`, `mcq-xfrm-or-vti`, `mcq-filter-what-you-accept`, `mcq-two-tunnels-med`, `mcq-static-or-bgp`, `mcq-psk-or-identity`, `predict-which-exchange`, `mcq-ts-unacceptable`, `est-gcm-inner-mtu`, `est-clamp-value`, `est-cbc-inner-mtu`. Six produce an answer.

## 10. What needs platform work first, and the kernel

**Platform work:** none new. The labs use what exists or is agreed: systemd labs and plain labs, estimate items, the per-check `timeout:`, the debug page that hides checks until a first try.

**What the labs need from the network-lab base** (smallest version, every piece **tried** in the prototype):

1. The Module 3 network layer with `strongswan-swanctl charon-systemd libstrongswan-standard-plugins frr` (27.6 MB) plus `frr-pythontools` (for recipe R2), disabled at build (`systemctl disable frr strongswan`); ideally the one layer every Module 3 lab shares (with `haproxy socat` for topic 33; `frr-labs-common.md` N1 asks for the same). One difference from the routing labs: there, no router runs in the main namespace; here the lab machine **is** the VPN gateway (as the NAT labs' gateway is), so the learner enables the default `frr.service` there, because strongSwan, the VTI and BGP must share one namespace. The cloud's router follows the routing labs' pattern exactly (N4 to N6, N9: `frr@cloud.service`, its own hostname, `looking-glass cloud`), and its seeded config uses their timers (`timers bgp 3 9`, `neighbor ... timers connect 5`), which also cures the 120-s reconnect wait this prototype hit.
2. A boot script for three namespaces (`office`, `internet`, `cloud`) and their veths, forwarding in `internet` and on the lab, the cloud's `vpc0` dummy and `vti0`, and the route to the provider via the ISP; parameters (addresses, key, MTU, the ICMP rule) from one small file per lab, so the example, fill, build and debug differ only in that file.
3. `cloud-enter` and `on-cloud` (the `dc-enter` pattern: bind `/srv/cloud/swanctl` over `/etc/swanctl` and `/srv/cloud/strongswan.conf` over `/etc/strongswan.conf`; the cloud's vici socket at `/run/cloud/charon.vici` with `swanctl.socket` pointing at it); `lab-cloud.service` (charon-systemd, `Type=notify`, `ExecStartPost=swanctl --load-all`) and the cloud's FRR (`frr@cloud.service` with the routing labs' drop-in; the prototype used its own unit running `frrinit.sh start cloud`, which works the same), both ordered `Before=strongswan.service frr.service`; the cloud's BGP with short timers and an outbound policy the probe checks can widen. The far side is proved untouched with the routing labs' recipe R6 (a checksum of `/etc/frr/cloud/frr.conf` and R2 on `cloud`) plus a checksum of `/srv/cloud/`.
4. `cloud-vpn-status`, `cloud-vpn-log`, `/srv/provider/vpn-config.txt`.
5. `/etc/strongswan.d/charon-lab.conf` (`install_routes = no`) and `/etc/strongswan.d/swanctl.conf` (the plugin list).
6. For the write lab only: the plain-lab image with `python3` and the log generator; no network.

**Kernel**, for both places labs run:

| Needs | Docker Desktop (owner's PC) | GitHub `ubuntu-24.04` runner |
| --- | --- | --- |
| `xfrm_user`, `xfrm_algo` | loaded already (Docker uses them) | in `linux-modules-7.0.0-1017-azure`; on-demand load from a privileged container not yet run |
| `esp4`, AES-GCM | `esp4` loaded on demand, tried; GCM built in | `esp4` in the module package; untried |
| `ip_vti`, `tunnel4` | loaded on demand, tried | in the module package; untried |
| XFRM interfaces | **not built**: not used | in the package; not used, for parity |
| `ip_forward`, `disable_policy` per namespace | tried | standard per-namespace sysctls |
| MSS clamping (`nft ... tcp option maxseg size set`) | tried | standard nftables |
| WireGuard (fallback only) | loaded on demand, tried | not in the standard module list; built in or in the extra package: unknown |

**Side effect for every lab on the same Docker machine** (tried): once `ip_vti` is loaded, every new network namespace gets `ip_vti0` and `ip6_vti0` devices (as `gre0`, `sit0`, `tunl0` appear once their modules load). CI runs four labs at once, so any Module 3 check that lists *all* interfaces would break when an IPsec lab runs beside it. Rule for the module brief: checks name the interface they read (`ip -br addr show dev eth1`), never the whole list. Module 1's `firewall-survives-reboot` check already tolerates it (its `ip link add` of an existing name fails quietly).

**The CI test, and what happens if it fails.** The first pull request that adds a VPN lab (the worked example is enough) is the test: its Labs job either keeps the contract or shows the missing module in the check output. If on-demand loading fails on the runner, in this order:

1. **Load the modules on the runner before the labs** (smallest change): one step in `.github/workflows/labs.yml`, `sudo modprobe -a esp4 ip_vti xfrm_user` (the runner has passwordless `sudo`; the modules are in its standard package). Note the memory about workflow-file pull requests: a branch touching `.github/workflows` must merge `main`'s version first. Proves everything the labs were designed to prove.
2. **If the runner's kernel lacks them** (for example, if public-repository jobs move to a host image without them): run the IPsec labs' contract only where they work (a `needs: kernel-ipsec` marker in `exercise.yaml` that CI skips, the owner running `labcheck test` locally before merging), and say so on the lab page. Proves the same, with a human step in place of CI.
3. **The honest fallback if IPsec can't run at all somewhere that matters:** WireGuard for the route-based tunnel and BGP (WireGuard interfaces work in a Docker Desktop container, tried; it is route-based by design, so `route-based-tunnel`, `bgp-over-tunnel` and `tunnel-mtu` are proven unchanged, with different overhead numbers), and IPsec itself taught from captured logs: `write-ike-diagnose` already proves `read-ike-logs` without a tunnel, and the explain covers `ipsec-building-blocks`. What would then go unproven: configuring IKE and ESP with strongSwan from a sheet, which is the spec's first verb for this topic. That gap is why the fallback is last.

## 11. Cost and time

**Money:** none. Nothing touches a cloud account. A real-cloud version (an AWS Site-to-Site VPN costs per connection-hour, outside the free tier; Azure's Basic VPN gateway bills hourly from the credit) is not proposed: the local tunnel proves every skill, and the spec's "stand-in for what one person can't buy" is exactly this.

**Learner's time**, worked out: lesson 15; assigned reading 45 (R1 12, R2 15, R3 8, R4 5, R5 5); 25 quick items at 1.5 = 38; worked example 40; fill-in 25; write 30; build 60; debug 45; explain 20. **Total 318 minutes**; `estimated_minutes: 320`. Over Module 2's 240 to 300; open question 1.

**CI:** five labs (four systemd, one plain), 31 wrong fixes, 41 container runs. From the prototype: boot 3 s, solution and convergence 7 to 8 s, checks: maintenance about 10 s, the BGP probe about 5 s, the rekey 3 to 5 s, transfers up to 10 s each. Estimates: example 4 runs × 1.5 min, fill 6 × 2, write (plain) 8 × 0.3, build 12 × 3, debug 11 × 3 = **about 83 minutes of runs, about 21 minutes on one shard at `--jobs 4`**. Image 361 MB, of which 27.6 MB is the VPN layer; build 17 to 23 s with the base cached.

## 12. Open questions, each with a recommendation

1. **318 minutes.** Split into "Building VPN tunnels" (topic 35a: the building blocks, route-based, BGP over it, making it last) and "Debugging VPN tunnels" (35b: logs and MTU)? Recommendation: **keep one topic**; trim the example to 35 minutes by giving step 4's capture as an optional step, and move `mcq-azure-timers` and `mcq-install-routes` to review-only, for about **310**. The debug needs the build's skills and the build's restart lessons; splitting would put a proof on half a picture.
2. **A second tunnel**, as AWS always gives? Recommendation: **not in the build** (time); teach it in 4.4 and 4.5, in two recall items and the explain. A two-tunnel lab with failover by MED is a good fresh version for Checkpoint 3's part 2 or for Module 11 (Cloud networking), where hybrid connectivity is designed.
3. **Certificates instead of a PSK?** Module 4 (PKI, topic 41) teaches certificates properly. Recommendation: **PSK here**, with one paragraph on certificates (strongSwan's "Authentication Basics"); topic 41 can add a certificate-authenticated tunnel as an exercise.
4. **Showing the provider's log** (`cloud-vpn-log`) makes PSK and identity tellable apart. A real provider gives this only if you turn on its VPN logs. Recommendation: **keep it**, and say in the lesson that it stands in for AWS's tunnel logs and Azure's gateway diagnostics, and that without them the configuration sheet is the evidence.
5. **ECP-384 in the build** is untested end to end. Recommendation: the writer runs it first; if it misbehaves, use `modp3072` (group 15), which needs nothing new.

## For the checkpoint designer: Checkpoint 3, part 2

"Routers, a DNS server and an app, an intermittent outage, three faults." A VPN gives two faults that are intermittent in the checkpoint's sense, both proven here: a **PFS mismatch** (works for 66 minutes after every restart, then drops; the checkpoint can shorten `rekey_time` in its scenery to a few minutes so it shows within a session) and an **MTU black hole** (some requests work, big ones hang). Either can be one of the three faults, with `test_skills` `csa.net.ipsec/read-ike-logs` or `/tunnel-mtu`, if the checkpoint's network reaches its app through a tunnel. The VPN scenery above (cloud namespace with its own strongSwan and FRR) is the part to reuse.

## Appendix: what was tried

All in `prototypes/lb-ipsec/README.md` ("IPsec: commands and timings"), with the logs in `prototypes/lb-ipsec/ipsec/`. In short: route-based IKEv2 with a VTI, AES-GCM ESP and BGP over it works in a Docker Desktop lab container and survives `docker restart`; XFRM interfaces don't exist there; eight failure modes were produced and both ends' logs captured; the MTU black hole and its two-direction fix reproduce; a provider restart recovers only with `close_action = start`; a prefix advertised at check time arrives in 0.3 s. Not tried: anything on a GitHub runner; ECP-384; the fill-in and debug labs' exact files; the log generator for the write lab.

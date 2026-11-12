# Topic 34: `csa.net.bgp`, BGP sessions and policy

Designer's brief, 2026-11-11. Shared lab pattern, prototype findings ("finding N"), check recipes ("R1" to "R8") and network-lab base requirements ("N1" to "N11"): [frr-labs-common.md](frr-labs-common.md). Captured output: `prototypes/frr/CAPTURES.md`. The second half of the spec's topic 34 is [csa.net.bgp-steering.md](csa.net.bgp-steering.md).

## 0. Split topic 34 in two

The spec's topic 34 asks for six things: bring up sessions; advertise and filter prefixes; steer traffic with local preference, AS-path prepending, MED and communities; explain route reflection; and explain how BGP drives Direct Connect, ExpressRoute and Cloud Interconnect. Designed as one topic it came to about 365 minutes (lesson 20, reading 95, 26 quick questions 39, five labs and an explain 210), past Module 2's range of 240 to 300, with six skills, the most a topic may have. Module 2 split its two oversized topics along the seams their designers drew (its brief, decision 1), for the reason that holds here: shorter topics reach their proofs and first reviews sooner, and every proof tests skills the topic just practised.

The seam is natural. **34, `csa.net.bgp`, "BGP sessions and policy"**: make BGP work, and safely: sessions, what you announce and accept, how a router picks a path, choosing your exit. **34b, `csa.net.bgp-steering`, "Steering traffic and cloud circuits"**: make BGP do what you want across several links and routers and on the clouds: inbound steering (prepending, MED, communities, more-specific prefixes), route reflection, failure detection, and Direct Connect, ExpressRoute and Cloud Interconnect. 34 takes about 285 minutes, 34b about 295.

**Decision under the owner's rule:** split (better learning and retention, free). If the owner overturns it, merge the two briefs' ladders, keep both builds as the build and a further practice lab, and accept a 365-minute topic.

**Spec text** (`docs/specs/cloud-solutions-architect.md`, the Module 3 table): replace row 34 with two rows, then renumber every later row by one, as Module 2's brief did (its section 10.2's `awk`, with the module heading changed to the next module and `s = 1`). If other Module 3 designers also split topics, the critic renumbers once for all of them.

```markdown
| 34  | BGP sessions and policy     | `csa.net.bgp`             | bring up BGP sessions and read their state; announce your own prefixes and filter what you send and accept, so you never leak routes or accept a hijack; predict which path BGP chooses and choose your exit with local preference |
| 35  | Steering traffic and cloud circuits | `csa.net.bgp-steering` | steer incoming traffic with more-specific prefixes, AS-path prepending, MED and communities; explain route reflection; detect failures fast with BFD; make one circuit primary in both directions on Direct Connect, ExpressRoute and Cloud Interconnect, and plan the backup |
```

Then `python -m uv run python tools/outline_cloud_track.py` creates the outline for `csa.net.bgp-steering`. Topic 35 (`csa.net.ipsec`, BGP over IPsec) needs only this topic; its designer may add 34b where it covers VPN as a circuit's backup.

## 1. What the learner will be able to do

- Bring up eBGP sessions on a router (FRR), read `show bgp summary`, and say why a session isn't working from its state and its last error.
- Announce the shop's own prefix and nothing else, accept only what makes sense, and say why both filters are compulsory (route leaks, hijacks, RFC 8212).
- Predict which of several paths BGP chooses from a real `show bgp` table, by the decision process (local preference, AS path length, origin, MED between paths from one neighbour AS, eBGP over iBGP, tie-breaks).
- Choose the exit for outbound traffic with local preference, and prove it in the kernel's forwarding table and with traceroute.

**The six-month core.** A session is two routers, two AS numbers, TCP 179 and a policy each way; `Established` with `(Policy)` means "up, but exchanging nothing". Announce only your own prefixes; refuse your own space and anything absurd coming in. The decision order's top three (local preference, AS path length, origin) and that MED only compares paths from one neighbour. Local preference picks **your** exit; it says nothing about how others reach you.

## 2. Prerequisites and terms

**`prerequisites: [csa.net.routing]`** (and through it CIDR and layers). NAT isn't needed.

**Builds on, for the writer.** `csa.net.routing`: longest-prefix match and its use against a hijacked more-specific prefix; FRR, `router NAME`, `show ip route`, distance (eBGP 20), `write memory`; static against dynamic, the silent failure. `csa.linux.net-tools`: TCP and its states, port numbers, `ss`, tcpdump. `csa.net.cidr`: prefixes inside prefixes (`le 32` needs it). Module 1's `nc` for testing TCP 179.

**Terms this topic defines:** autonomous system (AS); AS number (ASN), 2-byte and 4-byte, and the private ranges 64512 to 65534 and 4200000000 to 4294967294 (RFC 6996); BGP; eBGP and iBGP; peer or neighbour; session; TCP port 179; the session states (Idle, Connect, Active, OpenSent, OpenConfirm, Established); keepalive and hold timer; prefix announcement (advertisement) and withdrawal; path attributes (AS_PATH, NEXT_HOP, LOCAL_PREF, MED, ORIGIN); best path; import and export policy; prefix list (with `le` and `ge`); route map; RFC 8212's "no policy, no routes"; transit, customer and peer relationships; route leak; prefix hijack (and RPKI, named in one sentence); maximum prefixes; the `network` statement and its import check; received and advertised routes; looking glass; weight (FRR-local).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `bgp-sessions` | Configure an eBGP neighbour (`router bgp ASN`, `neighbor ADDRESS remote-as ASN`); read `show bgp summary` (the state column, received and sent prefix counts, `(Policy)`); what each state means; why a session doesn't come up (wrong remote AS, wrong address, TCP 179 blocked, no route to the neighbour) and where the evidence is (`show bgp neighbors`, its "Last reset" line); keepalive and hold timers |
| `announce-and-filter` | Originate a prefix (`network` needs that exact prefix in the routing table); export only your own prefixes (prefix list, route map) so you are never a transit between providers; import sensibly: refuse your own space, including more-specifics (`le 32`), and what a provider shouldn't send; RFC 8212 and FRR's `bgp ebgp-requires-policy`; maximum prefixes; route leaks and hijacks from real incidents |
| `best-path` | Predict the winner among several paths to one prefix from `show bgp ipv4 unicast` (`>` best, `LocPrf`, `Metric`, `Path`): weight (local to the router), local preference, locally originated, AS path length, origin, MED (only between paths from the same neighbour AS), eBGP over iBGP, IGP cost to the next hop, then tie-breaks (router ID, neighbour address); and that the kernel installs only the winner |
| `local-preference` | Choose the exit for outbound traffic: set local preference on routes learned from the preferred neighbour (an inbound route map); confirm in `show bgp` and with `ip route get` and traceroute; know it is shared with the AS's other routers and has no effect on how the rest of the internet reaches you |

No calculation skill.

## 4. Lesson plan

What the lesson adds to the resources: the session as two people agreeing to talk and what each promises to say, the announce-and-accept picture with arrows, the decision order as a short checklist with one worked table, and the gap between what BGP chose and what the kernel forwards.

1. **Why BGP exists** (resource B2, Computerphile with Tim Griffin, 16 min; or the first part of B1). No one runs the internet; tens of thousands of networks, each an **autonomous system** with a number, tell their neighbours which address blocks they can reach. The clouds use it too: a VPN or a dedicated circuit to a cloud is a BGP session (34b).
2. **A session** (resource B1, Jim Kurose's lecture, 18 min, the main resource; B6's NSRC "Introduction" optional). Two routers open TCP port 179, exchange OPEN messages naming their AS numbers, then keepalives; `Established` means they are talking. eBGP joins two ASes, iBGP two routers of one AS. *Picture in words:* two neighbours over a fence agreeing first who they are, then exchanging lists, then nodding every few seconds; if one stops nodding for the hold time, the other assumes they've gone and forgets everything they said. FRR's traditional defaults are a 60-second keepalive and a 180-second hold time (connect retry 120 s); the labs use 3 and 9. The states, and which ones mean "trying and failing" (Connect, Active) or "configured but stopped" (Idle).
3. **Configuring it in FRR** (resource B4, FRR 8.4's "Defining Peers" and "Require policy on EBGP", 5 min). `router bgp 65001`, `neighbor 192.0.2.2 remote-as 65010`. Then the surprise the prototype showed (finding 9): the session comes up and nothing happens, `(Policy)` in both prefix columns. **RFC 8212** (resource B7): an eBGP session with no import policy accepts nothing and with no export policy sends nothing, because permissive defaults caused route leaks. FRR follows it by default. `no bgp ebgp-requires-policy` turns that off, and every lab treats it as the wrong fix it is.
4. **What you announce** (resource B3, the Systems Approach's "Basics of BGP" and "Common AS Relationships and Policies", 11 min). `network 198.51.100.0/24` announces a prefix only if the routing table holds exactly that prefix (finding 10). *Picture in words:* the shop sits between two providers; it tells each "you can reach 198.51.100.0/24 through me" and nothing else. If it also passes ISP A's routes to ISP B, it has told ISP B "you can reach ISP A's customers through me": a **route leak**, and the shop's small link becomes a path for other people's traffic. The prototype showed it (ISP B received `203.0.113.0/24` with path `65001 65010 65100`). Customer, provider and peer: you carry traffic for your customers and nobody else.
5. **What you accept.** Refuse your own prefix and anything inside it (`ip prefix-list NOT-OURS deny 198.51.100.0/24 le 32`): if a provider sends you `198.51.100.128/25`, longest-prefix match (`csa.net.routing`) makes it beat your own connected /24, and half your own servers become unreachable from your own office. That is a **hijack** when it's deliberate and a mistake when it isn't; RPKI, which lets a network check who may originate a prefix, is named in one sentence. Maximum prefixes: a session that suddenly receives a full table from a customer should shut, not flood. Route maps and prefix lists in FRR (B4's filter sections), with `permit`, `deny`, sequence numbers and the implicit deny at the end.
6. **Two real incidents** (resource B5, Cloudflare on the 2019 route leak, 11 min; B8, the 2021 Facebook withdrawal, optional). A small network accepted more-specific routes from one customer and passed them to its provider, which accepted them too: two missing filters, a large part of the internet rerouted through a small company. The lesson asks: which filter, on which router, would have stopped it?
7. **How a router chooses** (B4's "Route Selection", 3 min; B1's part on path selection). The checklist: highest weight (FRR's own, never sent to anyone), highest local preference (default 100), a route this router originated, shortest AS path, lowest origin (IGP before incomplete), lowest MED (only among paths from the same neighbour AS), eBGP over iBGP, nearest next hop, then tie-breaks. *Worked table:* three paths to `203.0.113.0/24`, read row by row. The prototype's lesson for the labs (finding 7): when everything else ties, FRR prefers the older path, which depends on which session came up first.
8. **Choosing your exit: local preference.** Set local preference 200 on everything learned from the cheaper ISP (an inbound route map) and every router in your AS prefers that exit. Confirm three ways: `show bgp` (the `LocPrf` column and `>`), `ip route get` (what the kernel will do), traceroute from the office. Local preference changes **your** outbound traffic only; how the internet reaches you is 34b's problem.
9. **Saving and looking.** `write memory`, as in topic 26; a looking glass (`looking-glass ispa 'show bgp ...'`) to see what the far side received, as operators do with real providers' public looking glasses.

**Read now:** B1 (18), B3's two sections (11), B4's four sections (11), B5 (11). B2, B6, B7 and B8 are "more resources".

## 5. Verified facts

Each read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| F1 | BGP listens on TCP port 179; the session states Idle, Connect, Active, OpenSent, OpenConfirm, Established | RFC 4271, https://www.rfc-editor.org/rfc/rfc4271 |
| F2 | RFC 8212: "Routes contained in an Adj-RIB-In associated with an EBGP peer SHALL NOT be considered eligible in the Decision Process if no explicit Import Policy has been applied", and none added to an eBGP peer's Adj-RIB-Out "if no explicit Export Policy has been applied"; the reason given is route leaks | https://www.rfc-editor.org/rfc/rfc8212 |
| F3 | Private ASNs: 64512 to 65534 and 4200000000 to 4294967294 | RFC 6996, https://www.rfc-editor.org/rfc/rfc6996 |
| F4 | FRR `bgp ebgp-requires-policy`: "enabled by default for the traditional configuration and turned off by default for datacenter configuration"; shows "(Policy)" in `show bgp summary` | https://docs.frrouting.org/en/stable-8.4/bgp.html, "Require policy on EBGP" |
| F5 | FRR's route selection order: weight, local preference, local route, AS path length, origin, MED ("Where routes with a MED were received from the same AS"), external over internal, IGP cost, multipath, already-selected external, router ID, cluster-list length, peer address; `bgp bestpath compare-routerid` skips the already-selected check | F4's page, "Route Selection" |
| F6 | FRR's `network` import check: for 7.4 and later "both traditional and datacenter the network must exist" in the RIB | F4's page |
| F7 | FRR 8.4 defaults (source): keepalive 60, hold 180, connect retry 120 (datacenter profile 3, 9, 10); default local preference 100; eBGP minimum advertisement interval 0 | `bgpd/bgpd.h` and `bgpd/bgp_vty.c` at https://github.com/FRRouting/frr/tree/stable/8.4 |
| F8 | FRR: `neighbor PEER maximum-prefix NUMBER`: "If this number is exceeded, the BGP session will be destroyed"; `set as-path prepend`; `bgp fast-external-failover` is the default | F4's page |
| F9 | In FRR 8.4: an eBGP session without route maps shows `(Policy)`, `"peerState": "Policy"`; permit-all policies leak a provider's routes to the other provider; a prefix filter stops it within 0.25 s of being applied; an unsaved change is gone after a restart and a saved one isn't | prototype (findings 8, 9) |
| F10 | The 2019 leak: Cloudflare's account of a route leak through a BGP optimizer and a provider that accepted it | https://blog.cloudflare.com/how-verizon-and-a-bgp-optimizer-knocked-large-parts-of-the-internet-offline-today/ (2019-06-24) |
| F11 | Facebook's routes withdrawn on 2021-10-04, and its DNS with them | https://blog.cloudflare.com/october-2021-facebook-outage/ (2021-10-04) |
| F12 | The Systems Approach: AS relationships (customer, provider, peer) and the policies that follow | https://book.systemsapproach.org/scaling/global.html, 4.1.2 |

## 6. Resources

All opened on 2026-11-11; linked, never copied.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 (main) | Jim Kurose, "5.4 BGP: the Border Gateway Protocol" (lecture for *Computer Networking: a Top-Down Approach*) | https://www.youtube.com/watch?v=2rV4tJkP-CQ | video (18:06, 2022-01-15, embeddable) | Standard YouTube licence; embedded, not copied | 18 | `bgp-sessions`, `best-path` | 2026-11-11 |
| B2 | Computerphile, "BGP: Border Gateway Protocol" (Tim Griffin) | https://www.youtube.com/watch?v=O6tCoD5c_U0 | video (16:17, 2016-05-04, embeddable) | Standard YouTube licence | 16 | `announce-and-filter` | 2026-11-11 |
| B3 | Peterson and Davie, *Computer Networks: A Systems Approach*, 4.1.2: "Basics of BGP" and "Common AS Relationships and Policies" (the rest of 4.1.2 optional) | https://book.systemsapproach.org/scaling/global.html | reading (1,451 words assigned; 3,746 in 4.1.2) | CC BY 4.0 | 11 | `announce-and-filter`, `best-path` | 2026-11-11 |
| B4 | FRR 8.4 user guide, BGP: "Defining Peers", "Require policy on EBGP", "Route Selection", and the prefix-list and route-map sections | https://docs.frrouting.org/en/stable-8.4/bgp.html | reference | FRR's documentation licence (custom, permissive, per the FRR repository's COPYING); linked | 11 | all four | 2026-11-11 |
| B5 | Cloudflare, "How Verizon and a BGP Optimizer Knocked Large Parts of the Internet Offline Today" | https://blog.cloudflare.com/how-verizon-and-a-bgp-optimizer-knocked-large-parts-of-the-internet-offline-today/ | reading (1,402 words, 2019-06-24) | © Cloudflare; linked | 11 | `announce-and-filter` | 2026-11-11 |
| B6 | NSRC, "Introduction to Border Gateway Protocol" and "Overview of Applying Policy with BGP" | https://www.youtube.com/watch?v=DnnZ0yPRVWg and https://www.youtube.com/watch?v=MAdg3x2_RmM | video (5:51, 2019-04-02; 3:48, 2019-05-30; both embeddable) | the first: standard YouTube licence; the second: Creative Commons Attribution (YouTube's licence field) | 10 | `bgp-sessions`, `announce-and-filter` | 2026-11-11 |
| B7 | RFC 8212, "Default External BGP (EBGP) Route Propagation Behavior without Policies" | https://www.rfc-editor.org/rfc/rfc8212 | reading (short; sections 1 to 4) | IETF Trust Legal Provisions; linked | 6 | `announce-and-filter` | 2026-11-11 |
| B8 | Cloudflare, "Understanding how Facebook disappeared from the Internet" | https://blog.cloudflare.com/october-2021-facebook-outage/ | reading (1,642 words, 2021-10-04) | © Cloudflare | 13 | `bgp-sessions` | 2026-11-11 |

## 7. Practice ladder

**The dual-homed shop** (all labs; `prototypes/frr/bgp/` plus a transit AS): `edge` (AS 65001, the learner's router) has `lan` 198.51.100.1/24 with `office` 198.51.100.10 and `shopweb` 198.51.100.200, a link to `ispa` (AS 65010, 192.0.2.0/30, edge .1) and one to `ispb` (AS 65020, 192.0.2.4/30, edge .5). ispb reaches `cloud` (AS 65100, which originates 203.0.113.0/24 where `web` 203.0.113.10 serves port 80) directly; ispa reaches it through `transit` (AS 65030). So paths from edge to 203.0.113.0/24 are `65010 65030 65100` through ispa and `65020 65100` through ispb, and **ispb wins by default** (finding 7: no lab may depend on a tie). Every seeded router config has `timers bgp 3 9`, `neighbor X timers connect 5` and `bgp bestpath compare-routerid`. The ISP, transit and cloud routers are configured and saved; the learner reads them with `looking-glass NAME 'show ...'` (N9). Addresses are RFC 5737's documentation ranges and ASNs are private (F3), so nothing in the lab is anybody's real network.

1. **`example-first-session`** (worked example, systemd; edge has only its hostname and interfaces). Labelled steps:
   1. *Nothing yet.* `router edge`, `show bgp summary`: no BGP. `on office curl -m 3 http://203.0.113.10/`: no route.
   2. *Open a session.* `configure terminal`, `router bgp 65001`, `neighbor 192.0.2.2 remote-as 65010`, `end`; watch `show bgp summary` go from Connect or Active to an uptime: Established. Then the `(Policy)` columns, explained (RFC 8212).
   3. *Policies.* A route map that permits everything, applied in and out (`neighbor 192.0.2.2 route-map ALLOW in`, `... out`); `show bgp ipv4 unicast` now lists 203.0.113.0/24 with its AS path; `show ip route` shows it as `B>*`; the office reaches web.
   4. *Announce the shop.* `address-family ipv4 unicast`, `network 198.51.100.0/24`; `looking-glass ispa 'show bgp ipv4 unicast 198.51.100.0/24'` shows it arriving.
   5. *A second provider, and a leak.* The same for ispb with the permit-all map; `looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes'` shows 203.0.113.0/24 with path `65001 65010 65030 65100`: the shop is offering transit. Read why that's a leak.
   6. *Fix it.* `ip prefix-list OURS seq 5 permit 198.51.100.0/24`, a route map `TO-ISPS` matching it, applied out to both; ispb's looking glass now shows only 198.51.100.0/24.
   7. *Read the choice.* `show bgp ipv4 unicast 203.0.113.0/24`: two paths, the one through ispb best (`AS Path`), and `ip route get 203.0.113.10` agrees.
   8. *Save.* `write memory`.
   Checks: both sessions Established (R4); ispa and ispb each received exactly 198.51.100.0/24 from edge (R4, far side); the office reaches web (R1); edge still requires policy (R7); saved (R2). Wrong fixes: `leak-left.sh` (permit-all out to ispb), `not-saved.sh`, `policy-off.sh` (`no bgp ebgp-requires-policy` with no route maps: the leak returns).
2. **`bgp-summary-read`** (predict_shell, `bgp-sessions`, captured). File: the captured `show bgp summary` with two Established neighbours. Command: `awk '$1 ~ /^[0-9]+\./ {print $1, "AS" $3, "received", $10, "sent", $11}' summary.txt`. Explanation: the column that holds a count for an Established session holds the state otherwise.
3. **`bgp-summary-policy`** (predict_shell, `bgp-sessions` and `announce-and-filter`, captured). File: the captured summary with `(Policy) (Policy)`. Command: `awk '$1 ~ /^[0-9]+\./ && $10 !~ /^[0-9]+$/ {print $1, $10}' summary.txt`. Output `192.0.2.1 (Policy)`. Explanation: the session is up and exchanging nothing because it has no policy (RFC 8212); the fix is a policy, never `no bgp ebgp-requires-policy`.
4. **`mcq-session-active`** (mcq, `bgp-sessions`). `show bgp summary` shows a neighbour in `Active` for ten minutes. Right: "The router keeps trying to open the TCP connection to that neighbour and failing". Wrong: "The session is up and the neighbour is actively sending routes"; "The neighbour is configured but an administrator has shut it down"; "The two routers are agreeing which address families to exchange". (Same length band, about 70 characters.)
5. **`mcq-why-no-session`** (mcq, `bgp-sessions`). `show bgp neighbors 192.0.2.2` ends `Last reset 00:00:04, Notification sent (OPEN Message Error/Bad Peer AS)`. Right: "The neighbour's AS number differs from the `remote-as` this router was given". Wrong: "TCP port 179 is blocked between the routers, so OPEN never arrives"; "The neighbour has no route back to this router's address"; "The hold timers differ, and the routers can't agree on one". Explanation: the other three each look different (no TCP at all: Connect or Active; hold timers are negotiated down to the lower, F7's page).
6. **`mcq-network-needs-route`** (mcq, `announce-and-filter`). The router's LAN is 198.51.100.0/24 (connected). Its BGP config says `network 198.51.100.0/25`. What do the providers receive? Right: "Nothing: FRR announces a network only if that exact prefix is in its routing table". Wrong: "198.51.100.0/25, because it lies inside a connected network"; "198.51.100.0/24, because FRR widens the prefix to the connected one"; "Both halves of the /24, because a /25 implies its neighbour".
7. **`mcq-route-leak`** (mcq, `announce-and-filter`). The shop is connected to ISP A and ISP B and passes everything it learns from each to the other. Right: "ISP B may send traffic for ISP A's customers through the shop's small link". Wrong: "Nothing happens, because each ISP ignores routes that passed through a customer"; "ISP A will drop the session, because routes it sent came back to it"; "The shop's own prefix is withdrawn, because its AS path becomes too long". (The second wrong answer is subtle: an ISP *should* filter its customers, which is the point of the explanation and B5.)
8. **`mcq-hijack-more-specific`** (mcq, `announce-and-filter`). The edge accepts everything from ISP B, which announces 198.51.100.128/25 by mistake. The shop's server 198.51.100.200 is on the edge's own LAN. What happens to the office's traffic to it? Right: "It goes to ISP B: the /25 is longer than the edge's connected /24". Wrong: "It stays on the LAN: connected routes always beat routes from BGP"; "It stays on the LAN: eBGP routes have distance 20, connected 0"; "It is dropped: the edge sees two routes for its own server and uses neither". Explanation: distance only matters for equal prefixes (`csa.net.routing`); `deny 198.51.100.0/24 le 32` is the filter.
9. **`mcq-rfc8212`** (mcq, `announce-and-filter`). Why do FRR's eBGP sessions exchange nothing until a route map is applied each way? Right: "RFC 8212 says eBGP routes need an explicit policy to be accepted or sent". Wrong: "FRR waits for the first route refresh, which a route map triggers"; "eBGP sessions start passive until either side sends a route map"; "The neighbour's AS must be listed in a route map before it is trusted".
10. **`prefix-list-le`** (predict_shell, `announce-and-filter`, constructed). File: five prefixes, one a line. Command: a short `awk` that implements "permit 198.51.100.0/24 le 32" on them (prints `permit` or `deny` per line, written plainly with the integer recipe of `csa.net.routing`'s write lab). The learner predicts which lines a provider-facing filter would match. Explanation: `le 32` means "this prefix and everything inside it".
11. **`bgp-table-best`** (predict_shell, `best-path`, captured). File: the captured `show bgp ipv4 unicast` from the cloud router. Command: `awk '$1 ~ /\*>/ {print $2, $3}' table.txt` plus the continuation line's handling (the writer pins it: the second path line has no prefix). Output: the best next hop for each prefix. Explanation: why `>` sits on that line (`selectionReason`).
12. **`mcq-localpref-beats-path`** (mcq, `best-path`). Two paths: LocPrf 150 with path `65010 65030 65040 65100`, LocPrf 100 with path `65020 65100`. Right: "The first: local preference is compared before AS path length". Wrong: "The second: two AS hops are fewer than four"; "Both, shared: BGP balances paths with equal origin"; "The second: a local preference of 100 is the default and preferred". (Captured analogue: `CAPTURES.md`, circuits, "Local Pref".)
13. **`mcq-med-other-as`** (mcq, `best-path`). Two paths to the same prefix with equal local preference and AS path length, from AS 65010 with MED 50 and from AS 65020 with MED 10. Which wins on MED? Right: "Neither on MED: MED compares only paths from the same neighbour AS". Wrong: "The one with MED 10, because a lower MED is preferred"; "The one with MED 50, because a higher MED is preferred"; "Both, because MED decides only between iBGP paths". Explanation: FRR's wording (F5), and `always-compare-med` named.
14. **`mcq-ebgp-over-ibgp`** (mcq, `best-path`). Everything equal up to MED; one path learned from an eBGP neighbour, one from a router in the same AS. Right: the eBGP path. Wrong choices: the iBGP one ("internal routes are trusted more", which is administrative distance thinking: eBGP's distance 20 is lower than iBGP's 200, the same answer for a different reason, so word that distractor as "because iBGP's distance of 200 is preferred to eBGP's 20", plainly wrong), the lower router ID, the newer path.
15. **`mcq-weight-local`** (mcq, `best-path`). What is FRR's `weight`? Right: "A preference only this router uses; it is never sent to any neighbour". Wrong: "A preference shared with every router in the AS, like local preference"; "A preference sent to the neighbour AS, telling it which link to use"; "The number of equal paths the router may use at once".
16. **`localpref-table`** (predict_shell, `local-preference`, constructed in FRR's format). Three paths to 203.0.113.0/24 with LocPrf `200`, blank (100) and `100`, and AS paths of 3, 2 and 2. Command prints the next hop of the path with the highest LocPrf (blank read as 100). The learner predicts it. Explanation: a blank LocPrf on an eBGP path means the default, 100.
17. **`mcq-localpref-direction`** (mcq, `local-preference`). The shop sets local preference 200 on routes from ISP A. Which traffic changes? Right: "Traffic from the shop to the internet now leaves through ISP A". Wrong: "Traffic from the internet to the shop now arrives through ISP A"; "Both directions now use ISP A, since BGP keeps paths symmetric"; "Neither until ISP A agrees to the same local preference". Explanation: local preference never leaves the AS; incoming traffic is 34b.
18. **`mcq-localpref-where`** (mcq, `local-preference`). Where does the setting go? Right: "In a route map applied inbound to the session with ISP A". Wrong: "In a route map applied outbound to the session with ISP A"; "In the `network` statement of the shop's own prefix"; "In ISP A's router, as a route map on its session to the shop".
19. **`fill-isp-policy`** (fill-in, systemd; edge configured with both sessions and saved, its policy section with gaps). `/etc/frr/edge/frr.conf` holds four gaps (`___`): the prefix in the `OURS` prefix list; the `match` line of the outbound route map; the `le` clause of the inbound `NOT-OURS` list; and the route map applied inbound from ispb. ispb is seeded to announce 198.51.100.128/25 (a "mistake at ISP B"). The prompt: edit with `sudo nano`, then `sudo systemctl restart frr@edge`. Checks: ispa and ispb each received exactly 198.51.100.0/24 (R4, far side); edge's table holds no prefix inside 198.51.100.0/24 learned from an ISP; `ip -n edge route get 198.51.100.200` is `dev lan`, and the office reaches shopweb; the office reaches web; policy required (R7); running equals saved (R2). Wrong fixes: `export-everything.sh` (leak), `no-le-32.sh` (denies only the exact /24, so the /25 gets in), `in-filter-on-ispa-only.sh`, `policy-off.sh`.
20. **`write-cloud-session`** (write, systemd). The shop adds a direct session to the cloud (AS 65100) over a new link `vpn` (169.254.30.0/30, edge .1, cloud .2), a stand-in for a VPN with BGP. From nothing (edge's ISP config is done; the cloud side is configured): a neighbour with the lab's timers, an export policy announcing only 198.51.100.0/24, an import policy accepting only 203.0.113.0/24 (the cloud also announces 10.200.0.0/16 and a default route, to test the filter), saved. Checks: the session is Established; the cloud received exactly 198.51.100.0/24 from edge over `vpn` (the ISPs' routes not passed on); edge accepted from the cloud only 203.0.113.0/24; edge's best path to it is now the direct session (path length 1) and `ip route get 203.0.113.10` names 169.254.30.2; policy required; saved. Wrong fixes: `accept-everything.sh` (the default route gets in), `leak-to-cloud.sh` (permit-all out: the cloud receives the ISPs' routes), `policy-off.sh`, `not-saved.sh`.

Recall items in practice: 17 (items 2 to 18). Labs: 3.

## 8. Proofs

### Build: `build-dual-homed` (systemd, 55 minutes)

The dual-homed shop with edge's BGP configuration empty (hostname, interfaces, saved). ispb announces 198.51.100.128/25 by mistake (stated in the prompt as "ISP B has been known to send routes it shouldn't"; the prefix isn't named). ISP A is the cheaper contract.

**Prompt (summary).** Configure edge from nothing:

1. BGP sessions with ISP A (192.0.2.2, AS 65010) and ISP B (192.0.2.6, AS 65020), with the lab's timers (`timers bgp 3 9`);
2. announce 198.51.100.0/24 to both, and nothing else, ever;
3. accept nothing inside 198.51.100.0/24 from either ISP;
4. while both sessions are up, all traffic to the internet leaves through ISP A, using local preference; when ISP A's session is down, it leaves through ISP B, without anyone changing anything;
5. keep eBGP's policy requirement on;
6. it all survives a reboot.

**Checks.**

| id | Tests | Skill |
| --- | --- | --- |
| `sessions-up` | Both sessions Established (R4) | `bgp-sessions` |
| `announced-exactly` | ispa and ispb each accepted exactly [198.51.100.0/24] from edge (`neighbors ... routes json` on each, R4) | `announce-and-filter` |
| `own-space-refused` | edge's BGP table holds no path for any prefix inside 198.51.100.0/24 from an ISP; `ip -n edge route get 198.51.100.200` is `dev lan`; office reaches shopweb | `announce-and-filter` |
| `exit-via-a` | `bgp-best edge 203.0.113.0/24` names 192.0.2.2 with a local preference above 100 on the ispa path; `ip -n edge route get 203.0.113.10` names 192.0.2.2; office reaches web | `local-preference`, `best-path` |
| `policy-kept` | R7 | `announce-and-filter` |
| `saved` | R2 on edge | `bgp-sessions` |
| `isps-untouched` | R6 on ispa, ispb, transit, cloud | `bgp-sessions` |
| `fails-over-to-b` | `lab-link edge ispa down`; within 5 s office reaches web and edge's route names 192.0.2.6; restore; within 15 s the route names 192.0.2.2 again (R5, `timeout: 60`, last in the file) | `local-preference` |

**Wrong fixes:** `transit-leak.sh` (permit-all out), `no-local-pref.sh` (the default picks ispb: `exit-via-a` fails deterministically, finding 7), `weight-instead.sh` (`neighbor 192.0.2.2 weight 100`: traffic goes via A, but the prompt asked for local preference, which other routers in the AS would share; `exit-via-a` reads `locPrf`), `prepend-instead.sh` (prepends toward ispb, which changes incoming traffic only), `localpref-on-b.sh`, `hijack-accepted.sh` (no inbound filter), `policy-off.sh`, `not-saved.sh`.

### Debug: `debug-shop-unreachable` (systemd, 45 minutes)

The dual-homed shop, configured and saved, with three faults.

**The system, stated:** edge announces 198.51.100.0/24 to both ISPs and nothing else; it sends outbound traffic through ISP A while that session is up (local preference 200 on ISP A's routes); it refuses anything inside its own prefix from either ISP.

**Symptoms, stated:** since Tuesday night's maintenance the shop's website (198.51.100.200) can't be reached from the cloud's network, the office's traffic to the internet goes out through ISP B although ISP A says its side is fine, and ISP B's network operations centre has written to say the shop is announcing routes it has no business announcing. **Three faults.**

**The faults** (author's eyes only):

1. The route map that sets local preference 200 is applied inbound on the session with **ispb**, not ispa: every path through B now beats every path through A (`local-preference`, `best-path`). Evidence: `show bgp ipv4 unicast 203.0.113.0/24` shows `LocPrf 200` on the path via 192.0.2.6.
2. `network 198.51.100.0/25` in place of `/24`: nothing is originated (import check, finding 10), so the cloud has no route to the shop (`announce-and-filter`). Evidence: `show bgp ipv4 unicast 198.51.100.0/25` says the network isn't in the table; ispa's looking glass shows nothing from edge.
3. The outbound route map toward ispb has lost its `match ip address prefix-list OURS` line, so everything edge learned from ISP A goes on to ISP B (`announce-and-filter`). Evidence: ispb's looking glass shows paths from edge starting `65001 65010`.

All three are visible at the start, and each has its own evidence. Sessions are not among the faults: the build and the write prove `bgp-sessions`, and a session fault here would hide fault 3 (with ISP A's session down there is nothing to leak).

**Rules of the fix, stated:** change only edge; ISP A's and ISP B's routers are theirs (look at them with `looking-glass`); keep eBGP's policy requirement; announce only 198.51.100.0/24; save.

**Checks:** `sessions-up`, `announced-exactly`, `cloud-reaches-shop` (from `web`, 198.51.100.200:80 answers, and `bgp-best cloud 198.51.100.0/24` names a path), `exit-via-a`, `policy-kept`, `saved`, `isps-untouched`; skills as in the build (`cloud-reaches-shop`: `announce-and-filter`).

**Wrong fixes:** `filter-at-ispb.sh` (adds an inbound filter on ispb's router to drop the leaked routes: `isps-untouched` fails), `no-import-check.sh` (`no bgp network import-check` keeps the /25 and announces it: `announced-exactly` fails), `announce-slash-16.sh` (`network 198.51.0.0/16` with a blackhole route to make it valid: announces space that isn't the shop's), `localpref-on-both.sh` (the 200 route map on both sessions: the tie is broken by AS path, so B still wins: `exit-via-a` fails), `leak-left.sh`, `policy-off.sh`, `not-saved.sh`.

### Explain (20 minutes)

**Prompt.** Your company is about to connect its data centre to two internet providers with BGP, and a colleague says: "Once BGP is on, the internet just finds us." Explain, in your own words: how two routers become BGP neighbours and what they tell each other; what your router should announce and accept, and what goes wrong without each filter (with a real kind of incident); how a router chooses between several paths to the same network; how you'd make your outbound traffic use the cheaper provider, and what that does not change; and what happens to your traffic when a session drops.

**Rubric.**

| id | Required | Description |
| --- | --- | --- |
| `sessions` | yes | A TCP session on port 179 between two routers, each told the other's address and AS number; OPEN, then keepalives; the session is declared down when the hold time passes without one; eBGP between ASes, iBGP inside one |
| `announce-filter` | yes | Announce only your own prefixes (the `network` must exist in the routing table); never pass one provider's routes to another (a route leak makes you transit); refuse your own space and more-specifics of it (a hijack or mistake beats your own route by longest prefix); RFC 8212: no policy, no routes; maximum prefixes as a fuse |
| `best-path` | yes | The order at least to MED: local preference, AS path length, origin, MED (only between paths from one neighbour AS); then eBGP over iBGP and tie-breaks; the kernel installs only the winner |
| `exit` | yes | Local preference set on routes from the preferred provider (inbound route map) chooses the exit for outbound traffic, for every router in the AS; it doesn't affect how others reach you, which needs other tools |
| `failure` | no | When a session drops (link down at once, or after the hold time if the path dies silently), its routes are withdrawn and the next best path is used, as the backup provider |

## 9. Review pool

Fourteen items, at least two per skill:

- `bgp-sessions`: `bgp-summary-policy`, `mcq-why-no-session`, `mcq-session-active`.
- `announce-and-filter`: `mcq-hijack-more-specific`, `mcq-network-needs-route`, `mcq-route-leak`; review-only `mcq-max-prefix` (what `maximum-prefix 1000` does when a customer sends a full table: the session is torn down, F8).
- `best-path`: `bgp-table-best`, `mcq-localpref-beats-path`, `mcq-med-other-as`; review-only `mcq-tie-older-path` (two paths equal to the last attribute: FRR keeps the older; why that makes a lab or a network behave differently from day to day).
- `local-preference`: `mcq-localpref-direction`, `localpref-table`; review-only `mcq-localpref-ibgp` (local preference set on edge 1 also steers edge 2 in the same AS, because it travels in iBGP; weight wouldn't).

## 10. Platform work first

The network-lab base (common brief F1) with `looking-glass` (N9) and `bgp-best` (N11). The CI spike (F2) uses this topic's worked example.

## 11. Cost and time

- **Money:** none.
- **Labs and CI:** 5 systemd labs, 26 wrong fixes; five routers per lab (edge, ispa, ispb, transit, cloud) plus three hosts; boot and convergence about 9 s per container. Estimated contract time: example 2.5 min, fill-in 3 min, write 3 min, build 5 min (eight wrong fixes and a failover check), debug 4.5 min: about 18 minutes of runner time.
- **Learner minutes:** lesson 15, reading 51 (B1 18, B3 11, B4 11, B5 11), recall 17 items 26, worked example 30, fill-in 20, write 25, build 55, debug 45, explain 20: **287, `estimated_minutes: 285`**.

## 12. Open questions

1. **Split topic 34?** Recommendation: yes (section 0).
2. **Should the learner be able to configure the ISP routers?** They have `sudo`, so they can. Recommendation: give them `looking-glass` (read-only) as the documented way to see the far side, say in each prompt that the far routers aren't theirs, and prove it with R6. This is how real BGP work feels and it makes "fix the other side" a rejectable shortcut.
3. **Real ASNs and addresses in the lesson?** The clouds' ASNs (7224, 12076, 16550) appear in 34b's lesson as facts; the labs use private ASNs and RFC 5737 addresses only. Recommendation: keep it so; nothing in a lab imitates a real organisation's network.

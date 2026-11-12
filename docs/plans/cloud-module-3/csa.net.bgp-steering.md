# Topic 34b (proposed): `csa.net.bgp-steering`, Steering traffic and cloud circuits

Designer's brief, 2026-11-11. This is the second half of the spec's topic 34; why it is split, and the spec text, are in [csa.net.bgp.md](csa.net.bgp.md), section 0. Shared lab pattern, findings ("finding N"), check recipes ("R1" to "R8") and base requirements ("N1" to "N11"): [frr-labs-common.md](frr-labs-common.md). Captured output: `prototypes/frr/CAPTURES.md` (the two-circuit and route-reflection prototypes).

## 1. What the learner will be able to do

- Make the rest of the world choose your preferred way in: a more-specific prefix, AS-path prepending, MED (between links to the same neighbour), and the communities a provider documents; and know which of these each cloud honours and in what order.
- Explain why routers inside one AS don't pass each other's BGP routes on, what a route reflector does about it, and the next-hop trap that comes with it; work out how many sessions a full mesh needs.
- Detect a failed link quickly: carrier loss against hold timer against BFD, and work out each one's detection time from the clouds' documented timers.
- Design and build two circuits to a cloud (Direct Connect, ExpressRoute, Cloud Interconnect) with one primary in both directions, a second circuit and a VPN as backups, within the provider's prefix limits.

**The six-month core.** Outbound: local preference (topic 34). Inbound: the longest prefix wins first; then whatever the provider honours (AWS: its local-preference communities, then AS path; Azure: AS path and more-specifics, never your communities; Google: MED as advertised-route priority). iBGP doesn't relay iBGP routes; a reflector does. A silent failure costs the hold time unless BFD is on (about a second). Exceeding a provider's prefix limit takes the session down.

## 2. Prerequisites and terms

**`prerequisites: [csa.net.bgp]`**.

**Builds on, for the writer.** `csa.net.bgp`: sessions, `network`, prefix lists, route maps, `show bgp`, the decision order, local preference, `looking-glass`, RFC 8212. `csa.net.routing`: longest-prefix match, the silent failure, floating statics (the static analogue of a backup circuit). `csa.net.cidr`: summarising eight /24s into one /21 (the build needs it).

**Terms this topic defines:** inbound and outbound traffic engineering; more-specific announcement; AS-path prepending; MED (multi-exit discriminator); community (standard, `ASN:VALUE`), the well-known `NO_EXPORT` and `NO_ADVERTISE` (RFC 1997), and provider-defined communities; aggregation (`aggregate-address ... summary-only`); the iBGP rule (routes learned from one iBGP peer aren't sent to another) and full mesh; route reflector, client, cluster, originator ID; next-hop-self; BFD (bidirectional forwarding detection), interval and multiplier; graceful restart (named); Direct Connect (connection, virtual interface: private, transit, public; Direct Connect gateway); ExpressRoute (circuit, private and Microsoft peering, MSEE, primary and secondary links); Cloud Interconnect (Dedicated and Partner, VLAN attachment, Cloud Router); associated Region (AWS); connection weight (Azure); advertised route priority and base priority (Google); active/active and active/passive; ECMP across circuits; a VPN as backup.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `inbound-steering` | Make another network choose your preferred entrance: a more-specific prefix (longest match beats every attribute), AS-path prepending (longer path, less preferred), MED (lower preferred, compared only between paths from one AS: use it toward one neighbour over two links), communities the neighbour documents (AWS's `7224:7100/7200/7300` become local preference on its side, evaluated before AS path); which tool works where, and why local preference on the far side beats your prepending |
| `route-reflection` | The iBGP rule and why it exists (loop prevention without AS_PATH); a full mesh needs n(n−1)/2 sessions; a route reflector passes client routes to other clients, marking originator and cluster; two reflectors for redundancy; next-hop-self at the edge so inside routers can resolve the next hop (FRR won't use a default route for that) |
| `failure-detection` | How fast each kind of failure is noticed: carrier loss at once (FRR's fast external failover: 73 ms in the prototype); a silent failure only when the hold time runs out (FRR's default 180 s, the labs' 9 s, AWS 90 s, Microsoft's edge 180 s); BFD in under a second or a few (AWS and Microsoft 300 ms × 3; Google 1,000 ms × 5 by default, and off unless enabled); the arithmetic of interval × multiplier; why graceful restart and BFD aren't used together on AWS |
| `cloud-circuits` | BGP over Direct Connect, ExpressRoute and Cloud Interconnect: whose ASN on each side (AWS 7224 on public VIFs, a private ASN such as the default 64512 on Direct Connect gateways; Microsoft 12076; Google's Cloud Router 16550 for Partner Interconnect), two sessions for redundancy (Microsoft requires both for its SLA; Google's 99.99% needs four attachments in two metros), prefix limits and what exceeding them does (AWS private VIF 100 by default, raisable to 1,000, session goes idle; Azure private peering 4,000, 10,000 with Premium, session drops), how to make a circuit primary in each direction on each cloud, a VPN as backup, and what each cloud's documentation says it ignores |

`route-reflection` and `failure-detection` are calculation skills: each has three or more estimate items (ADR-0024 rule 6).

## 4. Lesson plan

The lesson's own contribution: one diagram in words of "who decides which way traffic goes" (you decide your outbound; the other side decides your inbound; you can only influence it with what they listen to), the three clouds' rules in one table, and the timer arithmetic.

1. **Two directions, two deciders** (resources S2, NSRC's outbound and inbound traffic-engineering videos, 9 min). *Picture in words:* your router chooses how your packets leave (local preference, topic 34); the cloud's router chooses how its packets come back to you, from the routes you announced. You can't set its local preference; you can only change what you announce.
2. **The tools, strongest first.** A **more-specific prefix** on the preferred link (`10.1.0.0/24` on dx1, `10.1.0.0/23` on both) wins by longest match before any attribute. **Communities** the provider documents can set its local preference, which it compares before AS path. **AS-path prepending** makes one path longer. **MED** asks one neighbour AS to prefer one of your links to it; it compares only paths from the same AS, and it is near the bottom of the order. The prototype showed the order (finding 6 and `CAPTURES.md`): MED moved the cloud's choice when nothing else differed; prepending moved it when local preference was equal; a low-preference community beat a three-times prepend.
3. **Communities** (resource S7, RFC 1997, its definitions; FRR's community sections in S6). A label on a route, `ASN:VALUE`, meaningful only by agreement; `NO_EXPORT` ("don't pass outside your AS") and `NO_ADVERTISE` are well known. In FRR: `set community 64512:7300`, `bgp community-list`, `match community`.
4. **The clouds, side by side** (resources S1, S4, S5). The lesson's table:

   | | AWS Direct Connect | Azure ExpressRoute | Google Cloud Interconnect |
   | --- | --- | --- | --- |
   | Its ASN | 7224 on public VIFs; your choice of private ASN on the gateway (default 64512) | 12076 | Cloud Router: a private ASN, or 16550 for Partner Interconnect |
   | Redundancy | Two connections, ideally two locations | Two BGP sessions per peering, both required for the SLA | 99.99%: four VLAN attachments in two metros, two Cloud Routers |
   | Your prefixes it accepts | 100 per private or transit VIF by default (up to 1,000); 1,000 on public; more and the session goes idle | 4,000 on private peering (10,000 Premium), 100 IPv6; 200 per session on Microsoft peering; more and the session drops | a quota of unique prefixes per region and network; beyond it, routes are dropped |
   | To make it send to you on one circuit | Longest prefix, then your local-preference communities `7224:7100/7200/7300`, then AS path, then MED ("not recommended") | Longest prefix, then AS path (prepend); "Microsoft doesn't honor any community values" you send | Its routing uses the routes you advertise by MED and, in standard mode, AS path |
   | To prefer a circuit for traffic to it | Your local preference | Your local preference; for VNet-to-on-premises, connection weight, "considered before the AS Path length" | Your local preference; Google's advertised route priority (MED, base 100) tells your routers its preference |
   | BGP timers / BFD | Hold 90 s, keepalive 30 s; BFD 300 ms × 3, on by default on AWS's side | Microsoft's edge: keepalive 60 s, hold 180 s; BFD on by default, 300 ms (sometimes 750) | BFD off by default; 1,000 ms × 5 when on |

   One AWS subtlety that the build uses: with no community, AWS gives a location in the circuit's associated Region medium local preference and others a lower one, so prepending can't override it; only a community can.
5. **Inside your own AS: route reflection** (resource S3, NSRC's route-reflector video, 7 min; S6's route-reflector section). eBGP stops loops with the AS path; iBGP can't (every router has the same AS), so a router never passes an iBGP-learned route to another iBGP peer. Every router must then peer with every other: n(n−1)/2 sessions, 45 for ten routers. A **route reflector** is allowed to pass client routes on, adding `Originator` and `Cluster list` to stop loops (the prototype's captured output). Two reflectors so one can fail. The **next-hop trap**: a reflected route keeps the edge router's next hop, which an inside router must be able to reach; FRR won't resolve it through a default route, so the edge sets `next-hop-self` or the inside routers carry routes to the links (the prototype used static routes).
6. **Noticing failure** (resource S8, AWS's BGP settings table; S4's BFD page). A link that loses carrier is noticed at once; one that dies silently is noticed when the hold timer runs out: 9 s in the labs, 90 s on AWS by default, up to 180 s on Microsoft's side, during which traffic is lost. BFD exchanges tiny packets every few hundred milliseconds and declares the path dead after a few are missed: detection time is interval × multiplier, 300 ms × 3 = 0.9 s. The prototype: 11.2 s without BFD, 1.08 s with it.
7. **Designing two circuits and a VPN.** Primary and secondary in both directions; the VPN last (AWS itself prefers Direct Connect routes over VPN routes for the same prefix, topic 26's priority list); summarise to stay under the prefix limit; BFD on. A real circuit is weeks of lead time and a monthly bill: this topic models them with FRR, as the spec's "stand-ins for what one person can't buy" says; Module 11 (`csa.cnet.hybrid`) builds a VPN with BGP to a real cloud.

**Read now:** S2 (9), S1 (12), S4's routing and optimize-routing pages (11), S5 (6), S3 (7). S6, S7 and S8 are reference.

## 5. Verified facts

Each read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| F1 | AWS private and transit VIFs: longest prefix first; local preference via communities `7224:7100` low, `7224:7200` medium, `7224:7300` high, "evaluated before any AS_PATH attribute"; without a community, locations in the associated Region get medium (7200) and others a lower value; then AS_PATH length; then MED ("AWS does not recommend using MED values given their lower priority"); ECMP across VIFs with equal attributes; a route whose AS_PATH contains 7224 twice is treated as a loop | https://docs.aws.amazon.com/directconnect/latest/UserGuide/routing-and-bgp.html |
| F2 | AWS public VIFs: AWS ASN 7224; private ASNs 64512–65534 and 4200000000–4294967294 allowed and replaced by 7224 (so prepending a private ASN is stripped); all routes from AWS carry `NO_EXPORT`; scope communities `7224:9100` (local Region), `9200` (continent), `9300` (global) | F1's page |
| F3 | Direct Connect quotas: routes per BGP session on a private or transit VIF "Default of 100 each for IPv4 and IPv6", up to 1,000 with prefix controls; above it "the BGP session will go into an idle state"; 1,000 on a public VIF | https://docs.aws.amazon.com/directconnect/latest/UserGuide/limits.html |
| F4 | Direct Connect BGP settings: default hold timer 90 s, minimum 3 s; default keepalive 30 s; BFD minimum interval 300 ms, multiplier 3; graceful restart 120 s, "We recommend that you do not configure graceful restart and BFD at the same time"; BGP TTL 1 (no multihop) | https://docs.aws.amazon.com/directconnect/latest/UserGuide/bgp-specific-settings.html |
| F5 | The default Amazon-side ASN 64512 for a Transit Gateway and a Direct Connect gateway ("if you use the default ASN 64512 for both ... the association request fails") | https://docs.aws.amazon.com/directconnect/latest/UserGuide/create-vif.html |
| F6 | ExpressRoute: Microsoft uses AS 12076 (65515 to 65520 reserved); two BGP sessions per peering, "You must set up both BGP sessions for the availability SLA to be valid"; /30 per link, first address yours; 4,000 IPv4 prefixes on private peering (10,000 with Premium), 100 IPv6, 200 per session on Microsoft peering; "The BGP session drops if the number of prefixes exceeds the limit"; "Microsoft doesn't honor any community values tagged to routes advertised to Microsoft"; regional communities such as East US `12076:50004` (private) and `12076:51004` (Microsoft peering) | https://learn.microsoft.com/en-us/azure/expressroute/expressroute-routing (ms.date 2026-08-27) |
| F7 | ExpressRoute optimise routing: AS-path prepending or advertising prefixes on the right circuit for Microsoft-to-customer traffic; local preference on your side for customer-to-Microsoft ("The default local preference is typically 100"); "The connection weight is considered before the AS Path length" for VNet to on-premises | https://learn.microsoft.com/en-us/azure/expressroute/expressroute-optimize-routing (ms.date 2025-01-31) |
| F8 | ExpressRoute BFD: MSEE "BGP keep-alive and hold-time are typically configured as 60 and 180 seconds"; BFD configured by default on new peerings; MSEE intervals 300 ms, "In certain scenarios ... 750 milliseconds"; example `bfd interval 300 min_rx 300 multiplier 3` | https://learn.microsoft.com/en-us/azure/expressroute/expressroute-bfd (ms.date 2026-03-12) |
| F9 | Google Cloud Router: BGP speaker only, "Cloud Routers don't provide packet routing or forwarding capability"; supports BFD | https://docs.cloud.google.com/network-connectivity/docs/router/concepts/overview |
| F10 | Google: "you define a base advertised priority that is used as a value for the BGP MED attribute", default 100; other regions' subnets get the base plus an inter-region cost | https://docs.cloud.google.com/network-connectivity/docs/router/concepts/advertised-routes |
| F11 | Google learned routes: lowest MED preferred; in legacy best-path mode "the dynamic route control plane doesn't use the AS path information", in standard mode AS path is considered; quotas on unique dynamic route prefixes per region per network, prefixes beyond them dropped | https://docs.cloud.google.com/network-connectivity/docs/router/concepts/learned-routes |
| F12 | Google BFD: disabled by default; transmit and receive intervals 1,000 ms by default (1,000 to 30,000); multiplier 5 by default (5 to 16) | https://docs.cloud.google.com/network-connectivity/docs/router/concepts/bfd |
| F13 | Google Partner Interconnect: Cloud Routers use ASN 16550; 99.99% "requires at least four VLAN attachments across two metros" and two Cloud Routers | https://docs.cloud.google.com/network-connectivity/docs/interconnect/tutorials/partner-creating-999-availability (via search, 2026-11-11) and https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/partner-overview |
| F14 | RFC 4456: without reflection, iBGP speakers in an AS "must be fully meshed"; route reflection as the alternative | https://www.rfc-editor.org/rfc/rfc4456 |
| F15 | RFC 1997: `NO_EXPORT` (0xFFFFFF01), `NO_ADVERTISE` (0xFFFFFF02) | https://www.rfc-editor.org/rfc/rfc1997 |
| F16 | FRR: `neighbor PEER route-reflector-client`; clusters; `set as-path prepend`; `set community`; MED compared "Where routes with a MED were received from the same AS"; `neighbor PEER maximum-prefix NUMBER` destroys the session when exceeded | https://docs.frrouting.org/en/stable-8.4/bgp.html |
| F18 | In FRR 8.4, `neighbor X maximum-prefix 5 restart 1` with eight prefixes received: the session goes `Idle (PfxCt)`, the receiver logs `Notification sent (Cease/Maximum Number of Prefixes Reached)` and "will restart in 51 seconds" (8 s after the teardown), the sender `Notification received (Cease/Maximum Number of Prefixes Reached/Hard Reset)`; re-establishment after the minute was not timed | prototype (`circuits/`, `CAPTURES.md`) |
| F17 | In FRR 8.4: MED 50 beat MED 100 when all else was equal; a prepend moved the choice when local preference was equal; a low-preference community beat a three-times prepend; carrier-loss failover 73 ms; silent failure 11.2 s with 9 s hold; 1.08 s with BFD 300 ms × 3; a new route-reflector client got routes 4.3 s later; reflected routes carried `Originator` and `Cluster list` | prototype (`circuits/`, `rr/`) |

## 6. Resources

All opened on 2026-11-11; linked, never copied.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 (main) | AWS, "Direct Connect routing policies and BGP communities" | https://docs.aws.amazon.com/directconnect/latest/UserGuide/routing-and-bgp.html | reading | Copyright Amazon Web Services; linked | 12 | `inbound-steering`, `cloud-circuits` | 2026-11-11 |
| S2 | NSRC, "Outbound Traffic Engineering" and "Inbound Traffic Engineering" | https://www.youtube.com/watch?v=YrRALAz2F3E and https://www.youtube.com/watch?v=M8zWe5NPHc0 | video (6:39 and 2:00, 2019-04-01, embeddable) | Creative Commons Attribution (YouTube's licence field, both) | 9 | `inbound-steering` | 2026-11-11 |
| S3 | NSRC, "BGP Scaling Techniques: Route Reflector Deployment" | https://www.youtube.com/watch?v=GLHlODwn8vU | video (7:18, 2019-04-12, embeddable) | Creative Commons Attribution | 7 | `route-reflection` | 2026-11-11 |
| S4 | Azure ExpressRoute: "Routing requirements" (ASN, prefix limits, communities, transit), "Optimize routing" and "Configure BFD" | https://learn.microsoft.com/en-us/azure/expressroute/expressroute-routing, .../expressroute-optimize-routing, .../expressroute-bfd | reading | CC BY 4.0 (MicrosoftDocs/azure-docs) | 14 | `cloud-circuits`, `failure-detection` | 2026-11-11 |
| S5 | Google Cloud Router, "Advertised routes" (with "Learned routes" and "BFD" for reference) | https://docs.cloud.google.com/network-connectivity/docs/router/concepts/advertised-routes | reading | CC BY 4.0 | 6 | `cloud-circuits` | 2026-11-11 |
| S6 | FRR 8.4 user guide, BGP: "Route Reflector", "Communities Attribute", "Using Communities in Route Maps", "Multi-Exit Discriminator" (its first part) | https://docs.frrouting.org/en/stable-8.4/bgp.html | reference | FRR's documentation licence (custom, permissive); linked | 10 | `route-reflection`, `inbound-steering` | 2026-11-11 |
| S7 | RFC 1997, "BGP Communities Attribute" | https://www.rfc-editor.org/rfc/rfc1997 | reading (short) | IETF Trust; linked | 5 | `inbound-steering` | 2026-11-11 |
| S8 | AWS, "BGP-specific settings" (Direct Connect's timers and BFD) | https://docs.aws.amazon.com/directconnect/latest/UserGuide/bgp-specific-settings.html | reference | Copyright Amazon Web Services | 2 | `failure-detection` | 2026-11-11 |
| S9 | LearnCantrill, "BGP Communities" (AWS-focused) | https://www.youtube.com/watch?v=1pKXkwf2FgM | video (7:50, 2022-07-07, embeddable) | Standard YouTube licence | 8 | `inbound-steering`, `cloud-circuits` | 2026-11-11 |

## 7. Practice ladder

**The two circuits** (example, write, build; `prototypes/frr/circuits/`): `edge` (AS 65001, the learner's router; `lan` 10.1.0.1/24 with `office` 10.1.0.10) and `cloud` (AS 64512; `vpc` 10.100.0.0/16 with `app` 10.100.0.10) joined by `dx1` and `dx2`, two /30 links standing in for two circuits. Addresses are chosen so that **dx2 wins every tie** (its addresses are the lower ones), so no lab's "make dx1 primary" passes unchanged (finding 7). The cloud router is configured and saved, and stands for one provider's documented behaviour, which each prompt states and links: the **AWS-like** cloud turns `64512:7100/7200/7300` into local preference 100/200/300 and gives dx2 (its "associated Region") 200 and dx1 150 when no community is sent; the **Azure-like** cloud ignores communities and MED (its inbound route map strips them) and has a maximum-prefix limit. `looking-glass cloud 'show ...'` reads it.

**The data centre** (fill-in and debug; `prototypes/frr/rr/`, extended): AS 65001 with `access` (the office behind it), `core`, `dc1` (dx1) and `dc2` (dx2), iBGP on the links access–core, core–dc1, core–dc2 only; static routes for the links inside the AS (no IGP), so next hops resolve.

1. **`example-two-circuits`** (worked example, systemd, AWS-like cloud; edge has both sessions and its own prefix, nothing else). Labelled steps:
   1. *Who wins now.* `show bgp ipv4 unicast 10.100.0.0/16` on edge: dx2 wins the tie. `looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'`: dx2 wins there too, by local preference 200 against 150.
   2. *Outbound: dx1 first.* A route map setting local preference 300 on dx1's routes; edge's `ip route get 10.100.0.10` now names dx1.
   3. *Inbound, three tries.* MED 50 on dx1 and 100 on dx2: the cloud doesn't move (its local preference is compared first). Prepend twice toward dx2: still no (local preference again). Community `64512:7300` on dx1: it moves. The learner reads `selectionReason` each time.
   4. *Failure, loud and silent.* `lab-link edge dx1 down`: office still reaches app within a second; `lab-link edge dx1 up`. `lab-link edge dx1 silent`: about ten seconds of loss (hold time 9 s); `lab-link edge dx1 restore`.
   5. *BFD.* `bfdd=yes` is already in the daemons file; a `bfd` profile of 300 ms × 3 on both sessions (the cloud already runs BFD, as AWS does on its side); `show bfd peers`; the silent cut again: about one second.
   6. *Save* (`write memory`).
   Checks: edge's best to 10.100.0.0/16 is dx1 (R4) and the kernel agrees (R1); the cloud's best to 10.1.0.0/24 is dx1 with local preference 300; BFD peers up on both sessions; a silent cut of dx1 is survived within 3 s (R5); saved (R2). Wrong fixes: `prepend-only.sh`, `no-bfd.sh`, `not-saved.sh`.
2. **`mcq-who-decides-inbound`** (mcq, `inbound-steering`). The shop wants traffic **from** the cloud to arrive on circuit 1. Which setting on the shop's router decides it? Right: "None directly: the cloud decides; the shop can only change what it announces". Wrong: "Local preference on routes learned over circuit 1"; "Weight on the session over circuit 1"; "A lower IGP cost toward circuit 1's router". Explanation: each wrong one changes outbound only.
3. **`mcq-more-specific-wins`** (mcq, `inbound-steering`). The shop announces 10.1.0.0/23 over both circuits and 10.1.0.0/24 over circuit 1 only; the cloud gives circuit 2 a higher local preference. Traffic from the cloud to 10.1.0.20 arrives over: Right: "circuit 1: the /24 is longer, and prefix length comes before any attribute". Wrong: "circuit 2, because the cloud's local preference for it is higher"; "both, because the /23 and the /24 share the traffic"; "circuit 2, because the /23 was announced first".
4. **`mcq-med-scope`** (mcq, `inbound-steering`). When does MED help? Right: "To ask one neighbour AS to prefer one of two links you have to it". Wrong: "To ask every provider on the internet to prefer one of your providers"; "To make your own routers prefer one exit over another"; "To ask a neighbour to drop routes it shouldn't pass on".
5. **`mcq-prepend-loses`** (mcq, `inbound-steering`, AWS facts). The shop prepends three times on its backup Direct Connect VIF, and AWS still sends traffic down it. Why? Right: "The backup's location is in the associated Region, so AWS gives it higher local preference, which comes before AS path". Wrong: "AWS strips prepending from private ASNs on every kind of virtual interface"; "AWS compares MED before AS path, and both paths have MED 0"; "Prepending only works when it uses the provider's own ASN". (The second wrong answer is true for **public** VIFs (F2), which makes it a strong distractor; the explanation says so and what fixes it: a `7224:7100` or `7224:7300` community.)
6. **`mcq-azure-communities`** (mcq, `cloud-circuits`). A design tags the backup ExpressRoute circuit's routes with a low-preference community, as it does on AWS. What does Azure do? Right: "It ignores the community; prepend on the backup or announce more-specifics on the primary". Wrong: "It maps the community to its own local preference, as AWS does"; "It rejects the routes, because Azure accepts no communities at all"; "It honours the community only on Microsoft peering, not private peering".
7. **`mcq-gcp-priority`** (mcq, `cloud-circuits`). Google's Cloud Router advertises the VPC's subnets with "advertised route priority" 100 on one attachment and 200 on another. What should the on-premises router do with that? Right: "Treat it as MED: prefer the attachment advertising 100". Wrong: "Treat it as local preference: prefer the attachment advertising 200"; "Ignore it: it only orders routes inside Google's VPC"; "Treat it as weight, which stays on the Cloud Router".
8. **`communities-table`** (predict_shell, `inbound-steering`, captured). File: the captured cloud table with LocPrf 300 and 100. Command prints the best next hop and its LocPrf (the writer pins the `awk`). Explanation: the community became local preference on the far side.
9. **`est-full-mesh`** (estimate, `route-reflection`). "An AS has 12 routers that run BGP with each other, all in a full mesh. How many iBGP sessions is that? Exactly." `given: {n: 12}`, `working: n * (n - 1) / 2`, 66. Mistakes: 132 (`n * (n - 1)`: "each session counted from both ends"), 11 (`n - 1`: "that's one router's sessions").
10. **`est-two-reflectors`** (estimate, `route-reflection`). "The same 12 routers: 2 become route reflectors, peered with each other, and each of the other 10 peers with both reflectors only. How many sessions? Exactly." `working: 2 * clients + 1` with `given: {clients: 10}`, 21. Mistakes: 20 (forgot the reflectors' session with each other), 66 (the full mesh).
11. **`est-sessions-saved`** (estimate, `route-reflection`). "20 routers: a full mesh, or 2 reflectors serving the other 18. How many sessions does the reflector design save? Exactly." `working: 20 * 19 / 2 - (2 * 18 + 1)`, 153. Mistakes: 154 (no session between the reflectors), 343 (`20 * 19 - 37`).
12. **`mcq-ibgp-rule`** (mcq, `route-reflection`, captured). r1 learns the cloud's routes by eBGP and passes them to r2 by iBGP; r3 peers only with r2 and has nothing. Right: "r2 won't pass a route it learned by iBGP to another iBGP peer". Wrong: "r3 drops the routes because their AS path contains its own AS"; "r2 passes them on only after its hold timer expires once"; "r1's routes need `send-community` before r2 can forward them".
13. **`mcq-next-hop-self`** (mcq, `route-reflection`). After reflection, r3 has the cloud's route but `show bgp` marks it not valid and it isn't installed; r3 has a default route to r2. Right: "r3 can't resolve the route's next hop, the cloud's link address; FRR won't use a default route for that". Wrong: "r3 rejects reflected routes unless it is a reflector too"; "The route's originator ID equals r3's router ID, so it is ignored"; "r3 needs `bgp bestpath compare-routerid` to install reflected routes". Explanation: `next-hop-self` on r1, or routes to the links.
14. **`est-bfd-aws`** (estimate, `failure-detection`). "BFD on a Direct Connect VIF with a 300 ms interval and a multiplier of 3. How many milliseconds after the last packet does BFD declare the link down? Exactly." `working: interval * mult`, 900. Mistakes: 300 (interval only), 100 (`interval / mult`).
15. **`est-bfd-google`** (estimate, `failure-detection`). "Google Cloud Router BFD at its defaults: 1000 ms interval, multiplier 5. Detection time in seconds? Exactly." `working: interval * mult / 1000`, 5. Mistakes: 5000 (the unit: the box asks for seconds), 1.
16. **`est-hold-vs-bfd`** (estimate, `failure-detection`). "A circuit to Azure dies silently just after a keepalive arrived. Microsoft's edge uses a 180 s hold time; with BFD at 300 ms × 3 instead, how many seconds sooner is the failure detected, at most? Within 1 second." `working: hold - interval * mult / 1000`, 179.1. Mistakes: 177 (`hold - 3`: "used the hold timer's minimum"), 120 (`hold - 60`: "subtracted the keepalive"). Tolerance 1 keeps 179 and 179.1 right.
17. **`mcq-silent-failure-bgp`** (mcq, `failure-detection`, captured timings). Two circuits, BGP with hold time 9 s, no BFD. The provider's equipment fails with your interface still up. Right: "Traffic is lost for up to 9 s, then BGP moves to the other circuit". Wrong: "Traffic moves within a second, as when a cable is pulled"; "Traffic is lost until someone clears the BGP session"; "Traffic moves after 9 s, but only if graceful restart is on".
18. **`mcq-prefix-limit`** (mcq, `cloud-circuits`). A data centre announces 140 prefixes to AWS over a private VIF with the default limit. Right: "The session goes idle and no routes are exchanged until fewer are sent (or the limit is raised)". Wrong: "AWS accepts the first 100 and ignores the rest"; "AWS summarises them into fewer, larger prefixes itself"; "AWS accepts all 140 and raises an alarm". Explanation: summarise (`aggregate-address`), F3; Azure's limit is 4,000 and also drops the session (F6).
19. **`est-summarise`** (estimate, `cloud-circuits`). "A site uses the 8 networks 10.40.0.0/24 to 10.40.7.0/24 and must announce them to a provider as one prefix. What is that prefix's length? Exactly." `given: {len: 24, count: 8}`, `working: len - 3` (3, the number of bits that count 8 networks, written in as a known number), 21. Mistakes: 16 (`len - count`), 27 (`len + 3`: "a shorter prefix covers more; /27 covers less than one /24"). (It uses `csa.net.cidr`'s skill for `cloud-circuits`.)
20. **`fill-route-reflector`** (fill-in, systemd, the data centre with core not yet a reflector). `/etc/frr/core/frr.conf` with gaps: the reflector-client lines for access, dc1 and dc2 (three gaps of one word each); and dc1's `next-hop-self` toward core is given, dc2's is a gap. Checks: access's BGP table holds the cloud's prefix with a valid, installed path (R4, R1); office reaches app; with dx1 cut, office still reaches app via dc2 (R5); access has exactly one BGP neighbour (core); saved on core and dc2 (R2). Wrong fixes: `client-on-access-only.sh` (dc1's routes reach access, dc2's don't: the cut fails), `no-next-hop-self-dc2.sh` (the cut fails: access can't resolve dc2's routes' next hop), `mesh-instead.sh` (access peers with dc1 and dc2 directly: the one-neighbour check fails), `not-saved.sh`.
21. **`write-azure-style`** (write, systemd, the Azure-like cloud). From nothing beyond the two sessions: make dx1 primary in both directions, using only what the Azure-like cloud honours (the prompt quotes F6 and F7: no communities, so AS path and prefix length), with the shop's prefix the only one announced. Checks: edge's best to the cloud via dx1 (local preference) and the kernel agrees; the cloud's best to 10.1.0.0/24 via dx1 (by AS path, since dx2 wins ties); with dx1 cut, both directions use dx2, and dx1 again when restored (R5); the cloud received only 10.1.0.0/24 on each session; policy kept (R7); saved. Wrong fixes: `communities-only.sh` (stripped by the cloud: it stays on dx2), `med-only.sh` (stripped too), `prepend-dx1.sh` (prepends the wrong circuit), `not-saved.sh`.

Recall items in practice: 18 (items 2 to 19). Labs: 3.

## 8. Proofs

### Build: `build-primary-and-backup` (systemd, 60 minutes)

The two circuits with the AWS-like cloud, plus a third link `vpn` (169.254.30.0/30) standing in for a site-to-site VPN; the cloud gives VPN-learned routes local preference 50 (AWS prefers Direct Connect routes over VPN routes, F1 and topic 26's priority list) and accepts at most **5 prefixes per session**, tearing the session down above that and retrying after a minute (a scaled-down Direct Connect limit, stated as such). Edge has the office's eight networks, 10.1.0.0/24 to 10.1.7.0/24, as eight addresses on its `lan` (so eight connected routes; `office` is 10.1.0.10), sessions configured on all three links, no policy. A learner who trips the cloud's limit while working waits a minute for the cloud's retry; the check's failure message says so.

**Prompt (summary).**

1. circuit 1 (dx1) carries traffic in both directions while it's up; circuit 2 (dx2) when dx1 is down; the VPN only when both circuits are down;
2. use what the cloud's documentation offers (it is modelled on AWS Direct Connect: the prompt quotes F1's community list and the associated-Region rule);
3. announce the office's networks and nothing else, within the cloud's limit of 5 prefixes per session;
4. a circuit that fails silently must be noticed within 3 seconds;
5. keep eBGP's policy requirement; don't change the cloud's router; save.

**Checks.**

| id | Tests | Skill |
| --- | --- | --- |
| `sessions-up` | Three sessions Established, and each has been up for longer than this check's 10-second wait (no flapping) | `cloud-circuits` |
| `announced-within-limit` | The cloud accepted from edge, on each session, at most 5 prefixes, and between them they cover all eight office networks and nothing outside 10.1.0.0/21 | `cloud-circuits` |
| `outbound-order` | Edge's best path to 10.100.0.0/16 is via dx1, and the kernel agrees | `cloud-circuits` |
| `inbound-order` | The cloud's best path to every office network is via dx1 | `inbound-steering` |
| `bfd` | BFD peers up on dx1 and dx2 | `failure-detection` |
| `policy-kept`, `saved`, `cloud-untouched` | R7, R2, R6 | `cloud-circuits` |
| `failover-order` | Cut dx1: both directions on dx2 within 3 s; cut dx2 too: both directions on the VPN within 3 s; restore both: back on dx1 within 15 s (R5, `timeout: 90`) | `cloud-circuits`, `failure-detection` |
| `silent-failure` | `lab-link silent` on dx1: office reaches app again within 3 s; restore (R5, `timeout: 60`, last) | `failure-detection` |

**Wrong fixes:** `prepend-only.sh` (inbound stays on dx2: the cloud's local preference for dx2 beats prepending), `med-only.sh`, `communities-swapped.sh` (`7300` on dx2: inbound on dx2), `no-summary.sh` (eight /24s: the cloud tears the sessions down: `sessions-up` fails), `vpn-preferred-outbound.sh` (local preference highest on the VPN), `no-bfd.sh` (silent failure takes about 11 s), `policy-off.sh`, `not-saved.sh`.

### Debug: `debug-wrong-circuit` (systemd, 45 minutes)

The data centre (access, core, dc1, dc2) with the **Azure-like** cloud (ignores communities and MED; at most 10 prefixes per session, retry after a minute).

**The system, stated:** the office sits behind `access`, which peers only with `core`; `core` is the route reflector for access, dc1 and dc2; dc1's circuit (dx1) is the primary in both directions and dc2's (dx2) the backup; each data-centre router announces the data centre's networks summarised; the cloud follows ExpressRoute's documented behaviour (the prompt links F6 and F7).

**Symptoms, stated:** traffic from the cloud to the data centre arrives over the backup circuit; since core was rebuilt last week the office can't reach anything in the cloud; and the backup circuit's session goes down every couple of minutes and comes back. **Three faults.**

**The faults** (author's eyes only):

1. dc2 tags its routes with a low-preference community (copied from the AWS design) and doesn't prepend: the Azure-like cloud ignores the community and prefers dx2 on the tie (`inbound-steering`, `cloud-circuits`).
2. core has lost `route-reflector-client` for access: access learns nothing (`route-reflection`).
3. dc2 announces its twelve /24s instead of the summary: above the cloud's 10, the session is torn down and retried every minute; `show bgp neighbors` on dc2 shows the Cease notification for the maximum prefix count (`cloud-circuits`).

**Rules of the fix, stated:** the cloud's router isn't yours; access keeps one BGP neighbour; keep eBGP's policy requirement; announce only the data centre's own space; save.

**Checks:** `inbound-on-dx1` (the cloud's best to the data centre's summary via dc1) `inbound-steering`; `office-reaches-cloud` (and access's table has a valid, installed route; access has exactly one neighbour) `route-reflection`; `dx2-stable` (dc2 sends at most 10 prefixes and its session is Established after up to 75 s of waiting for the cloud's retry: `timeout: 90`) `cloud-circuits`; `failover` (cut dx1: both directions on dx2, restore: back) `cloud-circuits`; `policy-kept`, `saved` on core and dc2, `cloud-untouched`.

**Wrong fixes:** `community-still.sh`, `prepend-dx1.sh` (the wrong circuit made longer), `mesh-instead.sh` (access peers with dc1 and dc2), `raise-cloud-limit.sh` (edits the cloud's maximum-prefix: `cloud-untouched` fails), `no-summary.sh`, `not-saved.sh`.

### Explain (20 minutes)

**Prompt.** Your company is connecting its data centre to one cloud with two dedicated circuits and a VPN, and to keep the network small it has four routers that run BGP. Explain, in your own words: how you'd make one circuit carry traffic in both directions and the other take over, and why the two directions need different tools; how this differs between two of AWS, Azure and Google Cloud; why the routers inside your company can't simply pass each other the cloud's routes, and what you'd do about it; how quickly a failed circuit would be noticed, with and without BFD, with numbers; and what happens if you announce more prefixes than the provider accepts.

**Rubric.**

| id | Required | Description |
| --- | --- | --- |
| `two-directions` | yes | Outbound is your decision (local preference on routes learned over the primary); inbound is the provider's, influenced only by what you announce: a more-specific prefix first, then what the provider honours (documented communities, prepending, MED to one neighbour) |
| `clouds-differ` | yes | Two clouds correctly: AWS honours its local-preference communities (7224:7100/7200/7300) before AS path, and its associated-Region rule defeats prepending alone; Azure ignores your communities, so prepend or announce more-specifics, with connection weight for VNet-to-on-premises; Google uses advertised route priority as MED (base 100), and its learned-route choice uses MED and, in standard mode, AS path |
| `reflection` | yes | iBGP doesn't pass iBGP-learned routes on; a full mesh needs n(n−1)/2 sessions; route reflectors (two, for redundancy) pass client routes on; the next hop must be reachable inside (next-hop-self) |
| `detection` | yes | Carrier loss is noticed at once; a silent failure only when the hold time runs out (90 s on AWS by default, 180 s on Microsoft's side); BFD at 300 ms × 3 detects in about a second; Google's BFD is off unless enabled (1 s × 5) |
| `limits` | no | Exceeding the provider's prefix limit takes the session down (AWS private VIF 100 by default, session idle; Azure 4,000, session drops), so summarise |

## 9. Review pool

Fourteen items, at least two per skill:

- `inbound-steering`: `mcq-more-specific-wins`, `mcq-prepend-loses`, `communities-table`; review-only `mcq-no-export` (what `NO_EXPORT` on a route sent to a provider does: the provider keeps it inside its own AS).
- `route-reflection`: `est-full-mesh`, `est-two-reflectors`, `mcq-next-hop-self`; review-only `est-sessions-saved`.
- `failure-detection`: `est-bfd-aws`, `est-hold-vs-bfd`, `mcq-silent-failure-bgp`; review-only `est-bfd-google`, review-only `est-bfd-750` ("Microsoft's edge sometimes uses 750 ms; with a multiplier of 3, detection in seconds?" 2.25; mistakes 0.75 and 0.25).
- `cloud-circuits`: `mcq-azure-communities`, `mcq-prefix-limit`, `mcq-gcp-priority`.

## 10. Platform work first

The network-lab base (common brief F1) with BFD available (`bfdd=yes` in a router's daemons file; nothing to install), `lab-link silent` (N8), `looking-glass` and `bgp-best`. The cloud models' behaviours are route maps in the cloud router's saved configuration (scenery), so nothing new is needed in the platform.

## 11. Cost and time

- **Money:** none. No circuit, VPN or Cloud Router is created; the three clouds' behaviours are read from their documentation and modelled.
- **Labs and CI:** 5 systemd labs, 25 wrong fixes. The build's failover checks (`timeout: 90` and `60`) and the debug's wait for the cloud's one-minute retry make these the slowest labs of the four topics: estimated contract time example 3 min, fill-in 3 min, write 3 min, build 7 min, debug 6 min: about 22 minutes of runner time. Within the 600-second limit per lab (ADR-0018): the build's checks add up to 90 + 60 + 9 × 30 = 420 s at most.
- **Learner minutes:** lesson 15, reading 48 (S2 9, S1 12, S4's parts 11, S5 6, S3 7, S8 3), recall 18 items 27, worked example 35, fill-in 20, write 25, build 60, debug 45, explain 20: **295, `estimated_minutes: 295`**.

## 12. Open questions

1. **Model the clouds' rules in the cloud router, or only teach them?** Recommendation: model them, one cloud per lab, with the rule quoted and linked in the prompt (the AWS-like and Azure-like clouds above). The learner then meets the real consequence (prepending that doesn't work against AWS's associated-Region preference; communities that do nothing on Azure) instead of memorising a table, which is the best learning experience under the owner's rule. The lab never pretends to be the provider: it says "modelled on".
2. **Google in a lab too?** Recommendation: no third model; Google appears in the lesson, recall items and the explain. Google's interesting difference (MED as advertised priority, best-path mode) is a fact about what Google tells you, which recall tests well; a third cloud model adds a lab without a new skill.
3. **Should topic 35 (`csa.net.ipsec`) depend on this topic?** Recommendation: on `csa.net.bgp` only; its designer may add this topic if the IPsec build uses a VPN as a circuit's backup, which this build already practises with a plain link.

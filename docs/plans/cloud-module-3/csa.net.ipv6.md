# Topic 25: `csa.net.ipv6`, IPv6

Designer's brief, 2026-11-11 (key `layers-cidr-ipv6`, with `csa.net.layers` and `csa.net.cidr`). Prototypes: `prototypes/layers-cidr-ipv6/` (folder `d25/` is this topic's debug lab, run end to end with its restart trial and seven wrong fixes; `topo-25.sh` is the first exploration). The network-lab base is another designer's; section 10 says what these labs need from it.

## 1. What the learner will be able to do

- Read and write IPv6 addresses: eight groups of four hex digits, the short form's rules (leading zeros go, one `::` for the longest run of zero groups, lower case), prefixes on nibble boundaries.
- Tell the address kinds apart on sight (global, link-local `fe80::`, unique local `fd..`, multicast `ff..`, loopback, documentation) and say what each is for; say why IPv6 has no broadcast and what replaces ARP.
- Plan IPv6 addressing: a /48 per site, a /64 per subnet, readable hex digits for region, zone and tier, and count what a prefix holds; fit the plan to each cloud's sizes.
- Explain how a host configures itself (router advertisements, SLAAC, duplicate address detection, a default route to the router's link-local address), and run dual stack: both families on every interface, clients preferring IPv6 and falling back fast, one firewall table for both.
- Explain why IPv6 egress doesn't need NAT, what gives the same "nobody can call in" protection (a stateful firewall: AWS's egress-only internet gateway), where a cloud does translate anyway (Azure), and why ICMPv6 must not be blocked.
- Find and fix the classic "IPv4 works, IPv6 doesn't" faults: a router advertising the wrong prefix length, IPv6 forwarding off, ICMPv6 dropped.

**The six-month core.** Read an IPv6 address, expand and shorten it. /48 site, /64 subnet, always; a /48 holds 65,536 subnets. SLAAC needs a /64 in the router advertisement, and the default route points at a link-local address. No NAT for IPv6 egress: a stateful firewall does the protecting. Never drop Packet Too Big. Azure is the cloud that translates IPv6 anyway.

## 2. Prerequisites and terms

**`prerequisites: [csa.net.cidr]`** (prefix arithmetic and planning are this topic's foundation; `csa.net.layers` comes through it: ARP, ICMP, MTU and path MTU discovery, which IPv6 builds on).

**Builds on, for the writer:**

| Topic | What this topic leans on |
| --- | --- |
| `csa.linux.net-tools` | `ip -br addr` (its recall item `net-ip-addr-up` already showed `fe80::1a2b:3c4d:5e6f:7a8b/64` and called it "the link-local IPv6 address, present on every interface"); `ip route`; nftables' `inet` table "covers IPv4 and IPv6 at once"; `ct state established,related accept`; `masquerade` named; `dig` with A records |
| `csa.hw.windows-ad` | DNS, resolver, record (A, SRV, PTR) defined; this topic adds the AAAA record |
| `csa.net.layers` | hex digits and bytes; ARP and the neighbour table; ICMP and its types; MTU; path MTU discovery and the black hole; captures read field by field |
| `csa.net.cidr` | prefix length and block size as powers of two; splitting and summarising; overlaps; bash `$(( ))` and `printf` |

**Terms this topic must define itself:** IPv6; hextet (a group; the word is optional, "group" is enough); nibble (one hex digit, 4 bits); the short form (RFC 5952); global unicast address; link-local address and the zone index (`%eth0`); unique local address (ULA); multicast, all-nodes `ff02::1`, all-routers `ff02::2`, solicited-node multicast; loopback `::1` and unspecified `::`; documentation prefixes `2001:db8::/32` and `3fff::/20`; interface identifier; EUI-64 (one paragraph); stable and temporary (privacy) addresses, in two sentences; Neighbor Discovery (NDP) and its messages: router solicitation (RS, 133), router advertisement (RA, 134), neighbor solicitation (NS, 135), neighbor advertisement (NA, 136), redirect (137); SLAAC; duplicate address detection (DAD); DHCPv6 (one sentence: the alternative the labs don't use); `radvd`; prefix delegation (one sentence); dual stack; AAAA record; Happy Eyeballs; address selection; Packet Too Big (ICMPv6 type 2); NAT66 and NPTv6 (one sentence each); egress-only internet gateway; NAT64 and DNS64 (two sentences).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `v6-notation` | 128 bits in eight 16-bit groups; dropping leading zeros, one `::` for the longest run of zero groups (the first if two tie, never for a single group), lower case; expanding a short form; prefix lengths on nibble boundaries (/48, /52, /56, /60, /64); `[address]:port` in URLs |
| `v6-address-types` | Global unicast, link-local (every interface, `%iface` to use one), ULA (`fd` + 40 random bits), multicast (`ff02::1`, `ff02::2`, solicited-node), loopback and unspecified, documentation; no broadcast; NDP in place of ARP (NS to a solicited-node group, NA back); what `ip -6 addr` and `ip -6 neigh` show |
| `v6-plan` | A /48 per site (or /56 for a small one), a /64 per subnet always; counting: 2^(64 − p) /64s in a /p; plans whose hex digits mean something (region, zone, tier); the clouds' sizes (AWS: an Amazon /56 per VPC and /64 subnets, /44–/64 allowed; Azure: subnets exactly /64; Google: /64 subnets, a /96 per VM interface, a ULA /48 from `fd20::/20` per network) |
| `slaac-dual-stack` | RA and SLAAC (the prefix must be a /64, or hosts ignore it); EUI-64 against stable and temporary interface IDs; DAD; the default route via the router's link-local address (`proto ra`); router-side settings (IPv6 forwarding, `radvd`); dual stack on hosts: IPv6 preferred (RFC 6724), Happy Eyeballs' 250 ms; AAAA records; one `inet` firewall table for both families |
| `v6-egress` | Why IPv6 needs no NAT for egress and why NAT was never the security (RFC 4864); a stateful filter's "outbound only" (AWS's egress-only internet gateway; Google's implied deny-ingress); the Azure exception (its IPv6 reaches the internet through translated public addresses: load-balancer outbound rules, a StandardV2 NAT gateway); NAT64 for IPv6-only to IPv4; which ICMPv6 a firewall must pass (Packet Too Big above all; NDP on the link) |

One calculation skill, `v6-plan`: five estimate items (ADR-0024 asks for three).

## 4. Lesson plan

1. **Why IPv6, in one paragraph** (no resource; the lesson's own). IPv4's 4.3 billion addresses ran out; NAT stretched them (topic 27 teaches NAT in full) at the cost of every connection passing through a translator; IPv6's 128 bits give every device its own global address again.

2. **Writing addresses** (main resource: Beej ch. 8, sections 8.1 and 8.2, 4 min of its 6; RFC 5952 §4 as optional reference). **The lesson supplies** the rules as four numbered steps with one address worked through all of them (`2001:0db8:0000:0000:0000:ff00:0042:8329` → `2001:db8::ff00:42:8329`), the two traps (a lone zero group stays `0`; `::` only once, because twice is ambiguous), and nibbles: each hex digit is 4 bits, so prefix lengths that are multiples of 4 cut between digits (/48 ends after the third group; /56 after the first two digits of the fourth). `sipcalc ADDRESS/64` expands and shortens for checking (the writer captures its output in the lab; it wasn't captured here).

3. **The kinds of address** (Beej 8.3; RFC 4291 §2.4 as optional). Table: prefix, kind, example, where you meet it. Every interface has a link-local `fe80::` address (Module 1's item already showed one), and IPv6 uses it for the protocol's own housekeeping: routers advertise from it, and hosts' default routes point at it. ULAs are IPv6's private space, `fd` followed by 40 random bits so two companies' ULAs almost never collide (unlike 10.0.0.0/8), and Google gives every network a ULA /48 from `fd20::/20`. No broadcast: NDP sends a neighbour solicitation to a *solicited-node* multicast group built from the target's last 24 bits, so only the right host (almost always) is woken. **Picture the lesson supplies:** the ARP exchange from topic 23 beside its IPv6 twin (NS to `ff02::1:ffXX:XXXX`, NA back), from the worked example's capture.

4. **How a host gets its address** (APNIC, "How to: IPv6 Neighbor Discovery", 12 min). The host makes its link-local address, checks nobody has it (DAD), sends a router solicitation; the router's advertisement carries the prefix and says "you may build your own address" (SLAAC) and "I'm a default router"; the host joins the /64 prefix to a 64-bit interface identifier. **The lesson supplies** EUI-64 worked from a MAC (insert `ff:fe` in the middle, flip the second-lowest bit of the first byte: `12:5b:20:ac:a2:1a` → `105b:20ff:feac:a21a`, as h1's address in the prototype shows), and why most systems now use stable or temporary random identifiers instead (the MAC follows a laptop around the internet). The rule that bites: the prefix in the advertisement must be a /64; given a /56, hosts make no address at all and say nothing (fact F9, the debug's first fault). DHCPv6 exists; the labs don't use it; on the clouds the platform hands out addresses.

5. **Planning** (SURFnet/RIPE NCC, "Preparing an IPv6 Address Plan", sections 2.2–2.4 and 4.1–4.4, about 18 min). A site gets a /48 (65,536 subnets) or a /56 (256); every subnet is a /64, however few machines, because SLAAC needs it and nobody runs short. Plans read best on nibble boundaries: one hex digit for the region, one for the zone, two for the tier, so `2001:db8:abcd:1302::/64` *says* region 1, zone 3, tier 02. **Where the clouds differ** (table; facts F17–F20): AWS assigns each VPC a /56 from its own pool (you can't choose it) and subnets are /64 (/44–/64 allowed in steps of 4); Azure lets you choose your VNet's IPv6 space and requires every subnet to be exactly /64; Google gives each subnet a /64 and each VM interface a /96 from it, and each network a ULA /48 for internal-only IPv6. AWS keeps 5 addresses of each IPv6 subnet too (the first four and the last).

6. **Dual stack** (no single resource; RFC 6724 and RFC 8305 are linked as optional). Both families on every interface; a name with both A and AAAA records; clients prefer IPv6 (RFC 6724's default table) and race IPv4 250 ms behind it (Happy Eyeballs), so a broken IPv6 path costs a quarter of a second, not an outage, which is exactly why broken IPv6 goes unnoticed for months. The firewall: nftables' `inet` table covers both (Module 1); an `ip` table covers IPv4 only, and a server "protected" by one is wide open on IPv6. One more trap from RFC 6724's table: a ULA destination ranks below IPv4, so a host with only ULAs and IPv4 prefers IPv4.

7. **Egress without NAT** (AWS, "Enable outbound IPv6 traffic using an egress-only internet gateway", 3 min; the SURFnet plan's §4.2, 2 min). With a global address for every host there's no shortage to hide; what NAT seemed to give (nobody on the internet can open a connection to you) came from its state table, and a stateful firewall gives the same thing without rewriting anything (RFC 4864). AWS sells exactly that as the egress-only internet gateway: IPv6 only, stateful, free itself, a route `::/0 → eigw-…`. **The clouds differ, and Azure is the exception the learner must know:** AWS translates nothing for IPv6 (a NAT gateway is for IPv4); Google gives VMs external IPv6 addresses and filters with its implied deny-ingress rule, and offers NAT64 only for IPv6-only VMs reaching IPv4; Azure has you choose the VNet's IPv6 range and reaches the internet through a public IPv6 address the platform maps onto the VM, load-balancer outbound rules (which Microsoft calls source NAT, IPv6 included) or a StandardV2 NAT gateway with IPv6 public addresses, so on Azure IPv6 egress *is* translated (facts F21–F23; open question 3). And Azure's network security groups don't support ICMPv6 rules (F21), which matters for the next section.

8. **ICMPv6 is not optional** (RFC 4890 §4.3.1, optional, 5 min). IPv6 routers never fragment (RFC 8200), so Packet Too Big is the only way a sender learns a path's MTU; drop it and topic 23's black hole is back, on IPv6 only, while IPv4 works (the debug's third fault). NDP is ICMPv6 too, but it never leaves the link (hop limit 255), so a firewall's forward chain needn't mention it, while its input chain must let it in or the router can't be found.

**Recap:** the short-form rules; the address-kind table; /48 and /64 and the count; RS, RA, SLAAC, DAD and the `fe80::` default route; dual stack's preference and 250 ms; `inet` not `ip`; egress-only, the Azure exception; never drop Packet Too Big.

## 5. Verified facts

"Captured" means the prototype labs on the owner's PC, 2026-11-11 (radvd 1:2.19-1ubuntu1, iproute2 6.1.0, kernel 6.18 WSL2, Docker Desktop 29.8.2).

| # | Claim | Source, read 2026-11-11 |
| --- | --- | --- |
| F1 | No broadcast in IPv6; type prefixes: `::/128` unspecified, `::1/128` loopback, `ff00::/8` multicast, `fe80::/10` link-local, global unicast everything else; unicast addresses (except those starting 000) have 64-bit interface IDs; solicited-node group = `ff02:0:0:0:0:1:ff00::/104` + the address's low 24 bits; `ff02::1` all nodes, `ff02::2` all routers | https://www.rfc-editor.org/rfc/rfc4291.html (February 2006) |
| F2 | Text form: leading zeros MUST be suppressed; `::` used to its maximum, never for a single zero group, the longest run (the first on a tie); lower case; brackets for address and port | https://www.rfc-editor.org/rfc/rfc5952.html (August 2010) |
| F3 | SLAAC ignores a prefix whose length plus the interface ID's isn't 128 bits; DAD runs on every unicast address before it's assigned | https://www.rfc-editor.org/rfc/rfc4862.html (September 2007) |
| F4 | Every link's MTU ≥ 1280; only source nodes fragment; PMTUD strongly recommended; hop limit decremented by each node that forwards | https://www.rfc-editor.org/rfc/rfc8200.html (July 2017) |
| F5 | ULA: `fc00::/7`, L bit 1 for locally assigned (so `fd`), 40-bit pseudo-random Global ID, 16-bit Subnet ID, not expected to be routed on the internet | https://www.rfc-editor.org/rfc/rfc4193.html (October 2005) |
| F6 | End sites: a one-size /48 is no longer the single default; RIRs encourage /56; at least one /64 and usually many more; /128 not recommended | https://www.rfc-editor.org/rfc/rfc6177.html (March 2011, BCP 157) |
| F7 | Transit ICMPv6 that must not be dropped: Destination Unreachable (1), Packet Too Big (2), Time Exceeded (3) code 0, Parameter Problem (4) codes 1–2, Echo Request/Reply (128/129); NDP (133–137) never leaves its link (hop limit 255) | https://www.rfc-editor.org/rfc/rfc4890.html (May 2007, Informational) |
| F8 | NAT "was not developed as a security mechanism"; its protection comes from lacking mapping state; IPv6 gets it from a stateful firewall that lets in only return traffic | https://www.rfc-editor.org/rfc/rfc4864.html (May 2007, Informational) |
| F9 | radvd advertising a /56: the host gets an on-link route `2001:db8:42::/56` and a default route via the router's link-local address, but **no global address**; radvd prints no warning | Captured |
| F10 | radvd with IPv6 forwarding off logs "IPv6 forwarding seems to be disabled, but continuing anyway" and still advertises a default router; hosts get a default route; ping to the internet is silent, traceroute6 shows `*` from hop 1 | Captured |
| F11 | SLAAC from radvd: `2001:db8:42:a:105b:20ff:feac:a21a/64 scope global dynamic mngtmpaddr` beside `fe80::105b:20ff:feac:a21a/64`; default route `via fe80::... dev eth0 proto ra ... expires 1797sec` (EUI-64: new namespaces take the kernel's defaults, `use_tempaddr` 0) | Captured |
| F12 | Through a 1400-byte link, an IPv6 probe from h1 got `From 2001:db8:ffff:1::1 icmp_seq=1 Packet too big: mtu=1400`; with ICMPv6 dropped in r1's forward chain and a cold cache, a 2 MB upload over IPv6 stalled (0 bytes in 8 s) while the same upload over IPv4 through NAT worked | Captured |
| F13 | With `masquerade` for IPv6 on r1, web saw h1's packets from r1's address `2001:db8:ffff:1::2`; without it, from h1's own SLAAC address | Captured |
| F14 | An egress-only forward chain (`policy drop`, `ct state established,related accept`, `iifname "lan" oifname "wan" accept`) made new connections from web to h1's global address time out (2,007 ms) while h1's own connections out worked | Captured |
| F15 | Default address selection prefers IPv6 to IPv4 (`::/0` precedence 40 above `::ffff:0:0/96` at 35); `fc00::/7` has precedence 3 | https://www.rfc-editor.org/rfc/rfc6724.html (September 2012) |
| F16 | Happy Eyeballs v2: connection attempts staggered by a recommended 250 ms; a 50 ms resolution delay for the AAAA answer | https://www.rfc-editor.org/rfc/rfc8305.html (December 2017) |
| F17 | AWS: a VPC may have an Amazon-provided IPv6 /56 (you can't choose the range), or up to five blocks /44–/60; subnets /44–/64 in steps of /4; the first four and the last address of an IPv6 subnet are reserved; the router also answers at `fe80:ec2::1` | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html; https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html |
| F18 | AWS egress-only internet gateway: IPv6 only (IPv4 uses a NAT gateway); "IPv6 addresses are globally unique, and are therefore public by default"; stateful; no charge for the gateway itself (data transfer charged); route `::/0` → `eigw-id`; no security group on it, network ACLs apply | https://docs.aws.amazon.com/vpc/latest/userguide/egress-only-internet-gateway.html |
| F19 | Azure: IPv6 subnets "must be exactly /64"; customers define their own IPv6 VNet space; IPv6-only VMs aren't supported (every NIC needs an IPv4 configuration); "ICMPv6 isn't currently supported in Network Security Groups"; Azure Firewall doesn't support IPv6; the load balancer does no NAT64; no charge for public IPv6 addresses (page dated 2024-10-16, updated 2026-07-27) | https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/ipv6-overview |
| F20 | Google: each subnet's IPv6 range is a /64; a dual-stack or IPv6-only interface gets a /96 from it; the first and last /96 are reserved; each network gets a ULA /48 from `fd20::/20`; external IPv4 and IPv6 addresses are always public; internal addresses can't be reached from the internet | https://docs.cloud.google.com/vpc/docs/subnets; https://docs.cloud.google.com/vpc/docs/ip-addresses |
| F21 | Azure NAT Gateway StandardV2 "supports both IPv4 and IPv6 public IP addresses and prefixes for outbound connectivity" and NAT64 with `64:ff9b::/96` (needs a third-party DNS64); a NAT gateway admits no unsolicited inbound connections (page dated 2026-08-31) | https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview |
| F22 | Azure load-balancer outbound rules "define SNAT (source network address translation)", translating backend VMs to the frontend's public addresses; outbound rules for a secondary IP configuration "are only supported for IPv6" (page dated 2026-01-08) | https://learn.microsoft.com/en-us/azure/load-balancer/outbound-rules |
| F23 | Google Cloud NAT translates IPv4 to IPv4 and IPv6 to IPv4 (NAT64); the page mentions no IPv6-to-IPv6 translation; Google's VPC overview supports DNS64 and NAT64 for IPv6-only instances; implied rules: deny ingress, allow egress | https://docs.cloud.google.com/nat/docs/overview; https://docs.cloud.google.com/vpc/docs/ipv6-support; https://docs.cloud.google.com/firewall/docs/firewalls |
| F24 | Documentation prefixes: `2001:db8::/32` (the original) and `3fff::/20` (added because the /32 "is inadequate" for realistic large examples; IANA 2024-07) | https://www.rfc-editor.org/rfc/rfc9637.html (August 2024) |
| F25 | SURFnet/RIPE NCC manual: a /48 gives 65,536 subnets; nibble boundaries (/32, /48, /52, /56, /60, /64); /56 may suit consumers, /48 "when there is any doubt"; §4.2 on why NAT isn't needed and its side effects (version 2, 18 September 2013; its point-to-point section predates RFC 6164's /127, which a mailing-list reply noted) | https://www.ripe.net/documents/1453/BasicIPv6-Appendix-AddressingPlanHowTo.pdf (27 pages, CC BY 3.0 NL per its last page) |
| F26 | A simplified short-form rule for `PREFIX/48` plans (strip each group's leading zeros, then replace the trailing run of zero groups with `::`) gives the same text as Python's `ipaddress` (RFC 5952) on seven edge cases, including `2001:db8::/48 1 0 10` → `2001:db8:0:100a::/64` (a lone zero stays) and `2001:db8::/48 0 0 0` → `2001:db8::/64` | Captured (Git Bash and Python 3, 2026-11-11) |

Not confirmed, so not claimed: whether Azure's instance-level public IPv6 is mapped by NAT exactly as its public IPv4 is (community answers say so for IPv4; no Microsoft page read says it for IPv6: the lesson says Azure "maps" a public address and cites F21–F22 for translation); global IPv6 adoption figures (Google's statistics page wasn't read); `sipcalc`'s IPv6 output (to capture).

## 6. Resources

Fetched on 2026-11-11.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | Beej's Guide to Network Concepts, ch. 8 "The Internet Protocol version 6" (representation, link-local addresses, special addresses, IPv6 and DNS, IPv6 in URLs) | https://beej.us/guide/bgnet0/html/split/the-internet-protocol-version-6.html | reading | CC BY-NC-ND 3.0; linked, not copied | 6 (724 words) | `v6-notation`, `v6-address-types` | headings confirmed |
| 1 | APNIC Blog, "How to: IPv6 Neighbor Discovery" (2019-10-18): RS, RA, NS, NA and redirect, with Wireshark captures | https://blog.apnic.net/2019/10/18/how-to-ipv6-neighbor-discovery/ | reading | © APNIC; linked, not copied | 12 | `slaac-dual-stack`, `v6-address-types` | opened; the five message types confirmed |
| 2 | SURFnet / RIPE NCC, "Preparing an IPv6 Address Plan" (manual, version 2, 2013): sections 2.2–2.4 and 4.1–4.4 | https://www.ripe.net/documents/1453/BasicIPv6-Appendix-AddressingPlanHowTo.pdf | reading (PDF) | CC BY 3.0 NL (its last page); linked, not copied | 18 (of 8,886 words) | `v6-plan`, `v6-egress` | downloaded and read; dated, see F25 |
| 3 | AWS, "Enable outbound IPv6 traffic using an egress-only internet gateway" | https://docs.aws.amazon.com/vpc/latest/userguide/egress-only-internet-gateway.html | reading | © Amazon Web Services; linked | 3 | `v6-egress` | opened |
| 4 | Azure, "Overview of IPv6 for Azure Virtual Network": "Capabilities" and "Limitations" | https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/ipv6-overview | reading | CC BY 4.0 (MicrosoftDocs, as Module 2 recorded); linked | 5 | `v6-plan`, `v6-egress` | opened (2024-10-16, updated 2026-07-27) |
| 5 | Google Cloud, "Subnets": the IPv6 sections | https://docs.cloud.google.com/vpc/docs/subnets | reading | CC BY 4.0 (as Module 2 recorded) | 3 | `v6-plan` | opened |
| 6 | Chris Grundemann, "Introducing IPv6: Neighbor Discovery & SLAAC" (2012), optional | https://chrisgrundemann.com/index.php/2012/introducing-ipv6-neighbor-discovery-slaac/ | reading | copyright the author (no licence stated); linked | 8 (1,044 words) | `slaac-dual-stack` | opened; covers ND, DAD on the link-local address, RAs carrying prefixes |
| 7 | RFC 4890 §4.3.1, optional | https://www.rfc-editor.org/rfc/rfc4890.html | reading | IETF Trust; linked | 5 | `v6-egress` | opened |
| 8 | RFC 5952 §4, optional | https://www.rfc-editor.org/rfc/rfc5952.html | reading | IETF Trust; linked | 4 | `v6-notation` | opened |
| 9 | Azure, "What is Azure NAT Gateway?": the StandardV2 sections, optional | https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview | reading | CC BY 4.0 (MicrosoftDocs); linked | 4 | `v6-egress` | opened (2026-08-31) |

Required minutes: 6 + 12 + 18 + 3 + 5 + 3 = 47.

Also considered: RIPE NCC Academy's IPv6 courses (free, but behind an account; not opened); no video was found and checked in the time available (open question 4).

## 7. Practice ladder

### 7.1 `example-meet-ipv6` (worked example, systemd network lab, 35 minutes)

**Topology** (as `d25/`, healthy): LAN `lan` with `h1`, `h2` and `r1` (2001:db8:42:a::1/64, 192.168.10.1/24); `r1` wan 2001:db8:ffff:1::2/64, 198.51.100.2/30 to `isp`; `isp` —link, MTU 1400— `core`; `core` serves `web` (2001:db8:80::80, 203.0.113.80; the test server `web-svc`: port 8080 answers with the address the connection came from, port 9000 counts the bytes it was sent). r1 runs `radvd` (prefix 2001:db8:42:a::/64), forwards both families, and has the egress-only firewall with NAT44 (`d25`'s file without its fault line). A name `web.shop.test` with A and AAAA records (the base's resolver or the hosts' `/etc/netns/M/hosts`; not in the prototype, which used addresses). **This lab turns DAD back on for the hosts** (`sysctl h1 net.ipv6.conf.all.accept_dad=1`, and `default`), which the base switches off.

**Steps:**

1. *A host's addresses.* `on h1 ip -6 addr show dev eth0`: the link-local, the global `dynamic mngtmpaddr`; the note builds the EUI-64 identifier from `on h1 cat /sys/class/net/eth0/address`.
2. *Watch a host configure itself.* `on r1 tcpdump -nn -l -i lan icmp6 > ~/example/slaac.txt &`, `on h2 ip link set eth0 down`, `on h2 ip link set eth0 up`, wait 4 s, `kill %1`: a router solicitation, an advertisement, a neighbour solicitation from `::` (DAD). (The interface change is live only; a restart undoes it.)
3. *The default route.* `on h1 ip -6 route`: `default via fe80::... proto ra`; `on r1 ip -6 addr show dev lan scope link` shows that `fe80::` is r1's.
4. *Neighbours.* `on h1 ping -6 -c1 2001:db8:80::80`, `on h1 ip -6 neigh`: r1's link-local address with its MAC, the IPv6 ARP table.
5. *Dual stack.* `on h1 nc -w3 web.shop.test 8080 < /dev/null` (IPv6 preferred: h1's own address comes back), then with `-4` (r1's 198.51.100.2 comes back): saved to `~/example/whoami6.txt` and `whoami4.txt`.
6. *Nobody can call in.* `on h1 timeout 5 nc -6 -l -p 22 &`, then `on web nc -6 -z -w2 H1ADDR 22; echo $?`: 1 after 2 s; the note reads r1's forward chain line by line.
7. *Packet Too Big.* `on h1 ping -6 -c1 -M do -s 1452 2001:db8:80::80`: `Packet too big: mtu=1400` from the ISP's router.

**Checks:** `slaac.txt` holds `router solicitation`, `router advertisement` and a `neighbor solicitation` (tcpdump's wording, pinned by the writer); `whoami6.txt` equals h1's current global address; `whoami4.txt` equals 198.51.100.2; h2's interface is up again and has a global address. **Wrong fixes:** `capture-too-late.sh` (the capture starts after the link comes up: no RS), `v4-only.sh` (both whoami files taken with `-4`), `left-down.sh` (h2's link left down).

### 7.2 Recall: notation

2. **`mcq-short-form`** (mcq, `v6-notation`). "What is the RFC 5952 short form of `2001:0db8:0000:0000:0000:ff00:0042:8329`?" Right: "`2001:db8::ff00:42:8329`". Wrong: "`2001:db8:0:0:0:ff00:42:8329`", "`2001:db8::ff00:0042:8329`", "`2001:db8:::ff00:42:8329`". Explanation: each rule, and that the second is a valid address but not the short form; the fourth isn't an address.
3. **`est-groups-in-colons`** (estimate, `v6-notation`). "An IPv6 address always has 8 groups. In `2001:db8::1`, how many groups of zeros does `::` stand for? Exactly." given `{groups: 8}`, working `groups - 3`, answer 5. Mistakes: 6 (`groups - 2`, didn't count the final 1), 2 (`"2"`, read `::` as two zero groups).
4. **`mcq-lone-zero`** (mcq, `v6-notation`). "All four of these are the same address, `2001:db8:0:1:0:0:0:1`. Which one is RFC 5952's short form?" Right: "`2001:db8:0:1::1`". Wrong: "`2001:db8::1:0:0:0:1`" (`::` used for the lone zero, not the longest run), "`2001:DB8:0:1::1`" (upper case), "`2001:db8:0:1:0:0:0:1`" (no `::` at all). Explanation: the longest run wins; a lone zero stays `0`. (Avoid tied runs in any item unless it is about the tie: with two equal runs, RFC 5952 compresses the first, so `2001:db8::1:0:0:1` *is* correct.)
5. **`v6-plan-print`** (predict_shell, `v6-notation`, `v6-plan`). Command: `printf '2001:db8:abcd:%x%x%02x::/64\n' 1 3 10`. Output `2001:db8:abcd:130a::/64`. The prompt explains `%x` (hex) and `%02x` (two hex digits, zero-padded). Explanation: region 1, zone 3, tier 10 = `0a`.
6. **`v6-short-form`** (predict_shell, `v6-notation`, F26). The simplified formatter (8 lines, `prototypes/layers-cidr-ipv6/w25/v6plan.sh`) applied to `2001:db8::/48 1 0 10` and `2001:db8:a::/48 0 0 0`. Output `2001:db8:0:100a::/64` and `2001:db8:a::/64`. Explanation: why the lone zero stays and why a zero tier group joins the `::`.

### 7.3 Recall: kinds of address

7. **`v6-kinds`** (predict_shell, `v6-address-types`). `addrs.txt`: `fe80::1`, `fd12:3456:789a:1::10`, `ff02::1`, `2600:1f18:abcd::5`, `::1`, `2001:db8::42`. Command: `while read -r a; do case $a in fe80:*) k=link-local;; fd*|fc*) k=unique-local;; ff*) k=multicast;; ::1) k=loopback;; 2001:db8:*) k=documentation;; 2*|3*) k=global;; esac; echo "$a $k"; done < addrs.txt`. (Order of the `case` patterns matters and is part of the reading: `2001:db8:` before `2*`.) Explanation per line.
8. **`mcq-default-via-fe80`** (mcq, `v6-address-types`, `slaac-dual-stack`). "Why does an IPv6 host's default route point at `fe80::4cc:c2ff:fe67:1ab1` and not at the router's global address?" Right: "Routers advertise from their link-local address, which survives renumbering". Wrong: "The global address is still being checked by DAD, so the host uses the other one"; "Link-local addresses are faster to route, because routers skip the lookup"; "The router has no global address on that LAN, only the link-local one". Explanation: F11; renumbering the prefix leaves every host's route intact.
9. **`mcq-ndp-not-arp`** (mcq, `v6-address-types`). "With no broadcast in IPv6, how does h1 find the MAC address of a neighbour at `2001:db8:42:a::25`?" Right: "It sends a neighbour solicitation to the address's solicited-node group". Wrong: "It sends an ARP request to the all-nodes group `ff02::1`, which every host answers"; "It reads the MAC from the address, because every IPv6 address contains one"; "It asks the router, which keeps the only table of MACs on the link". Explanation: F1; why the third is tempting (EUI-64) and wrong (most addresses no longer contain the MAC).
10. **`mcq-ula-use`** (mcq, `v6-address-types`). "When does a ULA (`fd…`) make sense, and what's its catch?" Right: "For networks that must never reach the internet; IPv4 is preferred over it by default". Wrong: "For every server, because the internet can't reach a ULA and a NAT then reaches it"; "For laptops only, because routers refuse to forward ULAs between subnets"; "Never: ULAs were deprecated, and site-local addresses replaced them". Explanation: F5, F15 (precedence 3), Google's internal IPv6 (F20); the third and fourth have it backwards (site-local `fec0::/10` was deprecated, ULA replaced it).

### 7.4 Recall: planning

11. **`est-64s-in-48`** (estimate, `v6-plan`). "A site has a /48. How many /64 subnets does it hold? Exactly." given `{site: 48, sub: 64}`, working `2 ** (sub - site)`, answer 65536. Mistakes: 16 (`sub - site`), 256 (`2 ** 8`, a /56's).
12. **`est-52s-in-48`** (estimate, `v6-plan`). "A company splits its /48 into a /52 for each region. How many regions can it number? Exactly." given `{site: 48, region: 52}`, working `2 ** (region - site)`, answer 16. Mistakes: 4 (`region - site`), 4096 (`2 ** (64 - region)`, the /64s in one region).
13. **`est-aws-subnets`** (estimate, `v6-plan`). "AWS gives a VPC an IPv6 /56. How many /64 subnets can it be split into? Exactly." given `{vpc: 56, sub: 64}`, working `2 ** (sub - vpc)`, answer 256. Mistakes: 8 (`sub - vpc`), 65536 (`2 ** 16`, a /48's).
14. **`est-zone-subnets`** (estimate, `v6-plan`). "A large company has a /40. Its plan gives one hex digit to the region, one to the site and one to the zone; the rest of the bits up to /64 number the subnets in a zone. How many /64 subnets does one zone get? Exactly." given `{org: 40, region: 4, site: 4, zone: 4, sub: 64}`, working `2 ** (sub - org - region - site - zone)`, answer 4096. Mistakes: 12 (`sub - org - region - site - zone`), 65536 (`2 ** (sub - 48)`, as if the org had a /48), 256 (`2 ** (sub - org - region - site - zone - 4)`, one digit too many).
15. **`est-gcp-vm-bits`** (estimate, `v6-plan`). "A Google Cloud VM's interface gets a /96 of IPv6. How many bits at the end of the address are the VM's to choose? Exactly." given `{p: 96}`, working `128 - p`, answer 32. Mistakes: 64 (`64`, a whole /64), 96.
16. **`mcq-why-64`** (mcq, `v6-plan`, `slaac-dual-stack`). "A small team proposes /120 subnets for IPv6 'to save addresses'. What breaks?" Right: "SLAAC: hosts ignore a router prefix that isn't a /64". Wrong: "Routing: routers can't forward prefixes longer than /64"; "DNS: AAAA records must point into a /64"; "Nothing, but the cloud charges per subnet". Explanation: F3, F19 (Azure demands /64), F17 (AWS /64 at most); and there is nothing to save.

### 7.5 Recall: SLAAC and dual stack

17. **`slaac-read-addr`** (predict_shell, `slaac-dual-stack`, captured F11). `addr.txt`: h1's `ip -6 addr show dev eth0` lines. Command: `awk '/inet6/ {print $2, $4, ($5 == "dynamic" ? "from an RA" : "configured")}' addr.txt`. Output pinned (`2001:db8:42:a:105b:20ff:feac:a21a/64 global from an RA` and `fe80::105b:20ff:feac:a21a/64 link configured`). Explanation: `dynamic` means it has a lifetime from the RA; the link-local is made locally.
18. **`slaac-eui64`** (predict_shell, `slaac-dual-stack`). Command: `m=12:5b:20:ac:a2:1a; IFS=: read -r a b c d e f <<< "$m"; printf '%02x%s:%sff:fe%s:%s%s\n' $(( 0x$a ^ 2 )) "$b" "$c" "$d" "$e" "$f"`. Output `105b:20ff:feac:a21a`. The prompt explains `^` (flip bits) and that `ff:fe` goes in the middle. Explanation: and why privacy addresses exist.
19. **`mcq-rs-ra-order`** (mcq, `slaac-dual-stack`). A captured four-line `tcpdump icmp6` sequence (from step 2 of the worked example, the writer captures it) with the lines shuffled into the choices' orders. Right: the real order (DAD NS from `::`, RS, RA, then the global address's DAD NS). Wrong: three plausible other orders.
20. **`mcq-prefix-56`** (mcq, `slaac-dual-stack`; the debug's fault 1 in another story). "A branch router's radvd advertises `2001:db8:77::/56`. The laptops show only `fe80::` addresses, though they have a default route. Why?" Right: "SLAAC needs a /64 prefix, so the laptops ignore the one they got". Wrong: "A /56 is too many addresses, so the laptops wait for DHCPv6"; "The router must be rebooted before laptops accept a new prefix"; "The laptops' privacy setting hides global addresses from `ip -6 addr`". Explanation: F3, F9.
21. **`mcq-happy-eyeballs`** (mcq, `slaac-dual-stack`). "A web app's AAAA record points at an address that drops every packet; its A record works. What do users with dual-stack browsers see?" Right: "Pages load, a quarter of a second later than they should". Wrong: "Nothing loads, because browsers always use IPv6 when there's a AAAA record"; "Pages load normally, because browsers try IPv4 first and IPv6 only if it fails"; "An error page, because the two records disagree and the browser stops". Explanation: F15, F16; why broken IPv6 hides.
22. **`mcq-ip-table-not-inet`** (mcq, `slaac-dual-stack`, `v6-egress`). "A server's nftables rules are all in `table ip filter` with `policy drop`. It has a global IPv6 address. What can reach it over IPv6?" Right: "Everything: an `ip` table filters IPv4 only". Wrong: "Nothing: `policy drop` applies to both families"; "Only established connections, because conntrack covers both"; "Only ICMPv6, which IPv6 always lets through". Explanation: Module 1's `inet` sentence; the fix.

### 7.6 Recall: egress

23. **`mcq-why-no-nat66`** (mcq, `v6-egress`). "Why do AWS and Google offer no NAT gateway for IPv6-to-IPv6 traffic?" Right: "Every host has its own address, and a stateful filter protects it as well". Wrong: "IPv6 encrypts every packet with IPsec, so a translator can't rewrite them"; "IPv6 headers are checksummed end to end, so a rewritten address breaks them"; "NAT for IPv6 was tried in the 2000s and then forbidden by an IETF standard". Explanation: F8, F18, F23; IPsec is optional in practice; the IPv6 header has no checksum at all (TCP's and UDP's cover the addresses, as in IPv4, which every NAT already fixes up); NPTv6 exists (experimental) and NAT66 can be built (the debug's wrong fix does).
24. **`mcq-egress-only`** (mcq, `v6-egress`). "What does an AWS egress-only internet gateway do?" Right: "Lets instances open IPv6 connections out and blocks connections in". Wrong: "Translates instances' IPv6 addresses to one public IPv6 address"; "Lets instances reach IPv4 sites by translating IPv6 to IPv4"; "Carries IPv4 and IPv6 out, and blocks inbound for both". Explanation: F18 (NAT64 is the NAT gateway's job; IPv4 egress is the NAT gateway's).
25. **`mcq-azure-ipv6`** (mcq, `v6-egress`). "Which statement about IPv6 on Azure is true?" Right: "VMs reach the IPv6 internet through translated public addresses". Wrong: "VMs can be IPv6-only, with no IPv4 configuration on their network card"; "Network security groups can allow or deny ICMPv6 messages by their type"; "Subnets may be any size from a /48 down to a /64, as on AWS". Explanation: F19, F21, F22: Azure translates; IPv6-only VMs aren't supported; ICMPv6 isn't supported in NSGs; subnets are exactly /64.
26. **`mcq-icmpv6-firewall`** (mcq, `v6-egress`). "IPv4 uploads from a branch work. IPv6 uploads hang after the first few kilobytes, though IPv6 pages load. The branch router's forward chain has `meta l4proto ipv6-icmp drop` before its `ct` rule. Why does that matter only for IPv6?" Right: "IPv6 routers never fragment, so blocked Packet Too Big is a black hole". Wrong: "NDP runs through the forward chain, so the router loses its neighbours"; "IPv6 uses ICMPv6 for TCP acknowledgements, which are dropped"; "ICMPv6 carries IPv6's DNS answers, so names stop resolving". Explanation: F4, F7, F12; NDP stays on the link (input, not forward).

### 7.7 `fill-radvd-conf` (fill-in, systemd network lab, 25 minutes)

**Topology:** as the worked example, renamed for a new office: r1's LAN gets the plan's subnet `1a` (hex) of the site's `2001:db8:77::/48`, and **r1's radvd and IPv6 forwarding aren't set up**. **Starter:** r1's `radvd.conf` and r1's sysctl file, with gaps:

```
interface ___ {
    AdvSendAdvert ___;
    prefix ___ {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
```

and `net.ipv6.conf.all.forwarding = ___`. r1's own LAN address (`2001:db8:77:1a::1/64`) is in its network file already. **Checks:** (a) h1 and h2 have SLAAC addresses in `2001:db8:77:1a::/64` (`dynamic`); (b) their default route is via r1's link-local address; (c) h1 reaches web over IPv6 with its own address (`web-svc` on 8080); (d) the fix lasts (fresh build: r1's forwarding is 1; radvd's file holds the prefix). **Wrong fixes:** `decimal-subnet.sh` (`2001:db8:77:26::/64`: 26 decimal is `1a`; check a), `prefix-48.sh` (the site's /48: check a), `advert-off.sh` (`AdvSendAdvert off`: a, b), `forwarding-live-only.sh` (check d).

### 7.8 `write-v6-plan` (write, plain lab, 30 minutes)

**Task:** from a blank file, `~/bin/v6-plan PREFIX REGIONS ZONES TIERS`, where PREFIX is a /48 written short (`2001:db8:abcd::/48`), prints one line per region, zone and tier, in that nested order, `rR-zZ-tTT SUBNET`, where R and Z are one hex digit each, TT two (`t0a`), and SUBNET is the /64 `PREFIX` + group `RZTT`, in the short form. The prompt gives the simplified short-form rule (F26: strip each group's leading zeros with `printf '%x'`, then drop trailing zero groups and add `::`), explains why it's enough for these plans (the interface identifier's four zero groups always make the longest run), and recalls `printf '%x%x%02x'` from item 5.

**Checks:** (a) exists, executable, shebang, `shellcheck --norc` quiet; (b) three prefixes made at check time, each from a fixed category with random digits (a prefix with no zero groups; one whose third group is 0, so `r0-z0-t00` must print `PREFIX-with-two-groups::/64`; a ULA `fdXX:XXXX:XXXX::/48`), each with random counts (regions 2–4, zones 2–3, tiers 2–12, so a tier above 9 appears), compared line by line with `python3`'s `ipaddress` (the check's own truth); (c) the count of lines is regions × zones × tiers. **Wrong fixes:** `no-zero-strip.sh` (`2001:db8:abcd:0102::/64`), `decimal-tier.sh` (`t10` and `...:0110::`), `upper-case.sh` (RFC 5952 wants lower case), `zero-group-kept.sh` (`2001:db8:a:0::/64` instead of `2001:db8:a::/64`), `wrong-order.sh` (tiers outermost).

## 8. Proofs

### Build: `build-dual-stack-branch` (systemd network lab, 50 minutes)

**Story and topology:** the d25 topology, renamed: a new branch whose router `r1` arrives with its addresses on both sides (`2001:db8:c0de:ffff::2/64` and 198.51.100.10/30 on wan, toward the ISP) and **nothing else**: no LAN address, no radvd, no forwarding, no firewall. The ISP routes the company's `2001:db8:c0de::/48` to r1. `isp` —link, MTU 1400— `core` —`web` as before. Hosts h1, h2 on the LAN have IPv4 addresses in 192.168.20.0/24 (scenery, as a DHCP server would give) and nothing for IPv6.

**The brief:** the company's plan gives this branch the subnet `25` (hex) of its `2001:db8:c0de::/48`. Give the branch LAN IPv6: r1 takes the first address of the subnet; the branch's machines configure themselves from r1's advertisements; r1 forwards both families. r1 is the branch's firewall: over IPv6, the branch's machines open connections to the internet with their own addresses and nobody on the internet can open a connection to them, and whatever IPv6 needs to work must get through; over IPv4, the branch's private addresses leave as r1's. Don't touch the branch machines' own settings. Everything survives a restart.

**Checks:** `slaac` (h1 and h2 have `dynamic` addresses in `2001:db8:c0de:25::/64`, default via r1's link-local `proto ra`), `own-address` (web's whoami returns h1's own address over IPv6), `v4-nat` (over IPv4, web sees 198.51.100.10), `egress-only` (new connections from web to h1 and h2 on 22, 80, 8080 time out; and to r1's own 22 and 8080 from web), `ptb` (h1's DF probe to a fresh `2001:db8:80::1000/116` address shows `mtu=1400`; the hosts' and r1's MTUs are 1500), `hosts-untouched` (the base's seal on h1's and h2's files: "the branch machines' settings are as they were"), `lasts` (fresh build equals live; in it, r1's forwarding and firewall match).

**Wrong fixes:** `nat66.sh` (own-address), `forward-open.sh` (egress-only), `prefix-56.sh` (slaac), `decimal-25.sh` (reads the plan's `25` as a decimal number and converts it, advertising `2001:db8:c0de:19::/64`: slaac), `forwarding-live-only.sh` (lasts), `icmpv6-dropped.sh` (ptb), `no-nat44.sh` (v4-nat), `static-on-hosts.sh` (hosts-untouched, slaac). 8 wrong fixes, about 25 s each.

`test_skills`: not used (topic build).

### Debug: `debug-ipv6-half-works` (systemd network lab, 45 minutes): prototyped and passing

**Topology:** `d25/`, as section 7.1 but with three faults in r1's files:

1. `radvd.conf` advertises `2001:db8:42::/56` (F9).
2. r1's sysctl file sets only `net.ipv4.ip_forward = 1` (F10).
3. r1's `nftables.conf` forward chain starts with `meta l4proto ipv6-icmp drop` ("copied from the old IPv4 hardening"; F12).

**Prompt:** "The office runs dual stack: laptops h1 and h2 get IPv4 from the office router r1 and are meant to configure IPv6 for themselves from r1's advertisements, using the office's subnet `2001:db8:42:a::/64`. r1 forwards both, translates IPv4 to its own address, and lets nobody on the internet open connections to the office. web, in the cloud, has a test service: port 8080 answers with the address your connection came from, port 9000 counts what you send it. IPv4 works. IPv6 doesn't: the laptops can't reach anything over it. There are three faults. Fix each at its cause. The rules: no translation for IPv6 (each laptop keeps its own address on the internet); the internet still can't open connections to the office; the laptops configure themselves (type no addresses onto them); leave every MTU as it is; every fix survives a restart."

**Checks** (`d25/checks.sh`): `slaac`, `reach` (whoami equals h1's own address), `v4` (still 198.51.100.2), `upload` (2 MB to port 9000 over IPv6 within 15 s), `ptb` (MTUs unchanged; h1's DF probe to a random `2001:db8:80::1xxx` shows `mtu ?= ?1400`), `egress_only`, `lasts`.

**Wrong fixes** (all proved): `nat66.sh` (fails `reach` only), `forward-open.sh` (`egress_only` only), `static-addresses.sh` (`slaac` only), `forwarding-live-only.sh` (`lasts` only), `hosts-mtu-lowered.sh` (`ptb` only), `wrong-subnet.sh` (`slaac` only). Each fails exactly the one check aimed at it, which is the shape the README asks for (a failure points at the right part).

**Prototype results (2026-11-11):** pristine fails 4 of 7 (`v4` and `egress_only` pass, as they should: IPv4 works and nothing is open); the solution passes 7 of 7, and again after `docker restart`; a full contract run of 8 scenarios took 230 s (boot 2–3 s, fixes 7–9 s with a network restart, checks 13–22 s). Two prototype bugs found and fixed on the way, for the writer: `curl` refuses the test server's bare one-line answer (it isn't HTTP; use `nc`), and the fresh-build comparison must skip kernel `anycast` routes, which appear a moment after a router's addresses settle.

### Explain (20 minutes)

**Prompt:** "Your company is adding IPv6 to its offices and cloud networks. A colleague asks: 'Do we need NAT gateways for IPv6? And how do machines get addresses without DHCP?' Explain, in your own words: how an IPv6 address is written and why subnets are /64; how you'd lay out a plan from a /48; how a laptop configures itself, and where its default route points; what dual stack means for clients and for firewalls; why IPv6 egress needs no NAT and what protects the machines instead; why ICMPv6 must get through a firewall; and how the three clouds differ on any two of these."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `notation-and-64` | yes | 128 bits in eight hex groups; leading zeros dropped and one `::` for the longest zero run; /64 subnets because SLAAC needs a 64-bit interface identifier |
| `plan` | yes | A /48 per site (65,536 /64s) or /56 for small sites; hex digits for region, zone, tier on nibble boundaries; plan for readability, not scarcity |
| `slaac` | yes | The router advertises the prefix (RA); hosts build an address from it (SLAAC), check it's free (DAD) and take a default route to the router's link-local address; a prefix that isn't /64 gives no address |
| `dual-stack` | yes | Both families on every interface; clients prefer IPv6 and fall back to IPv4 within about 250 ms (so broken IPv6 hides); one firewall table for both families (`inet`), or IPv6 is unfiltered |
| `egress-no-nat` | yes | Every host has a global address; NAT's protection came from its state, and a stateful firewall that admits only replies gives the same (AWS's egress-only internet gateway; Google's deny-ingress default) |
| `icmpv6` | yes | Routers don't fragment IPv6, so Packet Too Big must reach senders or big transfers hang; NDP is ICMPv6 on the link and must reach the router |
| `clouds-differ` | yes | Any two: AWS assigns a /56 per VPC and /64 subnets, egress-only gateway for IPv6 and NAT gateway for IPv4; Azure requires /64 subnets, has no IPv6-only VMs, translates IPv6 egress through public addresses, load-balancer outbound rules or a StandardV2 NAT gateway, and its NSGs can't filter ICMPv6; Google gives each VM a /96, a ULA /48 per network, external IPv6 addresses that are public, and NAT64 only for IPv6-only VMs |

## 9. Review pool

† marks review-only items with numbers of their own.

| Skill | Items |
| --- | --- |
| `v6-notation` | `mcq-short-form`, `est-groups-in-colons`, `v6-short-form`, † `mcq-expand` (the full form of `fd00:12::3:4`: `fd00:0012:0000:0000:0000:0000:0003:0004`, against three wrong expansions) |
| `v6-address-types` | `v6-kinds`, `mcq-ndp-not-arp`, `mcq-default-via-fe80` |
| `v6-plan` | `est-64s-in-48`, `est-zone-subnets`, `est-gcp-vm-bits`, † `est-sites-in-32` (an organisation's /32 gives /48 sites: 65,536; mistakes 16, 4,096), † `est-region-nibble` (a /44 per region from a /40: 16; mistakes 4, 256) |
| `slaac-dual-stack` | `slaac-eui64`, `mcq-prefix-56`, `mcq-happy-eyeballs`, `mcq-ip-table-not-inet` |
| `v6-egress` | `mcq-why-no-nat66`, `mcq-egress-only`, `mcq-azure-ipv6`, `mcq-icmpv6-firewall` |

## 10. Platform work first

| # | Need | Smallest version | Proved? |
| --- | --- | --- | --- |
| P-1 | `radvd` as a machine's service | `radvd` in the base's second `RUN` line (149 KB installed); `run r1 radvd` with `ETC_OF[radvd]="radvd.conf"`; a unit `radvd@.service` running `radvd --nodaemon -C /etc/radvd.conf -p /run/radvd-%i.pid` in the machine (my prototype's unit, `d25/radvd-r1.service`, used `NetworkNamespacePath=/run/netns/r1` and `PartOf=` the network unit) | Yes |
| P-2 | Per-lab override of the base's IPv6 defaults | The base sets `accept_dad=0` on every machine and adds addresses with `nodad`; the worked example needs DAD on the hosts to show it (`sysctl h1 net.ipv6.conf.all.accept_dad=1` and `default`, after the `machine` line). A host with DAD takes about a second before its address is usable, so checks wait with the base's `wait_for` | Not needed in d25 (DAD off); the override is the base's `sysctl` word |
| P-3 | Routers that are routers for one family only | The debug's fault 2 needs r1 forwarding IPv4 but not IPv6. With the base, declare `machine r1 host` and set `sysctl r1 net.ipv4.ip_forward=1` in the file the learner fixes (or the per-machine sysctl file, my prototype's form). The base's `router` role sets both, which is right everywhere else | Yes (my prototype's per-machine sysctl file) |
| P-4 | A dual-stack test server | `web-svc` (40 lines of Python, `d25/web-svc`): 8080 echoes the client's address, 9000 counts bytes; scenery, under `/usr/local/bin`. The base's nginx can't say which address a connection came from without a custom config, and this is shorter | Yes |
| P-5 | IPv6 inside the lab container | IPv6 is enabled in Docker Desktop's container and in new namespaces (`disable_ipv6` 0). On GitHub's runners Docker may set `disable_ipv6=1` in the container's own namespace; new namespaces created inside get the kernel's defaults, so it shouldn't matter, but **this wasn't tried on a runner**: add an IPv6 lab to the base's CI spike | Docker Desktop only |
| P-6 | Network files, fresh-build check, sealing | Topic 23's N-A and N-D; the base's `netlab seal` for "hosts untouched" | Yes (N-A, N-D); seal is the base's |
| P-7 | Plain lab with `python3` | As topic 24's P-4, for the write lab | — |

## 11. Cost and time

**Money:** nothing. The clouds' IPv6 behaviour is taught from their documentation. An optional real run (an AWS VPC with an egress-only gateway and two instances, or an Azure dual-stack VNet) would show the console's view but nothing the local labs don't prove; Module 11 (`csa.cnet.egress`, "control egress for IPv6") is the place for it. Recommendation: none here.

**Learner time:** lesson 18; required resources 47; 25 recall items × 1.5 = 38; worked example 35; fill-in 25; write 30; build 50; debug 45; explain 20. **Total 308 minutes.** Trim: make the SURFnet reading 12 minutes (sections 2.3, 4.1, 4.4 only), and move `mcq-ula-use` and `mcq-rs-ra-order` to review-only. **`estimated_minutes: 300`.**

**CI time:** worked example, fill-in, build and debug are systemd network labs (debug measured at 230 s for 8 scenarios; build about 250 s for 9; fill-in and worked example about 120 s each); the write is a plain lab (about 60 s). **About 13 minutes sequential, 3–4 of a shard.** For the three topics together: about 33 minutes sequential, 8–10 minutes of wall time across shards at four labs at a time; the base designer's shard plan should count them.

## 12. Open questions, each with a recommendation

1. **A real cloud run?** Recommendation: no (section 11); every claim about the clouds here is from their documentation and dated, and the behaviour that matters (no NAT66, egress-only filtering, Packet Too Big) is proved locally.
2. **DAD on or off in the labs.** The base switches it off so addresses are ready at once. Recommendation: off everywhere except the worked example, which turns it on to show the neighbour solicitation from `::`; one sentence in the lesson says why the other labs skip it.
3. **How to word Azure.** The spec says "explain why IPv6 egress doesn't use NAT", which is true of the protocol's design, of AWS and of Google, and not of Azure's IPv6 egress, which Microsoft's own pages describe as source NAT (F21, F22). Recommendation: teach the design reason, and teach Azure as the honest exception, in the lesson, the explain rubric and one review item; change the spec's line to "explain why IPv6 egress needs no NAT, and where a cloud translates anyway" (one line; for the critic to put in the spec change list).
4. **A video for IPv6.** None was found and checked in the time I had. Recommendation: the writer looks for one (APNIC's and RIPE NCC's channels first) and adds it only once its licence and length are confirmed; the topic stands without one.
5. **Privacy addresses.** New namespaces use EUI-64 (`use_tempaddr` 0), so the labs' addresses are MAC-based and change at every boot with the MAC. Recommendation: say so in the worked example's note, and have every check read the current address rather than store one (the prototype's checks do).
6. **Checkpoint 3 part 1's IPv6 half.** Recommendation for the checkpoint designer: reuse this build's rules (a /48 per site, /64 subnets, hex fields on nibble boundaries, a summary per cloud that fits the cloud's own sizes: AWS's /56 per VPC, Azure's /64 subnets, Google's /64 subnets) and the write lab's formatter as the check's way of printing expected subnets.

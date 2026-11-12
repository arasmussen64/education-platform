# Topic 23: `csa.net.layers`, Layers and packets

Designer's brief, 2026-11-11 (key `layers-cidr-ipv6`, with `csa.net.cidr` and `csa.net.ipv6`). Prototypes, captures and contract logs: `prototypes/layers-cidr-ipv6/` (folder `d23/` is this topic's debug lab, run end to end; the appendix lists what was tried). The network-lab base is another designer's (`prototypes/network-lab-base/`); section 10 says what these labs need from it, and where the base already has a form of the thing, the base's form wins.

## 1. What the learner will be able to do

- Follow one request from a laptop to a server and back, layer by layer, in real captures: which headers wrap the data, what each router changes (the Ethernet addresses, the TTL, the checksum) and what it leaves alone (the IP addresses, the ports), read field by field in `tcpdump -e -v` text and in a hex dump.
- Use the layer models (OSI's seven, TCP/IP's four) as a debugging order: link, then neighbour, then route, then port, then protocol; name the layer a symptom belongs to and the tool that tests it.
- Explain ARP: why a packet to a far host carries the gateway's hardware address, what `ip neigh` states mean, and what a stale or failed entry looks like from both ends.
- Read ICMP: echo, destination unreachable and its codes (port, host, fragmentation needed), time exceeded; say which ICMP messages a firewall must never drop.
- Do encapsulation arithmetic on sight: MTU, MSS, what a tunnel's headers cost, the largest `ping -M do` that fits.
- Recognise a path-MTU black hole (handshake fine, small pages fine, big transfers hang), prove it with captures and a DF probe, and fix it at its cause rather than around it.

**The six-month core.** Shown a capture from two points on a path, say what changed and why. Shown a symptom, start at the right layer. Know that ICMP "fragmentation needed" (and IPv6's "packet too big") must get through, and recognise the black hole the moment someone says "small things work, big things hang". Subtract a tunnel's overhead from an MTU in your head (1500 − 24 = 1476 for GRE, − 50 = 1450 for VXLAN, − 40 = 1460 for a TCP payload).

## 2. Prerequisites and terms

**`prerequisites: [csa.m1.checkpoint]`** (the outline's, kept: Module 3 opens straight after Module 1, and this is its first topic).

**Builds on, for the writer** (Module 1 taught each of these; this topic never re-teaches them):

| Module 1 topic | What this topic leans on |
| --- | --- |
| `csa.linux.net-tools` | `ip -br addr`, `ip route` and the default gateway, "the kernel picks the most specific matching line"; `ip neigh` named as the ARP table in one sentence; `ss`; `tcpdump -nn -i IF FILTER`, `-c`, `-w`, the handshake flags, refused (`[R.]`) against dropped (repeated SYN); traceroute and `* * *` (and that it listens for "time exceeded"); nftables hooks, chains, `policy drop`, `ct state established,related accept` (its recall item `mcq-conntrack` already says "related means something like an ICMP error about a known connection"); `reject` sends ICMP port-unreachable; network namespaces, veth pairs, the office pattern and `from-office`; NAT named. |
| `csa.linux.permissions` | octal digits as groups of bits (`rwx` = 7), the first time the track turns bits into a number |
| `csa.linux.scripting` | writing a bash script, `chmod +x`, exit statuses, `$(...)`, `if`, ShellCheck |
| `csa.linux.shell` | `grep`, `awk` fields, `cut`, `sort`, pipes |
| `csa.linux.services` | `systemctl`, `journalctl` |
| `csa.linux.hardening` | a fix never weakens security; a fix lives in the file, not only in the running system |

**Terms this topic must define itself** (none is defined earlier in the track; the routing designer asks that TTL, "time exceeded" and "unreachable" be defined here, and they are): layer; protocol; the OSI model and the TCP/IP (internet) model; header and payload; encapsulation and decapsulation; frame, packet, segment, datagram (each word with its layer); hexadecimal (Module 1 taught octal only: one paragraph, "two hex digits are one byte, `0x40` is 64") and byte (octet); MAC address (hardware address) and EtherType; broadcast (`ff:ff:ff:ff:ff:ff`); switch and bridge, in one sentence each; ARP, request and reply, the neighbour table and its states (`REACHABLE`, `STALE`, `DELAY`, `INCOMPLETE`, `FAILED`, `PERMANENT`); gratuitous ARP; hop; TTL; checksum (one sentence: a router rewrites it because the TTL changed); ICMP, type and code; echo request and reply; destination unreachable (net, host, port, fragmentation needed); time exceeded; MTU; jumbo frame; MSS; fragmentation and the DF ("don't fragment") flag; path MTU and path MTU discovery (PMTUD); black hole; MSS clamping; tunnel; overlay and underlay; GRE; VXLAN (one paragraph); `tracepath`; `tshark` (Wireshark's command-line twin, in the lab image).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `layer-model` | The OSI and TCP/IP models as a map, not a creed: which layer a header, a device, a tool and a symptom belong to; working up the layers to place a fault (link up? neighbour resolved? route? port? protocol?); why "it pings" proves only layer 3; where the clouds hide layers 1 and 2 from you |
| `read-headers` | Read a capture field by field: Ethernet (destination and source MAC, EtherType), IPv4 (version and header length, total length, identification, flags and DF, TTL, protocol number, addresses), the transport ports; the same packet on two sides of a router (MACs and TTL change, addresses and id don't); the same fields in a hex dump; `tcpdump -e -v`, `-xx`, `tshark -V` |
| `arp-neighbours` | ARP request (broadcast, "who has") and reply (unicast, "is at"); the gateway's MAC on every packet to another network; `ip neigh` states and what `FAILED`, `INCOMPLETE` and a wrong `PERMANENT` entry mean; why clouds answer ARP themselves and carry no broadcast (so a floating address by gratuitous ARP doesn't work there) |
| `icmp-messages` | ICMP's types and codes and what each tells you: echo (ping), destination unreachable (net, host, port, fragmentation needed with the next hop's MTU), time exceeded (traceroute, and a routing loop); that ICMP errors carry the start of the packet that caused them (which is how connection tracking calls them `related`); which ICMP a firewall must let through |
| `encapsulation-mtu` | The arithmetic: MTU against frame size against MSS; IPv4 20, TCP 20, UDP 8, ICMP 8, Ethernet 14 bytes; a tunnel's cost (IPIP 20, GRE 24, VXLAN 50) and the inner MTU it leaves; the largest `ping -M do -s` that fits (MTU − 28); the clouds' MTUs (AWS 9001 inside a VPC and 1500 at its edges, Google 1460 by default, Azure 1500) |
| `pmtud-blackholes` | How path MTU discovery works (DF, "fragmentation needed", the sender's per-destination cache); the black hole when that ICMP is dropped (handshake and small replies fine, bulk transfers hang); proving it (`tracepath`, `ping -M do -s`, `ip route get`'s cached `mtu`, a capture at the sender showing the ICMP arriving); fixing it at the cause (let the ICMP through) and why MSS clamping, a lowered MTU on every host or a static route MTU are workarounds, not fixes |

`encapsulation-mtu` is a calculation skill: seven estimate items below (ADR-0024 rule 6 asks for three).

## 4. Lesson plan

The lesson's job is to make five pictures concrete; the labs then make the learner produce them. Every claim in the lesson is checked against section 5. The labs' machines are named in the lesson so the intro and the worked example tell one story: **office** (a laptop), **r1** (the office router), a **GRE tunnel** across the internet, **r2** (the cloud router) and **web** (a server).

1. **Why layers exist** (main resource, Beej ch. 4, 11 min). Each layer solves one problem and trusts the one below: the link layer moves a frame to the next box on the same wire; the internet layer moves a packet across many links; the transport layer gives a program a port and (with TCP) reliability; the application layer is the conversation itself. **Picture the lesson supplies** (Beej describes layering in prose; a beginner needs it drawn): the nested envelope, drawn as text, for one HTTP request leaving the office laptop:

   ```
   | Ethernet: to r1's MAC, from office's MAC, type 0x0800 | IPv4: 10.0.1.10 -> 10.0.2.20, TTL 64, proto 6 | TCP: 51514 -> 80 | GET / HTTP/1.1 ... |
   ```

   Then the same request leaving r2 towards web: only the Ethernet part and the TTL changed. The OSI model's seven layers in a table beside TCP/IP's four, with **one** example of each and the tool that tests it (`ip link` and `ethtool`: 1–2; `ip neigh`: 2; `ping`, `ip route get`, `traceroute`: 3; `ss`, `nc -z`: 4; `curl`, `dig`: 7), and the honest remark that layers 5 and 6 rarely earn their names in practice and that TLS sits awkwardly between 4 and 7: the model is a debugging order, not a law.

2. **Down and up, hop by hop** (Ben Eater, "Hop-by-hop routing", 14 min; "Looking at ARP and ping packets", 9 min). The worked example's own captures carry this section (section 7, item 1): the same echo request captured on r1's office side and r2's cloud side. **The lesson's table, from the prototype's capture** (2026-11-11):

   | Field | Office side (r1 eth0) | Cloud side (r2 lan) |
   | --- | --- | --- |
   | Source MAC | office's | r2's |
   | Destination MAC | r1's | web's |
   | IP source → destination | 10.0.1.10 → 10.0.2.20 | 10.0.1.10 → 10.0.2.20 |
   | IP identification | 42369 | 42369 |
   | TTL | 64 | 62 |

   Two routers, two decrements. **Where the clouds differ:** none of the three lets a VM see layers 1 and 2 of the physical network; the hypervisor answers ARP, and AWS, Azure and Google all say their networks carry no broadcast (facts F15–F17).

3. **ARP** (Ben Eater, "ARP: Mapping between IP and Ethernet", 10 min; Beej ch. 21 as the reading alternative, 8 min). The laptop asks "who has 10.0.1.1?" (broadcast) and never asks for web's MAC: it can't reach web's wire. The `ip neigh` states, and the two failures a learner will meet: `FAILED` (nobody answered: wrong address, wrong netmask, the host is down) and a `PERMANENT` entry someone typed in that is now wrong (frames go to a card that isn't there). **The lesson supplies:** a bridge (a switch) floods a frame for an unknown MAC to every port, so a capture on another host can show frames addressed to someone else (`tcpdump` listens promiscuously); a host drops them. The prototype showed exactly this (fact F21).

4. **Reading a header in hex** (the worked example's step 4; Ben Eater's "The Internet Protocol" as optional viewing, 10 min). **The lesson supplies** the byte map for the first 34 bytes of the captured echo request (fact F22), one line per field: 6 bytes destination MAC, 6 source MAC, 2 EtherType (`0800`), then IPv4: `45` (version 4, header 5 × 4 = 20 bytes), `00`, total length `0054` (84), id `a5e8`, flags `4000` (DF), TTL `40` (64), protocol `01` (ICMP), checksum, source `0a00010a` (10.0.1.10), destination `0a000214` (10.0.2.20). Then `tshark -V` on the same packet prints the same thing in words. Hex: two digits per byte, `0x40` = 4 × 16 + 0 = 64.

5. **ICMP, the network's error channel** (Cloudflare blog's first half, 10 min; RFC 792's type list as optional reference). Types and codes in a table (echo 8 and 0; destination unreachable 3 with codes 0 net, 1 host, 3 port, 4 fragmentation needed; time exceeded 11). What each looks like in `ping` and `traceroute` output (`Destination Host Unreachable`, `Time to live exceeded`, `Frag needed and DF set (mtu = 1476)`, `!H`, `!N`). An ICMP error carries the IP header and the first 8 bytes of the packet that caused it (RFC 792), which is how connection tracking matches it to a connection and calls it `related`: the lesson ties this to Module 1's `ct state established,related accept`, which is why that one rule lets path-MTU messages in.

6. **Encapsulation and MTU** (Cloudflare, "What is MTU?", 11 min). MTU is the biggest IP packet a link carries; a full-size Ethernet frame is 1500 + 14 bytes in a capture (`length 1514`); MSS is what TCP can carry after 40 bytes of headers (1460). A tunnel puts a whole packet inside another: GRE adds a 20-byte outer IPv4 header and a 4-byte GRE header, so its inner MTU is 1476 over a 1500 link; VXLAN carries a whole Ethernet frame inside UDP (14 + 8 + 8 + 20 = 50 bytes, 1450). **Correct the main MTU resource here:** Cloudflare's page says "1,500 bytes is the maximum MTU size"; it's the maximum on most of the internet, but inside clouds bigger "jumbo" frames are normal (AWS 9001, Google up to 8896, Azure up to 9000 on its newest adapter; facts F12–F14). **Where the clouds differ** (a table: default MTU, maximum, where it drops to 1500, whether the provider clamps MSS for you): AWS 9001 inside a VPC, 1500 over an internet gateway or a VPN, 8500 over inter-region peering; Google 1460 by default, settable 1300–8896, clamps MSS for traffic leaving the VPC and not inside it; Azure 1500, larger only inside a VNet or same-region peering. Azure blocks GRE inside a VNet entirely, while Google supports it (fact F15, F16): an architect who plans a GRE overlay between VMs has to know that.

7. **Path MTU discovery and the black hole** (Cloudflare blog's ICMP black-hole section; RFC 2923 §2.1 optional, 5 min). The sender sets DF; a router whose next link is too small drops the packet and sends "fragmentation needed" with that link's MTU; the sender caches it for that destination (Linux: ten minutes, fact F7) and resends smaller. Drop that ICMP and the handshake still works (SYNs are small), small pages still load, and the first full-size data packet vanishes: the download stalls until the connection times out. **The lesson supplies the proof sequence** the debug lab needs, exactly as the prototype ran it: `tracepath` from the client; `ping -M do -s 1472` from the *sender* (the server, for a download); a capture on the server showing `ICMP ... unreachable - need to frag (mtu 1476)` arriving (tcpdump sees a packet before the firewall drops it, fact F20); the server's `ip route get CLIENT` showing no cached `mtu`; then the firewall rule. And the honest ranking of fixes: let the ICMP through (the cause); MSS clamping on the tunnel's routers (common, and Google's VPC does it itself for traffic leaving the network, F13, but it rescues TCP only); lowering every host's MTU (works, on every host, forever). IPv6 forbids routers to fragment at all, so the same message (Packet Too Big) is even more vital there; topic 25 returns to it.

**Recap** (the lesson's last block): the envelope picture; the two-sided table; ARP's two failures; the ICMP table; the overhead numbers (14, 20, 20, 8, 8; GRE 24, VXLAN 50; ping's 28); the black-hole signature and the three fixes ranked.

## 5. Verified facts

Every specific claim the lesson, the items or the labs rely on. "Captured" means real output of the prototype labs on the owner's PC (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, Ubuntu 24.04 packages: iproute2 6.1.0-1ubuntu6.4, tcpdump 4.99.4-3ubuntu4.24.04.1, nftables 1.0.9-1ubuntu0.1, iputils 20240117) on 2026-11-11.

| # | Claim | Source, read 2026-11-11 |
| --- | --- | --- |
| F1 | IPv4 header fields in order; IHL counts 32-bit words, minimum 5 (20 bytes); flags hold DF and MF; fragment offset in 8-byte units; each hop reduces TTL by at least one and a datagram at zero is destroyed; every host accepts 576-byte datagrams | https://www.rfc-editor.org/rfc/rfc791.html (September 1981) |
| F2 | ICMP types: 0 echo reply, 3 destination unreachable, 5 redirect, 8 echo, 11 time exceeded; unreachable codes 0 net, 1 host, 2 protocol, 3 port, 4 fragmentation needed and DF set; time exceeded code 0 TTL, 1 reassembly; an error carries the original IP header and the first 64 bits of its data | https://www.rfc-editor.org/rfc/rfc792.html (September 1981) |
| F3 | ARP: the request is broadcast; the reply goes straight back to the requester; opcodes 1 (request) and 2 (reply); the receiver records the sender's pair before looking at the opcode | https://www.rfc-editor.org/rfc/rfc826.html (November 1982) |
| F4 | EtherType 0x0800 is IPv4 and 0x0806 is ARP; a full-size frame shows `length 1514` in `tcpdump -e`; ARP frames `length 42` | Captured (tcpdump prints `ethertype IPv4 (0x0800)`, `ethertype ARP (0x0806)`) |
| F5 | PMTUD sets DF; a router that can't forward sends type 3 code 4 with the next hop's MTU in the low 16 bits; a host never lowers its estimate below 68; probing for a larger PMTU no sooner than every 5 minutes, 10 recommended | https://www.rfc-editor.org/rfc/rfc1191.html (November 1990) |
| F6 | The black hole: when "fragmentation needed" doesn't arrive, the SYN (small) gets through, the first large data packet doesn't, bulk transfers fail and the connection times out | https://www.rfc-editor.org/rfc/rfc2923.html §2.1 (September 2000, Informational) |
| F7 | Linux caches a learned path MTU per destination for 10 minutes: `ip route get` printed `cache expires 599sec mtu 1476` after one "fragmentation needed". The kernel's sysctl page describes `mtu_expires` but gives no default; the 600 s comes from the capture | Captured; https://docs.kernel.org/networking/ip-sysctl.html |
| F8 | `ip_no_pmtu_disc` disables PMTUD (default off); `tcp_mtu_probing` 0 off, 1 on when a black hole is detected, 2 always | https://docs.kernel.org/networking/ip-sysctl.html |
| F9 | Over a 1500-byte link the kernel gives a new tunnel these MTUs: GRE 1476, IPIP 1480, SIT 1480, VXLAN 1450, gretap 1462, ip6gre 1448, WireGuard 1420 | Captured (`ip link add ... type X`, then `ip -o link`) |
| F10 | A GRE packet: outer IPv4 `proto GRE (47)`, outer length 108 for an 84-byte inner packet (20 + 4 bytes added) | Captured (`tcpdump -nn -v -i vb proto gre`) |
| F11 | VXLAN: 8-byte header, UDP destination port 4789, the inner Ethernet frame carried whole; VTEPs must not fragment | https://www.rfc-editor.org/rfc/rfc7348.html (August 2014) |
| F12 | AWS: all instance types support 1500; current generation supports 9001 jumbo frames; 1500 is the limit over an internet gateway, VPN connections, and between Regions unless a transit gateway is used; 8500 over inter-region peering; packets over the limit are fragmented, or dropped if DF is set; PMTUD needs inbound ICMP type 3 code 4 to reach the instance, which a security group or network ACL can block | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/network_mtu.html |
| F13 | Google: VPC default MTU 1,460; settable 1,300 to 8,896; oversized packets are dropped, never fragmented by the VPC; with DF set Google sends Fragmentation Needed or Packet Too Big; no MSS clamping inside a VPC, MSS clamping for destinations outside it | https://docs.cloud.google.com/vpc/docs/mtu |
| F14 | Azure: default MTU 1500; larger only for traffic inside the VNet and directly peered VNets in the same region (gateways, global peering and the internet are not supported); largest 3900 on Mellanox adapters, 9000 on the Microsoft Azure Network Adapter (MANA); its own instructions subtract 28 for `ping -M do -s` (page dated 2024-07-22, updated 2026-08-07) | https://learn.microsoft.com/en-us/azure/virtual-network/how-to-virtual-machine-mtu |
| F15 | Azure: "Multicast, broadcast, IP-in-IP encapsulated packets, and Generic Routing Encapsulation (GRE) packets are blocked in virtual networks" (FAQ dated 2026-07-08) | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq |
| F16 | Google: VPC networks don't support broadcast or multicast; they support GRE version 0 (Cloud NAT and Application Load Balancers don't) | https://docs.cloud.google.com/vpc/docs/vpc |
| F17 | AWS: "We do not support broadcast in a VPC" (the reason x.x.x.255 is reserved). AWS's VPC FAQ says nothing about broadcast, multicast or GRE, and no AWS page read says whether GRE between instances is allowed: the lesson claims nothing about GRE on AWS | https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html; https://aws.amazon.com/vpc/faqs/ |
| F18 | Cloudflare's MTU page says "1,500 bytes is the maximum MTU size". Contradicted for clouds by F12–F14: the lesson says so | https://www.cloudflare.com/learning/network-layer/what-is-mtu/ |
| F19 | Linux `ping` sets DF on its echo requests (`flags [DF]` in the capture); `ping -M do -s N` sends N bytes of data in an N + 28 byte packet (`1472(1500) bytes of data`); after one "fragmentation needed" a repeat says `local error: message too long, mtu=1476` | Captured (iputils 20240117) |
| F20 | `tcpdump` on a host shows an incoming packet that the host's nftables `input` chain then drops: `ICMP 10.0.1.10 unreachable - need to frag (mtu 1476)` was captured on web while its firewall dropped every ICMP, and the download stalled | Captured |
| F21 | With a wrong `PERMANENT` neighbour entry on r2, frames for files went to `02:00:00:00:00:99`; the bridge flooded them, so `tcpdump -e` on files showed them addressed to a MAC that isn't files'; traceroute stopped after r2 | Captured |
| F22 | The captured echo request's first 34 bytes: `2604 1a3a 09dd c62e 2b1c a275 0800 4500 0054 a5e8 4000 4001 7da3 0a00 010a 0a00 0214` (r1's MAC, office's MAC, IPv4, IHL 5, length 84, id 0xa5e8, DF, TTL 64, ICMP, checksum, 10.0.1.10, 10.0.2.20) | Captured (`tcpdump -nn -xx -c1`) |
| F23 | The same echo request on both sides: id 42369 on both; TTL 64 on the office side, 62 on the cloud side; MACs office→r1 and r2→web; ARP asked for 10.0.1.1 on the office side and 10.0.2.20 on the cloud side | Captured |
| F24 | A loop made by a link that's down (r2's printer link down, r2's default route back through the tunnel, r1's route for 10.0.0.0/16 into the tunnel): `ping` printed `From 10.255.0.2 icmp_seq=1 Time to live exceeded`; traceroute alternated 10.0.1.1 and 10.255.0.2 | Captured |
| F25 | `tracepath` across the GRE tunnel: `2:  10.0.1.1  pmtu 1476` and `Resume: pmtu 1476 hops 3 back 3` | Captured |
| F26 | `nc -z -w2` without `-v` prints nothing on failure and exits 1 for both refused (4 ms) and dropped (2,006 ms); an on-link address nobody owns ends `FAILED` in `ip neigh` | Captured (netcat-openbsd, Ubuntu 24.04) |
| F27 | IPv6 routers never fragment; "fragmentation is performed only by source nodes"; the equivalent message is ICMPv6 Packet Too Big (type 2) | https://www.rfc-editor.org/rfc/rfc8200.html; AWS page in F12 |

Not confirmed, so not claimed: the GRE header size from RFC 2784 itself (not re-read; F10's capture shows 4 bytes), WireGuard's overhead breakdown (wg-quick's manual doesn't state it; F9's 1420 is only the kernel's default for a new device), PLPMTUD's RFCs (4821, 8899; named in one optional sentence, not read).

## 6. Resources

Each fetched on 2026-11-11. Minutes are reading at about 130 words a minute, or the video's length.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | Beej's Guide to Network Concepts, ch. 4 "The Layered Network Model" (sections 4.1–4.4: layering of protocols on data, the Internet layer model, the ISO OSI model) | https://beej.us/guide/bgnet0/html/split/the-layered-network-model.html | reading | CC BY-NC-ND 3.0 (the guide's foreword); linked, not copied | 11 (1,473 words) | `layer-model`, `encapsulation-mtu` | exists, free, headings confirmed; guide v1.11.4 |
| 1 | Ben Eater, "Hop-by-hop routing" (Networking tutorial 11 of 13) | https://www.youtube.com/watch?v=VWJ8GmYnjTs | video | YouTube standard licence; embeddable (oEmbed and `playableInEmbed` true) | 14 (13:49) | `read-headers`, `layer-model` | exists on Ben Eater's channel; content judged by title and the series page only: **watch once before writing** |
| 2 | Ben Eater, "Looking at ARP and ping packets" (10 of 13) | https://www.youtube.com/watch?v=xNbdeyEI-nE | video | as above | 9 (8:50) | `arp-neighbours`, `icmp-messages`, `read-headers` | as above |
| 3 | Ben Eater, "ARP: Mapping between IP and Ethernet" (9 of 13) | https://www.youtube.com/watch?v=aamG4-tH_m8 | video | as above | 10 (10:06) | `arp-neighbours` | as above |
| 4 | Cloudflare Learning Center, "What is MTU (maximum transmission unit)?" (to the end of "What is MSS?") | https://www.cloudflare.com/learning/network-layer/what-is-mtu/ | reading | © 2026 Cloudflare, Inc.; linked, not copied | 11 (about 1,450 words) | `encapsulation-mtu`, `pmtud-blackholes` | opened (WebFetch was refused with 403; a plain fetch got the page); the "1,500 is the maximum" line is corrected by the lesson (F18) |
| 5 | Marek Majkowski, "Path MTU discovery in practice" (Cloudflare blog, 2015-02-04): read to the end of the black-hole section | https://blog.cloudflare.com/path-mtu-discovery-in-practice/ | reading | © Cloudflare, Inc.; linked, not copied | 10 (first half of 2,827 words) | `pmtud-blackholes`, `icmp-messages` | opened; covers DF, type 3 code 4, the tcpdump filter `icmp[0] == 3 and icmp[1] == 4`, the black hole and `tcp_mtu_probing` |
| 6 | Ben Eater, "The Internet Protocol" (8 of 13), optional | https://www.youtube.com/watch?v=rPoalUa4m8E | video | as row 1 | 10 (9:33) | `read-headers` | as row 1 |
| 7 | Beej, ch. 21 "ARP: The Address Resolution Protocol", optional reading alternative to row 3 | https://beej.us/guide/bgnet0/html/split/arp-the-address-resolution-protocol.html | reading | CC BY-NC-ND 3.0 | 8 (1,077 words) | `arp-neighbours` | headings confirmed (broadcast frames, caching, request/response, announcements) |
| 8 | Beej, ch. 20 "The Link Layer and Ethernet", optional | https://beej.us/guide/bgnet0/html/split/the-link-layer-and-ethernet.html | reading | CC BY-NC-ND 3.0 | 15 (1,900 words) | `layer-model`, `read-headers` | headings confirmed (frames against packets, MAC addresses) |
| 9 | AWS, "Network maximum transmission unit (MTU) for your EC2 instance": "Jumbo frames" and "Path MTU Discovery" | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/network_mtu.html | reading | © Amazon Web Services; linked, not copied | 5 | `encapsulation-mtu`, `pmtud-blackholes` | opened |
| 10 | Google Cloud, "Maximum transmission unit" (VPC) | https://docs.cloud.google.com/vpc/docs/mtu | reading | CC BY 4.0 (Google Cloud docs, as Module 2 recorded; the footer wasn't in the text fetched) | 5 | `encapsulation-mtu`, `pmtud-blackholes` | opened |
| 11 | Azure, "Configure MTU for virtual machines in Azure": "Precautions" and "Path MTU Discovery" | https://learn.microsoft.com/en-us/azure/virtual-network/how-to-virtual-machine-mtu | reading | CC BY 4.0 (MicrosoftDocs, as Module 2 recorded); linked | 4 | `encapsulation-mtu` | opened (dated 2024-07-22, updated 2026-08-07) |
| 12 | RFC 2923, section 2.1 "Black Hole Detection", optional | https://www.rfc-editor.org/rfc/rfc2923.html | reading | IETF Trust Legal Provisions; linked, not copied | 5 | `pmtud-blackholes` | opened |
| 13 | RFC 792, the type and code lists, optional reference | https://www.rfc-editor.org/rfc/rfc792.html | reading | IETF Trust; linked | 5 | `icmp-messages` | opened |

Assigned minutes (rows 0 to 5 and 9 to 11): 11 + 14 + 9 + 10 + 11 + 10 + 5 + 5 + 4 = 79. The ARP video (row 3) and Beej's ARP chapter (row 7) are alternatives; the lesson says "one of the two", so 69 minutes are required.

Also considered and not used: Practical Networking's "Packet Traveling" series page (a 200-word index; the articles weren't opened); Cloudflare's ICMP page (404 at the URL tried).

## 7. Practice ladder

Order for `topic.yaml`'s `practice:` is the order below. "Captured" items use the prototype's real output (section 5, identifiers already harmless: documentation and private addresses, random MACs); "constructed" items say so in their prompt.

### 7.1 `example-follow-a-request` (worked example, systemd network lab, 35 minutes)

**Topology** (the base's topology words): `office` 10.0.1.10/24 —lan— `r1` (eth0 10.0.1.1/24, wan 203.0.113.1/24) —link "internet" 203.0.113.0/24— `r2` (wan 203.0.113.2/24, lan 10.0.2.1/24) —lan— `web` 10.0.2.20/24 running nginx (or the base's test server) with `/` and a 2 MB `/pricelist.csv`. A GRE tunnel r1 ⇄ r2 (10.255.0.1/30 ⇄ 10.255.0.2/30) carries 10.0.0.0/16 (r1: `10.0.0.0/16 dev gre1`; r2: `10.0.1.0/24 dev gre1`); both tunnel ends are scenery here. Everything works.

**Steps** (each a labelled step with a `note`, typed by the learner):

1. *Where packets go.* `on office ip -br addr`, `on office ip route`, `on r1 ip route`: the office's default gateway, r1's route into the tunnel.
2. *Start from empty neighbour tables, capture both sides.* `for m in office r1 r2 web; do on $m ip neigh flush all; done`; then two background captures, `on r1 tcpdump -e -nn -v -l -i eth0 'arp or icmp' > ~/example/office-side.txt &` and `on r2 tcpdump -e -nn -v -l -i lan 'arp or icmp' > ~/example/cloud-side.txt &`, one `on office ping -c1 10.0.2.20`, then `kill %1 %2`.
3. *Read the two files side by side* (the note walks the lesson's table: ARP for the gateway only; MACs differ per side; id and addresses identical; TTL 64 then 62).
4. *The same packet in hex.* `on r1 tcpdump -nn -xx -c1 -i eth0 icmp > ~/example/hex.txt &`, a ping, `wait`; then `on r1 tshark -V -c1 -i eth0 icmp` (with a ping in another line) for the dissection in words. The note maps the bytes (lesson section 4).
5. *Encapsulation on the wire.* `on r1 tcpdump -nn -v -c2 -i wan > ~/example/wan.txt &`, a ping, `wait`: outer `203.0.113.1 > 203.0.113.2: GREv0`, inner `10.0.1.10 > 10.0.2.20`; outer length = inner + 24. Then `on r1 tcpdump -nn -c2 -i gre1`: on the tunnel interface only the inner packet is seen.
6. *The path's MTU.* `on office tracepath -n 10.0.2.20 | tee ~/example/pmtu.txt`; `on office ping -c1 -M do -s 1448 10.0.2.20` (passes) and `-s 1449` (first `Frag needed and DF set (mtu = 1476)`, then `local error`); `on office ip route get 10.0.2.20` shows `cache expires ... mtu 1476`.
7. *Save.* The four files above under `~/example/`.

**Checks:** `office-side` holds an ARP request for 10.0.1.1 from 10.0.1.10 and its reply, and an echo request with `ttl 64`; `cloud-side` holds an echo request with `ttl 62` whose IP `id` equals the office-side one (the check extracts both ids: one packet, seen twice); `hex` holds a line beginning `0x0000:` whose 13th–14th bytes are `0800`; `wan` holds `proto GRE (47)` with both inner addresses; `pmtu` holds `pmtu 1476`.

**Wrong fixes:** `two-pings.sh` (each capture got its own ping, so the ids differ); `no-flush.sh` (no ARP in the capture); `tunnel-interface.sh` (the encapsulation capture taken on `gre1`, so no GRE in it).

### 7.2 Recall: layers and headers

2. **`mcq-which-layer`** (mcq, `layer-model`). "From the office, `ping 10.0.2.20` gets replies, but `nc -zv 10.0.2.20 5432` says the connection was refused. At which layer is the problem, and what does it mean?" Right: "The transport layer: the machine is reachable, but nothing listens on that port". Wrong: "The link layer: the switch port to the server is down, so only small pings get through"; "The network layer: a router drops TCP but forwards ICMP, so pings work and connections don't"; "The application layer: the database rejected the password, which nc reports as refused". Explanation: a reset is the server's kernel answering (Module 1); a router dropping TCP would give a timeout, not a refusal; nc sends no password.
3. **`mcq-tool-for-layer`** (mcq, `layer-model`). "A server 'can't be reached'. You want to test layer 2 only, on the server's own network: does the next box answer for its address?" Right: "`ip neigh show` after a ping, to see whether the gateway's entry resolved". Wrong: "`traceroute -n` to the gateway, to see whether the first hop shows a time"; "`nc -zv` to the gateway on port 22, to see whether the port is open"; "`dig` for the gateway's name, to see whether it resolves to an address". Explanation names each tool's layer.
4. **`hdr-two-sides`** (predict_shell, `read-headers`, captured). Files `office-side.txt` and `cloud-side.txt`: the two echo-request lines of F23 (with their `-e -v` second lines). Command: `for f in office-side.txt cloud-side.txt; do awk '/ICMP echo request/ {print FILENAME, prev} {prev = $0}' "$f"; done | grep -o '^[a-z-]*\.txt\|[0-9a-f:]\{17\} > [0-9a-f:]\{17\}\|ttl [0-9]*\|id [0-9]*'`. The writer pins the output under real bash (it must print, per file, the MAC pair, `ttl` and `id`) and simplifies the command if the pinned output is hard to read; the prompt explains each piece. Explanation: what changed (MACs, TTL) and what didn't (id, addresses), and why two decrements means two routers.
5. **`hdr-hex-ttl`** (predict_shell, `read-headers`, captured F22). `hex.txt`: the dump's first two lines. Command: `set -- $(sed -n 2p hex.txt); printf 'length=%d ttl=%d proto=%d\n' 0x$2 0x${5:0:2} 0x${5:2:2}`. Output `length=84 ttl=64 proto=1`. The prompt says which group holds which field ("the 0x0010 line's second group is the total length; its fifth group is the TTL byte then the protocol byte") and that `printf %d 0x40` turns hex into decimal; the learner predicts the decimal values. Explanation: 0x54 = 5 × 16 + 4 = 84; 0x40 = 64; protocol 1 is ICMP (6 TCP, 17 UDP, 47 GRE).
6. **`est-ping-data-bytes`** (estimate, `encapsulation-mtu`, `read-headers`). "A capture of a ping shows the IPv4 header's total length as 84 bytes. The IPv4 header is 20 bytes and the ICMP header 8. How many bytes of data did ping put in the packet? Exactly." given `{total: 84, ip: 20, icmp: 8}`, working `total - ip - icmp`, answer 56. Mistakes: 64 (`total - ip`, forgot ICMP's header), 76 (`total - icmp`), 70 (`total - 14`, took off an Ethernet header that isn't part of the IP length).

### 7.3 Recall: ARP

7. **`arp-who-has`** (predict_shell, `arp-neighbours`, captured F23). The office-side file's two ARP lines and one echo request. Command: `grep -o 'who-has [0-9.]* tell [0-9.]*\|[0-9.]* is-at [0-9a-f:]*' office-side.txt`. Output: `who-has 10.0.1.1 tell 10.0.1.10` and `10.0.1.1 is-at 26:04:1a:3a:09:dd`. Explanation: the laptop asked for the gateway, never for 10.0.2.20; the request went to `ff:ff:ff:ff:ff:ff`, the reply straight back.
8. **`mcq-gateway-mac`** (mcq, `arp-neighbours`). "The office laptop (10.0.1.10/24, gateway 10.0.1.1) sends a packet to 10.0.2.20. Which destination MAC does the frame leaving the laptop carry?" Right: "The MAC of 10.0.1.1, the gateway, which the laptop found with ARP". Wrong: "The MAC of 10.0.2.20, which the laptop found by asking ARP across the router"; "The broadcast MAC, so every machine on the office network sees it"; "No MAC at all, because routed packets travel at layer 3 only". Explanation: ARP never crosses a router; each hop has its own frame.
9. **`arp-neigh-states`** (predict_shell, `arp-neighbours`, constructed in `ip neigh` format). `neigh.txt`: six lines, states `REACHABLE`, `STALE`, `DELAY`, `FAILED`, `INCOMPLETE`, `PERMANENT`. Command: `awk '$NF == "FAILED" || $NF == "INCOMPLETE" {print $1, "no answer"} $NF == "PERMANENT" {print $1, "typed in by hand:", $5}' neigh.txt`. Explanation: what each state means; a `PERMANENT` entry is never checked again, so a replaced card breaks it silently.
10. **`mcq-stale-permanent`** (mcq, `arp-neighbours`). Scenario from the debug's fault but in another story (a printer at 192.168.5.40, card replaced, router shows `192.168.5.40 dev lan lladdr 02:00:00:00:00:41 PERMANENT`, printer's `ip link` shows another MAC). Right: "The router sends every frame to the old card's MAC, which the printer ignores". Wrong: "The printer's address is in use twice, so the switch sends frames to both cards"; "ARP entries expire after a minute, so it will fix itself if you wait"; "The router can't route to 192.168.5.0/24 until someone adds a static route". Explanation: `PERMANENT` never expires; delete the pin and let ARP work.
11. **`mcq-cloud-floating-ip`** (mcq, `arp-neighbours`, `layer-model`). "Two VMs in a cloud network share a 'floating' address: when one fails, keepalived on the other announces the address with a gratuitous ARP. On a data-centre LAN this works. Why not in AWS, Azure or Google Cloud?" Right: "The cloud answers ARP itself and carries no broadcast, so nobody hears it". Wrong: "Cloud VMs have no MAC addresses of their own, so ARP can't name the new owner"; "The clouds block every ARP packet to stop spoofing, so VMs can't find each other"; "Gratuitous ARP needs IPv6, and the clouds' networks carry IPv4 unless you ask". Explanation: F15–F17; the cloud way is to move the address with the provider's API, or put a load balancer in front.

### 7.4 Recall: ICMP

12. **`icmp-ping-verdicts`** (predict_shell, `icmp-messages`, captured lines F19, F24 plus one constructed `Destination Host Unreachable`). `ping.txt`: four lines (`64 bytes from ...`, `From 10.255.0.2 icmp_seq=1 Time to live exceeded`, `From 10.0.2.1 icmp_seq=1 Frag needed and DF set (mtu = 1476)`, `From 10.0.7.10 icmp_seq=1 Destination Host Unreachable`). Command: `awk '/bytes from/ {print "reply"} /Time to live/ {print "loop or too far:", $2} /Frag needed/ {print "too big for the path:", $NF} /Host Unreachable/ {print "no ARP answer, says", $2}' ping.txt` (the writer pins `$NF` and the closing bracket). Explanation per line: type 0; type 11 code 0, who sent it; type 3 code 4 and the next hop's MTU; type 3 code 1 (the sender's own stack, after ARP failed).
13. **`mcq-traceroute-loop`** (mcq, `icmp-messages`). Captured F24 traceroute (hops alternating 10.0.1.1 and 10.255.0.2). Right: "Two routers pass these packets back and forth until their TTL runs out". Wrong: "Two routers share the load, and traceroute shows whichever one answered"; "The destination is down, so the routers report their own addresses instead"; "The tunnel drops traceroute's probes, so the same hops are retried". Explanation: time exceeded comes from the router where TTL hit zero; a loop alternates; the cause is usually a route (or a link that's down, so a default route takes over: the debug).
14. **`mcq-icmp-related`** (mcq, `icmp-messages`, `pmtud-blackholes`). "A server's firewall is `policy drop` with `ct state established,related accept` and `tcp dport 443 accept`. A router on the path sends it 'fragmentation needed' about one of its HTTPS connections. What happens?" Right: "It is accepted: it is related to a tracked connection, because it quotes that packet". Wrong: "It is dropped: no rule mentions ICMP, so the policy applies to it"; "It is accepted: every ICMP message counts as established once a connection exists"; "It is dropped: related only covers FTP's data connections, not ICMP". Explanation: RFC 792's "header + 64 bits", Module 1's `mcq-conntrack`; and the trap the debug plants: a rule that drops ICMP *before* the `ct` line overrides this.
15. **`mcq-never-block`** (mcq, `icmp-messages`). "A security review wants to drop all ICMP at the edge to 'hide' the servers. Which ICMP message is the most important to keep letting in, and why?" Right: "Fragmentation needed, because without it large transfers silently hang". Wrong: "Echo request, because without it monitoring can't tell a server is up"; "Redirect, because without it routers can't send hosts a better path"; "Timestamp, because without it clocks drift and TLS certificates fail". Explanation: echo is a policy choice; redirects are better off; timestamp is unused; "fragmentation needed" (and IPv6's Packet Too Big, topic 25) is load-bearing.

### 7.5 Recall: encapsulation and MTU

16. **`est-mss-from-mtu`** (estimate, `encapsulation-mtu`). "A link's MTU is 1500 bytes. A TCP connection over IPv4, with no IP or TCP options, may carry at most how many bytes of data in one packet (its MSS)? Exactly." given `{mtu: 1500}`, working `mtu - 20 - 20`, answer 1460. Mistakes: 1480 (`mtu - 20`, only the IP header), 1446 (`mtu - 54`, subtracted the Ethernet header too, which isn't inside the MTU), 1500.
17. **`est-gre-mtu`** (estimate, `encapsulation-mtu`). "Two VMs in a Google Cloud network with the default MTU of 1460 build a GRE tunnel between them. GRE adds a 20-byte outer IPv4 header and a 4-byte GRE header. What MTU should the tunnel interface have so nothing on it is ever fragmented? Exactly." given `{path: 1460, outer_ip: 20, gre: 4}`, working `path - outer_ip - gre`, answer 1436. Mistakes: 1440 (`path - outer_ip`), 1484 (`path + outer_ip + gre`), 1476 (`"1476"`, the kernel's default for a tunnel over 1500). (Not 1400, which is the build's path.)
18. **`est-vxlan-mtu`** (estimate, `encapsulation-mtu`). "VXLAN carries a whole Ethernet frame (14-byte header) inside UDP (8) with an 8-byte VXLAN header, in a new 20-byte IPv4 packet. Over a 1500-byte network, what is the largest inner packet (the overlay's MTU)? Exactly." given `{mtu: 1500, eth: 14, udp: 8, vxlan: 8, ip: 20}`, working `mtu - eth - udp - vxlan - ip`, answer 1450. Mistakes: 1464 (`mtu - udp - vxlan - ip`, forgot the inner Ethernet header), 1472 (`mtu - udp - ip`), 1550 (added instead).
19. **`est-df-ping-size`** (estimate, `encapsulation-mtu`, `pmtud-blackholes`). "`tracepath` reports `pmtu 1476`. What is the largest N for which `ping -M do -s N` still gets replies? The IPv4 header is 20 bytes and the ICMP header 8. Exactly." given `{pmtu: 1476}`, working `pmtu - 20 - 8`, answer 1448. Mistakes: 1456 (`pmtu - 20`), 1468 (`pmtu - 8`), 1476.
20. **`est-jumbo-mss`** (estimate, `encapsulation-mtu`). "Two EC2 instances in the same VPC use jumbo frames, MTU 9001. What MSS does an IPv4 TCP connection between them get, with no options? Exactly." given `{mtu: 9001}`, working `mtu - 40`, answer 8961. Mistakes: 8981 (`mtu - 20`), 1460 (the internet's).
21. **`mcq-cloud-mtus`** (mcq, `encapsulation-mtu`). "An EC2 instance in a VPC uses MTU 9001 and sends large files to a server on the internet through an internet gateway. What happens to its 9001-byte packets?" Right: "They are limited to 1500 at the gateway, so the instance relies on PMTUD or MSS". Wrong: "They cross the internet at 9001, because AWS's backbone carries jumbo frames"; "The gateway fragments them into 1500-byte pieces, even when DF is set"; "They are rejected when the connection opens, so the instance falls back to 1500". Explanation: F12; Google's default is 1460 and it clamps MSS for traffic leaving the VPC (F13); Azure stays at 1500 except inside a VNet (F14).

### 7.6 Recall: path MTU discovery and black holes

22. **`mcq-blackhole-symptom`** (mcq, `pmtud-blackholes`). "After a VPN goes live, users can log in to the intranet and small pages load, but downloading reports hangs at 0%, and `ping` works. What's the most likely cause?" Right: "ICMP 'fragmentation needed' is dropped, so full-size packets vanish". Wrong: "The VPN's encryption is too slow, so large transfers time out before finishing"; "The server's TCP window is too small, so it can't send more than a few kilobytes"; "DNS over the VPN is failing, so the browser can't find the download server". Explanation: F6; ping sends 84 bytes; why the other three look different (slow but progressing; a window gives slow, not stuck; DNS fails before anything loads).
23. **`pmtud-tracepath`** (predict_shell, `pmtud-blackholes`, captured F25). `tracepath.txt` as captured. Command: `grep -o 'pmtu [0-9]*' tracepath.txt | sort -u; awk '/Resume/ {print "hops:", $5}' tracepath.txt`. Output pinned by the writer (`pmtu 1476`, `pmtu 1500`, `hops: 3`). Explanation: tracepath starts at the local MTU and learns the smaller one at the hop before the tunnel.
24. **`mcq-capture-sees-it`** (mcq, `pmtud-blackholes`, captured F20). "During a stalled download, `tcpdump -nn -i eth0 icmp` on the server shows `ICMP ... unreachable - need to frag (mtu 1476)` arriving. Yet the download stays stuck. Why?" Right: "tcpdump sees packets before the firewall, which then drops this one". Wrong: "The message is for the client, so the server's kernel ignores it"; "The server already lowered its MTU, but only new connections use it"; "tcpdump shows a copy, and the original was lost on the way in". Explanation: capture taps the wire side of netfilter; `ip route get CLIENT` with no `mtu` proves the kernel never took it in.
25. **`mcq-mss-clamp`** (mcq, `pmtud-blackholes`). "Engineers 'fix' a black hole by clamping the TCP MSS on the tunnel's routers. Downloads work again. What is still broken?" Right: "Anything that isn't TCP, which still sends full-size packets that vanish". Wrong: "Nothing: clamping removes the need for ICMP for every protocol"; "New TCP connections, because clamping only changes connections already open"; "Small packets, because the clamp now pads them to the full MSS". Explanation: MSS is a TCP option; UDP-based protocols (DNS answers with DNSSEC, QUIC, VPN payloads) still need PMTUD; clamping is fine as an extra, not as the fix.

### 7.7 `fill-tunnel-up` (fill-in, systemd network lab, 20 minutes)

**Topology:** the worked example's, with **r1's tunnel removed**. r2's end (remote 203.0.113.1, 10.255.0.2/30, MTU as the kernel sets it) is scenery. **Starter:** r1's network file (the base's per-machine file; my prototype's `/etc/netlab/r1/up`) with four gaps, each a `___` on its own line part:

```
ip link add gre1 type ___ local 203.0.113.1 remote ___ ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu ___
ip link set gre1 up
ip route add 10.0.0.0/16 dev ___
```

The prompt: the internet path between r1 and r2 carries 1500 bytes; fill the gaps so that office reaches web through the tunnel and no packet on the tunnel is fragmented; apply with the base's restart command (my prototype: `sudo systemctl restart netlab`). Checks: (a) r1 has a GRE tunnel whose remote is 203.0.113.2 (`ip -d link show gre1`); (b) gre1's MTU is exactly 1476; (c) office downloads the 2 MB file whole within 15 s; (d) the fix lasts: a fresh copy of the network built from the files reaches web (section 10, N-D). Description of (b) says "the tunnel's MTU leaves room for its own headers on a 1500-byte path, and wastes none", never the number. **Wrong fixes:** `mtu-1500.sh`, `remote-is-own-address.sh` (tunnel never forms), `route-via-wan.sh` (`10.0.0.0/16 via 203.0.113.2`: the internet doesn't route private addresses, check c fails).

### 7.8 `write-why-not` (write, systemd network lab, 35 minutes)

**Task:** from a blank file, `~/bin/why-not HOST PORT`, run as `on office ~/bin/why-not HOST PORT`, prints exactly one word: `no-arp` (the next hop for HOST, which is HOST itself when it's on the office's network and the gateway otherwise, never answered ARP), `refused` (a reset came back), `dropped` (nothing came back within 2 seconds), or `open`. The prompt gives the order to test in (link, then port), names the tools (`ip route get` and its `via`; `ping -c1 -W3` to make the kernel ARP; `ip neigh show ADDRESS`; `nc -z -w2`, timed with `date +%s%N`, because without `-v` nc says nothing either way: F26), and how to make the file and `chmod +x` it.

**Topology:** `office` 10.0.7.10/24 on a lan with `srv` 10.0.7.20 and `r1` 10.0.7.1; `r1` routes to `far` 10.0.9.30/24. `srv` and `far` each run listeners on a set of ports and an nftables input chain that drops some ports and drops ICMP echo (realistic, and it defeats a ping-based script); which ports are open, closed or dropped is chosen at random at each boot by the scenery and written to a root-only file the checks read. Addresses 10.0.7.200–249 belong to nobody.

**Checks:** (a) the script exists, is executable, starts with a shebang, and `shellcheck --norc` is quiet (Module 1's habit); (b) a fixed case for each outcome on-link (`srv` open, closed, dropped; a random unowned on-link address: `no-arp`); (c) the same three port outcomes off-link through `far` (the next hop is r1, which answers ARP); (d) four further random cases mixed. Each case compares the one word. `timeout: 60` on (b)–(d) (up to 3 s of ARP per unowned address). **Wrong fixes:** `ping-decides.sh` (ping fails on `srv`, so it prints `no-arp` for an open port: fails b), `arp-for-the-host.sh` (looks up HOST itself in `ip neigh` even when it's off-link: fails c), `timeout-is-refused.sh` (no timing: fails the dropped cases), `always-open.sh` (prints `open` when nc returns 0 and `refused` otherwise).

## 8. Proofs

### Build: `build-branch-tunnel` (systemd network lab, 50 minutes)

**Story:** the shop opens a branch. **Machines:** `branch` 10.0.5.10/24 —lan— `r3` (eth0 10.0.5.1/24, wan 198.51.100.6/30) —link, **MTU 1400 on both ends** ("the branch's line")— `isp` (198.51.100.5/30; 203.0.113.1/24 towards the cloud) —lan— `r2` (wan 203.0.113.2/24, lan 10.0.2.1/24) —lan— `web` 10.0.2.20/24 (index page and a 2 MB file; `local 10.0.5.128/25`-style AnyIP routes are *not* needed here: the probe goes the other way). r2's tunnel end is scenery: `gre-br` remote 198.51.100.6, 10.255.1.1/30, MTU 1376, route `10.0.5.0/24 dev gre-br`. `branch` answers for 10.0.5.128/25 too (`route branch local 10.0.5.128/25 dev lo`), for the probe. r3 starts with addresses and a default route via the isp and nothing else.

**The brief** (prompt): connect the branch to the cloud network through a GRE tunnel from r3 to r2's public address, using 10.255.1.2/30 at r3's end, so that branch machines reach 10.0.2.0/24 and everything else still goes to the internet. Find out how big a packet the internet path between r3 and r2 carries, and give the tunnel the largest MTU that never needs fragmenting. r3 is also the branch's firewall: from the internet it accepts only the tunnel itself and what belongs to connections the branch opened, and forwards nothing new inward. Save a capture of one packet on r3's internet side that shows both the outer and the inner addresses, as `~/build/tunnel.txt`. Everything must survive a restart of the lab.

**Checks** (descriptions state end states):

1. `tunnel-up`: r3 has a GRE tunnel to 203.0.113.2 with 10.255.1.2/30, and 10.255.1.1 answers through it.
2. `branch-reaches-web`: branch fetches web's index and the 2 MB file whole within 15 s.
3. `tunnel-mtu`: the tunnel's MTU leaves room for its headers on this path and wastes none (gre MTU = 1376; and from branch, a DF ping with 1348 bytes of data reaches web while 1349 is answered with "fragmentation needed").
4. `pmtud-works`: web is told the path's MTU when it sends too big a packet towards the branch (`on web ping -M do -s 1472` to a random address in 10.0.5.128/25 shows `mtu = 1376` or `mtu=1376`).
5. `firewall-strict`: from `isp`, listeners the check starts on r3 (22, 80, 8080) and on branch (22, 8080) get no answer for 2 s; and the tunnel still works (so a forgotten GRE rule shows here and in 1).
6. `capture-saved`: `~/build/tunnel.txt` shows a packet with `198.51.100.6` and `203.0.113.2` as outer addresses, `GRE`, and a 10.0.5.x ↔ 10.0.2.x inner pair.
7. `fixes-last`: the live machines equal a fresh build from their files, and in the fresh build branch reaches web through the tunnel (N-D).

**Wrong fixes:** `mtu-default.sh` (1476: check 3), `mtu-safe-1280.sh` (check 3), `mtu-path-not-minus.sh` (1400: check 3), `firewall-open.sh` (input and forward `policy accept`: check 5), `icmp-dropped.sh` (an `ip protocol icmp drop` before the `ct` rule in r3's input and forward chains: check 4), `capture-on-tunnel.sh` (captured on the tunnel interface, so no outer header: check 6), `not-saved.sh` (all done live: check 7), `forgot-gre-rule.sh` (input `policy drop` without accepting protocol 47 from 203.0.113.2: checks 1 and 2). `test_skills`: none (a topic build; ADR-0012's names are for checkpoints), but the writer may tag the checks for the future.

**Why it's a fair build:** every element was practised (the tunnel and its MTU in the fill-in, discovering a path MTU with `tracepath` and DF pings in the worked example, the firewall in Module 1, the related ICMP in 7.4, the capture on the right interface in the worked example).

### Debug: `debug-big-downloads-hang` (systemd network lab, 45 minutes): prototyped and passing

**Topology** (as prototyped in `prototypes/layers-cidr-ipv6/d23/`): `office` 10.0.1.10/24 (also answers for 10.0.1.128/25) —lan— `r1` (eth0 10.0.1.1/24, wan 203.0.113.1/24) —link— `r2` (wan 203.0.113.2/24); GRE r1 ⇄ r2, 10.255.0.1/30 ⇄ 10.255.0.2/30; r1 routes `10.0.0.0/16 dev gre1`; r2 routes `default dev gre1` (all the cloud's internet traffic leaves through the office: "forced tunnelling", which Azure customers do on purpose). r2's LAN `lan` 10.0.2.1/24 holds `web` 10.0.2.20 (HTTP: `/` and a 2 MB `/pricelist.csv`) and `files` 10.0.2.30 (HTTP); r2's `prn` 10.0.3.1/24 links to `printer` 10.0.3.5. web has a host firewall (nftables, `policy drop`, port 80 open).

**Faults** (each in a file a boot reads, so each survives a restart until fixed):

1. web's `nftables.conf` has `ip protocol icmp drop` *before* `ct state established,related accept` (the server team's "no ping" hardening). Symptom: pages load, the price list download stalls; ping to web fails.
2. r2's network file pins `10.0.2.30 lladdr 02:4c:41:42:00:30 dev lan nud permanent` (an old card's MAC). Symptom: files unreachable from everywhere off its LAN; traceroute stops after r2.
3. r2's network file has `ip link set prn down` after giving prn its address. Symptom: the printer is unreachable, and ping says `Time to live exceeded` (the loop of F24).

**Prompt** (rules of the debug: purpose, symptoms, number of faults, rules of the fix, never what or where): "The shop's cloud network hangs off the office through a GRE tunnel from r1 to r2. In the cloud are web (the shop's site and its price list), files (the file server) and the cloud office's printer. Since the weekend, staff in the office report three things: the site's pages load but downloading the price list never finishes; the file server can't be reached at all; and printing to the printer fails. There are three faults. Find each one from the evidence and fix it at its cause. The rules: don't change any interface's MTU (the tunnel's is what the provider allows; the networks are standard Ethernet); leave the office laptop's settings as they are (there are forty like it); web keeps refusing everything except its website from outside; and every fix must survive a restart of the lab. `on MACHINE COMMAND` runs a command on a machine; each machine's settings are in its files (the base's location); `netlab show` lists the machines." Check descriptions are listed only after the first try (#235).

**Checks** (as in `d23/checks.sh`):

| id | End state | How |
| --- | --- | --- |
| `download` | The price list arrives whole in 15 s | `on office curl` to sha256, compared with the file's sum saved at build |
| `pmtu` | No interface or route MTU changed, web does PMTUD, and web is told the path's MTU | the nine interface MTUs; no route anywhere has `mtu`; web's `ip_no_pmtu_disc` = 0; `on web ping -c1 -W2 -M do -s 1472` to a random 10.0.1.128–254 address shows `mtu ?= ?1476` |
| `strict` | web answers on port 80 and nothing else from outside | listeners the check starts on web 22, 8080, 3306; each `nc -z -w2` from office must fail *and* take ≥ 1.5 s (dropped, not refused) |
| `files` | files answers from the office | `on office curl` its index |
| `printer` | the printer answers from the office | `on office ping` |
| `lasts` | every machine is as its files say, and a fresh build from the files works | the base's fresh-build comparison (N-D): build a `chk-` copy, compare each machine's normalised state, then in the copy office reaches web's port 80 (a throwaway listener), files and the printer by ping, and the copy's web learns the 1476 |

**Wrong fixes** (all proved failing in the prototype, section 11): `firewall-off.sh` (web `policy accept`: strict fails), `mss-clamp.sh` (an MSS clamp on r2's forward chain: download passes, `pmtu` fails), `web-mtu-lowered.sh` (`pmtu` fails on the MTU list), `route-mtu.sh` (`mtu 1476` on web's default route: `pmtu` fails), `live-only.sh` (all three fixed with live commands only: `lasts` fails), `pinned-new-mac.sh` (the pin rewritten with files' current MAC and applied live: passes everything live, fails `lasts`, because the fresh build gives files a new MAC as a replaced card would). Add for the writer: `two-of-three.sh` (the ICMP rule and the pin fixed, the link not: `printer` and `lasts` fail; proves each fault has its own check).

**Prototype results** (2026-11-11, Docker Desktop): pristine fails 5 of 6 checks; the solution passes 6 of 6 and again after `docker restart`; each wrong fix fails at least one. Boot 2–4 s; a contract run of 8 scenarios took 178 s. The checks take 8–10 s after the solution and 34 s on a broken lab (timeouts).

### Explain (20 minutes)

**Prompt:** "Staff say the shop's site loads but big downloads hang, and a colleague says 'the firewall must be broken, turn it off'. Explain, in your own words: how one request travels from a laptop to a server across a router and a tunnel, layer by layer, and what each router changes and leaves alone; how the laptop finds the router's hardware address; what ICMP is for, and which of its messages must never be blocked; what MTU and encapsulation overhead are, and how path MTU discovery works; why dropping ICMP makes small pages work but big downloads hang, how you'd prove that's what's happening, and how you'd fix it without turning the firewall off; and one way the three clouds differ in any of this."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `layers-and-encapsulation` | yes | Each layer wraps the one above in a header (application data in TCP in IP in an Ethernet frame); the models are a debugging order (link, neighbour, route, port, protocol) |
| `hop-by-hop` | yes | Each hop builds a new frame (new source and destination MACs) and lowers the TTL (and so rewrites the checksum); the IP addresses and ports stay the same end to end (without NAT); a tunnel adds an outer IP header around the whole packet |
| `arp` | yes | The laptop broadcasts an ARP request for the gateway's IP and gets its MAC in a unicast reply; it never asks for the far server's MAC; entries are cached (states) |
| `icmp` | yes | ICMP carries errors and diagnostics (echo, unreachable with codes, time exceeded); errors quote the packet that caused them, so a stateful firewall can treat them as related; "fragmentation needed" (IPv6's Packet Too Big) must get through |
| `mtu-pmtud` | yes | MTU is the largest packet a link carries; headers and tunnels take room (GRE 24, so 1476 on 1500); the sender sets DF, a router that can't forward sends "fragmentation needed" with its MTU, the sender remembers it and resends smaller |
| `black-hole` | yes | Small packets fit, so handshakes and small pages work; the first full-size packet is dropped and its ICMP blocked, so bulk transfers stall; proof: a DF ping from the sender, `tracepath`, a capture on the sender showing the ICMP arriving, `ip route get` with no cached MTU; fix: let the ICMP through (related, or the specific type), not turn the firewall off; MSS clamping only helps TCP |
| `clouds-differ` | no | Any correct difference: AWS 9001 inside a VPC and 1500 at its edges; Google 1460 by default and MSS clamping on the way out; Azure 1500 except inside a VNet; Azure blocks GRE in a VNet while Google allows it; no broadcast, so no gratuitous-ARP failover |

**Model answer** (about 330 words, for the writer to put in `topic.yaml`): to be written from the rubric, in the voice of Module 2's model answers.

## 9. Review pool

At least two per skill; the estimate items carry the calculation skill. Items marked † are review-only (not in practice), with numbers no practice item or proof uses.

| Skill | Items |
| --- | --- |
| `layer-model` | `mcq-which-layer`, `mcq-tool-for-layer`, `mcq-cloud-floating-ip` |
| `read-headers` | `hdr-two-sides`, `hdr-hex-ttl`, † `hdr-udp-length` (predict_shell over a DNS query's `tcpdump -v` line, which the writer captures in the worked example's lab with `on office dig @10.0.2.1 ...`: `proto UDP (17), length N`; the command prints the payload size after 20 + 8 bytes) |
| `arp-neighbours` | `mcq-gateway-mac`, `arp-neigh-states`, `mcq-stale-permanent` |
| `icmp-messages` | `icmp-ping-verdicts`, `mcq-icmp-related`, † `mcq-port-unreachable` (UDP to a closed port on a host that answers with ICMP port unreachable against one that drops: which does `nc -zu` report how) |
| `encapsulation-mtu` | `est-gre-mtu`, `est-vxlan-mtu`, `est-df-ping-size`, † `est-ipip-mtu` (an IPIP tunnel over Google's default 1460: 1440; mistakes 1436, 1460), † `est-full-frames` (1 MB = 1,000,000 bytes sent as TCP with MSS 1460: how many full-size packets, rounded up: 685; mistakes 667 at 1500, 684 rounded down) |
| `pmtud-blackholes` | `mcq-blackhole-symptom`, `mcq-capture-sees-it`, `mcq-mss-clamp`, `pmtud-tracepath` |

Retention design: the pool is mostly judgement on real output (captures, ping lines, traceroute, tracepath) and quick sums with fresh numbers; nothing asks for a number or a name the learner would only ever look up (no "what is ICMP type 13").

## 10. Platform work first

What these labs need, beyond what the network-lab base already has. N-numbers are this brief's; where the base already provides it, the base's form wins.

| # | Need | Smallest version | Proved? |
| --- | --- | --- | --- |
| N-A | A machine's own network settings, editable and applied at boot | The base's topology words build the cables; then each machine runs its own file, `/etc/netns/M/<name>` (my prototype: `/etc/netlab/M/up`, a list of `ip` commands run inside the machine), after the topology, before its services. The learner edits it with nano and applies with the base's restart. This is where r2's pin and link-down faults live, where the fill-in and build put the tunnel, and where topic 24's debug keeps addresses and routes. A real server's equivalent is netplan or `/etc/network/interfaces`; the lesson says so in one line. The base's `tunnel` word stays for scenery tunnels. | Yes (`d23/netlab-up`) |
| N-B | Each machine's firewall from its own file | The base's `run M nftables` with `/etc/netns/M/nftables.conf` | Base has it |
| N-C | A restart of the lab's network that the learner can run | My prototype: `sudo systemctl restart netlab`, with each in-machine service `PartOf=` the network unit so it restarts too | Yes |
| N-D | **"The fix lasts" as a check** | A base command, say `netlab verify`: build a throwaway copy of every machine with a prefix (`chk-r1`...) from the files, with no services; compare each machine's normalised state (links up or down with MTUs; configured addresses, not link-local or advertised ones; routes, without the kernel's local, broadcast and anycast entries, advertised routes or the PMTU cache; permanent neighbours; `nft -s list ruleset`; `ip_forward`, IPv6 forwarding, `ip_no_pmtu_disc`); then let the lab's check run probes inside the copy; then remove it. My `netlab-state` is the comparison (24 lines). It catches live-only fixes and pins of something that changes at boot, which a reading of the files can't. | Yes (`d23/netlab-state`, `d25/netlab-state`, both labs) |
| N-E | MACs that change at every boot | The default for a new veth pair; the base must not fix MACs (or let a lab opt out of fixed ones). The pinned-MAC fault and its wrong fix depend on it | Yes |
| N-F | GRE in the kernel | `ip link add ... type gre` works in a privileged lab container on Docker Desktop (kernel 6.18 WSL2). On GitHub's runners it needs the `ip_gre` module, which the kernel loads on demand from the host for a privileged container: **not tried**. Add it to the base's CI spike. Fallback if it fails: the narrow link becomes a plain veth with MTU 1400 ("the provider's link") and the tunnel moves to topic 35 (IPsec) only; the debug's ICMP fault works unchanged (it needs only a smaller link) | Docker Desktop only |
| N-G | Packages | Already in the base's second layer: `tshark`, `iputils-tracepath`, `iputils-arping`, `mtr-tiny`, `ndisc6`. Nothing else for this topic | — |
| N-H | Predict-shell portability | Commands here use `grep -o`, `awk` fields, `sort`, `sed`, bash `printf` with `0x`: all behave the same in Git Bash and Linux. No `strtonum` (gawk only; Ubuntu's awk is mawk) | Yes (section 11) |

No platform code beyond the base is needed for the recall items: no new item type.

## 11. Cost and time

**Money:** nothing. Every lab is local. No cloud run is needed: the clouds' MTU behaviour is taught from their documentation, and nothing here would be better for being run there.

**Learner time:** lesson 15; required resources 69; 21 recall items × 1.5 = 32; worked example 35; fill-in 20; write 35; build 50; debug 45; explain 20. **Total 321 minutes.** That's over Module 2's 240–300. Two trims, both recommended: make Ben Eater's "Hop-by-hop routing" the only required video (the worked example's two-sided capture teaches the same thing hands-on; the ARP video or chapter stays as "one of"), saving 9 to 14 minutes; and drop `mcq-tool-for-layer` from practice to review-only. **`estimated_minutes: 300`** after the trims. See open question 1 for splitting the topic instead.

**CI time** (Labs job): five systemd network labs. The debug's contract (8 scenarios) took 178 s on Docker Desktop; the build has 9 scenarios (about 200 s), the write 5 (about 150 s, its random cases include up to 3 s of ARP each), the fill-in and worked example 4–5 each (about 100 s each). **About 12 minutes sequential, 3–4 minutes of a shard at four labs at a time.** Image layers: the base's two shared layers, then each lab's small `COPY` of files (seconds).

## 12. Open questions, each with a recommendation

1. **Split the topic in two** (layers, frames, ARP and ICMP; then encapsulation, MTU and PMTUD)? Module 2 split topics over 300 minutes. Recommendation: **don't**, if the trims in section 11 bring it to 300: the debug is a whole task across ARP, ICMP and MTU, and that whole-task proof (4C/ID) is worth more than shorter halves. Split only if the writer's real count stays above 310.
2. **GRE on CI** (N-F). Recommendation: put one GRE lab in the base's CI spike before writing the others; if the runner refuses, use the plain-veth fallback and say "a link with a smaller MTU" instead of "a tunnel" in the debug, keeping GRE only where it is shown (worked example) and skipping it on CI with a documented reason. Free either way.
3. **Ben Eater as resources[0]?** A video main resource gives the lesson words and pictures (dual coding), and his series is the best-known beginner walk through frames, ARP and hop-by-hop forwarding. I could confirm only titles, lengths and that they embed. Recommendation: keep Beej ch. 4 as resources[0] (read and confirmed) until a writer has watched "Hop-by-hop routing"; then swap if it covers the two-sided view as the title suggests.
4. **`tshark` in the learner's hands.** It's in the base image and dissects every field in words, which helps a beginner more than a hex dump does. Recommendation: use it once, in the worked example's hex step, and not in any check (its output format changes between versions more than tcpdump's).
5. **The "laptops stay as they are" rule** needs a check: the base's `netlab seal` of office's files, plus `netlab verify`. Recommendation: seal office's files in the debug, so changing the laptop is caught by a check that says "the office laptop's settings are as they were".
6. **For the routing designer** (their open question 2): the bash `$(( ))` method for addresses is taught in `csa.net.cidr` (that brief, section 4); their awk recipe is the same arithmetic. Recommendation: their write lab points to topic 24's recap and accepts either.

## Appendix: what was tried in Docker (2026-11-11)

All in `prototypes/layers-cidr-ipv6/`; every container, image and network made for it was removed afterwards (prefix `l1proto-`; no prune was run).

- **Base image:** `FROM ubuntu:24.04`, packages `systemd systemd-sysv dbus iproute2 iputils-ping iputils-tracepath tcpdump nftables conntrack traceroute dnsmasq radvd ndisc6 ipcalc sipcalc python3 curl netcat-openbsd procps sudo nano less bind9-dnsutils kmod`: 374 MB, built in 49 s. Run as `labcheck` runs a systemd lab (`--privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock`, `/sbin/init`); boot to `running` in 2–4 s.
- **Tunnel types** in a namespace inside the container: GRE, IPIP, SIT, VXLAN, gretap, ip6gre, WireGuard and Geneve all created (F9); `fou` didn't (no module). IPv6 was enabled in the container and in new namespaces (`disable_ipv6` 0).
- **Debug lab `d23/`:** topology as section 8; `netlab-up` (54 lines: namespaces, cables, then each machine's sysctl file, `up` script and nftables file), `netlab-state`, `checks.sh`, `solution.sh`, six wrong fixes, `contract.sh` (pristine, solution with a `docker restart` trial, each wrong fix, each in a fresh container). Results as in section 8.
- **Captures:** the two-sided echo request, the hex dump, the GRE packet, `tracepath`, the TTL loop, the dropped ICMP seen by tcpdump, the stale-MAC frames (section 5).
- **Two traps met, for the writer:** an interface named `a` or `down` breaks `ip` commands (`ip link add a ...` reads `a` as `address`; `down` is a keyword): name interfaces `eth0`, `wan`, `lan`, `prn`; and `pkill -f http.server` inside a `docker exec bash -c` kills its own shell (Module 1's bracket rule).

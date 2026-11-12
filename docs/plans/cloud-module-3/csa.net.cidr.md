# Topic 24: `csa.net.cidr`, IPv4 and CIDR

Designer's brief, 2026-11-11 (key `layers-cidr-ipv6`, with `csa.net.layers` and `csa.net.ipv6`). Prototypes: `prototypes/layers-cidr-ipv6/` (folder `w24/` is this topic's write lab: the check's generator, the reference script and six wrong scripts, run against 500 seeds). The network-lab base is another designer's; section 10 says what these labs need from it.

## 1. What the learner will be able to do

- Read and write an IPv4 address as bits, a prefix length as a mask, and say what an address/prefix means: which block, its first and last address, how many addresses, how many a cloud lets you use.
- Do block arithmetic on sight: a /27 is 32 addresses; 10.20.30.77/27 lives in 10.20.30.64–95; a /20 holds sixteen /24s; four consecutive /24s starting at a multiple of four summarise to a /22.
- Split a block into subnets of different sizes (variable-length masks) without overlaps and with room to grow, and summarise blocks into the shortest covering prefix, knowing what extra space that pulls in.
- Decide on sight whether two blocks overlap (CIDR blocks either nest or don't touch), say why an overlap breaks peering, VPNs and routing, and check a whole plan for overlaps with a script of their own.
- Use the RFC 1918 ranges and the other special ranges correctly, and plan within each cloud's rules (AWS and Azure keep 5 addresses of every subnet, Google 4; subnet size limits; ranges each refuses).
- See the same arithmetic in a live network: a wrong prefix length makes a host ARP for machines it can't reach; a block that doesn't start on a multiple of its size is silently moved by the kernel; a summary route that's too short leaves a subnet unreachable.

**The six-month core.** Block sizes as powers of two without thinking (/24 256, /25 128 … /28 16; /16 65,536; /20 4,096). "Where does this address's block start?": divide by the block size, keep the whole part. "Do these overlap?": compare them on the shorter prefix. The three private ranges and the 5/5/4 reserved addresses. And the habit: plan with room to double, never on the defaults everyone else uses.

## 2. Prerequisites and terms

**`prerequisites: [csa.net.layers]`**. The live labs read ARP failures and routes; the routing designer also assumes this chain (`csa.net.routing` depends on this topic, and through it on `csa.net.layers`).

**Builds on, for the writer:**

| Topic | What this topic leans on |
| --- | --- |
| `csa.linux.net-tools` | `ip -br addr` and `ip route` reading (`10.0.1.0/24 dev eth0` means "on this link"); `/24` and the default gateway used in examples without being explained; `ip neigh` |
| `csa.linux.permissions` | octal: groups of bits read as a number; the recall item `perm-umask` already ran `$((0666 & ~0022))`, a mask taking bits away with AND and NOT. A netmask is the same idea, and the lesson says so |
| `csa.linux.boot` | the metadata address 169.254.169.254 (its labs' `lab-imds`); this topic says why that range never leaves the machine's own link |
| `csa.linux.scripting` | bash scripts, `while read`, `if`, arrays are new (one paragraph here), ShellCheck |
| `csa.linux.containers` | containers get addresses from a bridge on the host (Docker's default range comes up in "ranges to avoid") |
| `csa.net.layers` | ARP and the neighbour table's `FAILED`; a hop; ICMP |

**Terms this topic must define itself:** bit and binary (place values 128 … 1; an octet is 8 bits, 0–255); dotted decimal; prefix and prefix length; CIDR (classless inter-domain routing) and why "class A/B/C" is history (ipcalc still prints "Class A", fact F12); netmask and wildcard mask; network address (the block's first address), broadcast address (its last), host part; block (a prefix as a range of addresses) and its size; aligned (a block starts on a multiple of its size); subnet and subnetting; VLSM (variable-length subnet masks); summarisation (aggregation, supernetting) and a summary route; overlap and nesting; RFC 1918 private ranges; shared address space (100.64.0.0/10) and carrier-grade NAT, in one sentence; link-local (169.254.0.0/16); documentation ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, which the labs use for "the internet"); loopback (127.0.0.0/8); multicast (224.0.0.0/4) in one sentence; reserved addresses (each cloud's); VPC and VNet in one sentence each (Module 11 teaches them); address plan; bash arrays; `ipcalc` and `sipcalc`.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `binary-and-masks` | An octet in binary and back; a prefix length as a dotted mask (/20 = 255.255.240.0) and back; the wildcard (0.0.15.255); AND with the mask gives the network, OR with the wildcard the last address; an address as one 32-bit number, in bash `$(( ))` with `<<`, `>>`, `&` and `|` |
| `block-math` | Block size 2^(32 − prefix); the block an address is in (its network and last address) by the "interesting octet"; alignment; usable addresses classically (− 2) and in each cloud (AWS − 5, Azure − 5, Google − 4); the smallest prefix that holds N machines plus the cloud's reserved addresses |
| `split-and-summarise` | How many /x fit in a /y (2^(x − y)); carving a block into subnets of different sizes, largest first, each aligned, leaving room to double; summarising contiguous aligned blocks into one prefix; the shortest prefix that covers a set of blocks and how much unused space it takes in |
| `overlaps` | Two CIDR blocks overlap exactly when they agree on the first k bits, k the shorter prefix (they nest or are apart, never half); spotting an overlap on sight; why overlaps break VPC peering (all three clouds refuse it), VPNs and routing; finding every overlap in a plan with a script |
| `private-and-reserved` | RFC 1918 (10/8, 172.16/12, 192.168/16, with sizes) and the traps (172.32.0.0 isn't private); 100.64.0.0/10 and when the clouds accept it; 169.254.0.0/16, 127/8, 0/8, 224/4, the documentation ranges; each cloud's reserved addresses (which ones) and size limits (AWS VPC and subnets /16–/28; Azure subnets /29–/2; Google /29 to /4, and Google's advice to stay at /8 or longer); ranges to avoid (172.17.0.0/16, which AWS warns some services use; 172.31.0.0/16, AWS's default VPC; home routers' 192.168.0.0/24 and 192.168.1.0/24) |

Three calculation skills (`binary-and-masks`, `block-math`, `split-and-summarise`): 15 estimate items below, at least three per skill with different numbers and stories (ADR-0024 rule 6).

**"In code" means bash arithmetic,** decided here (the task's open point; the routing designer's question 2 depends on it). Reasons, in order of the owner's rule: it builds on what the learner already did (`$((0666 & ~0022))` in Module 1 is exactly a mask); it has exact 64-bit integers and the bit operators, so the code reads like the method (`>> (32 - k)` *is* "divide by the block size"); it behaves identically in Git Bash (5.3) and Ubuntu's bash (5.2), which `predict_shell` needs (fact F14); and it needs no Python, which the track asks for only from Module 6. awk is the wrong tool for the bits: Ubuntu's awk is mawk, which has no `and()` (fact F15), though awk's `int(n / 2^k)` is the same arithmetic and the recap shows it once for topic 26's writer. `ipcalc` and `sipcalc` are taught as the everyday checking tools, never as the skill.

## 4. Lesson plan

1. **Bits and octets** (main resource: Beej ch. 17 "IP Subnets and Subnet Masks", sections 17.1–17.5, 11 min of its 14). **The lesson supplies** a table of the eight place values (128 64 32 16 8 4 2 1), three conversions worked both ways (10110100 = 180; 240 = 11110000; 255.255.240.0 = 20 ones), and the link to Module 1: `rwx` was three bits read as a number; an octet is eight. bash reads binary directly: `echo $((2#11110000))` prints 240.

2. **Prefix, mask, block** (Practical Networking, "Subnetting Mastery" parts 1–3, 17 min; Beej 17.6–17.7). A prefix length says how many leading bits name the network; the rest number hosts in it, so a /N block holds 2^(32 − N) addresses. The mask is those N bits as ones; ANDing an address with it keeps the network part (exactly the umask, the other way round). The "interesting octet" method the videos teach: the octet where the mask isn't 255 or 0; block size there = 256 − that mask octet; the network starts at the largest multiple of the block size not above the address's octet. **The lesson supplies** the method worked on 10.20.30.77/27 (mask octet 224, block 32, 77 → 64, last 95, matching `ipcalc`, fact F12) and on a prefix that crosses octets, 10.20.37.5/20 (third octet, block 16, 37 → 32: 10.20.32.0–10.20.47.255).

3. **Alignment, shown live** (the worked example's step 5). A block must start on a multiple of its size: 10.1.4.0/23 is a block; "10.1.3.0/23" isn't, and Linux, given `ip addr add 10.1.3.1/23`, quietly uses 10.1.2.0/23, which takes in 10.1.2.x too (fact F10). The debug plants exactly this.

4. **Splitting and summarising** (Practical Networking's FLSM/VLSM articles are linked as optional; the lesson's own worked plan carries the method). How many /x in a /y; carving variable sizes, biggest first so each stays aligned; summarising: blocks that together fill an aligned block become one prefix (four /24s from 10.8.4.0 = 10.8.4.0/22); the shortest single prefix covering 10.8.6.0/24 and 10.8.9.0/24 is 10.8.0.0/20, which takes in fourteen /24s nobody asked for. Room to double: plan each subnet for twice its machines; plan each region's block with spare space beside it, because a block can't grow into a neighbour.

5. **Overlaps** (the lesson's own, no resource does it as a rule a beginner can use). **The lesson supplies the rule** with a picture: two blocks either nest or are apart, never half-overlap, because each is "all addresses whose first N bits are these". So compare them on the shorter prefix: same leading bits, overlap. In bash, `(( a >> (32 - k) == b >> (32 - k) ))`. Why it matters: VPC peering refuses overlapping ranges on all three clouds (facts F6–F8), an AWS Direct Connect gateway's VPCs mustn't overlap, a VPN can't route a range that exists on both sides, and Module 11 has a whole topic on fixing one in production (`csa.cnet.ipam`).

6. **Private and special ranges, and the clouds' rules** (AWS "Subnet CIDR blocks", 4 min; the Azure FAQ's address answers, 3 min; Google's reserved-addresses section, 3 min; RFC 1918 §3, 2 min). RFC 1918's three blocks with their sizes (16,777,216; 1,048,576; 65,536) and the trap that 172.16/12 ends at 172.31.255.255. 100.64.0.0/10: carriers' space for carrier-grade NAT, which Azure and Google accept in a VNet or VPC and AWS allows only beside other non-RFC-1918 ranges. 169.254.0.0/16 never leaves its link (the metadata service lives there). The documentation ranges (and why the labs use them). **Where the clouds differ**, a table the lesson owns:

   | | AWS | Azure | Google Cloud |
   | --- | --- | --- | --- |
   | Reserved in each subnet | 5: network, +1 router, +2 DNS, +3 future, last | 5: network, +1 gateway, +2 and +3 DNS, last | 4: network, +1 gateway, second-to-last, last |
   | Subnet sizes | /16 to /28 | /29 to /2 | /29 to /4 (stay at /8 or longer, Google advises) |
   | VPC or VNet | /16 to /28 per CIDR block; up to five IPv4 blocks may be added | address spaces of any size within the rules | no network-wide range: each subnet has its own |
   | Refuses | 0.0.0.0/8, 127/8, 169.254/16, 224/4; restricts mixing RFC 1918 blocks; warns about 172.17.0.0/16 | 224/4, 255.255.255.255, 127/8, 169.254/16, 168.63.129.16 | 0/8, 127/8, 169.254/16, 224/4, 255.255.255.255, Google's own ranges |

   Every cell is a fact in section 5 (F2–F9).

7. **In code** (the worked example's steps 1–2 and the fill-in). Four lines of bash the learner keeps: `ip2int`, `int2ip`, the mask `$(( (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF ))`, and the overlap test; `ipcalc -n ADDRESS/PREFIX` and `sipcalc` to check by eye. One line for topic 26's writer: in awk the same block test is `int(n / 2^(32 - p))`.

**Recap:** the powers of two to /16; the interesting-octet method; alignment; how many /x in /y; summarise only aligned, contiguous blocks; the overlap rule; RFC 1918 with sizes; 5/5/4; the four bash lines.

## 5. Verified facts

| # | Claim | Source, read 2026-11-11 |
| --- | --- | --- |
| F1 | RFC 1918: 10.0.0.0–10.255.255.255 (10/8), 172.16.0.0–172.31.255.255 (172.16/12), 192.168.0.0–192.168.255.255 (192.168/16); routes and packets for them must not cross enterprise boundaries | https://www.rfc-editor.org/rfc/rfc1918.html (February 1996, BCP 5) |
| F2 | AWS subnets: /28 to /16; the first four addresses and the last are reserved: network, VPC router (+1), DNS (+2, "the base of the VPC network range plus two", and +2 of every subnet reserved), future use (+3), broadcast (last; "We do not support broadcast in a VPC"); IPv6 subnets /44 to /64 in steps of 4, the first four and the last reserved | https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html |
| F3 | AWS VPC blocks /16 to /28; RFC 1918 recommended; can't use 0.0.0.0/8, 127.0.0.0/8, 169.254.0.0/16, 224.0.0.0/4; some services (Cloud9, SageMaker AI) use 172.17.0.0/16, so don't; restrictions on adding blocks from other RFC 1918 ranges and 198.19.0.0/16; a CIDR given with host bits is turned into its canonical form (100.68.0.18/18 → 100.68.0.0/18); Amazon gives a VPC a /56 of IPv6 | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html |
| F4 | Azure: RFC 1918 recommended, 100.64.0.0/10 treated as private; can't use 224.0.0.0/4, 255.255.255.255/32, 127.0.0.0/8, 169.254.0.0/16, 168.63.129.16/32; five reserved per subnet: network, .1 gateway, .2 and .3 for Azure DNS, last; smallest IPv4 subnet /29, largest /2; IPv6 subnets exactly /64; subnets can't overlap (FAQ dated 2026-07-08) | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq |
| F5 | Google: 4 reserved in a subnet's primary range: network, default gateway (second), second-to-last ("reserved by Google Cloud for potential future use"), broadcast; smallest /29, shortest mask /4 with advice to stay at /8; valid ranges include RFC 1918, 100.64.0.0/10, the documentation ranges, 198.18.0.0/15, 240.0.0.0/4; prohibited include 0.0.0.0/8, 127.0.0.0/8, 169.254.0.0/16, 224.0.0.0/4, 255.255.255.255/32 and Google's own ranges | https://docs.cloud.google.com/vpc/docs/subnets |
| F6 | AWS: peered VPCs must not have overlapping CIDR blocks (stated for adding blocks to a peered VPC), and nor may VPCs on one Direct Connect gateway | F3's page |
| F7 | Azure: "You can't enable virtual network peering if address spaces overlap" | F4's page |
| F8 | Google: VPC peering requires non-overlapping subnet ranges | **Not read at source today**: the writer confirms on Google's VPC Network Peering page before using it; until then the lesson names AWS and Azure only |
| F9 | AWS's default VPC is 172.31.0.0/16 | F3's page names 172.31.0.0/16 in its example table and restricts it; **"default VPC" wording not confirmed** there: the writer checks AWS's default-VPC page before stating it |
| F10 | `ip addr add 10.1.3.1/23` makes the kernel's connected route `10.1.2.0/23`, beside an existing `10.1.2.0/24` on another interface; the host on the /23 can't reach 10.1.2.x hosts | Captured (iproute2 6.1.0, kernel 6.18 WSL2) |
| F11 | A host given 10.1.1.20/16 where its LAN is /24 tries ARP for 10.1.2.30 (`INCOMPLETE`) and can't reach it; turning on `proxy_arp` on the router hides the mistake (the router answers, the ping works) | Captured |
| F12 | `ipcalc 0.51` on Ubuntu 24.04 prints for 10.20.30.77/27: network 10.20.30.64/27, HostMin .65, HostMax .94, broadcast .95, `Hosts/Net: 30`, and still labels it `Class A, Private Internet`; `sipcalc 1.1.6` prints the same range, the address as decimal (169090637) and hex | Captured |
| F13 | CIDR prefix notation: an address followed by a number 0–32 of significant bits; classful A/B/C deprecated; aggregation: a provider advertises one route for the larger block | https://www.rfc-editor.org/rfc/rfc4632.html (August 2006, BCP 122) |
| F14 | bash arithmetic gives identical results in Git Bash's bash 5.3.9 and Ubuntu 24.04's bash 5.2.21 for `ip2int`, the mask, network, last address and the overlap test (10.20.30.77 → 169090637; /27 → 10.20.30.64–95; the five overlap cases) | Captured on both |
| F15 | Ubuntu 24.04's `awk` is mawk 1.3.4 20240123, which has no `and()` ("function and never defined") but prints 32-bit values exactly with `%d` | Captured |
| F16 | 100.64.0.0/10 is "Shared Address Space" for providers' carrier-grade NAT, distinct from RFC 1918; organisations using it for other purposes "are likely to experience problems" connecting to CGN service | https://www.rfc-editor.org/rfc/rfc6598.html (April 2012, BCP 153) |
| F17 | Documentation ranges: 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, which "SHOULD NOT appear on the public Internet" | https://www.rfc-editor.org/rfc/rfc5737.html (January 2010) |
| F18 | Docker's bridge page shows default-bridge containers at 172.17.0.2 and 172.17.0.3 but doesn't name the range; it changes with `bip` and `fixed-cidr` in `daemon.json` | https://docs.docker.com/engine/network/drivers/bridge/ (so the lesson cites AWS's warning, F3, and says "Docker's default bridge usually takes 172.17.0.0/16" only as what `ip route` shows on a Docker host, which Module 1's `net-ip-route-default` item already showed) |
| F19 | The overlap rule as a test: a generator with seven fixed cases (outer then inner across an octet boundary; inner then outer, never the first sub-block; identical blocks, one written with host bits; adjacent blocks; a /32 inside and one just outside a block written with host bits; the same first three octets in different blocks; far apart) separates the reference script from six wrong ones on all 500 seeds tried | Prototype `w24/` |

## 6. Resources

Fetched on 2026-11-11.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | Beej's Guide to Network Concepts, ch. 17 "IP Subnets and Subnet Masks" (17.1–17.7: representation, converting both ways, subnet and mask refreshers, the mask from slash notation, finding an address's subnet) | https://beej.us/guide/bgnet0/html/split/ip-subnets-and-subnet-masks.html | reading | CC BY-NC-ND 3.0; linked, not copied | 14 (1,881 words) | `binary-and-masks`, `block-math` | headings confirmed |
| 1 | Practical Networking, "What is Subnetting?" (Subnetting Mastery, part 1 of 7) | https://www.youtube.com/watch?v=BWZ-MHIhqjM | video | YouTube standard licence; embeddable (`playableInEmbed` true) | 9 (8:37) | `block-math`, `binary-and-masks` | exists on Practical Networking's channel; the series page says part 1 is "the basics; the seven subnetting attributes" |
| 2 | "Drawing the Cheat Sheet" (part 2 of 7) | https://www.youtube.com/watch?v=ljS07YTEJ2I | video | as row 1 | 2 (1:58) | `block-math` | as row 1 |
| 3 | "How to solve ANY Subnetting Problems in 60 seconds or less" (part 3 of 7) | https://www.youtube.com/watch?v=5-wlfAdcmFQ | video | as row 1 | 6 (6:10) | `block-math` | as row 1 |
| 4 | Parts 4 and 5 (practice examples; time-saving tricks), optional | https://www.youtube.com/watch?v=SM0kdVfhxZ0, https://www.youtube.com/watch?v=Pj_ubhpi0WQ | video | as row 1 | 18 (9:54 + 8:32) | `block-math` | as row 1 |
| 5 | Beej, ch. 7 "The Internet Protocol version 4": sections 7.5 and 7.6, special addresses and subnets | https://beej.us/guide/bgnet0/html/split/the-internet-protocol-version-4.html | reading | CC BY-NC-ND 3.0 | 4 (of 1,388 words) | `private-and-reserved` | headings confirmed |
| 6 | AWS, "Subnet CIDR blocks" | https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html | reading | © Amazon Web Services; linked, not copied | 4 | `private-and-reserved`, `block-math` | opened |
| 7 | Azure, "Azure Virtual Network FAQ": the answers "What address ranges can I use", "Are there any restrictions on using IP addresses within these subnets?" and "How small and how large can virtual networks and subnets be?" | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq | reading | CC BY 4.0 (MicrosoftDocs, as Module 2 recorded); linked | 3 | `private-and-reserved` | opened (dated 2026-07-08) |
| 8 | Google Cloud, "Subnets": the sections on IPv4 ranges, valid ranges and reserved addresses | https://docs.cloud.google.com/vpc/docs/subnets | reading | CC BY 4.0 (as Module 2 recorded) | 3 | `private-and-reserved` | opened |
| 9 | RFC 1918, section 3, optional | https://www.rfc-editor.org/rfc/rfc1918.html | reading | IETF Trust; linked | 2 | `private-and-reserved` | opened |
| 10 | AWS, "VPC CIDR blocks": the considerations and the association restrictions table, optional | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html | reading | © AWS; linked | 5 | `private-and-reserved`, `overlaps` | opened |
| 11 | SubnettingPractice.com, for unlimited extra drills, optional | https://subnettingpractice.com/ | interactive | © 2026 subnettingpractice.com; linked | — | `block-math` | opens; no account asked for; whether every page is free not confirmed |

Required minutes: 14 + 9 + 2 + 6 + 4 + 4 + 3 + 3 = 45.

## 7. Practice ladder

### 7.1 `example-carve-a-network` (worked example, systemd network lab, 30 minutes)

**Topology** (base words): `r1` with three LANs: `lana` 10.20.1.1/24 (host `h1` 10.20.1.10), `lanb` 10.20.2.1/24 (host `h2` 10.20.2.10), `lanc` (no address yet). **Steps:**

1. *Binary by bash.* `echo $((2#11110000))`, `printf '%d\n' 0xF0`; the note works 255.255.240.0 → /20.
2. *Address to number and back.* The learner types the two functions into `~/bin/cidr-lib.sh` (given in the step), sources it, and runs `ip2int 10.20.30.77`, the mask for /27, `int2ip $(( n & mask ))`, the last address; then `ipcalc -n 10.20.30.77/27` to check.
3. *A plan by loop.* `for z in 0 1 2; do echo "zone-$z 10.20.$((z * 16)).0/20"; done > ~/example/plan.txt`, and within zone 0, `/24`s with another loop; the note explains alignment.
4. *A wrong prefix, live.* `on h1 ip addr replace 10.20.1.10/16 dev eth0` (and delete the /24), `on h1 ip route` (now `10.20.0.0/16 dev eth0`), `on h1 ping -c1 -W3 10.20.2.10` (fails), `on h1 ip neigh` (`10.20.2.10 ... FAILED`) saved to `~/example/neigh.txt`; put the /24 back; ping works; `ip neigh` now shows the gateway, not h2.
5. *A block that isn't aligned, live.* `on r1 ip addr add 10.20.3.1/23 dev lanc`, `on r1 ip route | grep lanc` (`10.20.2.0/23`), saved to `~/example/moved.txt`; then delete it.
6. *Check yourself.* `ipcalc -n 10.20.3.1/23`.

**Checks:** `plan.txt` lists zone-0 to zone-2 as 10.20.0.0/20, 10.20.16.0/20, 10.20.32.0/20; `neigh.txt` holds `10.20.2.10` with `FAILED` or `INCOMPLETE`; `moved.txt` holds `10.20.2.0/23`; h1 is back on 10.20.1.10/24 and reaches h2; lanc has no address left. **Wrong fixes:** `left-on-16.sh` (h1 still /16: check 4), `plan-off-by-one.sh` (zones at 10.20.15.0 and 10.20.31.0), `aligned-instead.sh` (used 10.20.4.1/23, so nothing moved: `moved.txt` check).

### 7.2 Recall: binary and masks

2. **`est-mask-octet`** (estimate, `binary-and-masks`). "A /20 prefix written as a dotted mask is 255.255.?.0. What is the third number? Exactly." given `{p: 20}`, working `256 - 2 ** (24 - p)`, answer 240. Mistakes: 248 (`256 - 2 ** (23 - p)`, the /21's), 20, 224 (`256 - 2 ** (25 - p)`).
3. **`est-binary-octet`** (estimate, `binary-and-masks`). "The eight bits 10110100 are one octet; 4 of them are ones. What number is it in decimal? Exactly." given `{ones: 4}`, working `128 + 32 + 16 + 4` (a sum of the place values, which the learner must know rather than read), answer 180. Mistakes: 45 (`"45"`, the bits read right to left), 4 (`ones`, counted the ones). The writer checks the validator accepts a prompt containing the bit string (it reads 10110100 as a number too, harmlessly).
4. **`est-wildcard-octet`** (estimate, `binary-and-masks`). "A /22's wildcard mask (the mask with every bit flipped) is 0.0.?.255. What is the third number? Exactly." given `{p: 22}`, working `2 ** (24 - p) - 1`, answer 3. Mistakes: 4 (`2 ** (24 - p)`, the block size), 252 (the mask's own third number).
5. **`cidr-ip2int`** (predict_shell, `binary-and-masks`). Command: `IFS=. read -r a b c d <<< 10.20.30.77; echo $(( (a << 24) | (b << 16) | (c << 8) | d ))`. Output `169090637` (F14). The prompt explains `<<` ("shift left: multiply by 2 that many times") and `|`. Explanation: each octet moved to its place, the same as `10 × 16,777,216 + 20 × 65,536 + 30 × 256 + 77`.
6. **`cidr-network-of`** (predict_shell, `binary-and-masks`, `block-math`). Command (one line per function, as in the worked example): defines `ip2int` and `int2ip`, then `n=$(ip2int 10.20.37.5); m=$(( (0xFFFFFFFF << (32 - 20)) & 0xFFFFFFFF )); int2ip $(( n & m )); int2ip $(( n | (~m & 0xFFFFFFFF) ))`. Output `10.20.32.0` and `10.20.47.255`. (Numbers differ from the lesson's /27 example on purpose.)

### 7.3 Recall: block arithmetic

7. **`est-block-size`** (estimate, `block-math`). "How many addresses does a /27 block hold, counting every one? Exactly." given `{p: 27}`, working `2 ** (32 - p)`, answer 32. Mistakes: 30 (`2 ** (32 - p) - 2`), 5 (`32 - p`), 27.
8. **`est-aws-usable`** (estimate, `block-math`, `private-and-reserved`). "An AWS subnet is a /26. How many addresses can you give to instances? Exactly." given `{p: 26}`, working `2 ** (32 - p) - 5`, answer 59. Mistakes: 62 (`- 2`), 60 (`- 4`, Google's rule), 64.
9. **`est-google-usable`** (estimate, `block-math`, `private-and-reserved`). "A Google Cloud subnet's primary range is a /28. How many addresses can VMs use? Exactly." given `{p: 28}`, working `2 ** (32 - p) - 4`, answer 12. Mistakes: 11 (`- 5`), 14 (`- 2`), 16.
10. **`est-network-octet`** (estimate, `block-math`). "A VM has the address 10.44.9.150/26; the last number of its address is 150. What is the last number of its block's network address? Exactly." given `{last: 150, p: 26}`, working `floor(last / 2 ** (32 - p)) * 2 ** (32 - p)`, answer 128. Mistakes: 150 (`last`), 192 (`ceil(last / 2 ** (32 - p)) * 2 ** (32 - p)`), 64 (`2 ** (32 - p)`, the block size). (Until the validator reads dotted quads, platform work P-1, the prompt states "150" on its own, as here.)
11. **`est-last-octet`** (estimate, `block-math`). "A subnet starts at 192.168.40.96 and is a /28; its start's last number is 96. What is the last number of its last address? Exactly." given `{start: 96, p: 28}`, working `start + 2 ** (32 - p) - 1`, answer 111. Mistakes: 112 (`start + 2 ** (32 - p)`, the next block's start), 110 (`start + 2 ** (32 - p) - 2`, the last usable), 124 (`start + p`).
12. **`est-smallest-prefix`** (estimate, `block-math`). "An Azure subnet must hold 500 VMs, and Azure keeps 5 addresses of every subnet. What is the longest prefix (the smallest block) that fits? Exactly." given `{vms: 500, reserved: 5}`, working `32 - 9` (2^9 = 512 is the smallest power of two ≥ 505; the validator has no logarithm, so the working names the power, and the explanation shows it), answer 23. Mistakes: 24 (`"24"`: 256 is too small), 22 (`"22"`: one size too big). A second item, **`est-smallest-prefix-google`**, review-only: 120 VMs in Google (124 needed → /25); mistakes 26, 24.
13. **`mcq-aligned`** (mcq, `block-math`). "Which of these is a block's correct start address and prefix?" Right: "10.1.4.0/22". Wrong: "10.1.6.0/22", "10.1.3.0/23", "10.1.2.128/24". Explanation: a /22 starts on a multiple of 4 in the third octet; 10.1.6.0/22 is really 10.1.4.0/22; "10.1.3.0/23" is 10.1.2.0/23 (F10); .128 isn't a /24's start.
14. **`cidr-ipcalc-read`** (predict_shell, `block-math`, captured F12). `ipcalc.txt` as captured for 10.20.30.77/27. Command: `awk '/^Network:/ {print "block", $2} /^Broadcast:/ {print "last", $2} /^Hosts\/Net:/ {print "usable", $2}' ipcalc.txt`. Output `block 10.20.30.64/27`, `last 10.20.30.95`, `usable 30`. Explanation: ipcalc counts the classic two reserved; an AWS or Azure subnet of this size gives 27, Google 28; and "Class A" is history (F13).

### 7.4 Recall: splitting and summarising

15. **`est-how-many-in`** (estimate, `split-and-summarise`). "How many /24 subnets fit in a /20? Exactly." given `{big: 20, small: 24}`, working `2 ** (small - big)`, answer 16. Mistakes: 4 (`small - big`), 256.
16. **`est-spec-drill`** (estimate, `split-and-summarise`; the spec's own subnetting drill). "A /14 is split evenly across 4 regions × 3 zones × 3 tiers, leaving room for the number of subnets to double. All subnets are the same size. What prefix length does each get? Exactly." given `{p: 14, regions: 4, zones: 3, tiers: 3}`, working `p + 7` (36 subnets, room to double 72, the next power of two 128 = 2^7), answer 21. Mistakes: 20 (`p + 6`, 64 subnets: no room to double), 22 (`p + 8`).
17. **`est-summary-prefix`** (estimate, `split-and-summarise`). "Four subnets, 172.20.12.0/24, 172.20.13.0/24, 172.20.14.0/24 and 172.20.15.0/24, are to be advertised as one route. What prefix length covers exactly these four? Exactly." given `{p: 24, count: 4}`, working `p - 2`, answer 22. Mistakes: 20 (`p - 4`), 23.
18. **`est-summary-waste`** (estimate, `split-and-summarise`). "The shortest single prefix covering both 10.8.6.0/24 and 10.8.9.0/24 is a /20. How many /24s does it contain besides those two? Exactly." given `{cover: 20, p: 24, used: 2}`, working `2 ** (p - cover) - used`, answer 14. Mistakes: 16, 2.
19. **`est-vpc-usable`** (estimate, `split-and-summarise`, `block-math`). "An AWS VPC of /16 is split entirely into /20 subnets. How many addresses can instances use across all of them? Exactly." given `{vpc: 16, sub: 20}`, working `2 ** (sub - vpc) * (2 ** (32 - sub) - 5)`, answer 65456. Mistakes: 65536, 65504 (`- 2` each), 65472 (`- 4` each).
20. **`mcq-summary-or-not`** (mcq, `split-and-summarise`). "Which set of blocks can be advertised as one route that covers them and nothing else?" Right: "10.4.8.0/23 and 10.4.10.0/23". Wrong: "10.4.10.0/23 and 10.4.12.0/23", "10.4.8.0/24 and 10.4.10.0/24", "10.4.9.0/24 and 10.4.10.0/24". Explanation: the first pair fills 10.4.8.0/22 exactly; the second straddles a /22 boundary; the third leaves a gap (10.4.9.0); the fourth isn't aligned.

### 7.5 Recall: overlaps

21. **`cidr-overlap-rule`** (predict_shell, `overlaps`, F14). Command: the `ip2int` function and `overlap()` (as in `prototypes/layers-cidr-ipv6` notes), then five pairs: `10.0.0.0/8 10.200.0.0/16`, `10.0.0.0/25 10.0.0.128/25`, `172.16.0.0/12 172.32.0.0/16`, `0.0.0.0/0 192.168.1.0/24`, `192.168.1.5/32 192.168.1.0/30`. Output `yes no no yes no` one per line (captured identically in Git Bash and Ubuntu). Explanation per pair.
22. **`mcq-which-overlap`** (mcq, `overlaps`). "Which pair overlaps?" Right: "10.0.0.0/22 and 10.0.3.128/25". Wrong: "10.0.0.0/25 and 10.0.0.128/25", "10.0.4.0/22 and 10.0.8.0/22", "10.1.0.0/16 and 10.10.0.0/16". Explanation: compare on the shorter prefix.
23. **`mcq-peer-overlap`** (mcq, `overlaps`). "Two teams each built a VPC on 10.0.0.0/16 (the default in many templates) and now want to peer them. What happens?" Right: "Peering is refused, so one must be renumbered or joined some other way". Wrong: "Peering works, and each VPC reaches the other's addresses by its own name"; "Peering works for new instances only, which get addresses from a shared pool"; "Peering works, and the cloud translates one side's addresses automatically". Explanation: F6, F7; the other ways (NAT, PrivateLink and its equivalents) are Module 11's.

### 7.6 Recall: private and reserved

24. **`mcq-not-private`** (mcq, `private-and-reserved`). "Which block is not in the RFC 1918 private ranges?" Right: "172.32.0.0/16". Wrong: "172.31.0.0/16", "10.255.0.0/16", "192.168.200.0/24". Explanation: 172.16/12 ends at 172.31.255.255.
25. **`mcq-azure-first-vm`** (mcq, `private-and-reserved`). "In an Azure subnet 10.0.1.0/24, what is the first address a VM can be given?" Right: "10.0.1.4". Wrong: "10.0.1.1", "10.0.1.2", "10.0.1.5". Explanation: .0 network, .1 gateway, .2 and .3 DNS (F4); AWS is the same, Google gives .2 (F2, F5).
26. **`mcq-avoid-range`** (mcq, `private-and-reserved`). "A new VPC will host build servers that run Docker. Which range should it avoid, and why?" Right: "172.17.0.0/16, which Docker hosts use for their containers' bridge". Wrong: "10.0.0.0/16, which AWS keeps for its own VPC routers"; "192.168.0.0/16, which the clouds refuse for VPCs"; "100.64.0.0/10, which only works for IPv6". Explanation: F3, F18; and why the wrong ones are wrong (10.0.0.0/16 is allowed, if overused; 192.168/16 is allowed; 100.64/10 is IPv4 shared space, F16).
27. **`mcq-link-local`** (mcq, `private-and-reserved`). "Why can't 169.254.169.254 be reached from another network, though every cloud VM can reach it?" Right: "It's link-local: routers never forward 169.254.0.0/16, so each VM's own link answers". Wrong: "It's private like 10.0.0.0/8, so only the VM's own VPC can route to it"; "It's a broadcast address, so only machines on the same switch hear it"; "It's the documentation range, so the internet drops it at every border". Explanation: csa.linux.boot's metadata service; the clouds refuse it as a VPC range (F3–F5).

### 7.7 `fill-cidr-info` (fill-in, plain lab, 25 minutes)

`~/bin/cidr-info ADDRESS/PREFIX [aws|azure|google]` prints five lines: `network A`, `last A`, `addresses N`, `usable N`, `first-usable A` (classic when no cloud is given: usable − 2, first +1; AWS and Azure − 5 and +4; Google − 4 and +2). **Starter:** `ip2int` and `int2ip` complete; gaps for the mask expression, the network (`&`), the last address (`|` with the wildcard), and the two numbers per cloud in a `case`. The prompt says which gaps stop bash running (none: they're values, so the script runs and prints wrong numbers; README rule). **Checks** (plain lab, quick): (a) twelve inputs made at check time, from fixed categories with random numbers: one per cloud and none, prefixes /16, /20, /23, /26, /28, /29, an address equal to its block's start and one equal to its last; compared with `python3`'s `ipaddress` (the check's own code); (b) the script still has its shebang and is executable. **Wrong fixes:** `mask-off-by-one.sh` (`<< (33 - p)`), `last-plus-one.sh` (`network + size`), `google-reserves-five.sh`, `no-masking.sh` (prints the address as the network).

### 7.8 `write-cidr-overlaps` (write, plain lab, 35 minutes): prototyped and passing

**Task:** from a blank file, `~/bin/cidr-overlaps PLAN`, where PLAN has one `NAME BLOCK` per line (blank lines and `#` comments allowed; a block may be written with host bits, as engineers do), prints every overlapping pair as `NAME1 NAME2`, one per line, the earlier-listed name first, pairs in the order of their first name then second, nothing else. The prompt gives the overlap rule (section 4, step 5), recalls the `ip2int` function from the worked example, introduces bash arrays in four lines (`names+=("$name")`, `${names[i]}`, `${#names[@]}`), and says how to create the file and `chmod +x` it.

**Checks:** (a) exists, executable, shebang, `shellcheck --norc` quiet; (b) three plans made at check time by `w24/gen.py` with random seeds, each holding all seven fixed cases (F19) with random numbers, 15 named blocks, output compared exactly with the generator's; (c) a plan with comments, blank lines and a `/0` and a `/32` (edges); (d) a 60-block plan answered within 10 s (bash's nested loop does it in well under a second; this only catches a script that calls a slow tool per pair). **Wrong fixes** (each fails on all 500 seeds tried; F19): `network-equal.sh` (overlap only when the networks are equal: misses nesting), `one-way.sh` (tests only whether the later block is inside the earlier: misses inner-before-outer; this one passed 7 of 40 seeds until the generator pinned each nested pair's order and stopped putting the small block first in the big one: **keep both fixes**), `adjacent-counts.sh` (ranges compared with an off-by-one, so neighbours count), `host-bits-kept.sh` (ranges from the address as written: the block written with host bits swallows the /32 just outside it), `first-three-octets.sh` (compares /24s), `both-orders.sh` (prints each pair twice). Reference script: `w24/solution-cidr-overlaps` (27 lines). Timing: 10 ms for 15 blocks.

## 8. Proofs

### Build: `build-address-plan` (plain lab, 45 minutes)

**Brief** (prompt; numbers chosen so two traps bite, see wrong fixes): the company reserves **10.64.0.0/12** for its cloud networks. Inside it, **10.72.0.0/16** is already used by the old data centre's disaster-recovery site and must not be touched. Plan, in `~/plan/plan.txt` (one `NAME BLOCK` per line), these subnets, each the smallest block that holds **twice** its machines plus the cloud's reserved addresses:

| Cloud | Subnets (names) | Machines in each |
| --- | --- | --- |
| AWS, one region, zones a, b, c | `aws-a-web`, `aws-b-web`, `aws-c-web`; `-app`; `-data` (nine) | web 254, app 120, data 25 |
| Azure, one region | `az-web`, `az-app`, `az-data` | web 500, app 60, data 12 |
| Google, one region (Google's subnets are regional) | `gcp-web`, `gcp-app`, `gcp-data` | web 62, app 30, data 6 |

and in `~/plan/summary.txt`, one line per cloud, `aws BLOCK`, `azure BLOCK`, `gcp BLOCK`: the single block from which that cloud's subnets are drawn, inside 10.64.0.0/12, with room beside its subnets for at least as many again (each summary at least twice the total size of its subnets). No two blocks anywhere overlap, nor touch 10.72.0.0/16. The learner may check the plan with their own `cidr-overlaps`.

**Checks** (each computes its own truth with `python3`'s `ipaddress`):

1. `names-and-form`: every name present once; every block a valid CIDR written at its start (no host bits).
2. `big-enough`: each subnet holds 2 × machines + reserved (AWS 5, Azure 5, Google 4).
3. `not-oversized`: each subnet is exactly the smallest prefix that does (the brief says so).
4. `no-overlaps`: no two subnets overlap; none overlaps 10.72.0.0/16.
5. `summaries`: each cloud's summary is aligned, inside 10.64.0.0/12, contains all that cloud's subnets and none of another's, overlaps neither 10.72.0.0/16 nor another summary, and is at least twice its subnets' total.
6. `cloud-rules`: AWS subnets between /16 and /28, Azure and Google /29 or larger (all are, by design; it stops a plan that "saves" space with a /30).

**Wrong fixes:** `forgot-reserved.sh` (sizes from 2 × machines alone: aws web 508 fits a /23 only without the 5 reserved, so checks 2 fails), `same-reserved-everywhere.sh` (5 for Google too: gcp-web's 124 + 5 = 129 needs a /24 where 128 fits a /25: check 3), `no-room-to-double.sh` (sized for the machines: check 2), `uses-dr-range.sh` (Azure drawn from 10.72.0.0/16: check 4), `misaligned.sh` (one /22 at 10.64.2.0: check 1), `summary-misses-a-subnet.sh` (check 5), `summary-overlaps.sh` (AWS summary /13 swallowing Azure's: check 5), `no-room-in-summary.sh` (AWS summary exactly its subnets' size: check 5). 8 wrong fixes; plain lab, so about 8 s each.

The reference solution (`solution.sh`) writes one plan with `cat > FILE <<'EOF'` (its opening comment explains the form, as the README asks).

### Debug: `debug-new-warehouse` (systemd network lab, 40 minutes): mechanisms proved, contract not yet run

**Topology** (base words plus N-A network files): `r1` (HQ router) with LANs: store 10.1.1.0/24 (`till` 10.1.1.20), office 10.1.2.0/24 (`prn` 10.1.2.30), warehouse (`scan`), servers 10.1.8.0/24 (`srv` 10.1.8.10); link r1–`r2` 10.255.2.0/30; `r2` (branch router) with branch 10.1.16.0/24 (`kiosk` 10.1.16.20). `/etc/netlab/plan.txt` (named in the prompt as "the address plan, which the network must agree with") lists: hq 10.1.0.0/20, store, office, warehouse, servers, branch 10.1.16.0/24, wan 10.255.2.0/30.

**Faults:**

1. `till`'s network file gives it 10.1.1.20**/16** (F11). Symptom: the till reaches its own router and the other store machines, and nothing else: every 10.1.x.x address, the branch's included, now looks local to it, so it ARPs for each and gets no answer.
2. The plan and r1's file give the warehouse **10.1.3.0/23**, with `scan` at 10.1.3.40/23: the kernel makes it 10.1.2.0/23, overlapping the office (F10). Symptom: scanners can't reach the office printer.
3. `r2`'s file routes HQ as **10.1.0.0/22** via r1. Symptom: the branch can't reach the servers (10.1.8.0/24 is outside the /22); it reaches the store and the office.

**Prompt:** "The shop's HQ router r1 serves the store, the office, the new warehouse and the server room; the branch's router r2 reaches HQ over a link. The address plan, `/etc/netlab/plan.txt`, is the source of truth: the network must agree with it. Since the warehouse was added: the store's till can't print, reach the servers or reach the branch; the warehouse scanners can't reach the office printer; and the branch can't reach the servers. There are three faults. Fix each at its cause. The rules: HQ's networks stay inside 10.1.0.0/20 and the plan stays free of overlaps; the branch keeps a single route for all of HQ; hosts keep only their own network and a default route; r1 answers ARP only for its own addresses; and everything must survive a restart."

**Checks:** `reach` (ping matrix: till, scan at its plan address, kiosk → prn, srv, each other), `plan-sound` (no overlaps, every block aligned, HQ blocks inside 10.1.0.0/20, branch outside), `network-matches-plan` (every host's and r1's addresses sit in their plan block with the plan's prefix length), `no-workarounds` (`proxy_arp` 0 on every r1 interface; each host's route table is exactly its connected route plus `default`), `one-summary` (r2 has exactly one route via r1 towards HQ, covering every HQ block in the plan and not 10.1.16.0/24), `lasts` (N-D's fresh build equals the live machines, and the ping matrix passes in it).

**Wrong fixes:** `proxy-arp.sh` (F11's hide: `no-workarounds`), `host-route.sh` (`10.1.2.0/24 via 10.1.1.1` on the till: `no-workarounds`), `warehouse-still-misaligned.sh` (renumbered to 10.1.5.0/23: `plan-sound`), `plan-only.sh` (plan fixed, network not: `network-matches-plan`, `reach`), `second-route.sh` (an extra 10.1.8.0/24 route on r2: `one-summary`), `summary-too-wide.sh` (10.1.0.0/19, which covers the branch's own block; connectivity still works because the branch's /24 is more specific, so only `one-summary` catches it), `live-only.sh` (`lasts`). The solution renumbers the warehouse to a free aligned /23 inside HQ (10.1.4.0/23 in the reference; any of 10.1.4, .6, .10, .12, .14 /23 passes), sets the till's /24, and r2's summary to 10.1.0.0/20.

**What was proved and what wasn't:** the three mechanisms (the moved block, the /16 host's failed ARP, proxy ARP hiding it) were captured on 2026-11-11 (F10, F11). The lab itself wasn't built: its contract must be run under `labcheck test`, with the restart trial, before writing the lesson around it (the topic 23 and 25 debugs, which were, show the pattern holds).

### Explain (20 minutes)

**Prompt:** "A team is about to create its first three cloud networks, one on each cloud, and plans to use 10.0.0.0/16 for all three 'because that's what the templates use'. Explain, in your own words: what a prefix like /20 means in bits, and how you'd work out the first and last address and the size of any block; how you'd split a block into subnets of different sizes and summarise them again, and why blocks must start on a multiple of their size; how you tell on sight whether two blocks overlap, and what overlapping ranges break; which ranges you'd choose from and which you'd avoid, and how each cloud's reserved addresses change your sums; and how you'd check a whole plan before anyone builds it."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `prefix-in-bits` | yes | An address is 32 bits; /20 fixes the first 20 (mask 255.255.240.0) and leaves 12 for hosts, 4,096 addresses; the network address is the address with the host bits cleared (AND with the mask), the last with them set |
| `split-summarise` | yes | Biggest subnets first, each on a multiple of its size; a /y holds 2^(x−y) /x blocks; aligned contiguous blocks summarise to one shorter prefix; leave room to grow, because a block can't grow into its neighbour |
| `overlaps` | yes | Blocks either nest or are apart; compare them on the shorter prefix; overlaps make peering impossible (the clouds refuse it), break VPN and on-premises routing, and are expensive to undo; three networks on 10.0.0.0/16 can never be joined |
| `ranges` | yes | RFC 1918 (10/8, 172.16/12, 192.168/16); avoid the defaults everyone uses (10.0.0.0/16, 172.31/16, 172.17/16, 192.168.0/1.0/24) and anything on-premises; AWS and Azure keep 5 addresses per subnet, Google 4, so size subnets with them |
| `check-the-plan` | yes | A script or tool checks every pair for overlaps and every block for alignment and size before building (their own script, `ipcalc`, the clouds' IPAM tools named as Module 11's) |
| `cloud-detail` | no | Any correct cloud difference beyond the reserved counts: AWS subnet sizes /16–/28; Azure /29–/2; Google /29–/4 and regional subnets; AWS's warning about 172.17.0.0/16 |

## 9. Review pool

† marks review-only items with numbers of their own.

| Skill | Items |
| --- | --- |
| `binary-and-masks` | `est-mask-octet`, `est-wildcard-octet`, `cidr-ip2int`, † `est-prefix-from-mask` (255.255.255.192 is /?: 26; the prompt states "its last number is 192"; mistakes 25, 6) |
| `block-math` | `est-aws-usable`, `est-network-octet`, `est-smallest-prefix`, `mcq-aligned`, † `est-smallest-prefix-google`, † `est-broadcast-octet` (172.16.5.200/29: last number of the last address 207; mistakes 208, 206) |
| `split-and-summarise` | `est-spec-drill`, `est-summary-waste`, `mcq-summary-or-not`, † `est-subnets-for-zones` (a /16 VPC split into equal subnets for 6 zones × 4 tiers with room to double: /22; mistakes /21, /23) |
| `overlaps` | `cidr-overlap-rule`, `mcq-which-overlap`, `mcq-peer-overlap` |
| `private-and-reserved` | `mcq-not-private`, `mcq-azure-first-vm`, `mcq-avoid-range`, `est-google-usable` |

The pool is mostly typed numbers with fresh values and judgement on real-looking pairs, because the six-month core is speed on sight.

## 10. Platform work first

| # | Need | Smallest version | Blocks |
| --- | --- | --- | --- |
| P-1 | **The estimate validator should read a dotted-quad address as four numbers** | `numbers_in()` in `tools/validate_content.py` today reads `10.20.30.77/27` as 10.2, 0.3, 0.77 and 27 (checked against its regex on 2026-11-11), so an octet can't be a `given`. Before the general pattern, match `\b\d{1,3}(?:\.\d{1,3}){3}\b` and add each octet; one test. No ADR change (ADR-0024 says "every given number appears in the prompt"; this makes the check see them) | Nothing blocks: items can state the octet again in words ("its last number is 77") until it lands. Recommended before writing, for cleaner prompts in topics 24, 25 and the checkpoint |
| P-2 | Network files for machines (topic 23's N-A), the fresh-build check (N-D) | As in topic 23's section 10 | The debug |
| P-3 | Packages | `ipcalc` (71 KB installed) and `sipcalc` (72 KB) join the base's second layer | The worked example (and the learner's habit of checking) |
| P-4 | Plain labs with `python3` | The checks compute their truth with `python3`'s `ipaddress`, and Module 1's and 2's plain labs don't install it (their first `RUN` is `sudo nano less shellcheck ca-certificates`, checked 2026-11-11). Smallest version: this topic's three plain labs start from the network base's first `RUN` line (which has `python3`), so they share its cached layer, then add `shellcheck` in a second line; they run as plain labs (`sleep infinity`, no `lab: init`) | Fill-in, write and build |

## 11. Cost and time

**Money:** nothing.

**Learner time:** lesson 15; required resources 45; 26 recall items × 1.5 = 39; worked example 30; fill-in 25; write 35; build 45; debug 40; explain 20. **Total 294 minutes; `estimated_minutes: 295`.**

**CI time:** the worked example and the debug are systemd network labs (about 80 s and 220 s for their contracts, by topic 23's and 25's measured runs); the fill-in, write and build are plain labs with no boot (about 40, 70 and 90 s: 5, 8 and 9 scenarios of a few seconds each). **About 8 minutes sequential, 2–3 of a shard.**

## 12. Open questions, each with a recommendation

1. **Bash or awk for "in code"?** Decided above: bash `$(( ))`. The routing designer's write lab gives an awk recipe; recommendation: they point to this topic's recap, which shows the awk form beside the bash one, and their checks accept either.
2. **Should `ipcalc` be in the write lab's image?** It doesn't answer overlaps, so it can't shortcut the task. Recommendation: yes, in every network lab (P-3); a learner who checks their numbers with a tool is doing what engineers do.
3. **The build's "exactly the smallest prefix" rule.** A real planner sometimes rounds up for tidiness. Recommendation: keep "exactly", because the brief states the rule and a sizing rule that admits one size larger can't catch the reserved-address mistakes the topic most needs to catch; the explain covers judgement.
4. **Google peering and AWS's default VPC (F8, F9)** weren't confirmed at source today. Recommendation: the writer opens Google's VPC Network Peering page and AWS's default-VPC page before using either claim; until then the lesson names only what F6, F7 and F3 say.
5. **Checkpoint 3 part 1** (the address plan for three clouds, four regions and two data centres) is this topic's build grown up, plus IPv6. Recommendation for the checkpoint designer: reuse this build's check code (`python3 ipaddress` truth, the overlap rule, the "smallest that fits" and "summary at least twice" rules) and the topic 25 build's IPv6 rules, so the checkpoint introduces no rule the topics didn't practise.

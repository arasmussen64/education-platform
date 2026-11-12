# Checkpoint 3: the address plan, the outage and the cloud link (`csa.m3.checkpoint`)

Designer's brief, 2026-11-11. The writing brief for Module 3's checkpoint, in the shape of Module 2's checkpoint brief and the plan it was written from (`docs/plans/cloud-module-2/MODULE-2-BRIEF.md`, section 5), whose decisions stand: parts in the slots `prove.build`, `prove.debug` and `prove.more` (ADR-0012 as amended 2026-11-11); the explain opens once part 1 passes; time targets are stated and self-timed; everything proven locally and for free.

Prototypes, captured output and contract logs: `prototypes/troubleshooting-checkpoint/` (`plan/` is part 1's checker with a sample plan and 14 wrong plans; `labs/debug-the-outage/` and `labs/debug-outage-v2/` are part 2's two versions; `CAPTURES.md` and the `*-contract-*.log` files are the evidence).

## 1. The plan in one screen

- **Three parts, not two.** Part 1, the address plan (a build, in a plain lab, checked by code); part 2, the intermittent outage (a debug, in a network lab, three faults); and a new **part 3, the cloud link** (a build, in a network lab: a private circuit and a backup IPsec VPN with BGP over it, summaries advertised, traffic steered, failover proven). The spec's two parts barely touch BGP and IPsec, the two topics an architect leans on most when connecting clouds to data centres, and the hardest to keep without retrieval. Under the owner's rule (best learning, then retention, then free) part 3 is worth its hour; section 6 argues it and gives the spec text.
- **Part 1 is a file the checker reads.** The learner fills `~/plan/plan.csv` (a row for every block, IPv4 and IPv6) from `/srv/plan/` (the sites and their needs, the policy, the addresses already in use). The checker, a Python script in the image that the learner never needs to read or run, works out every right size, overlap and summary from the requirements, so a plan from another story fails. **Prototyped:** the checker passes the reference plan and each of 14 wrong plans fails the one check for its mistake (section 3.6).
- **Part 2 is a live network with three interacting faults** and an office monitor that logs every page load, so "intermittent" is something the learner can see and measure. **Prototyped twice:** version 1 (faults found to duplicate three topics' debugs, so not used) kept its contract with 13 wrong fixes in 353 s and passed the restart trial; version 2, the one recommended, has three faults no topic's debug uses and kept its contract with 11 wrong fixes in 413 s; two of its checks were then redesigned after a finding and tested by hand (section 10).
- **Support** (ADR-0012) for part 1: a solved sibling in another story, four steps, two fresh versions. Part 3 has one fresh version (a build part needs at least one). Part 2, a debug, has none.
- **Time:** part 1 60, part 2 60, part 3 60, explain 20; `estimated_minutes: 240` with starting labs and boots.
- **CI:** about 35 minutes of runner time for the checkpoint's 11 labs (section 9).

## 2. Prerequisites, objectives and the proof block

**`prerequisites:`** the fourteen Module 3 topics (as the outline has them): `csa.net.layers`, `csa.net.cidr`, `csa.net.ipv6`, `csa.net.routing`, `csa.net.nat`, `csa.net.transport`, `csa.net.congestion`, `csa.net.dns`, `csa.net.http-tls`, `csa.net.http-semantics`, `csa.net.load-balancing`, `csa.net.bgp`, `csa.net.ipsec`, `csa.net.troubleshooting`, plus `csa.net.bgp-steering` if the critic accepts the BGP designer's proposed topic 34b.

**Objectives** (no cause of part 2 named):

- "Plan IPv4 and IPv6 addresses for three clouds, four regions in each and two data centres, with room for five years' growth: blocks of the right size, no overlaps with each other or with what's already in use, and one summary for each cloud, aiming for 60 minutes on your own clock."
- "Find and fix an intermittent outage in a network of routers, name servers and an application from the evidence it leaves, without weakening it and with every fix lasting past a reboot, aiming for 60 minutes on your own clock."
- "Connect a data centre to a cloud over a private circuit and a backup IPsec VPN with BGP, advertising only the data centre's summary, preferring the circuit both ways and failing over to the VPN by itself, aiming for 60 minutes on your own clock."
- "Explain how an estate's networks are planned, joined, published and kept running, and how the three clouds differ."

```yaml
prove:
  build: build-the-address-plan              # part 1 (plain lab)
  debug: debug-the-outage                    # part 2 (network lab)
  more:
    - id: build-the-cloud-link               # part 3 (network lab)
      versions: [build-the-cloud-link-clinic]
  explain: ...                               # opens once part 1 passes
unstuck:
  example: example-address-plan-print-shop
  steps: [step-size-the-blocks, step-place-and-summarise, step-the-ipv6-plan, step-the-whole-plan]
  versions: [build-the-address-plan-clinic, build-the-address-plan-bakery]
```

The story names follow Checkpoint 2's (shop, clinic, bakery, print shop), so a learner meets familiar businesses with new networks.

## 3. Part 1: `build-the-address-plan` (plain lab, 60 minutes)

### 3.1 What the learner gets

In `/srv/plan/`, read-only:

- `README.txt`: the task, the rules below in plain words, the file formats, where every cloud fact came from (with the date read), and the one command the lab offers (`plan-show`, below).
- `sites.csv`: `site,kind,cloud,subnets_today,hosts_per_subnet_today`: twelve cloud regions (`aws-us-east` ... `gcp-asia`: the same four geographies in each cloud) and two data centres (`dc-dallas`, `dc-london`, kind `dc`).
- `policy.txt`: one setting a line: the shop's IPv4 space (`10.0.0.0/8`), the blocks already in use (each data centre's existing /16, a partner's network reached over a VPN, an old lab range), the growth factors (hosts per subnet ×3 and subnets ×2 over five years), the room each cloud's summary must keep (at least twice what its regions use), each cloud's reserved addresses per subnet (AWS 5, Azure 5, Google Cloud 4), the shop's IPv6 space (a /40 in the documentation range, standing for the shop's own provider-independent block), the IPv6 sizes (a /48 per site, a /44 per summary), and Google Cloud's internal IPv6 pool (`fd20::/20`, one /48 per network).

And `~/plan/plan.csv`, with the header `name,ipv4,ipv6` and one row per block already named (each cloud's summary, its four regions, `gcp`'s network, `onprem` and the two data centres), the address columns empty. The learner fills them (`nano ~/plan/plan.csv`). `plan-show` prints the plan as a tree with each block's first and last address and size, a convenience that checks nothing (the learner's own `sipcalc`/`ipcalc`, if topic 24 teaches them, are also installed; **assumption:** topic 24 teaches CIDR math by hand and with a calculator tool; the CIDR draft's check code uses Python's `ipaddress`, which is what this checker uses).

**Why a file and not code.** The learner may not know Python yet (the spec puts it at Module 6), and the skill being proven is the plan, not a program. The checker is code, as the spec says ("Code checks it"), and checks the file.

### 3.2 The rules (README, and what the checks enforce)

1. Every cell is a block written as its network address (`10.2.64.0/19`, not `10.2.65.0/19`), or `-` where the README says so (Google picks each region's IPv6 /64 itself, so `gcp-*` regions' IPv6 is `-`).
2. **Sizes.** A region's IPv4 block is the smallest that holds, after five years, twice today's subnets, each the smallest block that holds three times today's hosts plus the cloud's reserved addresses. Exact: neither smaller nor bigger. Every IPv6 site block is a /48, every IPv6 summary a /44, and every IPv6 prefix length a multiple of 4 (a nibble boundary, so reverse DNS and the hex digits line up: RIPE-690).
3. **No overlaps.** No two sites overlap; no site or cloud summary overlaps a block already in use; summaries don't overlap each other; everything IPv4 is inside the shop's 10.0.0.0/8 and everything IPv6 (except Google's network) inside the shop's /40.
4. **The data centres keep their addresses** (they can't be renumbered); `onprem` is the smallest block that holds both.
5. **Summaries.** Each cloud's regions sit inside that cloud's summary, which is the smallest block with at least twice the space its regions use (room for five years' new regions). In IPv6 the same, with the /44s; Google's network is one /48 inside `fd20::/20`.

The numbers are chosen off every knife edge: each region's need clears the next size down by at least 11% (the tightest: 9,216 addresses needs a /18 of 16,384; a /19 holds 8,192), and exactly one region, `azure-us-west`, needs the reserved addresses to land on its size (3 × 170 + 5 = 515 hosts needs a /22 subnet; forgetting the 5 gives 510, a /23), so that skill is tested once, on purpose, by its own wrong plan.

**Where the three clouds differ, in the README** (each a fact the checker or a check uses): AWS and Azure reserve five addresses in every subnet, Google Cloud four; AWS VPC IPv4 blocks are /16 to /28 and its IPv6 subnets /44 to /64 in steps of 4, Azure's IPv6 subnets are exactly /64, Google gives a network's internal IPv6 a /48 from `fd20::/20` (you may choose which) and picks each subnet's /64 itself; AWS asks you not to use 172.17.0.0/16 for a VPC (some of its services use it). Facts 1 to 8.

### 3.3 Checks (`test_skills` use the CIDR and IPv6 drafts' ids)

Each check runs `plancheck NAME` (the prototype is `prototypes/troubleshooting-checkpoint/plan/plancheck.py`, about 230 lines) and expects `ok`; on failure it prints one sentence naming the row and the rule, never the right value. One mistyped block fails only `plan-complete`: every other check skips a cell it can't read, so one slip doesn't fail seven checks (the README's "value tests" rule).

| id | End state | `test_skills` |
| --- | --- | --- |
| `plan-complete` | Every row is there, named as given, each cell a block written as its network address, or `-` exactly where the README says | `csa.net.cidr/block-math`, `csa.net.ipv6/v6-notation` |
| `requirements-untouched` | `/srv/plan` is as it was (checksum) | `csa.linux.shell/navigate` |
| `v4-sizes` | Every region's IPv4 block is the smallest that holds its five-year need | `csa.net.cidr/block-math` |
| `v4-dcs` | The data centres keep their addresses; `onprem` is the smallest block that holds both | `csa.net.cidr/split-and-summarise` |
| `v4-apart` | No two sites overlap; nothing overlaps a block in use; summaries don't overlap; all inside 10.0.0.0/8 | `csa.net.cidr/overlaps`, `csa.net.cidr/private-and-reserved` |
| `v4-summaries` | Each cloud's regions are inside its summary, which is the smallest with twice the room they use | `csa.net.cidr/split-and-summarise` |
| `v6-sizes` | Sites /48, summaries /44, Google's network /48, every prefix on a nibble boundary | `csa.net.ipv6/v6-plan` |
| `v6-apart` | Sites inside their summaries, summaries inside the shop's /40 and apart, no two sites overlapping, Google's network inside `fd20::/20` | `csa.net.ipv6/v6-plan`, `csa.net.ipv6/v6-address-types` |

The summary-room rule is computed from the **required** region sizes, not the learner's, so a wrongly sized region fails `v4-sizes` alone (prototype finding).

### 3.4 Wrong plans (each a `wrong/*.sh` that writes the plan; all prototyped)

| Wrong | Fails | Prototype result |
| --- | --- | --- |
| `host-bits.sh` (10.2.65.0/19) | `plan-complete` | fails only that |
| `forgot-growth.sh` (aws-us-east /20) | `v4-sizes` | only that |
| `forgot-reserved.sh` (azure-us-west /20) | `v4-sizes` | only that |
| `regions-overlap.sh` | `v4-apart` | only that |
| `in-use-range.sh` (Google inside the partner's 10.100.0.0/16) | `v4-apart` | only that |
| `dc-renumbered.sh` | `v4-dcs`, `v4-apart` | those two |
| `no-room-to-grow.sh` (aws /17) | `v4-summaries` | only that |
| `region-outside-summary.sh` | `v4-summaries` | only that |
| `summary-too-big.sh` (azure /14) | `v4-summaries` | only that |
| `v6-not-nibble.sh` (a /46) | `v6-sizes` | only that |
| `v6-gcp-own-range.sh` (Google's network in the shop's /40) | `v6-apart` | only that |
| `v6-overlap.sh` | `v6-apart` | only that |
| `v6-region-outside.sh` | `v6-apart` | only that |
| `gcp-region-v6.sh` (a /64 typed for a Google region) | `plan-complete`, `v6-sizes` | those two |
| `edited-requirements.sh` (sites.csv changed to fit) | `requirements-untouched` | not prototyped (a checksum) |
| `copied-other-story.sh` (the clinic's plan) | `v4-sizes`, `v4-apart`, ... | not prototyped: different sites and needs, so several checks fail |

Sixteen, at about 3 s a container run (plain lab): under a minute of CI.

### 3.5 The reference plan (the shop) and its arithmetic

The prompt never shows this; the solution does. AWS regions need 16,384 + 2,048 + 8,192 + 1,024 = 27,648 addresses, twice that is 55,296, so its summary is a /16; Azure's 33,792 × 2 needs a /15; Google's 30,720 × 2 a /16. With the data centres at 10.0.0.0/16 and 10.1.0.0/16 (`onprem` 10.0.0.0/15) and the partner at 10.100.0.0/16, one valid layout is AWS 10.2.0.0/16, Google 10.3.0.0/16, Azure 10.4.0.0/15, each region placed largest first on a multiple of its own size. IPv6: AWS 2001:db8:4800::/44, Azure 2001:db8:4810::/44, onprem 2001:db8:48f0::/44, a /48 per site inside each, Google `fd20:a7b:9c00::/48`. Many other layouts pass: the checks hold rules, not answers.

### 3.6 Support for part 1 (ADR-0012)

- **Solved sibling `example-address-plan-print-shop`** (worked example, plain lab, 25 minutes): a smaller estate (two clouds, two regions each, one data centre) in labelled steps: 1 read the policy; 2 size each subnet (hosts × growth + reserved, up to a power of two); 3 size each site; 4 size each summary with its room; 5 place the biggest blocks first, each on a multiple of its size, avoiding what's in use; 6 write the summaries; 7 the IPv6 column on nibble boundaries; 8 `plan-show` to look it over. Checks: the learner's copy of the worked plan passes the same `plancheck` checks (so the example teaches the checker's rules too).
- **Steps** (fill-in, plain lab, each the whole plan but one part, per ADR-0012 item 3): `step-size-the-blocks` (everything given but the twelve regions' IPv4 blocks; the summaries are there, so the learner sizes and places inside them); `step-place-and-summarise` (the regions' sizes given in a column of the README, the learner writes every IPv4 block and summary); `step-the-ipv6-plan` (IPv4 complete, the IPv6 column empty); `step-the-whole-plan` (an empty plan with the order of work as comments). Each step's checks are part 1's, with hints.
- **Fresh versions** `build-the-address-plan-clinic` and `-bakery`: other sites, other numbers, other in-use blocks (the clinic's data centres at 10.10.0.0/16 and 10.11.0.0/16, its partner at 10.64.0.0/16; the bakery's IPv4 space 172.16.0.0/12 with the data centres inside it), other /40s. The checks are the same script reading the story's own requirements, so the versions are copies with new data files. A writer checks the knife-edge rule (11% clearance) for each story's numbers by running the checker against plans one size off.

## 4. Part 2: `debug-the-outage` (network lab, 60 minutes, target stated)

### 4.1 Why version 2

Version 1 was built first and keeps its contract: a secondary name server stuck on an old copy because the primary refuses its transfers, a forgotten more-specific static route through a dead appliance, and an app server whose firewall drops the ICMP errors path MTU discovery needs. On reading the topic designers' drafts the same day, all three turned out to be close cousins of topic debugs: topic 30's debug has the identical refused-transfer fault, topic 23's has a server firewall that breaks PMTUD, and topic 26's has a stale more-specific blackhole that appears only once another fault is fixed. A checkpoint's debug is "unfamiliar work" (ADR-0002), so **version 2 keeps the network, the monitor and the harness and replaces the three faults** with ones that use the same skills but that no topic's debug uses. Version 1's captured evidence goes to topic 36's practice instead (its worked example and casebook), where familiar faults are the point.

### 4.2 The network (both versions; version 2 shown)

```
office 10.10.0.0/24                 data centre 10.20.0.0/24                cloud 10.30.0.0/24
pc .10   resolver .53 --- r1 ===== r2 --- ns1 .53   app1 .11       r2 ===(tun1, tun2)=== r3 --- app2 .11   ns2 .200
                      (AS 65010)  (AS 65020)                                         (AS 65030, the cloud provider's)
```

Nine machines on the network-lab base. **r1, r2, r3** run FRR with BGP (`timers bgp 3 9`, connect 5, route maps on every session, as the BGP draft requires); r2 reaches r3 over **two tunnels** and shares traffic between them connection by connection (`maximum-paths 2`, `fib_multipath_hash_policy=1`), as an AWS transit gateway can share traffic over VPN tunnels with ECMP (a virtual private gateway can't: it uses one tunnel; appendix fact 10's page says both). **ns1** is BIND, primary for `shop.test`; **ns2**, in the cloud since October, is its secondary. **resolver** is Unbound, the office's resolver, with a stub zone for `shop.test` naming both servers (`infra-host-ttl: 60`, section 10, finding 3). **app1** and **app2** run nginx and serve the shop (the same 67 KB catalogue and a health page); `www.shop.test` has both addresses, handed out in turn (`rrset-roundrobin: yes`). **r2** and **app2** run nftables. **pc** runs the office monitor (`shop-monitor`, scenery), which loads a page by name every two seconds, alternating the health page and the catalogue, and logs `TIME PAGE ADDRESSES-TRIED STATUS SECONDS exit=N` to `/var/log/shop-monitor.log`. r3 and the topology are sealed (`netlab seal`): the provider's.

### 4.3 The three faults (version 2)

1. **The name server: an edit without a new serial.** On 3 November someone moved `www` from the old single server (10.20.0.13, now gone) to app1 and app2 by editing ns1's zone file, and didn't raise the serial. ns1 loaded the edit; ns2, told by NOTIFY that the serial is the same, keeps October's copy. The resolver asks either server, so for 30-second stretches (the record's TTL) the whole office is given the dead address. Evidence: `dig @ns1` and `dig @ns2` give **the same serial and different answers**; ns2's log says `notify from 10.20.0.53#...: zone is up to date` (captured), a log that says all is well. Skill: `csa.net.dns/records-and-zones` *(draft)*. The DNS topic teaches the rule ("an edited zone needs a higher serial, or the secondaries never fetch it") but its debug uses a refused transfer, so this is the rule retrieved in a new form.
2. **The router: a filter on one of two tunnels.** r2's firewall still carries a rule from the second tunnel's acceptance test (`oifname "tun2" tcp dport { 80, 443 } drop`, commented "Change 4711"). About half the office's connections to the cloud are hashed onto tun2 and dropped; DNS (UDP) and ping pass. Evidence: some connections from the same laptop to the same server work and some hang (only the source port differs, so the variable is the path); captures on r2's `eth0`, `tun1` and `tun2` at once show every SYN arriving and only some leaving, none of them on `tun2`; the rule's counter rises. (Not `ip route get` with ports: on the kernel tried it did not predict which tunnel a forwarded connection took, section 10, finding 7; the lesson of topic 36 says so, and this fault rewards the learner who proves the path with captures.) Skills: `csa.net.troubleshooting/locate-on-the-path`, `csa.net.routing/static-or-dynamic` (ECMP) *(draft)*, `csa.linux.net-tools/firewall-path`.
3. **The app: a firewall that only knows the old network.** app2 was first set up behind the data centre's old load balancer, and its firewall lets the web port in from `10.20.0.0/24` only. The office's connections to app2 are dropped; curl gives up on app2 after half its time and falls back to app1 (fact 9), so these loads are 2.5 s slow, not failed. Evidence: the monitor's `10.30.0.11,10.20.0.11 200 2.503` lines; from the office app2's port 80 times out while app1's answers; from app1 (the data centre) app2 answers; app2's firewall counter rises. Skill: `csa.linux.net-tools/firewall-path`, `csa.net.troubleshooting/split-the-suspects`.

**How they interact** (what makes it one intermittent outage rather than three constant ones): fault 3 hides fault 2 (while no office connection reaches app2, it doesn't matter which tunnel it took); once fault 3 is fixed, the loads that go to app2 and whose connection is sent over tun2 (about half, over time; the spread in any one minute can be lopsided: 19 to 1 in one prototype run, 10 to 10 and 5 to 15 in others) hang instead of falling back quickly. Fault 1 is independent and comes in 30-second waves. The learner sees the failure pattern change after each fix, which is what the prompt warns about ("test again after each fix") and what topic 36 practised. Captured, pristine (`CAPTURES.md`; v2 log):

```
03:46:08 /catalog 10.20.0.11              200    0.002 exit=0
03:46:13 /health  10.30.0.11,10.20.0.11   200    2.502 exit=0
03:46:17 /catalog 10.30.0.11,10.20.0.11   200    2.503 exit=0
03:46:23 /health  10.20.0.13              000    3.061 exit=7
03:46:26 /catalog 10.20.0.13              000    1.055 exit=7
```

### 4.4 The prompt (substance; house rule 5)

What the system is (every part named, as in 4.2: the office, its resolver, the three routers, the two tunnels and that traffic is shared between them, the two name servers and which is primary, the two app servers, the monitor and its log format), and that `on MACHINE COMMAND` and `router NAME` reach each machine. **Symptom:** "Since the move to two servers, the office says the shop is unreliable: some page loads take a few seconds, and every so often, for half a minute or so, nothing loads at all." **Three faults.** "Fixing one can change what you see: measure again after each fix." **Rules of the fix:** r3 and the tunnels are the cloud provider's: change nothing there; both name servers stay in service, ns2 as a secondary; both tunnels stay in use; every machine keeps its firewall and nothing is opened wider than the shop's own networks need; every fix lasts a reboot. **Time yourself: 60 minutes.**

### 4.5 Checks (version 2; descriptions are end states; the page lists them after a first try)

| id | End state | How | `test_skills` |
| --- | --- | --- | --- |
| `catalogue-everywhere` | From the office, the whole catalogue loads from every address either name server gives (three loads each, checksum compared; `timeout: 60`) | `dig @ns1`, `dig @ns2`, `curl -H 'Host: ...'` by address | `csa.net.troubleshooting/split-the-suspects`, `csa.net.dns/records-and-zones` |
| `both-tunnels-carry` | Twenty connections from the office to app2 all bring the whole catalogue, and both tunnels carried some of them (`timeout: 60`) | **tested by hand, after the contract** (`both-tunnels-carry.sh`): connections from fresh source ports above Linux's ephemeral range (61000 and up, the range moving with the clock so a re-run within a minute meets no TIME-WAIT), with a capture on each tunnel. A filter on one tunnel either drops some connections or, if none happened to be sent its way, leaves that tunnel unused: both fail, so nothing is left to chance. Filtered: `failed=1 tun1=19 tun2=0`, fails; fixed: `10/10` and `5/15`, passes twice in a row | `csa.net.troubleshooting/locate-on-the-path`, `csa.net.troubleshooting/measure-intermittent` |
| `by-name` | Loads by name through the office's resolver for 40 seconds, one every 2 s (longer than the record's 30-second TTL, so the resolver refills its answer at least once during the check), each the whole catalogue in under a second (`timeout: 60`). **Change from the prototype**, which made ten loads in a row: running over time is what an intermittent fault needs, and a refill from a stale server inside the window fails it | | `csa.net.troubleshooting/measure-intermittent`, `csa.net.dns/ttl-and-caching` |
| `names-agree` | ns1 and ns2 serve the same, **newer** serial (above the original) and the same answers; ns2 is still a secondary copying from ns1, and ns1 lets it | `dig @each`, `named-checkconf -p` on ns2, an AXFR from ns2's address | `csa.net.dns/records-and-zones` |
| `zone-private` | Nobody in the office can copy the zone from either server | AXFR from pc refused | `csa.net.dns/records-and-zones` |
| `resolver-asks-both` | The office's resolver still asks both servers | `unbound-control list_stubs` | `csa.net.dns/trace-resolution` |
| `both-tunnels` | r2 shares traffic for the cloud over both tunnels by BGP's routes, and runs its saved configuration | `ip route show 10.30.0.0/24` has nexthops on tun1 and tun2, proto bgp; the base's `frr_saved r2` | `csa.net.bgp/best-path` *(draft)*, `csa.net.routing/static-or-dynamic` |
| `office-admin-closed` | Nothing in the cloud reaches the office's SSH or remote-desktop ports | the check holds listeners of its own on pc:22 and pc:3389 and times connections from app2 (drop, not refuse) | `csa.linux.net-tools/firewall-path` |
| `r2-firewall-saved` | r2's file loads the rules it runs; `nftables@r2` enabled | scratch-namespace comparison (Module 1's recipe, with dummy interfaces named as r2's) | `csa.linux.net-tools/firewall-path` |
| `app2-web-for-the-shop` | app2's input policy is drop; its web port answers the office and the data centre and gives no answer to a network that is neither | timing from app1 and from r2's tunnel address; for the office, **a change from the prototype** (whose office probe could be hashed onto the filtered tunnel, so `still-filtered` failed this check too): ten connection attempts from pc with a capture on app2's `eth0`, passing when every SYN from the office that reached app2 was answered with a SYN-ACK and at least one reached it. That points at app2's firewall alone, whatever r2 does | `csa.linux.net-tools/firewall-path`, `csa.net.troubleshooting/split-the-suspects` |
| `app2-firewall-saved` | app2's file loads the rules it runs; `nftables@app2` enabled | scratch namespace | `csa.linux.net-tools/firewall-path` |
| `provider-untouched` | The topology and r3 are as they were | `netlab intact` | `csa.net.troubleshooting/prove-and-record` |

Twelve checks, limits adding to 60 + 60 + 60 + 9 × 30 = 450 s, inside the 600 allowed.

### 4.6 Wrong fixes (version 2; all ran under `labcheck test`)

`still-same-serial.sh`, `still-filtered.sh`, `still-dc-only.sh` (two of three each), `ns2-edited-by-hand.sh` (ns1's file copied over ns2's copy, serial unchanged: `names-agree`), `secondary-made-primary.sh` (`names-agree`), `resolver-ns1-only.sh` (`resolver-asks-both`, `names-agree`), `one-tunnel-only.sh` (tun2's BGP session shut down and saved: `both-tunnels`), `r2-firewall-flushed.sh` (`office-admin-closed`, `r2-firewall-saved`), `filter-runtime-only.sh` (the rule deleted from the running firewall only: `r2-firewall-saved`), `app2-open-to-all.sh` (`app2-web-for-the-shop`), `app2-runtime-only.sh` (`app2-firewall-saved`). Eleven. Results: section 10, prototype findings.

### 4.7 Version 1, kept as evidence

Version 1's contract (`outage-contract-3.log`): 5 of 10 checks passed before any work, the solution passed all 10, and each of 13 wrong fixes failed exactly the checks for its own mistake (for example `kernel-route.sh` failed only `routes-by-bgp`; `mss-clamp.sh` failed `pmtud-works` and the end-to-end checks; `transfer-to-anyone.sh` only `zone-private`); 353 s for 15 container runs; restart trial passed (all 10 checks after `docker restart`). Its checks and wrong fixes show the patterns version 2 reuses (scratch-namespace saved-firewall comparison, `frr_saved`, `netlab intact`, the timed drop test).

## 5. Part 3: `build-the-cloud-link` (network lab, 60 minutes, in `prove.more`)

*Designed on parts proven elsewhere, not prototyped end to end by me* (open question 2): BGP over GRE inside IPsec on the network-lab base kept its contract in the base designer's prototype (`proto-bgp-over-ipsec`, 7 checks, 4 wrong fixes, 350 s); the FRR designer proved BGP failover on a cut link in 73 ms, deterministic tie-breaking with `bgp bestpath compare-routerid`, the in-place route-map delay of 5 s, and the "cut a link in a check" recipe (R5); the IPsec designer proved route-based IKEv2 with BGP and a check that advertises fresh prefixes from the cloud at check time.

### 5.1 The story and network

The shop's data centre reaches its cloud over a **private circuit** (a stand-in for Direct Connect, ExpressRoute or Cloud Interconnect: a plain link `dx` with a BGP session, as the spec's "stand-ins for what one person can't buy" says) and needs a **backup VPN** over the internet. The cloud side is sealed scenery, made to behave like a cloud's gateway: AS 64512 (AWS's default for a virtual private gateway, the IPsec draft's choice), one router `cloud` with both sessions, the cloud's network 10.100.0.0/16 with a VM at 10.100.1.10, a VPN responder with a fixed proposal sheet, inside addresses 169.254.44.0/30 (a /30 from 169.254.0.0/16, outside the blocks AWS reserves, fact 9).

```
dc LAN 10.20.0.0/24, 10.20.1.0/24, 10.20.2.0/24          cloud 10.100.0.0/16
  dcapp 10.20.1.10 --- edge ==dx (169.254.100.0/30)==== cloud --- vm 10.100.1.10
                         \==wan== inet ==== vgw (the cloud's VPN gateway, on cloud)
```

`edge` is the learner's (FRR and strongSwan); `inet` is the internet (a router, sealed); `cloud` and its VPN gateway are sealed. The tunnel interface is the module's route-based tunnel as the base settles it (GRE inside IPsec on Docker Desktop's kernel per the base brief, section 6.2; a VTI if the IPsec draft's working VTI is confirmed: the critic decides, and this part follows).

### 5.2 What the learner builds (the prompt's requirements, from a provider sheet in `/srv/cloud-link/sheet.txt`)

1. The IPsec tunnel to the cloud's gateway, from the sheet (IKEv2, the sheet's proposals with PFS, the pre-shared key readable only by root), coming back by itself after a reboot.
2. Two BGP sessions with the cloud, one over `dx` and one over the tunnel, both with route maps (FRR's RFC 8212 default kept).
3. **Advertise only the data centre's summary**, 10.20.0.0/16, never its /24s (summarisation from topic 24, as BGP does it: `aggregate-address ... summary-only` or a static summary with a prefix list, either passes).
4. **Accept only the cloud's network** (inside 10.100.0.0/16, no longer than /24; never a default route).
5. **Prefer the circuit both ways:** the data centre sends to the cloud over `dx` (local preference on routes learned over `dx`), and the cloud sends to the data centre over `dx` (AS-path prepending on what the data centre advertises over the VPN; the scenery's cloud compares AS paths, as AWS does between VPN connections; the README notes that AWS also prefers a Direct Connect route over a VPN route by itself, fact 10). Without the learner's change, the tie goes to the VPN deterministically (the cloud's `compare-routerid` falls to the lower neighbour address, the tunnel's 169.254.44.2), so a missing prepend fails.
6. **Fail over by itself:** when `dx` dies, traffic goes over the VPN within 10 seconds, both ways, and comes back to `dx` when it returns.
7. Everything saved (`write memory`; swanctl files; `strongswan@edge` enabled).

### 5.3 Checks (`test_skills` use the drafts' ids)

| id | End state | How | `test_skills` |
| --- | --- | --- | --- |
| `tunnel-up` | The IKE SA with the cloud's gateway is established and a CHILD SA installed | read on the cloud side (`swanctl --list-sas` in the sealed machine) | `csa.net.ipsec/route-based-tunnel` |
| `sheet-proposals` | The negotiated algorithms are the sheet's (the cloud also accepts a weak legacy pair, as real gateways do; a config that lists strong proposals behind a weak one fails) | the cloud side's view of the SA | `csa.net.ipsec/ipsec-building-blocks` |
| `sessions-up` | Both BGP sessions Established and up longer than the check's wait | the base's BGP helpers (FRR brief R4) | `csa.net.bgp/bgp-sessions` |
| `summary-only` | On each session the cloud received exactly 10.20.0.0/16 | `show bgp ipv4 unicast neighbors ... routes json` on cloud | `csa.net.bgp/announce-and-filter`, `csa.net.cidr/split-and-summarise` |
| `accepts-only-the-cloud` | The check advertises from the cloud a fresh 10.100.R.0/24 (R chosen now), a default route and a fresh 172.16.R.0/24; within 15 s edge's kernel has the first by BGP and neither of the others; the check withdraws them (`timeout: 45`) | the IPsec draft's recipe | `csa.net.bgp/announce-and-filter` |
| `dc-prefers-dx` | edge's best path to 10.100.0.0/16 is via dx, and the kernel agrees | `bgp-best`, `ip route get` | `csa.net.bgp/local-preference` |
| `cloud-prefers-dx` | cloud's best path to 10.20.0.0/16 is via dx | `bgp-best` on cloud | `csa.net.bgp-steering/inbound-steering` (or `csa.net.bgp/best-path` if 34b isn't accepted) |
| `fails-over` | With dx cut (the check cuts it, R5), dcapp reaches vm within 10 s and the cloud's best path is the VPN; a ping between them crosses the internet as ESP only; dx restored, traffic back on dx within 15 s (`timeout: 90`, last in the file) | `lab-link`, a capture on `inet` | `csa.net.bgp-steering/failure-detection`, `csa.net.ipsec/bgp-over-tunnel` |
| `kept-safe` | `ebgp-requires-policy` not switched off; the key file mode 600 root | | `csa.net.ipsec/ipsec-building-blocks`, `csa.net.bgp/announce-and-filter` |
| `saved` | edge's FRR runs its saved configuration (`frr_saved`); `strongswan@edge` enabled | | `csa.net.bgp/bgp-sessions` |
| `cloud-untouched` | the cloud side and the internet are as they were | `netlab intact` | `csa.net.troubleshooting/prove-and-record` |

Limits: 45 + 90 + 9 × 30 = 405 s. The convergence rule from the base brief applies: one check waits (up to 30 s for BGP), the rest read at once.

### 5.4 Wrong fixes

`not-saved.sh` (`saved`), `static-routes.sh` (routes typed, no BGP: `sessions-up`, `accepts-only-the-cloud`), `advertises-the-24s.sh` (`summary-only`), `accepts-everything.sh` (`accepts-only-the-cloud`), `no-prepend.sh` (`cloud-prefers-dx`), `gre-in-the-clear.sh` (no IPsec: `tunnel-up`, `fails-over`), `weak-proposal.sh` (`sheet-proposals`), `policy-off.sh` (`no bgp ebgp-requires-policy` with no route maps: `kept-safe`), `cloud-side-changed.sh` (`cloud-untouched`). Nine. CI at the base prototype's rate (about 58 s a container run for an IPsec-and-BGP lab): about 11 minutes, and the same again for the fresh version.

### 5.5 Fresh version `build-the-cloud-link-clinic`

Another story with an Azure-flavoured cloud: AS 65515 (Azure VPN gateways' default; Azure reserves 65515 and 65517 to 65520, fact 11), inside addresses from Azure's APIPA range for BGP (169.254.21.0 to 169.254.22.255), the clinic's data centre summary 10.40.0.0/14 (from four /16s it must aggregate), the cloud's network 10.200.0.0/16, a different proposal sheet. Same checks with the story's numbers.

## 6. Why a third part, and the spec text

**Coverage without part 3:** part 1 retrieves CIDR and IPv6; part 2 retrieves DNS, routing (ECMP, BGP's multipath as scenery), firewalls and the method. BGP's policy and steering and all of IPsec go unretrieved at the module's end, though they are the two Module 3 topics the cloud track leans on hardest later (Module 11's hybrid connectivity, cross-cloud connectivity and its checkpoint are BGP over IPsec on three clouds). **Under the owner's rule:** best learning experience (the module's capstone task for an architect, connecting a data centre to a cloud with a backup, done end to end), best retention (a build from a provider sheet weeks after the topics, which is the retrieval the checkpoint exists for), free (local). Cost: one more hour for the learner and about 22 minutes of CI. NAT, TCP, congestion, HTTP, TLS and load balancing stay out of the parts (each topic proved them; a fourth part would make a 5-hour checkpoint) and are covered by the explain (section 7).

**Replacement text for the spec** (`docs/specs/cloud-solutions-architect.md`, the Checkpoint 3 block under Module 3):

```markdown
**Checkpoint 3: the address plan, the outage and the cloud link** (`csa.m3.checkpoint`).

1. Build an IPv4 and IPv6 address plan for three clouds, four regions in each and two data centres, with room for five years' growth. Code checks it for overlaps, block sizes and summarization.
2. Fix a local network of routers, name servers and an app. It has an intermittent outage caused by three faults.
3. Connect a data centre to a cloud over a private circuit and a backup IPsec VPN with BGP: advertise only the summary, prefer the circuit both ways, and fail over by itself.
```

And the topic 36 row's last cell: "find a fault from its symptoms with a repeatable method, using captures, traceroute, DNS lookups and logs; measure a fault that comes and goes; prove a fault that's on a provider's side". Then run `python -m uv run python tools/outline_cloud_track.py` (it rewrites the checkpoint's outline title, summary and objectives, as it never touches a topic being written).

## 7. The explain (20 minutes, opens once part 1 passes)

**Prompt** (keeps parts 2 and 3's answers out: it names no fault of part 2 and asks about hybrid design only in principle): "A colleague's plan for the shop's new estate: give every new VPC or VNet a /16 from 10.0.0.0/8 as it's needed, add IPv6 later, put NAT in front of everything 'for security', connect the data centre to each cloud with one VPN and static routes, run the shop's website on two servers with one name server in front of them, and when something breaks, restart the router. In your own words: what goes wrong with handing out blocks as needed, and what a plan does instead; how IPv6 planning differs and why IPv6 doesn't need NAT; what NAT costs and when you'd avoid it; why the data-centre link should use BGP over a private circuit with a VPN as backup, and how you'd make traffic prefer one path and fail over; what a load balancer with TLS in front of the two servers would add, and what its health check must test; why 'restart the router' is not a method, and what is; and two ways the three clouds differ that would change this plan."

**Rubric:**

| id | Required | Description |
| --- | --- | --- |
| `plan` | yes | Blocks handed out as needed overlap with data centres and partners (which breaks peering, VPNs and routing), can't be summarised, and leave no room to grow; a plan sizes each site from its needs with growth, keeps one summary per cloud with room, avoids ranges in use, and is written down before the first VPC. |
| `ipv6` | yes | A /48 per site and /64 subnets on nibble boundaries; addresses are plentiful, so the plan is for structure, not scarcity; IPv6 egress needs no NAT: a stateful filter (an egress-only gateway) gives "outbound only", and NAT was never the security. |
| `nat` | yes | NAT hides addresses but isn't a firewall; it costs ports (exhaustion per destination), money (per-GB processing on cloud NAT gateways) and end-to-end reachability; avoid it with IPv6, private endpoints for cloud services, or routing. |
| `hybrid` | yes | Static routes over one VPN can't fail over or carry new prefixes; BGP over a private circuit with a VPN as backup: advertise only summaries, filter what's accepted, local preference for the way out, AS-path prepending (or MED) for the way in, and failure noticed by the link or by BGP's hold timer (or BFD). |
| `lb-tls` | yes | A load balancer spreads load and removes a failed server; TLS terminates there with a full chain; the health check must test the server itself, not a shared dependency, or one blip takes the whole fleet out. |
| `method` | yes | Restarting is a guess that destroys evidence; the method is scope, split, locate, read the logs and counters, name the cause, change one thing, prove it with enough samples. |
| `clouds` | yes | Two real differences, for example: Google's VPC is global while AWS's and Azure's are regional; reserved addresses per subnet (5, 5, 4); Azure's IPv6 subnets are exactly /64 and Google picks internal /64s from a /48 in `fd20::/20`; AWS prefers a Direct Connect route over a VPN route by itself. |
| `dns` | no | Two name servers, kept in step, and TTLs lowered before a move. (Not required, and worded generally, because part 2 is open while the explain is.) |

## 7a. The skills this checkpoint assumes each topic teaches

Every `test_skills` id above comes from the topic designers' drafts as they stood on 2026-11-11 (their skills tables). If a topic's final brief renames or drops one, the critic changes the id here; if a topic no longer teaches what a check needs, that check needs a practice item in the topic first.

| Topic | Skill ids used here | What the checkpoint needs from it |
| --- | --- | --- |
| `csa.net.cidr` | `block-math`, `split-and-summarise`, `overlaps`, `private-and-reserved` | block sizes from host counts (with a cloud's reserved addresses: **assumed taught**, please confirm), aligned placement largest first, summaries, overlap rule, RFC 1918 and ranges in use |
| `csa.net.ipv6` | `v6-notation`, `v6-plan`, `v6-address-types` | /48 per site, /64 subnets, nibble boundaries, ULA and Google's `fd20::/20` (**assumed taught** as a cloud difference) |
| `csa.net.dns` | `records-and-zones`, `ttl-and-caching`, `trace-resolution` | SOA serial and secondaries, NOTIFY, `dig @server`, TTL and the resolver's cache, a stub zone |
| `csa.net.routing` | `static-or-dynamic` (ECMP in one paragraph) | that equal routes share traffic per connection; `ip route get` |
| `csa.net.bgp` | `bgp-sessions`, `announce-and-filter`, `best-path`, `local-preference` | sessions with route maps, prefix lists, aggregation (**assumed**: `aggregate-address` or a summary route announced with `network`), local preference, `maximum-paths` as scenery only |
| `csa.net.bgp-steering` (proposed 34b) | `inbound-steering`, `failure-detection` | AS-path prepending, how fast a cut link is noticed; if 34b isn't accepted, `csa.net.bgp` must teach prepending and the ids fall back to `csa.net.bgp/best-path` |
| `csa.net.ipsec` | `ipsec-building-blocks`, `route-based-tunnel`, `bgp-over-tunnel` | a tunnel from a provider sheet, proposals with PFS, BGP over it, a key file only root can read |
| `csa.net.troubleshooting` | `split-the-suspects`, `locate-on-the-path`, `measure-intermittent`, `prove-and-record` | this designer's topic 36 |
| `csa.linux.net-tools` (Module 1) | `firewall-path` | nftables chains, policies, persistence in the file |

## 8. Time

Part 1: 60 (the target its prompt states, reading included). Part 2: 60 (a live network with three interacting faults; Checkpoint 1's debug targets 45 for a single server, and the topic debugs 45). Part 3: 60. Explain: 20. Work: 200 minutes; with starting three labs and their boots (a network lab is up in about 10 s; the IPsec lab converges in about 7 s more) and running checks (part 2's take about 25 s, part 3's up to 2 minutes because of the failover check): **`estimated_minutes: 240`**.

## 9. CI cost

| Lab | Kind | Container runs | Estimate |
| --- | --- | --- | --- |
| `build-the-address-plan`, 2 versions, example, 4 steps | plain | 8 labs × about 14 runs | 6 min |
| `debug-the-outage` (v2) | network | 13 runs | 7 min (version 1 measured 353 s for 15 runs; version 2 measured 413 s for 13; the capture-based tunnel check adds up to 18 s to each failing run) |
| `build-the-cloud-link` and `-clinic` | network, IPsec | 2 × 11 runs | 22 min (at the base prototype's 58 s a run) |
| **Checkpoint** | | | **about 35 minutes** |

The base brief already recommends eight CI shards when Module 3's labs land; this fits inside that.

## 10. Prototype findings (what was tried, on Docker Desktop 29.8.2, 2026-11-11)

1. **The network comes up and converges fast.** `labcheck start` (image cached) 19 s for version 1's ten machines including the image build on the base; BGP routes in r1's table 5 s after boot; a full check run 10 s (version 1) to 25 s (version 2).
2. **The symptom is visible and intermittent.** Version 1's monitor showed 2.5-second loads (curl's half-time fallback) and a 30-second window of total failure; version 2's the same, with the new monitor logging the addresses curl tried (CAPTURES.md).
3. **Unbound avoided ns2 for 15 minutes after boot** because its first queries timed out while BGP was still converging, and its host cache keeps a bad round-trip estimate for `infra-host-ttl` (900 s by default); the stale-secondary fault was invisible until then. `infra-host-ttl: 60` in the scenery makes it show within a minute (13 of 30 cache fills came from ns2). Any lab with a resolver in front of servers that boot later needs the same.
4. **A solution must wait for BGP, and must not be fooled by identical errors.** Version 1's solution first passed by luck of timing; a wait loop then exited at once because both `dig` commands failed with the same error text and compared equal. The fix: wait until the serial is a number and the two agree (and, in version 2, is above the original). Every Module 3 solution that acts on a far machine right after boot needs a wait like this.
5. **FRR seed files must be written by FRR.** Version 2's `both-tunnels` failed on a pristine router because the hand-written seed lacked lines FRR adds (`domainname localdomain`, the position of `line vty`); writing each seed with `write memory` once at authoring time fixed it (the FRR designer's finding 8). The base's `lab-enter` gives each machine a hostname but leaves the domain name as the container's (`localdomain`): harmless, but the base could set it, as the FRR brief's drop-in does.
6. **`curl --local-port` can't bind a port that a recent connection left in TIME-WAIT** (exit 45). Version 2's first per-tunnel check reused one port for two addresses in the same run and failed the solution. A check that picks source ports must take them from a range no one else uses (above `ip_local_port_range`'s 60999) that moves with the clock, and never reuse one in a run.
7. **`ip route get ... ipproto tcp sport P dport Q` on a router does not predict the tunnel a forwarded connection takes**, on this kernel at least. With the filter on tun2, "predicted tun1" connections were dropped and "predicted tun2" ones arrived, with no agreement (CAPTURES.md §3). The version 2 check that trusted it let `still-filtered.sh` pass it (the contract still held, through `by-name` and the app2 check, but only by chance of the hash). Replaced by the capture-based `both-tunnels-carry`, tested by hand: it fails with the filter and passes, twice in a row, without it. **Correction for the record:** an earlier draft of this brief (and of topic 36's) claimed the prediction worked, from seeing the predictions alone; the fetches that "behaved accordingly" were made after the fix, when every path worked, and proved nothing. Topic 36's lesson now uses this as its example of proving a path with real traffic rather than with a tool's prediction.
8. **MSS clamping on r2** (version 1's `mss-clamp.sh`) didn't even fix the symptom: it failed the end-to-end checks as well as PMTUD's. Not investigated further; version 2 doesn't use it.
9. **Restart trial** (version 1): solution applied, `docker restart` (4 s), all ten checks passed again 15 s later. Version 2 has the same kinds of fix (FRR saved, nftables files, a zone file and BIND's transferred copy under the machine's state folder) and was not restart-tried separately: do it before `ready`.

**Version 2's contract** (`outage-v2-contract-2.log`, with finding 6's fix and before finding 7's): 7 of 11 checks passed before any work; the solution passed all 11; every one of the 11 wrong fixes failed at least one check, each the check for its own mistake (`app2-open-to-all` only `app2-web-for-the-shop`, `filter-runtime-only` only `r2-firewall-saved`, `one-tunnel-only` only `both-tunnels`, `ns2-edited-by-hand` and `secondary-made-primary` only `names-agree`, `r2-firewall-flushed` `office-admin-closed` and `r2-firewall-saved`, and so on); 413 s for 13 container runs. The two checks redesigned after it (`both-tunnels-carry` from finding 7, and the office half of `app2-web-for-the-shop`) were tested by hand, not yet in a full contract run: the next run is the writer's first job.

## 11. Platform work needed first

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| C1 | The network-lab base and labcheck's shared bases | the base brief's N1 to N3 | parts 2 and 3 |
| C2 | `prove.more` | **exists** (built for Checkpoint 2, ADR-0012's amendment of 2026-11-11) | none |
| C3 | A plain-lab first `RUN` with `python3` (the checker) and the learner's calculator tools | one line shared by part 1's eight labs: `sudo nano less procps python3 sipcalc ipcalc` (sipcalc and ipcalc only if topic 24 teaches them) | part 1 |
| C4 | A check may cut a link and restore it (FRR brief's R5, its open question 2) | as specified there: `lab-link` in an `EXIT` trap, last in the file, `timeout: 60` to 90 | part 3's `fails-over` |
| C5 | The map's note on a checkpoint in progress lists further parts | ADR-0012's amendment says it should before a checkpoint with parts is `ready`; check whether Checkpoint 2's work did it | the checkpoint going `ready` |

No new item types, no migration.

**What the labs need from the kernel** (house rule 4):

| Need | Part | Docker Desktop 29.8.2 (2026-11-11) | GitHub's runners |
| --- | --- | --- | --- |
| Network namespaces, veth, bridges, `ip_forward` per namespace | 2, 3 | works (both prototypes) | works for Module 1 and 2's single extra namespace; nine machines not tried (the base's CI spike) |
| `fib_multipath_hash_policy=1` per namespace and FRR `maximum-paths` installing two next hops | 2 | works: two `nexthop` lines, and real connections spread over both tunnels (10/10 and 5/15 in two runs of 20); `ip route get` with ports does **not** predict which (finding 7) | expected, not tried |
| BIND primary and secondary, NOTIFY, AXFR between namespaces; Unbound stub zone | 2 | works | not tried |
| nftables `forward` and `input` chains with counters in machines | 2 | works | works in CI today |
| `ip_gre`, `xfrm_user`, `esp4` (GRE inside a tunnel-mode SA) | 3 | works per the base brief's prototype (VTI and XFRM interfaces don't, on this kernel) | **not tried**: the base's CI spike carries its BGP-over-IPsec prototype; part 3 waits on its result |
| Python 3 `ipaddress` in a plain lab | 1 | works: the checker gave identical results for the reference plan and all 14 wrong plans under CPython 3.14 on Windows and under Ubuntu 24.04's Python 3.12.3 (a throwaway container from the base image) | works (same image) |

## 12. Cost

**Money: none.** Part 3's circuit and VPN are local stand-ins, as the spec's "stand-ins for what one person can't buy" asks. An optional real-cloud version of part 3 (an Azure VPN gateway with BGP to a local strongSwan) would cost money (a VPN gateway bills by the hour) and needs the owner's run; it is **not** proposed for this checkpoint (open question 5).

## 13. Open questions, each with a recommendation under the owner's rule

1. **Part 2: version 2's faults or version 1's?** Version 1 is fully proven and its faults are the module's most classic, but they repeat three topic debugs. *Recommendation:* version 2 (unfamiliar work is what a debug proves; the skills are the same). Version 1's evidence is used in topic 36's practice.
2. **Part 3 isn't prototyped end to end.** Every mechanism is proven in another designer's prototype, but not together. *Recommendation:* prototype it before writing, starting from the base's `proto-bgp-over-ipsec` with a `dx` link and a second session added; the riskiest part is `fails-over` on a 4-CPU CI runner with four labs at a time, so measure it in the CI spike.
3. **Should part 1 ask for subnets too** (each region's tiers and zones), not just region blocks? *Recommendation:* no. Topic 24's build carves subnets; the checkpoint's skill is the estate-level plan, and twelve regions' subnets would be about 130 more rows to type in 60 minutes with no new skill in them.
4. **Should the checkpoint's part 2 include a VPN fault** (the IPsec designer offered a PFS mismatch that drops the tunnel at every rekey) or a load-balancer fault (the LB designer offered a deep health check)? *Recommendation:* no, for part 2: the spec names routers, a DNS server and an app, and version 2 has one fault in each; the VPN's faults are part 3's to retrieve, as builds.
5. **A real-cloud version of part 3?** *Recommendation:* not now. Module 11's checkpoint builds BGP over IPsec on three real clouds; adding it here would spend credit on what Module 11 proves properly.
6. **`estimated_minutes: 240`** is the longest checkpoint so far (Checkpoint 2 is 200). *Recommendation:* keep it; it's three parts that each retrieve a different skill set, and the parts count whenever they pass, so the learner can spread them over several sittings.

## Appendix: facts read for this checkpoint (2026-11-11)

| # | Claim | Source |
| --- | --- | --- |
| 1 | AWS: subnet IPv4 /16 to /28; first four and last address of each subnet reserved (5); IPv6 subnets /44 to /64 in increments of /4, also five reserved | https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html |
| 2 | AWS: VPC IPv4 /16 to /28; don't use 172.17.0.0/16 (some services use it); VPC IPv6 blocks /44 to /60 in increments of /4 (Amazon-provided /56 can't be chosen) | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html |
| 3 | Azure: five addresses reserved per subnet (first four and last); smallest IPv4 subnet /29, largest /2; IPv6 subnets exactly /64; unusable in a VNet: 224.0.0.0/4, 255.255.255.255/32, 127.0.0.0/8, 169.254.0.0/16, 168.63.129.16/32; RFC 6598 space accepted; page dated 2026-07-08 | https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq |
| 4 | Google Cloud: first two and last two addresses of a primary range reserved (4); minimum range 8 addresses (/29), shortest mask /4; internal IPv6: a /48 from fd20::/20 per network, chosen automatically or by you; subnet ranges /64 picked by Google | https://docs.cloud.google.com/vpc/docs/subnets |
| 5 | RFC 6177 (BCP 157): no single size required; "at least one /64, and in most cases significantly more"; plan for growth over a decade | https://www.rfc-editor.org/rfc/rfc6177.html |
| 6 | RIPE-690: /48 for business sites, /56 residential; prefixes on nibble boundaries to align with reverse DNS delegation | https://www.ripe.net/publications/docs/ripe-690/ |
| 7 | RFC 3849: 2001:db8::/32 is the IPv6 documentation prefix | (named in the IPv6 draft's facts; not re-read by me) |
| 8 | RFC 1918's three private ranges; RFC 6598's 100.64.0.0/10 | (the CIDR draft's facts) |
| 9 | AWS Site-to-Site VPN inside tunnel IPv4: a /30 from 169.254.0.0/16; reserved and unusable 169.254.0.0/30 to 169.254.5.0/30 and 169.254.169.252/30 (AWS's localised tunnel-options pages and the CloudFormation reference; the English page read didn't show the list) | https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNTunnels.html (and its localised versions) |
| 10 | AWS virtual private gateway route priority for the same prefix: Direct Connect BGP routes, then static VPN routes, then VPN BGP routes; between VPN connections the shortest AS path, then the lowest MED; "ECMP is not supported for Site-to-Site VPN connections on a virtual private gateway", but is on a transit gateway | https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-route-priority.html |
| 11 | Azure VPN gateways' default ASN is 65515; Azure reserves private ASNs 65515, 65517, 65518, 65519, 65520; APIPA BGP addresses for Azure gateways are set on the gateway | https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-vpn-faq (BGP section; page dated 2026-06-04) |
| 12 | BIND: the secondary compares serials and transfers only when the primary's is higher; captured ns2 log "notify from 10.20.0.53#...: zone is up to date" with equal serials and different data | captured (version 2 prototype) |
| 13 | Unbound: `rrset-roundrobin` default yes; `infra-host-ttl` default 900 s ("Time to live for entries in the host cache") | https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html |
| 14 | libcurl gives at most half the remaining time to each address while more remain and more than 600 ms is left | https://everything.curl.dev/transfers/conn/how.html |
| 15 | ct state RELATED includes ICMP errors for a tracked connection (version 1's PMTUD fault) | https://man7.org/linux/man-pages/man8/iptables-extensions.8.html |

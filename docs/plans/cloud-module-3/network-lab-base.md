# Module 3 design: the shared network-lab base

The one way every Module 3 lab builds a network of several machines inside its one container, so that fourteen topics and Checkpoint 3 don't invent it fourteen times. Designed and **prototyped on 2026-11-11** on the owner's PC (Docker Desktop 29.8.2, kernel `6.18.33.2-microsoft-standard-WSL2`, 8 CPUs, 16 GB), with the repository's own `tools/labcheck.py` running the contracts. Nothing here is in the repository yet.

**The prototype** (cite these paths) is in `<design folder>/prototypes/network-lab-base/`:

- `repo/content/lab-bases/net/`: the base image (`Dockerfile`), the engine (`netlab`, 329 lines of bash), `lab-enter`, `on`, the eight unit templates in `units/`, and the checks' helpers (`checklib.sh`).
- `repo/content/topics/csa.net.netlab-proto/exercises/proto-bgp-over-ipsec/`: a five-machine lab (two sites, an internet router, IPsec and BGP between the gateways). Full contract: solution, seven checks, four wrong fixes. **Keeps its contract under the real `labcheck test`** (`contract-run-4.log`).
- `repo/content/topics/csa.net.netlab-proto/exercises/proto-services/`: a nine-machine lab (a DNS hierarchy of three BIND servers, an Unbound resolver, an HAProxy load balancer in front of two nginx servers, an nftables NAT router, a slow link). Eight checks, a planted fault, one wrong fix. **Keeps its contract** (`contract-run-all.log`).
- `repo/tools/labcheck.py` with the one change the base needs (`labcheck-shared-base.diff`, 29 added lines), and `repo/tools/content_model.py`, an unchanged copy.

Run it from `prototypes/network-lab-base/repo/` with the repository's Python: `<repository>/.venv/Scripts/python.exe tools/labcheck.py test --all --jobs 2` (304 s for both labs), or `start`, `shell`, `check` as a learner would.

## 1. The plan in one screen

- **A machine is a network namespace** with its own `/etc` for each program it runs, its own `/run`, its own state folders and its own name. It's the same mechanism Module 2's `dc1` used (`csa.hw.windows-ad`), made general: one engine, `netlab`, builds every lab's machines at boot from a short **topology file**, and `on MACHINE COMMAND` runs a command on one (`on r1 vtysh`, `on host-a curl ...`). Learners met namespaces, veth pairs and `ip netns exec` in `csa.linux.net-tools` and `csa.linux.containers`.
- **Each daemon runs as a systemd unit per machine** on the lab container: `frr@r1`, `strongswan@vpn-a`, `named@ns1`, `unbound@resolver`, `nginx@web1`, `haproxy@lb1`, `nftables@edge`. They start at boot, so the restart trial passes with nothing extra. Inside a machine every program uses its normal paths (`/etc/frr/frr.conf`, `/etc/swanctl/`, `/run/charon.vici`), so what the learner types is what they'd type on a real router.
- **One shared base image**, `content/lab-bases/net/`, `FROM ubuntu:24.04`. Its first layer is byte-identical to the 86 existing systemd labs' first layer (Docker reused it from cache), the second adds the network software (291 MB, 42 to 53 s to build), the third the engine (under 60 kB). A lab's own Dockerfile is four lines. **`tools/labcheck.py` learns to build a base before a lab whose Dockerfile says `FROM lab-base-<name>`** (29 lines; an ADR-0018 amendment).
- **Checks read the network's real state**: FRR's JSON, the kernel's routes (whose `protocol` field tells a BGP route from one typed by hand), the kernel's IPsec SAs, HAProxy's own stats, a probe from another machine, a capture decoded by tcpdump or tshark. Two helpers close the usual shortcuts: `frr_saved` (the running routing is the saved routing) and `netlab intact` (the scenery the learner mustn't touch, such as the cloud's side of a VPN, is unchanged).
- **What works on Docker Desktop:** FRR (zebra, staticd, bgpd, ospfd; IPv6 router advertisements), strongSwan with policy-based tunnels and with GRE protected by a tunnel-mode SA, BIND, Unbound, nginx, HAProxy, nftables with NAT, conntrack, tc netem, BBR, IPv6 forwarding and SLAAC, tcpdump and tshark. **What doesn't:** XFRM interfaces (the kernel has no such device type), strongSwan with VTI interfaces (the SAs come up, every packet is dropped on arrival), and ESP transport mode (dropped on arrival even with hand-made SAs). So **the route-based VPN of `csa.net.ipsec` is a GRE tunnel inside a tunnel-mode IPsec SA**, which works and keeps its contract; section 6.2 says what that costs in faithfulness to the clouds.
- **Timings:** a five-machine lab boots in 2 to 3 s and a nine-machine one in about 6 s; the solution of the BGP-over-IPsec lab converges in 7 s; a check run takes 7 to 11 s; after `docker restart`, traffic flows again 5.7 s after boot and every check passes. A full contract with six container runs took 280 to 382 s, mostly checks waiting out failures; section 9 gives the rule that halves it, and the CI cost.

## 2. What a network lab is made of

### 2.1 The machine

| Part of a machine | How | Persists across a restart? |
| --- | --- | --- |
| Interfaces, addresses, routes, firewall, sockets, conntrack table, sysctls, qdiscs, IPsec SAs | its own network namespace (`ip netns add`), named after it | No: rebuilt at boot from the topology and the daemons' configuration, exactly as a server's kernel state is |
| `/etc/<program>` (`/etc/frr`, `/etc/swanctl`, `/etc/strongswan.conf`, `/etc/strongswan.d`, `/etc/bind`, `/etc/unbound`, `/etc/nginx`, `/etc/haproxy`, `/etc/nftables.conf`), `/etc/hosts`, `/etc/resolv.conf` | `/etc/netns/<machine>/`, which `ip netns exec` lays over `/etc` file by file (ip-netns(8)) | Yes (the container's disk) |
| `/run` | `/run/netlab/machines/<machine>/` bound over `/run` by `lab-enter`, with the lab machine's `/run/systemd` and `/run/log` still visible inside, so `systemctl` and `journalctl` work from a machine | Wiped at boot, as on a server |
| State folders (`/var/cache/bind`, `/var/lib/bind`, `/var/lib/unbound`, `/var/log/frr`, `/var/lib/frr`, `/var/log/nginx`, `/var/lib/nginx`, `/var/lib/haproxy`) | `/var/lib/netlab/machines/<machine>/...` bound by `lab-enter` | Yes |
| Name | a UTS namespace per entry; the prompt reads `root@r1:~#` | n/a |

What a machine **doesn't** have, which the first lesson must say plainly: its own systemd (its services are units on the lab machine, `systemctl status frr@r1`, and their logs are in the lab machine's journal, `journalctl -u frr@r1`), its own process list (`ps` inside r1 shows every machine's processes; `ip netns identify PID` says whose), and its own files outside the folders above (`/tmp`, `/home`, `/root` and the users are shared by all machines). Writers: never use a file in `/tmp` as a machine's private state.

`on MACHINE [COMMAND...]` (`/usr/local/bin/on`) runs `sudo ip netns exec MACHINE lab-enter MACHINE COMMAND`: the learner is root on every machine, as an administrator logged in to it would be, and the lab machine itself stays the console. With no command it opens a login shell in `/root`. `netlab show` lists the machines, what each runs, and their interfaces that are up.

The lab machine (the container's own namespace) is on **no lab network**. Switches (bridges) live in a namespace of their own, `switches`, so nothing the learner does to the lab machine's firewall touches lab traffic, and `on switches tcpdump -i office` works like a switch's mirror port. **No machine can reach the real internet**: a lab that needs "the internet" builds a small one (an ISP router, root and TLD name servers), as `proto-services` does. That keeps every lab the same on the owner's PC, on a CI runner and offline, and makes DNS answers the lab's own.

### 2.2 The topology file

`/etc/netlab/topology`, copied in from the lab's folder. It is bash calling ten words, one line each, so a learner can read it as the network diagram in text:

```bash
machine r1 router                    # a machine; a router forwards IPv4 and IPv6
machine host-a                       # a host doesn't, and accepts router advertisements
link r1:eth1=10.0.12.1/30,2001:db8:12::1/64 r2:eth1=10.0.12.2/30   # a cable (veth pair)
lan office r1:eth2=10.1.0.1/24 host-a:eth0=10.1.0.10/24 host-b:eth0=10.1.0.11/24   # a switch
route host-a default via 10.1.0.1    # a host's route (a router's routes belong in FRR)
dns host-a 10.1.0.53                 # resolv.conf, written afresh at every boot, as DHCP would
sysctl r1 net.ipv4.conf.all.rp_filter=1
netem isp eth2 delay 20ms loss 1%    # delay and loss on one end of a link (egress only)
mtu r1 eth1 1400
tunnel vpn-b gre1 gre local 203.0.113.2 remote 198.51.100.2 ttl 64 addr 169.254.10.2/30
run r1 frr                           # services: frr strongswan named unbound nginx haproxy nftables
```

What `netlab up` does for every machine, whatever the topology says, because a new namespace copies the IPv4 settings of the machine Docker runs on and resets IPv6 (kernel docs, `devconf_inherit_init_net`), and Docker Desktop and a CI runner differ: it sets `ip_forward` and IPv6 `forwarding` (1 on a router, 0 on a host; Docker Desktop hands every new namespace `ip_forward=1`), `rp_filter=0` (Docker Desktop hands `2`), redirects off, `accept_dad=0` (IPv6 addresses usable at once; the IPv6 topic can turn DAD back on with a `sysctl` line), `accept_ra` off on routers, the ephemeral port range, `cubic`, and `ping_group_range`. IPv6 addresses are added `nodad`. Interface names are the topology's (`eth0`, `eth1`), made under throwaway names and renamed in place. Names: machines up to 8 characters, lans up to 15, and `machine.interface` up to 15 (the kernel's limit on an interface name).

`netlab enable`, run once in the lab's Dockerfile, enables each `run` service as `<service>@<machine>` and gives each machine its own copy of what its services need: the package's defaults fill the gaps around the lab's own files (`cp -an`), and FRR's folder is made the `frr` user's so `write memory` works. `netlab seal FILE...` records checksums of the scenery; `netlab intact` prints `intact` or names what changed.

### 2.3 A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { init: systemd }
├── Dockerfile         four lines, below
├── topology
├── machines/<m>/...   each machine's /etc files: machines/r1/frr/frr.conf, machines/r1/frr/daemons,
│                      machines/vpn-b/swanctl/conf.d/shop.conf, machines/ns1/bind/named.conf ...
├── checks.yaml  solution.sh  wrong/*.sh
```

```dockerfile
FROM lab-base-net
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/vpn-b/frr/frr.conf /etc/netns/vpn-b/swanctl/conf.d/shop.conf
```

A topic that needs one more package (an ACME client for `csa.net.http-tls`, say) adds a `RUN apt-get install` after `FROM`, identical in all its labs so Docker shares it. The `story.sh`-style scenery of Module 2 (a service that fails at boot, a timer) works the same way as before.

### 2.4 The services

| Unit | Runs, inside the machine | Notes |
| --- | --- | --- |
| `netlab.service` | `netlab up` on the lab machine, before `network.target` | the scenery; every per-machine unit `Requires=` and `After=` it |
| `frr@M` | `frrinit.sh start` (watchfrr, then the daemons `/etc/frr/daemons` switches on) | replaces the package's own `frr@.service`, which means a second FRR in the same namespace ("pathspace", `-N`); `ExecReload` is FRR's own reload |
| `strongswan@M` | `charon-systemd`, then `swanctl --load-all` | `/run/charon.vici` is per machine because `/run` is |
| `named@M` | `named -f -u bind`, after `named-checkconf` | three on one lab worked, each with its own `/var/cache/bind` |
| `unbound@M` | `unbound -d -p` | no chroot, no trust-anchor helper; the lab's own `unbound.conf` replaces the package's |
| `nginx@M` | `nginx -g 'daemon off;'`, after `nginx -t` | |
| `haproxy@M` | `haproxy -Ws`, after `haproxy -c`; makes `/run/haproxy` | stats socket `/run/haproxy/admin.sock` |
| `nftables@M` | `nft -f /etc/nftables.conf` (the machine's) | oneshot, before the machine's other services |

The plain `frr`, `strongswan`, `named`, `unbound`, `unbound-resolvconf`, `nginx` and `haproxy` units are disabled on the lab machine. **Mask them instead** (not yet tried): a learner who types `sudo systemctl restart frr` out of habit would otherwise start an FRR on the lab machine itself. `tpm-udev` is masked (it fails in a container and left every lab `degraded`).

## 3. The base image

`content/lab-bases/net/Dockerfile`, in the prototype:

| Layer | What | Size | Build |
| --- | --- | --- | --- |
| 1 | The systemd labs' first `RUN`, byte for byte (systemd, SSH, disk tools, `iproute2`, `tcpdump`, `nftables`, `conntrack`, `dnsmasq`, `bind9-dnsutils`, `curl`, `python3`, the learner and `shop` accounts) | 153 MB | cached: shared with 86 labs |
| 2 | `frr frr-pythontools strongswan-swanctl charon-systemd strongswan-pki libstrongswan-standard-plugins libstrongswan-extra-plugins bind9 unbound nginx haproxy tshark iperf3 mtr-tiny iputils-tracepath iputils-arping ethtool socat openssl ndisc6`, then the packages' services disabled and `tpm-udev` masked | 291 MB | 42 to 53 s on this PC |
| 3 | `netlab`, `lab-enter`, `checklib.sh`, `on`, `units/`, `netlab.service` enabled | under 60 kB | under a second |

Versions installed (Ubuntu 24.04's archive, 2026-11-11): FRR 8.4.4, strongSwan 5.9.13, BIND 9.18.39, Unbound 1.19.2, nginx 1.24.0, HAProxy 2.8.30, tshark 4.2.2, iperf3 3.16, mtr 0.95, ndisc6 1.0.7. Docker Desktop reports the whole image as 688 MB.

**Why each, for teaching value:**

- **FRRouting** (the spec names it): `vtysh` reads like the routers in every cloud's documentation, `show ... json` gives checks the router's own answer, and one package covers static routes, OSPF, BGP, BFD and IPv6 router advertisements. Ubuntu's 8.4.4 needs no extra package source; FRR's own repository has newer versions and isn't needed.
- **strongSwan with `swanctl`** (the spec names strongSwan): the configuration is in named blocks that map one to one onto IKE phase 1 (`connections`, `proposals`, `local`, `remote`) and phase 2 (`children`, `esp_proposals`, `local_ts`, `remote_ts`), which is the vocabulary of every cloud VPN's settings page. The two plugin packages are needed or every `swanctl` command first prints 17 lines of "plugin ... failed to load".
- **BIND for authority, Unbound for recursion.** Two programs for the two jobs is the clearest way to teach that answering for a zone and looking names up for clients are different roles (`csa.hw.windows-ad` defined resolver and zone; `csa.net.dns` goes deep). BIND's zone files are the classic master-file format, and `named-checkzone` and `rndc` are the tools of the trade; Unbound's `unbound-control` (`dump_cache`, `flush`, `lookup`) shows a resolver's cache, TTLs and negative answers. `dnsmasq` stays in layer 1 for a "site resolver" role, as Module 2 used it.
- **HAProxy for load balancing, nginx for web servers.** HAProxy has active health checks, draining and a stats socket a check can read (`show stat`, CSV); open-source nginx has only passive health checks (active ones are in the commercial subscription), so it plays the backends and the TLS and HTTP/2 server.
- **tshark** is the largest package (`libwireshark17t64`, 125 MB installed), kept because captures run through six topics (transport, HTTP and TLS, BGP, IPsec, troubleshooting, the checkpoint) and `tshark -Y ... -T fields -e ...` lets a check read one field of a handshake or a DNS question. Dropping it would save about 125 MB and 15 to 20 s of build; open question 3.
- **iperf3** for congestion control, **mtr** and **tracepath** (path MTU), **arping** (ARP), **ethtool**, **socat** (HAProxy's socket), **openssl** (certificates, `s_client`), **ndisc6** (`rdisc6`, router advertisements).

Not in the base, and why: `radvd` (FRR sends router advertisements), `jq` (the labs have none, as `content/README.md` says; checks parse JSON with `python3`), an ACME server or client, `wireguard-tools`, `isc-dhcp`. Not tried: QUIC and HTTP/3 (whether Ubuntu's nginx 1.24 has its HTTP/3 module and Ubuntu's curl 8.5 can speak it is unchecked; `csa.net.congestion` must find out).

## 4. The labcheck change: shared bases (platform work N1)

Today every lab's Dockerfile starts `FROM ubuntu:24.04` and Docker's cache shares identical layers. That works for the build time, but a network kit of about twelve files copied into some 75 lab folders is 900 copies to keep identical. The smallest change that avoids it, prototyped and used for every contract run above:

- A base lives in `content/lab-bases/<name>/` (a Dockerfile and its files).
- `build_image` reads the lab's Dockerfile; if it has `FROM lab-base-<name>`, it first runs `docker build -t lab-base-<name> content/lab-bases/<name>`. With nothing changed that is a cache hit of about a second, so the base is always the one in the checkout, with no version number to keep in step. The diff is `prototypes/network-lab-base/labcheck-shared-base.diff`:

```python
LAB_BASES = ROOT / "content" / "lab-bases"
BASE_FROM = re.compile(r"^FROM\s+lab-base-([a-z0-9-]+)\s*$", re.MULTILINE)


def base_of(lab: Lab) -> str | None:
    found = BASE_FROM.search((lab.folder / "Dockerfile").read_text(encoding="utf-8"))
    return found.group(1) if found else None


def build_base(name: str, quiet: bool = True) -> None:
    folder = LAB_BASES / name
    if not (folder / "Dockerfile").exists():
        raise LabError(f"no lab base called {name} (expected {folder.as_posix()})")
    args = ["build", "-t", f"lab-base-{name}", str(folder)]
    if quiet:
        args.insert(1, "-q")
    docker(*args, timeout=BUILD_TIMEOUT_SECONDS)


# ...and in build_image, before building the lab:  base = base_of(lab); if base: build_base(base, quiet)
```

- `warm_images` already builds the first lab of each topic one at a time before a parallel run, so each CI shard builds the base once, then everything comes from its cache. Concurrent `docker build -t lab-base-net` calls with a warm cache only re-tag.
- **Also needed:** the validator checks that a `FROM lab-base-<name>` names an existing folder; `.github/workflows/labs.yml` adds `content/lab-bases/**` to its paths (a workflow change: the owner's `gh` token lacks the workflow scope, so the branch must already hold `main`'s version of the file before merging, per the standing note); `content/README.md` gets a "network lab" section from sections 2, 5 and 9 of this brief; tests for `base_of` and `build_base` in `tools/tests/`.
- **ADR:** an amendment to ADR-0018 (Proposed): "A lab may start from a shared base in `content/lab-bases/<name>/`, which the checker builds first; a base is still built locally from the content folder, so section 2's 'images are built locally' holds." The weekly from-nothing run covers the base as it covers every image.

A named BuildKit context (`--build-context`) was the alternative: it shares files but not the two package layers, so every lab would still repeat the `RUN` lines.

## 5. What works in namespaces on Docker Desktop, and on CI

Everything in this table was tried in the prototype on 2026-11-11 except where the last column says otherwise. Modules load on demand: a privileged container's request makes the kernel of Docker's machine load a module (`ip_vti`, `ip_gre`, `sch_netem`, `tcp_bbr` and others were loaded this way), so nothing is loaded by hand. GitHub's runner image `ubuntu-24.04` (20261101) uses kernel `7.0.0-1017-azure` and Docker 28.0.4; **nothing here has run on a runner yet** (platform work N3).

| Feature | Kernel needs | Docker Desktop (6.18 WSL2) | Notes, workaround |
| --- | --- | --- | --- |
| veth links, bridges in a `switches` namespace | veth, bridge | works | |
| IPv4 forwarding, static routes from FRR's `staticd` | `ip_forward` per namespace | works | set explicitly (section 2.2) |
| OSPF (`ospfd`) | multicast on veth | works: route in the kernel 6.1 s after FRR starts | use `ip ospf network point-to-point` on /30 links and `hello-interval 1`, `dead-interval 4`; on the default broadcast type the first try hadn't converged after 37 s |
| BGP (`bgpd`), IPv4 | TCP | works: established and routes installed within the solution's 7 s | `timers bgp 3 9` and `timers connect 5` on both sides; FRR's default "traditional" profile requires route-maps on eBGP (RFC 8212), a teaching point |
| BGP over IPv6, OSPFv3 | | not tried | |
| IPv6 dual stack, forwarding, no NAT on IPv6 | IPv6 per namespace (reset to enabled in a new namespace) | works | an IPv6 check saw the office's own address at the load balancer |
| IPv6 SLAAC from FRR router advertisements | `accept_ra` on the host | works: address and default route within 2 s | `no ipv6 nd suppress-ra`, `ipv6 nd prefix ...` in FRR |
| IKEv2 with strongSwan (`charon-systemd`, `swanctl`) | UDP 500/4500 | works: IKE SA and CHILD SA in about 1.6 s | with MOBIKE on (the default), IKE moves to UDP 4500 even with no NAT between the peers |
| IPsec, policy-based, tunnel mode | `xfrm_user`, `esp4` | works | |
| IPsec, GRE protected by a tunnel-mode SA (`local_ts = A/32[gre]`) | plus `ip_gre` | **works**, contract kept, 3 learner runs of 3 passed | the route-based design for `csa.net.ipsec` (section 6.2) |
| IPsec with VTI interfaces (`mark_in`, `mark_out`) | `ip_vti` | **fails**: SAs install, traffic goes out as ESP, every packet is dropped on arrival (`XfrmInTmplMismatch` in `/proc/net/xfrm_stat`) | hand-made SAs and policies over the same VTI devices work; replacing strongSwan's SAs or policies one kind at a time didn't help; cause not found (open question 1) |
| IPsec with XFRM interfaces (`if_id`) | `xfrm_interface` | **fails**: `ip link add ... type xfrm` says "Unknown device type" | not built into this kernel; Ubuntu's kernels have it as a module (not tried) |
| ESP transport mode | | **fails**, even with hand-made SAs (`XfrmInStateModeError`) | avoid transport mode in every lab |
| nftables, including NAT, in a machine | `nf_tables`, `nf_nat` | works | an SNAT port range needs a protocol match first: `meta l4proto { tcp, udp } snat to 198.51.100.1:40000-40099` |
| conntrack per machine | `nf_conntrack` | works: `on edge conntrack -L` shows the translated ports | |
| `meta ipsec missing drop` (GRE accepted only from inside IPsec) | | works | the cloud side's firewall in `proto-bgp-over-ipsec` |
| tc netem delay and loss | `sch_netem` | works | **delays egress only**: 30 ms on one end added 30 ms to the round trip, not each way |
| Congestion control per machine (CUBIC, BBR) | `tcp_bbr` | works: `reno cubic bbr` available; over 30 ms and 1% loss, iperf3 gave CUBIC 110 Mbit/s and BBR 566 Mbit/s (one run each) | compare ratios in checks, never absolute speeds |
| Path MTU discovery | | works: `tracepath` reports `pmtu 1400`; `ping -M do -s 1472` says `message too long, mtu=1400` | the kernel caches a learned path MTU: flush it between tries |
| tcpdump in a machine | | works | a capture written to a file left by an earlier run came back empty; with `-Z root` (Ubuntu's tcpdump otherwise switches to its own user) and a fresh `mktemp` file it worked every time. The cause wasn't pinned down; `pcap` does both |
| tshark reading a capture | | works: read one DNS question's name out of a capture | prints a "running as root" warning on stderr: `2>/dev/null` |
| BIND (three on one lab), Unbound, `dig +trace` against the lab's own root | | works | **Unbound answers every name under `.test` with NXDOMAIN by itself** (a default local zone, as RFC 6761 asks); the resolver needs `local-zone: "test." nodefault` |
| HAProxy health checks, stats socket | | works | |
| nginx per machine | | works | serve fixed answers (`return 200 "hello from web1\n"`); `/var/www` is shared by all machines |

Two side effects writers must know:

- **Placeholder tunnel interfaces.** Once a tunnel type's module is loaded on Docker's machine, the kernel adds its fallback interface (`gre0`, `gretap0`, `erspan0`, `sit0`, `tunl0`, `ip6tnl0`, `ip6gre0`, `ip_vti0`, `ip6_vti0`) to every new namespace, down and unused (kernel docs, `fb_tunnels_only_for_init_net`, default 0). Which appear depends on what any container has used since Docker started, so it differs between the owner's PC and a runner, and from day to day. **Never compare a whole `ip addr` listing in a check or a fixture**; `netlab show` lists only interfaces that are up; lessons say what the placeholders are.
- **Windows line endings.** A topology saved with CRLF failed on its first line (`$'\r': command not found`); `netlab` now strips carriage returns from the topology. The repository's `.gitattributes` keeps committed files LF, but a file written by Python on Windows outside git gets CRLF.

## 6. Decisions the topics inherit

### 6.1 Addresses and numbers

- Public addresses from the documentation ranges, `192.0.2.0/24`, `198.51.100.0/24` and `203.0.113.0/24` (RFC 5737), and `2001:db8::/32` for IPv6 (RFC 3849); sites and clouds in `10.0.0.0/8`; tunnel inside addresses as a `/30` from `169.254.0.0/16`, which is what AWS's Site-to-Site VPN uses for its inside tunnel addresses.
- Names under `.test` (reserved for testing, RFC 6761), as Module 2's `ad.shop.test`; with Unbound, `local-zone: "test." nodefault`.
- Private AS numbers (64512 to 65534) for every BGP speaker.

### 6.2 The route-based VPN is GRE inside IPsec

On Docker Desktop's kernel, neither of the two interfaces Linux offers for a route-based IPsec VPN works with strongSwan: XFRM interfaces don't exist, and VTI drops everything strongSwan protects (section 5). What works, and kept its contract in the last three contract runs and three learner runs out of three: each gateway has a GRE interface (`gre1`, scenery, made by `tunnel` lines) between the two public addresses; strongSwan protects GRE between those addresses with a tunnel-mode SA (`local_ts = 198.51.100.2/32[gre]`, `remote_ts = 203.0.113.2/32[gre]`); BGP runs between the GRE interfaces' inside addresses, and every route over `gre1` is therefore encrypted. The cloud's side is a responder (`start_action = none`), and its firewall drops GRE that didn't arrive inside IPsec (`ip protocol gre meta ipsec missing drop`), so a GRE tunnel without IPsec never comes up.

An earlier version of the prototype had both sides start the tunnel on demand (`start_action = trap`) and vpn-a's `gre1` made and removed by a strongSwan `updown` script; it failed one contract run in two, because two tunnels negotiated at once and the script took `gre1` away with the loser. Keep the tunnel interfaces as scenery and one side the initiator.

What it costs: the clouds' IPsec VPN gateways negotiate any-to-any traffic selectors (AWS's default is `0.0.0.0/0`, fact 19), so the customer's side is usually a VTI or XFRM interface, not GRE between two addresses. The IKE work (proposals, pre-shared keys, identities, DPD, phase 1 and phase 2 failures), the inside `/30`, BGP over the tunnel and route steering are the same, so the skills transfer; the lesson says in two sentences that in a cloud the tunnel interface is a VTI or XFRM interface and here a GRE tunnel plays its part, and why. Phase 2 debugging still has a traffic-selector mismatch to find. If a later Docker Desktop kernel or a CI spike shows VTI working (open question 1), switching is a change to the topology's `tunnel` lines and the `children` block.

### 6.3 Scenery and the learner's part

A lab says in its prompt which machines are the learner's and which are scenery ("vpn-b stands in for the cloud's VPN gateway and isn't yours"). Scenery files are sealed in the Dockerfile and a check runs `netlab intact`. Where the learner might change a scenery daemon live without touching its file, `frr_saved vpn-b` (running equals file) with `intact` (file equals original) covers FRR; for strongSwan, behaviour checks catch it (a weakened proposal broke the tunnel in `cloud-side-changed.sh`), which is the residual risk.

## 7. How a check reads the real state

`checklib.sh` (sourced as `. /usr/local/lib/netlab/checklib.sh`), all used in the prototype's checks:

| Helper | What it reads |
| --- | --- |
| `frr M 'show ... json'` | FRR's own answer: `show bgp neighbors X json` (`bgpState`, `remoteAs`), `show ip route P json` (`protocol`, `selected`, `nexthops[].interfaceName`) |
| `json EXPR` | JSON on stdin as `d`, via `python3` (no `jq` in the labs) |
| `wait_for SECONDS CMD` | retries once a second, for something that needs a moment after boot |
| `tcp_state FROM HOST PORT` | `open`, `refused` or `dropped`, by timing `nc -z -w 2` (Module 1's rule: a reset comes back in milliseconds, a drop takes the timeout) |
| `pcap M IF FILTER SECONDS -- CMD` and `capture ...` | a capture on one machine while another acts; the file for `tshark -r`, or the packets as `tcpdump -r` prints them |
| `frr_saved M` | FRR's running configuration equals `/etc/frr/frr.conf` (from `frr version` on, without `!` and `end`), so a restart brings the same routing back; prints the difference otherwise |
| `intact` | the sealed scenery is unchanged |

And the kernel's own state, from the lab machine: `ip -j -n M route` (its `protocol` is `bgp`, `ospf`, `static` for FRR's static routes, `kernel` for connected ones, and **absent for a route typed by hand with `ip route add`**, tried), `ip -j -n M addr`, `on M ip xfrm state` (no JSON in iproute2 6.1; count `src A dst B` lines), `on M ss -tanH`, `on M conntrack -L`, `on M nft -j list ruleset`, `on M tc -j qdisc`, `on M sysctl -n`. Daemons: `on resolver unbound-control ...`, `on lb1 sh -c 'echo "show stat" | socat stdio /run/haproxy/admin.sock'` (status is the 18th comma-separated field counting from 1), `dig @server`, `on M rndc status`, `on M swanctl --list-sas`.

### 7.1 The shortcuts every network lab must reject

| Shortcut | Caught by | Prototype |
| --- | --- | --- |
| Configured live in `vtysh`, never saved | `frr_saved` | `not-saved.sh` fails only `saved` |
| A route typed with `ip route add` on a router | the route's `protocol` in `ip -j route`, or FRR's `protocol` | tried by hand |
| A static route where the lab asks for BGP or OSPF | `protocol` must be `bgp` or `ospf` | `static-route.sh` fails `bgp-up`, `learned-by-bgp`, `hosts-reach` |
| The other side's configuration changed to match a mistake | `netlab intact`, plus behaviour | `cloud-side-changed.sh` |
| Encryption left out (`gre-in-the-clear.sh`), a firewall opened wide, a filter set to permit everything | a capture on the path (`encrypted`: ESP only, no ICMP or GRE), `tcp_state` on ports nobody asked for, the peer offering a prefix that must be refused | `gre-in-the-clear.sh` fails five checks |
| A name typed into `/etc/hosts` or `resolv.conf` pointed straight at an authoritative server | ask through the resolver, and see the resolver's own question in a capture on it | `resolv-direct.sh` fails `trace` and `tshark-decodes` |
| A kernel setting changed live (`sysctl -w`, `tc` by hand, `ip link set mtu`) that a reboot loses | compare with where the lab says it lives (the topology is scenery; a learner's lasting kernel setting needs a home, open question 5), and the restart trial | not built |

## 8. What the module's first lab must teach

`csa.net.layers` owns the first network lab, and its worked example teaches the lab layout before anything else. Terms to define there (with where the track taught the rest): **machine** in this lab (a network namespace with its own `/etc`, `/run` and name; namespaces and veth pairs: `csa.linux.net-tools`, `csa.linux.containers`), **switch** (a bridge), **topology file**, **scenery**, `on`, `netlab show`, per-machine services (`systemctl status frr@r1`; units: `csa.linux.services`), and the placeholder interfaces. A "Before your first network lab" note at the top of that prompt (`content/README.md`'s rule for a track's first lab) says: the lab is one container holding several machines; the lab machine is the console and is on none of their networks; `on MACHINE` is how to reach one; files outside each machine's `/etc` are shared. Prompts always give a machine's files by their path inside it (`on r1 nano /etc/frr/frr.conf`), never `/etc/netns/r1/...`.

The worked example's steps: `netlab show`; `cat /etc/netlab/topology`; `on host-a ip -br addr`; `on host-a ping` a machine two hops away; `on r1 tcpdump -nn -i eth1` while it does; `systemctl status frr@r1`; `on r1 vtysh -c 'show ip route'`. About 10 minutes on top of the topic's own content.

## 9. Timings and CI cost

| What (owner's PC, 2026-11-11) | Time |
| --- | --- |
| Base, layer 2 (first build, layer 1 cached) | 42 to 53 s |
| A lab's own image on the base | about 3 s |
| Boot to `running`, 5 machines, 4 services | 2.2 to 3.3 s |
| `labcheck start` (cached build and boot), 5 machines | 7.4 to 9.1 s; 9 machines 9.0 s |
| FRR start (`systemctl start frr@r1 frr@r2 frr@r3`) | 0.26 s |
| IPsec passing traffic after `systemctl restart strongswan@...` | 1.6 s |
| BGP-over-IPsec solution applied and converged | 6.7 to 7.6 s (3 runs) |
| OSPF, three routers, route in the kernel | 6.1 s |
| `labcheck check`, 7 checks (BGP lab) / 8 checks (services lab, with a 4 s capture and tshark) | 6.8 to 7.7 s / 10 to 11 s |
| Restart trial: `docker restart` to booted, then to traffic flowing | 2.2 s + 5.7 s; every check passed (both labs) |
| Full contract, BGP lab (pristine, solution, 4 wrong fixes: 6 container runs) | 280 to 382 s |
| Both prototype labs, `test --all --jobs 2` | 304 s |

Most of a contract run is checks waiting for things that will never happen: in a failing run, each check's `wait_for` runs to its limit. **The rule for writers: one check waits for convergence, with a limit (30 s for BGP, 15 s for IPsec); every later check reads at once.** With it, a failing run takes about 25 s instead of about 60. Use fast timers in scenery (BGP `timers bgp 3 9`, `timers connect 5`; OSPF point-to-point, hello 1, dead 4) and say in the lesson what the defaults are and why the lab differs.

**CI.** About 75 Module 3 labs at an average of five container runs of about 40 s each is about 4.2 hours of container time per full run. Spread over today's 4 shards with 4 labs at a time, that adds about 16 minutes a shard to today's 20, if a 4-CPU runner keeps four network labs at full speed, which nobody has measured. Each shard also builds the base once (about a minute). **Recommendation: raise the shards from 4 to 8 when Module 3's labs land** (public repository runners are free), and keep wrong fixes to what the checks need.

## 10. Platform work, in order

| # | What | Smallest version | ADR | Blocks |
| --- | --- | --- | --- | --- |
| N1 | Shared lab bases | Section 4: `content/lab-bases/net/` from the prototype, the 29-line `labcheck.py` change and its tests, the validator's base-exists rule, `labs.yml` paths, a README section | ADR-0018 amendment (Proposed) | every Module 3 lab |
| N2 | The restart trial in the contract | an opt-in `lab: { restart_trial: true }` in `exercise.yaml` (`content_model.LabOptions`); `test_lab` then, after the solution passes, runs `docker restart`, waits for the boot and runs the checks again, which must all pass. About 15 s a lab. Rule 3 becomes something CI proves, not something an author remembers | ADR-0018 amendment, same one | nothing; every Module 3 lab should opt in |
| N3 | A CI spike | one early pull request carrying the base and the two prototype labs, to read on GitHub's runner: the contracts, the timings with 4 labs at a time, which modules load, and whether strongSwan with VTI works on kernel 7.0 (if it does, the gap is Docker Desktop's alone) | none | `csa.net.ipsec`, `csa.net.bgp`, `csa.net.congestion`, the checkpoint; the shard count |
| N4 | Mask the plain daemon units; check the base on the next Docker Desktop kernel | one `systemctl mask` line; re-run section 5's table after a Docker Desktop update | none | nothing |

## 11. Verified facts

Each was read on 2026-11-11 unless it says "observed", which means seen in the prototype that day with the command given.

| # | Claim | Source |
| --- | --- | --- |
| 1 | FRR's `bgp ebgp-requires-policy` is on by default in the traditional profile and off in datacenter; without filters "no routes will be accepted" / "no routes will be announced" (RFC 8212) | https://docs.frrouting.org/en/latest/bgp.html, "Require policy on EBGP" |
| 2 | FRR profiles: `traditional` (IETF and internet practice) and `datacenter` (aggressive timers); FRR uses one integrated file, `/etc/frr/frr.conf`; `-N` adds a `/<namespace>` to state paths | https://docs.frrouting.org/en/latest/basic.html, "Profiles", "Integrated Config File", "Common Invocation Options" |
| 3 | FRR 8.4.4 ships `frr@.service`, which runs `frrinit.sh start %I` with a pathspace, not in a network namespace | observed: `/usr/lib/systemd/system/frr@.service`, `/usr/lib/frr/frrcommon.sh` |
| 4 | The default BGP advertisement interval in FRR's docs is 0; the docs page read doesn't state keepalive, hold or connect defaults | https://docs.frrouting.org/en/latest/bgp.html, `neighbor PEER advertisement-interval` |
| 5 | VTI devices since Linux 3.6 with important changes in 3.15; XFRM interfaces since 4.19 (strongSwan 5.8.0+, iproute2 5.1.0+); for VTI set `charon.install_routes = 0` and `disable_policy=1` on the device | https://docs.strongswan.org/docs/latest/features/routeBasedVpn.html |
| 6 | swanctl: `mode` defaults to tunnel; `start_action` none, trap or start; `mark_in_sa` defaults to no; protocol selectors in square brackets; `mobike` defaults to yes; `dpd_action` defaults to clear | https://docs.strongswan.org/docs/latest/swanctl/swanctlConf.html |
| 7 | `ip netns exec` makes a mount namespace and binds the files in `/etc/netns/NAME/` over their usual places; named namespaces are at `/var/run/netns/NAME` | https://man7.org/linux/man-pages/man8/ip-netns.8.html |
| 8 | `devconf_inherit_init_net` default 0: a new namespace inherits IPv4 settings from init_net and resets IPv6 to defaults | https://docs.kernel.org/admin-guide/sysctl/net.html |
| 9 | `fb_tunnels_only_for_init_net` default 0: fallback tunnels (tunl0, gre0, gretap0, erspan0, sit0, ip6tnl0, ip6gre0) are created in every namespace when the module loads | https://docs.kernel.org/admin-guide/sysctl/net.html |
| 10 | `rp_filter` 0 none, 1 strict, 2 loose (RFC 3704) | https://docs.kernel.org/networking/ip-sysctl.html |
| 11 | On Docker Desktop a new namespace starts with `ip_forward=1`, `rp_filter=2`, IPv6 enabled and IPv6 forwarding 0 | observed: `ip netns exec a sysctl ...` in a privileged container |
| 12 | Docker Desktop's kernel `6.18.33.2-microsoft-standard-WSL2` has no XFRM interface device ("Unknown device type"); VTI, VTI6, GRE, VXLAN, WireGuard, IPIP, SIT, VRF, dummy and bridge devices can be made | observed: `ip link add ... type xfrm|vti|...` |
| 13 | Unbound's default local zones include `test`, `invalid`, `onion`, `home.arpa`, localhost and AS112 zones; `nodefault` turns a default off | https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html, `local-zone` |
| 14 | RFC 6761: resolvers and authoritative servers should by default give immediate negative answers for names under `test.` | https://www.rfc-editor.org/rfc/rfc6761.html, section 6.2 |
| 15 | nftables `meta ipsec`: true if the packet was IPsec-encrypted (the obsolete keyword was `secpath`) | https://wiki.nftables.org/wiki-nftables/index.php/Matching_packet_metainformation |
| 16 | netem's examples delay packets "going out on device eth0"; delay and loss syntax | https://man7.org/linux/man-pages/man8/tc-netem.8.html |
| 17 | HAProxy `show stat` on the stats socket gives CSV; field 17 (counting from 0) is `status` (UP, DOWN, MAINT ...) | https://docs.haproxy.org/2.8/management.html, section 9.1 |
| 18 | nginx's active health checks (`health_check`) are in the commercial subscription only | https://nginx.org/en/docs/http/ngx_http_upstream_hc_module.html |
| 19 | AWS Site-to-Site VPN: inside tunnel addresses are a /30 from `169.254.0.0/16`; traffic selectors default to `0.0.0.0/0`; a tunnel's `StartupAction` can be `start` | https://docs.aws.amazon.com/vpn/latest/s2svpn/SetUpVPNConnections.html, step 5 |
| 20 | GitHub's `ubuntu-24.04` runner image 20261101.360.1: kernel `7.0.0-1017-azure`, Docker 28.0.4 | https://raw.githubusercontent.com/actions/runner-images/main/images/ubuntu/Ubuntu2404-Readme.md |
| 21 | Package versions in Ubuntu 24.04 (FRR 8.4.4, strongSwan 5.9.13, BIND 9.18.39, Unbound 1.19.2, nginx 1.24.0, HAProxy 2.8.30, tshark 4.2.2, iperf3 3.16) | observed: `apt-cache policy` in `ubuntu:24.04` |
| 22 | strongSwan + VTI: `XfrmInTmplMismatch` on the receiver; hand-made SAs over the same VTIs work; ESP transport mode fails with `XfrmInStateModeError`; GRE inside a tunnel-mode SA works | observed: `/proc/net/xfrm_stat`, five swap experiments, section 5 |
| 23 | A route added with `ip route add` has no `protocol` in `ip -j route`; FRR's static route has `static`, OSPF's `ospf`, BGP's `bgp` | observed |
| 24 | The documentation address blocks (RFC 5737, RFC 3849) | known standards; the RFCs were not re-opened for this brief |

Where sources disagree or I couldn't confirm: the FRR docs page didn't give BGP timer defaults (the lab sets its own, so nothing depends on them); AWS's page doesn't state the default Amazon-side ASN, so the prototype says only "a private AS number"; nobody has run any of this on a CI runner.

## 12. References for writers

These are for the authors of Module 3's labs; each topic picks its learners' resources itself. All linked, never copied.

| Title | URL | Type | Licence | Minutes | Use | Checked |
| --- | --- | --- | --- | --- | --- | --- |
| FRRouting User Guide: BGP | https://docs.frrouting.org/en/latest/bgp.html | reference | FRR project docs; licence not stated on the page | reference (very long) | configuration, `show ... json` | 2026-11-11 |
| FRRouting User Guide: Basic commands | https://docs.frrouting.org/en/latest/basic.html | reference | as above | 20 | profiles, integrated config, `-N` | 2026-11-11 |
| strongSwan: Route-based VPNs | https://docs.strongswan.org/docs/latest/features/routeBasedVpn.html | reference | not stated on the page | 10 | VTI and XFRM interfaces, marks | 2026-11-11 |
| strongSwan: swanctl.conf | https://docs.strongswan.org/docs/latest/swanctl/swanctlConf.html | reference | not stated on the page | reference | every setting the labs use | 2026-11-11 |
| ip-netns(8) | https://man7.org/linux/man-pages/man8/ip-netns.8.html | man page | iproute2 project; linked | 8 | `/etc/netns` overlay | 2026-11-11 |
| Linux kernel: sysctl net and ip-sysctl | https://docs.kernel.org/admin-guide/sysctl/net.html, https://docs.kernel.org/networking/ip-sysctl.html | reference | Linux kernel documentation; linked | reference | inherited settings, rp_filter | 2026-11-11 |
| unbound.conf(5) | https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html | reference | NLnet Labs; linked | reference | local zones, remote control | 2026-11-11 |
| HAProxy 2.8 Management Guide | https://docs.haproxy.org/2.8/management.html | reference | HAProxy docs; linked | reference | stats socket, `show stat` | 2026-11-11 |
| tc-netem(8) | https://man7.org/linux/man-pages/man8/tc-netem.8.html | man page | linked | 10 | delay, loss | 2026-11-11 |
| nftables wiki: matching packet metainformation | https://wiki.nftables.org/wiki-nftables/index.php/Matching_packet_metainformation | reference | wiki; linked | 10 | `meta ipsec`, `meta l4proto` | 2026-11-11 |

## 13. Cost and time

- **Money:** none. Everything runs in the lab container; no lab reaches a cloud or the internet.
- **Learner time:** the first Module 3 lab builds the base once (about a minute on this PC, with Module 1's layer already cached); the "Before your first network lab" note and the worked example's layout steps add about 10 minutes to `csa.net.layers`; later labs start in under 10 s.
- **Disk:** about 520 MB for the base (Docker Desktop reports 688 MB), shared by every Module 3 lab; each lab adds kilobytes.
- **CI:** section 9.

## 14. Open questions, each with a recommendation under the owner's rule

1. **VTI with strongSwan on Docker Desktop.** Is it a bug of this kernel, or something in strongSwan 5.9.13's SAs? *Recommendation:* teach and prove with GRE inside a tunnel-mode SA now (it works, it's free, the IKE skills are the same), explain the difference from the clouds' VTI-style interfaces in the lesson, and let N3 run the VTI variant on a runner; if a later Docker Desktop kernel fixes it, switch the `tunnel` lines and `children` block then. Best learning experience is a lab that works on the learner's machine.
2. **The restart trial in CI (N2).** *Recommendation:* yes, opt-in, every Module 3 lab opts in. Retention comes from fixes that last; about 15 s a lab and free.
3. **Keep tshark in the base?** *Recommendation:* keep. Six topics read handshakes and protocol fields in captures, and a decoded field is the most direct "real state" a check has; the cost is about 125 MB once and 15 to 20 s of build, free.
4. **FRR 8.4.4 or FRR's own repository (10.x)?** *Recommendation:* Ubuntu's 8.4.4: no extra package source, covered by Ubuntu's security updates, and everything Module 3 needs is there. Revisit only if a topic needs a feature 8.4 lacks.
5. **Where does a learner's lasting kernel setting live** (an MTU fix, a sysctl on a host)? The topology is scenery, and a router's settings belong in its daemons. *Recommendation:* a per-machine `/etc/sysctl.d/` and an `interfaces`-style file are new inventions; instead, a lab that needs one makes that machine run FRR (whose interface and route settings persist) or gives it `nftables@`, and the MTU topic's fix lives where the lab says (for example on the router's FRR interface, or as scenery the learner reports rather than changes). Ask `csa.net.layers`' and `csa.net.troubleshooting`'s designers which they need; add a word to `netlab` only for a real case.
6. **Four or eight CI shards.** *Recommendation:* eight when Module 3's labs land; free on a public repository, and it keeps a pull request's Labs job near 20 minutes.
7. **Mask or disable the plain daemon units on the lab machine.** *Recommendation:* mask (N4): a learner following an internet tutorial (`systemctl restart frr`) gets a clear refusal instead of an FRR on the console.

## 15. Docker cleanup

Created and removed during the prototype: images `netlabbase-pkgprobe`, `netlabbase-base:proto`, `netlabbase-lab1`, `netlabbase-dbg`, `lab-base-net`, `lab-csa.net.netlab-proto-proto-bgp-over-ipsec:r1`, `lab-csa.net.netlab-proto-proto-services:r1`; containers `netlabbase-probe`, `netlabbase-c1`, `netlabbase-ospf`, `netlabbase-p2`, `netlabbase-p3`, and the labcheck containers `lab-csa.net.netlab-proto-*` (and their `-test` copies, removed by `labcheck test` itself). No Docker network was created. Nothing was pruned and nothing belonging to anyone else was touched (other designers' `m3lbipsec-pkg`, `frrproto-*`, the existing `lab-csa.*` images and `vincit-itest-pg` were left alone). What remains: BuildKit's cache entries for the layers built (removable only by a prune, which the rules forbid), and the kernel modules the labs loaded on Docker's machine (`ip_vti`, `ip_gre`, `sch_netem` and the like), which stay until Docker Desktop restarts and are harmless.

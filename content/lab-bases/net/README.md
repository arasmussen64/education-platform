# The network-lab base

Every network lab (the Cloud Solutions Architect track's Module 3, and later modules that need several machines) starts `FROM lab-base-net`. This folder is that image. `tools/labcheck.py` builds it, tagged `lab-base-net`, before it builds any lab whose `Dockerfile` says `FROM lab-base-net`, for `start` and `test` alike (`check` builds nothing: it runs the checks in the lab that `start` made) ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), third amendment). When nothing here has changed, Docker's cache makes that a second or two.

Read this before writing a network lab. The plan behind it is [docs/plans/cloud-module-3/MODULE-3-BRIEF.md](../../../docs/plans/cloud-module-3/MODULE-3-BRIEF.md), sections 3.5 and 4.

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 1 | The systemd labs' first `RUN`, byte for byte | Shared with every systemd lab, so Docker builds it once. Change it only with all of them. |
| 2 | FRRouting 8.4, strongSwan 5.9 (`swanctl`, standard plugins only), BIND 9.18, Unbound 1.19, nginx 1.24, HAProxy 2.8, radvd, ipcalc, sipcalc, tshark, iperf3, mtr, tracepath, arping, ethtool, socat, openssl, rdisc6 | All from Ubuntu 24.04's archive. Each package's own service is switched off. |
| 3 | `netlab` and its helpers, `on`, the per-machine units, the check helpers, and the helpers a learner runs | Small; rebuilt in a moment when one of these files changes. |

Not in it: `jq` (checks read JSON with `python3`, through `json` below), `gawk` (`awk` is Ubuntu's mawk in every lab), and anything from outside Ubuntu's archive. A topic that needs one more package (congestion's Caddy, certificates' certbot) adds a second `RUN` after `FROM lab-base-net`, identical in all that topic's labs so Docker shares it.

strongSwan's `forecast` plugin makes a VTI tunnel drop every packet that arrives (`XfrmInTmplMismatch`; the Module 3 critic found it). The base leaves out the extra plugins package that the prototype had, but `strongswan-pki` still brings `libcharon-extra-plugins`, which has `forecast` and switches it on, so `/etc/strongswan.d/netlab.conf` switches it off again (and sets `install_routes = no`) for every machine that runs strongSwan. `/etc/strongswan.d/swanctl.conf` lists the plugins `swanctl` loads, which keeps it from printing a dozen "failed to load" lines.

## A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { init: systemd, restart_trial: true }
├── Dockerfile         the four lines below
├── topology           the network, in netlab's words
├── machines/<m>/...   each machine's own /etc files: machines/r1/frr/frr.conf,
│                      machines/r1/sysctl.d/90-forward.conf, machines/vpn/network/up ...
├── checks.yaml  solution.sh  wrong/*.sh
```

```dockerfile
FROM lab-base-net
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf
```

`netlab enable` gives each machine its own copy of what its services need (the package's defaults fill the gaps around the lab's own files), makes every machine its own `/etc/sysctl.d/` and `/etc/network/`, and enables each service as `name@machine`. `netlab seal FILE...` records the scenery's checksums for `intact`. Every Module 3 lab sets `restart_trial: true` (below).

## Machines

A **machine** is a network namespace (its own interfaces, addresses, routes, firewall and ports), with its own `/etc` for each program it runs, its own `/run`, its own state folders and its own name: the prompt reads `root@r1`. Its files live on the lab machine in `/etc/netns/<m>/`, which `ip netns exec` lays over `/etc`, so **inside the machine every program uses its normal paths**. Prompts always give a machine's files by their path inside it (`on r1 nano /etc/frr/frr.conf`), never `/etc/netns/r1/...`.

`on MACHINE [COMMAND...]` makes the learner root on a machine, as an administrator logged in to it (`on r1 vtysh`, `on office curl http://www.shop.test/`); with no command it opens a shell there. `netlab show` lists the machines, what each runs, and their interfaces that are up.

The **lab machine** (the container itself) is the console: it is on no lab network. Switches (bridges) live in a namespace of their own, `switches`, so `on switches tcpdump -i office` works like a switch's mirror port. **No machine reaches the real internet**: a lab that needs "the internet" builds a small one (an ISP router, root and TLD name servers).

A machine has its own copy of a file only when it has one in `/etc/netns/<m>/`: the lab gave it one (`machines/<m>/...`), or `netlab enable` copied the package's defaults there for a service the topology `run`s on it, or it is the `sysctl.d/` and `network/` every machine gets. Anywhere else, a program on the machine reads, **and writes**, the lab machine's own file, shared by every machine without a copy. So when a learner is to set up something the topology doesn't `run` there (a firewall they enable themselves with `systemctl enable --now nftables@gw`), give the machine its file: `machines/gw/nftables.conf`, even if it only says `flush ruleset`.

A machine's own file that sits straight in `/etc` (`nftables.conf`, `radvd.conf`, `hosts`, `resolv.conf`) is one file laid over the lab machine's, and the kernel won't let a program replace it: `sed -i`, which writes a new file and renames it over the old one, stops with `Device or resource busy`. Programs that write into the file work: nano, `tee`, a shell's `>`. So prompts say `on gw nano /etc/nftables.conf`, a solution writes the whole file with `on gw tee /etc/nftables.conf <<'EOF'`, and a `wrong/*.sh` may use `sudo sed -i` on the lab machine's path, `/etc/netns/gw/nftables.conf`. Files inside a machine's own folders (`/etc/network/up`, `/etc/sysctl.d/`, `/etc/frr/`) aren't affected.

What a machine doesn't have, which the first lesson says plainly: its own systemd (its services are units on the lab machine, `systemctl status frr@r1`, and their logs are in the lab machine's journal, `journalctl -u frr@r1`), its own process list (`ps` shows every machine's processes), and its own files outside the folders above (`/tmp`, `/home`, `/root` and the users are shared by all machines). Never use a file in `/tmp` as a machine's private state.

Names: machines up to 8 characters, lans up to 15, `machine.interface` up to 15 (the kernel's limit on an interface name). `switches` and names starting `chk-` are netlab's own. A machine's name is also a folder in the repository (`machines/<name>/`), so it can't be one of Windows' reserved device names (`con`, `prn`, `aux`, `nul`, `com1` to `com9`, `lpt1` to `lpt9`): git on Windows can't check such a folder out, though Docker builds it.

## The topology file

`/etc/netlab/topology` is bash calling ten words, one a line, so it reads as the network diagram in text. It is scenery: seal it.

```bash
machine r1 router                    # a machine; a router forwards IPv4 and IPv6
machine host-a                       # a host doesn't, and takes router advertisements
link r1:eth1=10.0.12.1/30,2001:db8:12::1/64 r2:eth1=10.0.12.2/30   # a cable (veth pair)
lan office r1:eth2=10.1.0.1/24 host-a:eth0=10.1.0.10/24            # a switch
route host-a default via 10.1.0.1    # a host's route (a router's routes belong in FRR)
dns host-a 10.1.0.53                 # resolv.conf, written afresh at every boot, as DHCP would
sysctl r1 net.ipv4.conf.all.rp_filter=1
netem isp eth2 delay 20ms loss 1%    # delay and loss on one end of a link (egress only)
mtu r1 eth1 1400
tunnel cloud vti0 vti local 203.0.113.2 remote 198.51.100.2 key 7 addr 169.254.10.2/30
run r1 frr                           # services: frr strongswan named unbound nginx haproxy nftables radvd web-svc
```

At every boot `netlab up` sets every kernel setting a lab depends on explicitly, in every machine, because a new namespace copies the settings of the machine Docker runs on and Docker Desktop and a CI runner differ: `ip_forward` and IPv6 forwarding first (1 on a router, 0 on a host), then `rp_filter` 0, redirects off, `accept_dad` 0 (IPv6 addresses usable at once; a lab can turn it back on with a `sysctl` word), `accept_ra` off on routers, the ephemeral port range 32768 to 60999, CUBIC and `ping_group_range`. IPv6 addresses are added `nodad`. A `tunnel` line of type `vti` also sets the tunnel's `disable_policy`.

**MAC addresses are not fixed:** each boot's new cables get new random ones, as new virtual NICs do. A lab can rely on that (a pinned MAC goes stale at the next boot).

## A machine's lasting settings: sysctl.d and the network file

These are the machine's own configuration, which a lab may give the learner. They last because they are files on the machine, and they come back at every boot and at `sudo netlab restart`. Order at boot: the topology, then each machine's `sysctl.d`, then its network file, then (after `netlab.service`) its services.

- **`/etc/sysctl.d/*.conf`**, the machine's kernel settings (`net.ipv4.ip_forward = 1`). Applied after the topology's, in name order, later files winning, as `systemd-sysctl` does on a server. **Only keys under `net.`** belong to a machine: anything else (`kernel.*`, `fs.*`, which belong to Docker's whole machine) is left out, with a line in `journalctl -u netlab`. Never run `sysctl --system` inside a machine: it also applies `/usr/lib/sysctl.d`'s global keys. A setting for an interface the network file makes (`net.ipv4.conf.vti0.disable_policy`) is tried again once the file has run, as a server's udev does when an interface appears.
- **`/etc/network/up`**, commands (usually `ip` commands) run inside the machine at boot: its own addresses, neighbours, link states, tunnels and routes. It stops at the first command that fails, and the journal says which line (`netlab: r1: /etc/network/up stopped at line 4: ...`); the rest of the network still comes up, as a server still boots with one interface misconfigured.

`sudo netlab restart` rebuilds the network as a reboot would: every machine's services stop (they are `PartOf=netlab.service`), the network is built again from the topology and the machines' files, and every enabled service starts again. A service started by hand and not enabled stays stopped, as after a reboot.

## Services: name@machine

Each daemon runs as a systemd unit per machine on the lab machine, all after `netlab.service` and `PartOf` it:

| Unit | Runs, inside the machine | Its files |
| --- | --- | --- |
| `frr@M` | FRR's daemons, as `/etc/frr/daemons` switches on | `/etc/frr/frr.conf`; `systemctl reload` is FRR's own reload |
| `strongswan@M` | `charon-systemd`, then `swanctl --load-all` | `/etc/swanctl/`; `/run/charon.vici` is the machine's |
| `named@M` | BIND, after `named-checkconf` | `/etc/bind/`, state in `/var/cache/bind` |
| `unbound@M` | Unbound | `/etc/unbound/unbound.conf` |
| `nginx@M` | nginx, after `nginx -t` | `/etc/nginx/` (`/var/www` is shared by all machines) |
| `haproxy@M` | HAProxy, after `haproxy -c` | `/etc/haproxy/haproxy.cfg`, stats socket `/run/haproxy/admin.sock` |
| `nftables@M` | `nft -f /etc/nftables.conf`, before the machine's other services | the machine's firewall, exactly as Module 1 taught for one server: `systemctl enable nftables@gw` |
| `radvd@M` | radvd, after `radvd --configtest` | `/etc/radvd.conf` |
| `web-svc@M` | the base's test server, `web-svc` (8080 answers with the caller's address, 9000 counts the bytes sent) | none |

So prompts say `sudo systemctl restart frr@r2`, `systemctl reload nginx@web`, `journalctl -u haproxy@lb`.

A unit's journal lines carry its name and machine (`unbound@resolver[812]: ...`), set by `SyslogIdentifier=`; a daemon that logs to syslog itself still uses its own name (`bgpd`, `named`).

**The plain units say what to type.** On the lab machine, `frr.service`, `strongswan`, `named` (and `bind9`), `unbound`, `nginx`, `haproxy`, `radvd` and `nftables` never start their daemon: a habit-typed `sudo systemctl restart frr` fails, systemd points at `systemctl status frr.service`, and that shows "Not on this lab machine: frr runs on each machine, as frr@MACHINE" and the line to type. (`reload` and `enable` on them only say the job doesn't apply; `status` always shows the advice.)

**A lab's own program on a machine** (a stand-in API, a watcher, a timer) is an ordinary unit whose `ExecStart` runs it inside the machine through `lab-enter`, after the network and part of it:

```ini
# /etc/systemd/system/shop-api@.service: the shop's API on a machine, "systemctl status shop-api@app".
[Unit]
Description=The shop's API on %i
After=netlab.service
Requires=netlab.service
PartOf=netlab.service

[Service]
ExecStart=/usr/sbin/ip netns exec %i /usr/local/lib/netlab/lab-enter %i /usr/local/bin/shop-api
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

The lab's Dockerfile copies it and runs `systemctl enable shop-api@app`. A unit for one machine only can be a plain unit (`move-watch.service`) with the machine's name written in. A timer works the same way (`certbot@web.timer` starting `certbot@web.service`). The unit runs with the machine's `/etc`, `/run`, state folders and name, as a daemon there would.

## netlab, the commands

| Command | What it does |
| --- | --- |
| `netlab show` | the machines, what each runs, and their interfaces that are up |
| `sudo netlab restart` | rebuild the network as a reboot would |
| `sudo netlab link M IF down` / `up` | unplug or plug in M's cable on IF; both ends see it at once |
| `sudo netlab link M IF silent` | the cable stays plugged in, but everything M sends over it vanishes as it arrives at the far end (the far machine, or the switch for a lan port): a dead path nothing notices at once |
| `sudo netlab link M IF restore` | plugged in and passing traffic again |
| `sudo netlab verify [M...] [-- COMMAND...]` | build a throwaway copy of every machine from its files, without services, and compare (below) |
| `netlab intact` | `intact`, or the sealed scenery files that changed (and then exits 1) |

`silent` drops arrivals with an nftables table of type `netdev` on the far interface (`netlab_silent_<interface>`); `restore` removes it. On a far machine that is the learner's, their own `nft flush ruleset` or a reload of `nftables@M` would remove it too.

## netlab verify: does the machine equal a fresh build of its files?

It builds a copy of every machine (`chk-r1` and so on) from the topology and the machines' own `sysctl.d`, network file and (where `nftables@M` is enabled) firewall, with no services; compares each machine, or the ones named, with its copy; prints `verified` or the first difference, up to three lines of it, each marked `now:` (only on the running machine) or `from its files:` (only in the fresh build), as in `r2 differs from a fresh build of its files: now: route 10.9.0.0/24 via 10.0.12.1 dev eth1`; and removes the copy. It exits 1 when they differ. With `-- COMMAND`, it runs the command while the copy exists instead of printing `verified`, so a check can probe inside the copy (`netlab verify -- on chk-office ping -c 1 10.0.2.30`); the copy sees each machine's own `/etc`.

What it compares: links (up or down, MTU, the bridge they're in), configured addresses, routes (the kernel's for connected networks, those `ip route add` makes, `proto static`), permanent neighbours, `nft -s list ruleset`, forwarding, and every key the machine's `sysctl.d` sets (a setting changed live that no file names isn't compared: `sysctl_saved` catches that). What it leaves out because it changes every boot or comes from a running program: MACs, link-local addresses, addresses and routes from router advertisements, the kernel's local and broadcast entries, the PMTU cache, placeholder tunnel interfaces, and routes a routing program installed (FRR's, which `frr_saved` covers). So a machine whose addresses FRR configures (`ip address` in `frr.conf`) can't be verified: keep addresses in the topology or the network file.

The copy also proves that a daemon's own configuration lasts, when the daemon has no saved-versus-running helper: start the daemon in the copy from the machine's files, ask it, stop it, and compare with the running one. A fix made only live (with `unbound-control`, say) then fails:

```bash
# Does an Unbound started from the resolver's files answer for the same zones itself?
live=$(on resolver unbound-control list_local_zones | sort)
fresh=$(netlab verify resolver -- bash -c '
  on chk-resolver unbound -d -p > /dev/null 2>&1 &
  for i in $(seq 1 50); do on chk-resolver unbound-control status > /dev/null 2>&1 && break; sleep 0.2; done
  on chk-resolver unbound-control list_local_zones | sort
  on chk-resolver unbound-control stop > /dev/null 2>&1
  wait')
[ -n "$live" ] && [ "$live" = "$fresh" ] && echo saved
```

The daemon started in the copy must be stopped by the same command, before `verify` removes the copy. The same way, charon started on `chk-vpn` from the machine's files shows whether a tunnel begins by itself at boot (`start_action = start`) or was only started by hand with `swanctl --initiate`, which `swanctl --list-conns` can't show (the draft topic `csa.net.base-probes` has both checks, while it exists).

## Check helpers

Checks source `. /usr/local/lib/netlab/checklib.sh` and run as root on the lab machine.

| Helper | What it reads |
| --- | --- |
| `frr M 'show ... json'` | FRR's own answer: `show bgp neighbors X json` (`bgpState`), `show ip route P json` (`protocol`, `selected`, `nexthops[].interfaceName`) |
| `json EXPR` | JSON on stdin as `d`, through `python3` (`json "d['peers']['10.0.0.2']['state']"`) |
| `wait_for TRIES CMD...` | tries CMD up to TRIES times, a second apart, for something that needs a moment after a boot. It counts tries, not seconds: with a command that can block (`curl -m 2`), keep TRIES times (its timeout + 1) under the check's limit (30 s unless it sets `timeout:`) |
| `tcp_state FROM HOST PORT` | `open`, `refused` or `dropped`, by timing `nc -z -w 2` from machine FROM |
| `pcap M IF FILTER SECONDS -- CMD...` | captures on M while CMD runs; prints the capture file's path (read it with `tcpdump -r`, remove it) |
| `capture ...` | as `pcap`, but prints the packets as `tcpdump -nn -r` reads them, and removes the file |
| `frr_saved M` | FRR's running configuration is `/etc/frr/frr.conf`, so a restart gives the same routing; prints the difference otherwise |
| `nft_saved M` | the running firewall is the one M's `/etc/nftables.conf` loads (in a scratch namespace with M's interface names) |
| `sysctl_saved M KEY` | KEY's live value is the one M's `/etc/sysctl.d` gives it (the last file that sets it); a key no file sets fails |
| `hand_routes M` | M's routes typed with `ip route add` (protocol `boot`), one a line, or nothing |
| `bgp-best M PREFIX` | the path BGP chose: `via 192.0.2.2, localpref 100, med 0, path 65010 65100, chosen by Local Pref`, or `none` |
| `intact` | the sealed scenery is unchanged |
| `python3 /usr/local/lib/netlab/cors-verdict PRE ACT ORIGIN METHOD [HEADER] [--credentials]` | what a browser decides about a cross-origin request from the server's two answers (`curl -si` output of the preflight and of the request): `allowed`, or `blocked:` and the Fetch standard's reason; its cases are `tools/tests/test_cors_verdict.py` |

And from `/usr/local/bin`, for learners and checks: `looking-glass M 'show ...'` (FRR's `vtysh` on a router that isn't yours, show commands only), `holdconns N HOST PORT [SECONDS]` (opens N connections at once with one 3-second deadline and holds them; prints `opened X of N`), `holdserver PORT...` (accepts connections, IPv4 and IPv6, and holds each one until the client closes it), `web-svc` (a test server: 8080 answers with the caller's address, 9000 counts the bytes sent).

The kernel's own state, from the lab machine: `ip -j -n M route`, `ip -j -n M addr`, `on M ip xfrm state`, `on M ss -tanH`, `on M conntrack -L`, `on M nft -j list ruleset`, `on M tc -j qdisc`, `on M sysctl -n KEY`. Daemons: `on resolver unbound-control ...`, `on lb sh -c 'echo "show stat" | socat stdio /run/haproxy/admin.sock'` (status is the 18th comma-separated field), `dig @server`, `on M rndc status`, `on M swanctl --list-sas`. Placeholder interfaces make whole interface lists unreliable, so checks name the interface they read.

## Rules for checks and labs on the base

From the Module 3 brief, sections 3.5 and 4.4.

- **Fixes last.** A check that a fix lasts reads the lasting place, never only the live state: `frr_saved` for FRR, `nft_saved` for a firewall, `sysctl_saved` for a kernel setting, `netlab verify` for a network file. Write a `wrong/*.sh` that makes the fix live only, to prove each.
- **The restart trial is in the contract.** Every Module 3 lab sets `lab: { restart_trial: true }`: once the solution passes, `labcheck test` restarts the container and runs every check again.
- **No hand-made routes.** `ip -j route` leaves out the protocol of a route typed with `ip route add`; it shows `"protocol":"boot"` only with `-d`. Use `hand_routes`, or `ip -d -j route`, and reject `boot` on machines whose routes come from FRR.
- **One wait per check run.** One check waits for convergence (30 s for BGP, 15 s for IPsec, 60 s for DNS after a boot); every later check reads at once. Seed fast timers (`timers bgp 3 9`, `timers connect 5`, OSPF hello 1 dead 4) and say in the lesson what the defaults are.
- **No ties decided by time.** Every BGP lab makes the default winner deterministic (`bgp bestpath compare-routerid`, and addresses chosen so the wrong path wins without the learner's change).
- **Never compare whole interface lists.** Placeholder tunnel interfaces (`gre0`, `ip_vti0` ...) appear in every new namespace once their type is in use on Docker's machine, which differs between machines and days.
- **Seed files written by FRR.** Generate every `frr.conf` seed with `write memory` at authoring time, or `frr_saved` fails a pristine router (it compares with what FRR itself writes). FRR writes static routes sorted by prefix length, keeping the file's order within one prefix, so a seed filled in by hand keeps that order.
- **Static routes name their interface** when a wider route covers their next hop. FRR finds a static route's next hop through its own table, so when a cable goes, a summary or blackhole that still covers the next hop's address (not the default route, which next-hop tracking doesn't use) keeps the dead route installed, shown as `(recursive)`. `ip route P NH IFNAME` ties it to the cable (found by the routing topic, 2026-11-12).
- **Read the route, not only the traffic,** where a wrong route can still carry it: with a default route through the backup path, a distance-255 backup passes any reachability test; and of two equal routes for one prefix, the kernel passes over a next hop whose neighbour entry has failed, so a forgotten old route stays wrong while traffic flows. Check the prefix's own kernel route as well.
- **A resolver in front of servers that boot later** sets `infra-host-ttl: 60`, and every Unbound config has `local-zone: "test." nodefault` (Unbound otherwise answers every `.test` name with NXDOMAIN itself).
- **Source ports a check chooses** come from above the ephemeral range (61000 and up), moving with the clock, never reused in a run.
- **A path is proved by traffic**: capture on each outgoing interface; `ip route get` doesn't predict the ECMP path of forwarded connections.
- **A check may cut a link to prove a backup works:** `netlab link` with the restore in an `EXIT` trap, waiting for the primary path to come back before it exits, last in `checks.yaml`, with a `timeout:` of 60 to 90. It changes nothing the learner made and leaves the lab as it found it (the exception to "checks only read" in ADR-0018's third amendment).
- **A check may start throwaway servers, listeners, BIND instances or namespaces of its own** (`chk-...`), and removes them.
- **A unit that failed at boot refuses an immediate restart.** A per-machine unit (`named@`, `unbound@` and the rest) that fails five times in a few seconds hits systemd's start limit, and `systemctl restart` is refused for about ten seconds. A solution or wrong fix that restarts such a unit runs `systemctl reset-failed UNIT` first (`csa.net.dns`' fill-in); a learner, who takes longer than that to fix a file, isn't affected.
- **BIND sends a NOTIFY about 5 s after a zone changes** (`notify-delay`), so a check or script that edits a primary waits for the secondary before it reads it.
- **`netlab verify` removes every `chk-*` namespace**, so a check that makes throwaway machines of its own doesn't run `verify` while they exist.
- **A check may offer a route of its own** to test a filter on routes the learner can't see (ADR-0018's third amendment): a kernel route added on a scenery router that redistributes kernel routes toward the learner through a route map limited to a fixed range (with `set ip next-hop peer-address`, or the learner's router refuses a next hop that is its own address), confirmed as advertised, watched for a few seconds, and removed in an `EXIT` trap. `csa.net.bgp`'s own-space checks are the example.
- **FRR 8.4's habits** (found writing `csa.net.bgp`): a route map edited while in use takes about 5 s to apply, so a solution defines its maps before applying them or waits in a loop; `vtysh` reads commands from standard input (`on edge vtysh <<'EOF' ... EOF`); FRR does send a route back to the peer it learned it from, which drops it as a loop, so a leak shows only for a prefix whose path doesn't hold the receiver's AS; a `network` line for a prefix not in the table shows as `inaccessible`.
- **Scenery the learner mustn't change** (an ISP, the cloud, the other side of a VPN) is sealed and checked with `intact`; a scenery daemon changed live is caught by its behaviour, or by `frr_saved` on it.
- **Addresses:** public ones from RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and `2001:db8::/32`, sites in `10.0.0.0/8`, tunnel inside addresses as `/30`s from `169.254.0.0/16`, names under `.test`, private AS numbers (64512 to 65534).
- **The route-based VPN is a VTI** with `keyingtries = 0` in the learner's connection and the provider's `strongswan@` ordered to start first (a drop-in with `Before=`), or the tunnel doesn't come back after a restart.
- **Windows line endings:** netlab strips carriage returns from the topology and network files; other files in `machines/` are committed with LF (`.gitattributes`).

## Kernel needs

The base asks Docker's machine's kernel for these. Each loads on demand when a privileged container first uses it. Seen on Docker Desktop 29.8.2 (kernel 6.18.33.2-microsoft-standard-WSL2) on 2026-11-11, and on GitHub's `ubuntu-26.04` runner (image 20261101.186.1) on 2026-11-12, where the six probe labs in `csa.net.base-probes` kept their contracts with no `modprobe` step (the CI spike, #253). A row still marked untried falls back to a `sudo modprobe` step in `.github/workflows/labs.yml` if the first lab that needs it fails there.

| Need | Topics | Docker Desktop | GitHub's runner |
| --- | --- | --- | --- |
| veth, bridges, namespaces, per-namespace `ip_forward` and `rp_filter` | all | works | works (every probe) |
| nftables NAT (`nf_nat`, `nft_chain_nat`, masquerade) | NAT, IPv6, transport | works | works (`example-nat-gateway`, `proto-services`) |
| nftables `netdev` ingress (`netlab link ... silent`) | routing, BGP steering, checkpoint part 3 | works | untried: no probe cuts a link |
| `ip_gre` | layers | works | works (`debug-big-downloads-hang`, now `csa.net.layers`' debug) |
| `xfrm_user`, `esp4`, `ip_vti` | IPsec, checkpoint part 3 | works (with the standard plugins only) | works (`proto-bgp-over-vti`) |
| `sch_netem` | transport, congestion, troubleshooting, the `netem` word | works, delays egress only | works (`probe-bbr-throughput`, `proto-services`) |
| `tcp_bbr` | congestion | works, loads from a machine's `sysctl.d` | works: BBR cleared 25 Mbit/s three times (`probe-bbr-throughput`) |
| nftables `reset tcp option window` | transport | works | untried |
| IPv6 in namespaces, forwarding, SLAAC | IPv6, NAT | works | works (`debug-ipv6-half-works`) |
| `fib_multipath_hash_policy` per namespace | routing, checkpoint part 2 | works | untried |

## Files here

| File | What it is |
| --- | --- |
| `Dockerfile` | the image, three layers |
| `netlab` | the engine: the topology's words, `up`, `down`, `restart`, `show`, `link`, `verify`, `enable`, `seal`, `intact` |
| `network-up` | runs a machine's `/etc/network/up` and names the line that fails |
| `machine-state` | a machine's network configuration, normalised, for `netlab verify` |
| `lab-enter` | what makes a namespace a machine: its `/run`, state folders, hostname and no domain name (so FRR never writes `domainname localdomain`) |
| `on` | `on MACHINE [COMMAND...]` |
| `checklib.sh` | the check helpers |
| `not-here`, `plain-units` | the plain daemon units that say what to type |
| `units/` | `netlab.service` and the per-machine units |
| `strongswan.d/` | charon's settings for every machine that runs strongSwan, and swanctl's plugin list |
| `sysctl.d-README` | the note in every machine's `/etc/sysctl.d/` |
| `looking-glass`, `holdconns`, `holdserver`, `web-svc` | helpers in `/usr/local/bin` |

## Size and time

On the owner's PC (2026-11-11): the first build of layer 2 about 45 s, a build with nothing changed about 2 s, a lab's own image on the base a few seconds. Docker Desktop reports the image as 659 MB (467 MB on disk inside it; tshark's library is the largest part, about 125 MB). A five-machine lab boots in 2 to 3 s, `sudo netlab restart` takes 1.5 to 2.5 s, `netlab verify` about 1 s for five machines and 2 to 5 s for nine, and the two probe labs' contract runs, restart trial included, 3 to 4.5 minutes each (2026-11-12: 195 s for the nine-machine one, 258 s for the VTI one). The CI cost is in ADR-0018's third amendment.

# Captured output, troubleshooting and Checkpoint 3 prototypes

Real output of real tools, captured on 2026-11-11 (container clock 2026-11-12 UTC) on Docker Desktop 29.8.2 (Windows, WSL 2), inside the prototype labs in `repo/content/topics/csa.m3tc-proto/exercises/` built on a copy of the network-lab base (`repo/content/lab-bases/m3tc/`, the base designer's prototype unchanged). Label each as **captured** when it is used as a fixture. MAC addresses are random per boot; addresses are the labs' own.

## 1. Checkpoint 3 part 2 (`debug-the-outage`), pristine

### The office monitor, showing all three symptoms that are visible before any fix

`/var/log/shop-monitor.log` (first version of the monitor; its address column was blank on failures, fixed since: it now logs the addresses curl tried):

```
03:18:49 /health  10.20.0.11  200 0.001028 exit=0
03:18:53 /catalog 10.20.0.11  200 2.502829 exit=0      <- tried app2 first, gave up after half of --max-time 5, then app1
03:18:58 /health  10.20.0.11  200 2.501861 exit=0
03:19:00 /catalog 10.20.0.11  200 0.001209 exit=0
03:19:56 /health  10.20.0.11  200 0.000978 exit=0
03:20:01 /catalog 000         3.057818      0 exit=7   <- the resolver's cached answer came from ns2: 10.20.0.13, nobody there
03:20:05 /health  000         1.067335      0 exit=7
03:20:10 /catalog 000         3.075094      0 exit=7
03:20:13 /health  000         1.055840      0 exit=7
03:20:18 /catalog 000         3.080784      0 exit=7
03:20:21 /health  000         1.058630      0 exit=7
03:20:26 /catalog 000         3.079417      0 exit=7
03:20:29 /health  000         1.064680      0 exit=7
03:20:31 /catalog 10.20.0.11  200 0.001953 exit=0      <- 30 seconds later the cache expired and was refilled from ns1
```

### The two name servers disagree

```
$ on pc dig +short @10.20.0.53 www.shop.test
10.20.0.11
10.30.0.11
$ on pc dig +short @10.30.0.200 www.shop.test
10.20.0.13
$ on pc dig +short @10.30.0.200 shop.test SOA
ns1.shop.test. hostmaster.shop.test. 2026101501 60 30 604800 60
```

### The logs that say why (journalctl -u named@ns1 and -u named@ns2)

```
Nov 12 03:16:43 lab ip[833]: notify: zone shop.test/IN: sending notifies (serial 2026110901)
Nov 12 03:16:49 lab ip[833]: security: client @0x704b3d3344d8 10.30.0.200#45859 (shop.test): zone transfer 'shop.test/IXFR/IN' denied
Nov 12 03:16:49 lab ip[833]: security: client @0x704b34007e38 10.30.0.200#33107 (shop.test): zone transfer 'shop.test/AXFR/IN' denied
Nov 12 03:16:49 lab ip[800]: xfer-in: transfer of 'shop.test/IN' from 10.20.0.53#53: connected using 10.20.0.53#53
Nov 12 03:16:49 lab ip[800]: xfer-in: transfer of 'shop.test/IN' from 10.20.0.53#53: failed while receiving responses: REFUSED
Nov 12 03:16:49 lab ip[800]: xfer-in: transfer of 'shop.test/IN' from 10.20.0.53#53: Transfer status: REFUSED
```

### r1's routing table: the static /25 beats BGP's /24

```
C>* 10.0.12.0/30 is directly connected, eth0, 00:00:17
C>* 10.0.99.0/30 is directly connected, old0, 00:00:17
C>* 10.10.0.0/24 is directly connected, eth1, 00:00:17
B>* 10.20.0.0/24 [20/0] via 10.0.12.2, eth0, weight 1, 00:00:12
B>* 10.30.0.0/24 [20/0] via 10.0.12.2, eth0, weight 1, 00:00:12
S>* 10.30.0.0/25 [1/0] via 10.0.99.2, old0, weight 1, 00:00:17
```

### The resolver avoided ns2 for 15 minutes after boot

Before `infra-host-ttl: 60` was added, Unbound had timed out on ns2 while BGP was still coming up and then kept away from it for its host cache's lifetime (default 900 s):

```
$ on resolver unbound-control dump_infra
10.30.0.200 shop.test. ttl 754 ping 0 var 94 rtt 376 rto 1504 tA 2 tAAAA 0 tother 0 ednsknown 0 edns 0 delay 0 lame dnssec 0 rec 0 A 0 other 0
10.20.0.53 shop.test. ttl 754 ping 0 var 3 rtt 50 rto 50 tA 0 tAAAA 0 tother 0 ednsknown 1 edns 0 delay 0 lame dnssec 0 rec 0 A 0 other 0
```

With `infra-host-ttl: 60`, 30 cache fills (flush, then ask): 17 from ns1 (`10.20.0.11 10.30.0.11`), 13 from ns2 (`10.20.0.13`).

## 2. Topic 36 mechanisms (`t36-mechanisms`)

### mtr from the branch: a rate-limited hop and real loss on the provider's last link

`netem isp2 eth2 loss 8%` (toward the data centre), `net.ipv4.icmp_ratelimit=2000` on isp1, 0 on the other routers:

```
$ on client mtr -n -r -c 40 10.20.0.80
Start: 2026-11-12T03:34:06+0000
HOST: client                      Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- 10.40.0.1                  0.0%    40    0.1   0.1   0.0   0.1   0.0
  2.|-- 203.0.113.1               37.5%    40    0.1   0.1   0.0   0.2   0.0
  3.|-- 192.0.2.2                  0.0%    40    0.1   0.1   0.0   0.2   0.0
  4.|-- 198.51.100.2              10.0%    40    0.1   0.1   0.1   0.3   0.0
  5.|-- 10.20.0.80                10.0%    40    0.1   0.1   0.1   0.2   0.0
```

The same path with `mtr -i 0.5` and Linux's default limit (1000 ms) on every router showed 33% at every hop: the defaults make every hop look lossy when probed twice a second. The labs set the limit explicitly on every router.

### A duplicate address: two machines answer one ARP request

```
$ on dc1 tcpdump -nn -e -i eth1 arp      (while: on dc1 arping -c 2 -I eth1 10.20.0.80)
03:35:29.237238 8e:0a:ba:b5:2c:0b > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806), length 42: Request who-has 10.20.0.80 (ff:ff:ff:ff:ff:ff) tell 10.20.0.1, length 28
03:35:29.237306 ba:03:1c:d0:a3:ff > 8e:0a:ba:b5:2c:0b, ethertype ARP (0x0806), length 42: Reply 10.20.0.80 is-at ba:03:1c:d0:a3:ff, length 28
03:35:29.237318 a6:6d:a2:53:f2:5e > 8e:0a:ba:b5:2c:0b, ethertype ARP (0x0806), length 42: Reply 10.20.0.80 is-at a6:6d:a2:53:f2:5e, length 28

$ on dc1 arping -c 3 -I eth1 10.20.0.80
ARPING 10.20.0.80 from 10.20.0.1 eth1
Unicast reply from 10.20.0.80 [BA:03:1C:D0:A3:FF]  0.558ms
Unicast reply from 10.20.0.80 [A6:6D:A2:53:F2:5E]  0.573ms
Unicast reply from 10.20.0.80 [A6:6D:A2:53:F2:5E]  0.546ms
Unicast reply from 10.20.0.80 [A6:6D:A2:53:F2:5E]  0.530ms
Sent 3 probes (1 broadcast(s))
Received 4 response(s)
```

Sixty seconds of requests from the branch every two seconds, with the MAC dc1 held for the address after each (counts of consecutive identical lines): `2 × 200 a6:6d` (the real load balancer), `24 × 503 ba:03` (the old one's maintenance page), `1 × 504 a6:6d`, `2 × 200 a6:6d`, `1 × 504 ba:03`.

### A backend whose outbound firewall blocks its database

```
$ on api3 tail -n 1 /var/log/nginx/error.log
2026/11/12 03:33:47 [error] 746#746: *48 upstream timed out (110: Connection timed out) while connecting to upstream, client: 10.20.0.79, server: , request: "GET /api/stock HTTP/1.1", upstream: "http://10.20.0.50:5000/stock", host: "10.20.0.80"
$ journalctl -u haproxy@lb | grep api3 | tail -n 1
Nov 12 03:33:47 lab ip[749]: 10.40.0.10:38360 [12/Nov/2026:03:33:45.975] api apis/api3 0/0/0/2002/2002 504 322 - - ---- 1/1/0/0/0 0/0 "GET /api/stock HTTP/1.1"
$ on api3 nft list chain inet filter output | grep counter
		counter packets 11 bytes 672
```

And with every backend's health check passing (`show stat`: api1, api2, api3 all `UP`): the health page doesn't touch the database.

### First version's mistake: the duplicate address took the whole load balancer down

When HAProxy's backend connections left from the shared address 10.20.0.80, the backends' replies followed the old box's ARP announcements, every health check failed and HAProxy answered `503 ... apis/<NOSRV> ... SC--` to everything. Giving the load balancer an address of its own for backend traffic (`source 10.20.0.79`, as real load balancers have) kept the fault where it belongs: on the service address only.

### curl's exit status names the layer

```
code=000 ip=[] t=0.000102 exit=6 <- http://nosuch.invalid/        (no address for the name)
code=000 ip=[] t=0.000225 exit=7 <- http://10.20.0.11:8080/       (refused: an answer, at once)
code=000 ip=[] t=2.001661 exit=28 <- http://10.20.0.13:8080/      (dropped by a firewall: no answer until --connect-timeout 2)
code=000 ip=[] t=2.001441 exit=28 <- http://10.20.0.99/           (nobody at the address; the router's "host unreachable" comes after about 3 s)
code=200 ip=[10.20.0.11] t=0.000379 exit=0 <- http://10.20.0.11/health
```

`%{remote_ip}` is empty when no connection was made, so a probe that wants the address it tried reads curl's `-v` line `Trying 10.20.0.13:8080...` instead.

## 3. Checkpoint 3 part 2, version 2 (`debug-outage-v2`)

### ns2 is told "nothing new" (same serial, different data)

```
$ on pc dig +short @10.20.0.53 shop.test SOA
ns1.shop.test. hostmaster.shop.test. 2026101501 60 30 604800 60
$ on pc dig +short @10.30.0.200 shop.test SOA
ns1.shop.test. hostmaster.shop.test. 2026101501 60 30 604800 60
$ on pc dig +short @10.30.0.200 www.shop.test
10.20.0.13
$ journalctl -u named@ns2 | grep notify | tail -n 3
Nov 12 03:45:39 lab ip[874]: notify: zone shop.test/IN: sending notifies (serial 2026101501)
Nov 12 03:45:49 lab ip[874]: notify: client @0x701540000e98 10.20.0.53#57663: received notify for zone 'shop.test'
Nov 12 03:45:49 lab ip[874]: general: zone shop.test/IN: notify from 10.20.0.53#57663: zone is up to date
```

### r2's two tunnels

```
$ on r2 ip route show 10.30.0.0/24
10.30.0.0/24 nhid 21 proto bgp metric 20
	nexthop via 10.0.23.2 dev tun1 weight 1
	nexthop via 10.0.24.2 dev tun2 weight 1
```

### The monitor, pristine (address column now lists the addresses curl tried)

```
03:46:08 /catalog 10.20.0.11              200    0.002 exit=0
03:46:13 /health  10.30.0.11,10.20.0.11   200    2.502 exit=0
03:46:17 /catalog 10.30.0.11,10.20.0.11   200    2.503 exit=0
03:46:23 /health  10.20.0.13              000    3.061 exit=7
03:46:26 /catalog 10.20.0.13              000    1.055 exit=7
```

### `ip route get` with ports does NOT predict the tunnel a forwarded connection takes

With the tun2 filter in place (`fib_multipath_hash_policy=1` on r2), the prediction against what happened to a connection from that source port:

```
45000 predicted:dev tun1 got:000      <- dropped, so it went over tun2
45001 predicted:dev tun2 got:200      <- arrived, so it went over tun1
45002 predicted:dev tun1 got:200
45003 predicted:dev tun2 got:000
45004 predicted:dev tun1 got:000
45005 predicted:dev tun1 got:200
...
oifname "tun2" tcp dport { 80, 443 } counter packets 15 bytes 900 drop
```

No agreement. Version 2's first per-tunnel check trusted the prediction and let `still-filtered.sh` pass it.

### The capture-based check that replaced it (`both-tunnels-carry.sh`)

```
== with the tun2 filter still in place
debug: failed=1 tun1=19 tun2=0
from the office, 1 of 20 connections to app2 didn't bring the whole catalogue      (18.7 s)
== after removing the filter
debug: failed=0 tun1=10 tun2=10
both tunnels carry it
== again at once (TIME-WAIT test)
debug: failed=0 tun1=5 tun2=15
both tunnels carry it
```

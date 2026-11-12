# Captured output from the FRR prototypes (2026-11-11)

Real output of the prototypes in this folder, run on Docker Desktop 29.8.2 (WSL 2 kernel 6.18.33.2) in `ubuntu:24.04` with Ubuntu's FRR 8.4.4-1.1ubuntu6.8. Label any recall item built on these **captured**. Timings in the last column of a route (`00:00:09`) and `ms` figures will differ in a new run; a writer pins an item's file to the text below, not to a new run.

## Routing prototype (`routing/`): r1 with static routes and floating statics

`router r1 -c "show ip route"` (static and connected lines, after the four `ip route` commands of the worked example):

```
C>* 10.0.12.0/30 is directly connected, r2, 00:00:11
C>* 10.0.13.0/30 is directly connected, r3, 00:00:11
C>* 10.1.0.0/24 is directly connected, lan, 00:00:11
S   10.2.0.0/24 [200/0] via 10.0.13.2, r3, weight 1, 00:00:01
S>* 10.2.0.0/24 [1/0] via 10.0.12.2, r2, weight 1, 00:00:01
S   10.3.0.0/24 [200/0] via 10.0.12.2, r2, weight 1, 00:00:01
S>* 10.3.0.0/24 [1/0] via 10.0.13.2, r3, weight 1, 00:00:01
```

`ip -n r1 route` (the kernel's table: only the selected routes, FRR's distance shown as the metric):

```
10.0.12.0/30 dev r2 proto kernel scope link src 10.0.12.1
10.0.13.0/30 dev r3 proto kernel scope link src 10.0.13.1
10.1.0.0/24 dev lan proto kernel scope link src 10.1.0.1
10.2.0.0/24 nhid 16 via 10.0.12.2 dev r2 proto static metric 20
10.3.0.0/24 nhid 15 via 10.0.13.2 dev r3 proto static metric 20
```

`ip -n r1 route get 10.3.0.10`:

```
10.3.0.10 via 10.0.13.2 dev r3 src 10.0.13.1 uid 0
    cache
```

No route at all (before any static route): `on office traceroute -n -w1 -q1 -m4 10.3.0.10`:

```
traceroute to 10.3.0.10 (10.3.0.10), 4 hops max, 60 byte packets
 1  10.1.0.1  0.033 ms !N
```

and `ip -n r1 route get 10.3.0.10` printed `RTNETLINK answers: Network is unreachable`.

After `ip -n r1 link set r3 down` (a veth pair loses carrier on both ends), the floating static takes over (`router r1 -c "show ip route 10.3.0.0/24"`, lines kept):

```
Routing entry for 10.3.0.0/24
  Known via "static", distance 200, metric 0, best
  * 10.0.12.2, via r2, weight 1
```

A routing loop (r1's default to r2, r2's default to r1), `on office traceroute -n -q1 -w1 -m8 10.99.0.1`:

```
traceroute to 10.99.0.1 (10.99.0.1), 8 hops max, 60 byte packets
 1  10.1.0.1  5.043 ms
 2  10.0.12.2  0.975 ms
 3  10.1.0.1  0.045 ms
 4  10.0.12.2  0.010 ms
 5  10.1.0.1  0.006 ms
 6  10.0.12.2  0.006 ms
 7  10.1.0.1  0.007 ms
 8  10.0.12.2  0.008 ms
```

and `on office ping -c1 -W1 10.99.0.1`: `From 10.0.12.2 icmp_seq=1 Time to live exceeded`.

A blackhole route on r1 (`ip route 10.0.0.0/8 blackhole`): traceroute prints `*` for all 8 hops, ping gets no answer at all, and:

```
S>* 10.0.0.0/8 [1/0] unreachable (blackhole), weight 1, 00:00:03     (FRR's show ip route)
blackhole 10.0.0.0/8 proto static metric 20                          (ip -n r1 route show)
RTNETLINK answers: Invalid argument                                  (ip -n r1 route get 10.99.0.1)
```

Forwarding switched off with FRR's `no ip forwarding` on r1: the namespace's `net.ipv4.ip_forward` became 0, the office's traceroute printed `*` from hop 1, and `ip netns exec r1 nstat -az` showed `IpInAddrErrors` counting the dropped packets (4 after one traceroute and one ping) while `IpForwDatagrams` stood still.

Asymmetric path through a stateful firewall on r2 (office to dc via r2, dc's replies straight to r1): ping worked, `curl` timed out after 4 s, and on r2:

```
		ct state invalid counter packets 9 bytes 900 drop
		ip saddr 10.1.0.0/24 ip daddr 10.3.0.0/24 tcp dport 80 ct state new counter packets 1 bytes 60 accept
tcp      6 115 SYN_SENT src=10.1.0.10 dst=10.3.0.10 sport=57106 dport=80 [UNREPLIED] src=10.3.0.10 dst=10.1.0.10 sport=80 dport=57106 mark=0 use=1
```

Strict reverse-path filtering on r1 (`rp_filter=1`) with the same asymmetric path and no firewall: curl and ping both failed, and `nstat -az TcpExtIPReversePathFilter` went from 1 to 8; with `rp_filter=2` (loose) curl answered 200.

ECMP with one dead path (r1 has two equal static routes to 10.3.0.0/24, one via r2, which has no route onward): with `net.ipv4.fib_multipath_hash_policy=0` (hash on addresses only) 0 of 20 connections from the office worked; with `=1` (hash on addresses and ports) 8 of 20 worked.

## BGP prototype (`bgp/`): edge (AS 65001) with ispa (65010), ispb (65020) and cloud (65100)

`router edge -c "show bgp summary"` with permit-all route-maps:

```
IPv4 Unicast Summary (VRF default):
BGP router identifier 198.51.100.1, local AS number 65001 vrf-id 0
BGP table version 2
RIB entries 3, using 576 bytes of memory
Peers 2, using 1448 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.0.2.2       4      65010        14        15        0    0    0 00:00:09            1        2 N/A
192.0.2.6       4      65020        12        15        0    0    0 00:00:09            1        2 N/A

Total number of neighbors 2
```

On ispa after its route-maps toward edge were removed (FRR's default `bgp ebgp-requires-policy`):

```
Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.0.2.1       4      65001        19        19        0    0    0 00:00:24     (Policy) (Policy) N/A
192.0.2.10      4      65100        22        20        0    0    0 00:00:24            2        2 N/A
```

and `show bgp neighbors 192.0.2.1` said `Inbound updates discarded due to missing policy` and `Outbound updates discarded due to missing policy`; in `show bgp summary json` the peer had `"state": "Established"`, `"peerState": "Policy"`, `"pfxRcd": 0`.

`router cloud -c "show bgp ipv4 unicast"` with permit-all policies:

```
   Network          Next Hop            Metric LocPrf Weight Path
*  198.51.100.0/24  192.0.2.13                             0 65020 65001 i
*>                  192.0.2.9                              0 65010 65001 i
*> 203.0.113.0/24   0.0.0.0                  0         32768 i
```

(the best path won on `"selectionReason":"Older Path"`, which depends on which session came up first: see the common brief, finding 7).

The route leak, seen from ispb (`show bgp ipv4 unicast neighbors 192.0.2.5 routes json`, trimmed): ispb received `198.51.100.0/24` with path `65001` and `203.0.113.0/24` with path `65001 65010 65100`: the shop was offering itself as a path from ISP B to ISP A's customer.

After edge's export filter (prefix-list `OURS`) and a prepend of two toward ispb:

```
*> 198.51.100.0/24  192.0.2.9                              0 65010 65001 i
*                   192.0.2.13                             0 65020 65001 65001 65001 i
```

## Two-circuit prototype (`circuits/`): edge (65001) and cloud (64512) over dx1 and dx2

`router cloud -c "show bgp ipv4 unicast"` with edge tagging dx1 `64512:7300` (the cloud's route-map turns it into local preference 300) and dx2 `64512:7100` (100):

```
   Network          Next Hop            Metric LocPrf Weight Path
*> 10.1.0.0/24      169.254.10.1             0    300      0 65001 i
*                   169.254.20.1             0    100      0 65001 i
*> 10.100.0.0/16    0.0.0.0                  0         32768 i
```

MED 100 on dx1 and 50 on dx2, equal local preference: best path via 169.254.20.1, reason `MED`, table:

```
*  10.1.0.0/24      169.254.10.1           100    200      0 65001 i
*>                  169.254.20.1            50    200      0 65001 i
```

dx1 prepended three times and dx2 tagged low preference: best stays dx1, reason `Local Pref` (local preference is compared before AS path length).

A prefix limit on the cloud (`neighbor 169.254.10.1 maximum-prefix 5 restart 1`) with edge announcing eight /24s. On the cloud, `show bgp summary`:

```
169.254.10.1    4      65001        10        15        0    0    0 00:00:08 Idle (PfxCt)        0 N/A
169.254.20.1    4      65001        14        18        0    0    0 00:00:10            8        9 N/A
```

and `show bgp neighbors 169.254.10.1` (lines kept):

```
  BGP state = Idle
  Maximum prefixes allowed 5
  Last reset 00:00:08,  Notification sent (Cease/Maximum Number of Prefixes Reached)
  Peer had exceeded the max. no. of prefixes configured.
  Reduce the no. of prefix from 169.254.10.1, will restart in 51 seconds
```

On edge, `show bgp neighbors 169.254.10.2`: `BGP state = Active` and `Last reset 00:00:08,  Notification received (Cease/Maximum Number of Prefixes Reached/Hard Reset)`. (After the restart the session comes back, receives eight prefixes again and goes down again: the flapping 34b's debug uses. The re-establishment itself was not timed: the test's own time limit ran out first.)

## Route-reflection prototype (`rr/`)

Before r2 was a route reflector, r2's summary showed r1 sending it 2 prefixes and r2 sending r3 none (`PfxSnt 0`), and r3's BGP table was empty. After `neighbor ... route-reflector-client` on r2, r3 had the cloud's route 4.3 s later:

```
    10.0.12.1 from 10.0.23.1 (10.0.12.1)
      Originator: 10.0.12.1, Cluster list: 10.0.12.2
```

## NAT prototype (`nat/`)

`conntrack -L` on gw while the office held connections through `snat to 198.51.100.2:20000-20009`:

```
tcp      6 431986 ESTABLISHED src=10.1.0.10 dst=203.0.113.10 sport=38620 dport=9000 src=203.0.113.10 dst=198.51.100.2 sport=9000 dport=20007 [ASSURED] mark=0 use=1
tcp      6 52 CLOSE_WAIT src=10.1.0.10 dst=203.0.113.10 sport=42956 dport=9001 src=203.0.113.10 dst=198.51.100.2 sport=9001 dport=20000 [ASSURED] mark=0 use=1
```

15 connections to 203.0.113.10:9000 through those 10 ports: `opened 10 of 15, failed 5 (last error: timed out)`; at the same time 5 connections to port 9001, another destination, all opened, reusing port 20000. `conntrack -S` afterwards (one line per CPU, trimmed to three counters):

```
insert_failed=0 drop=0 clash_resolve=0
insert_failed=1 drop=1 clash_resolve=0
insert_failed=0 drop=0 clash_resolve=0
insert_failed=0 drop=0 clash_resolve=0
insert_failed=10 drop=10 clash_resolve=0
insert_failed=3 drop=3 clash_resolve=0
insert_failed=0 drop=0 clash_resolve=0
insert_failed=7 drop=7 clash_resolve=0
```

With two public addresses (`snat to 198.51.100.2-198.51.100.3:20000-20009`, with or without `random` or `fully-random`), one client to one destination still got only 10 connections, all from 198.51.100.2: Linux maps a client to one address of the range.

DNAT of the gateway's port 443 to the app's 8443, seen by the app (a small server that prints the client's address):

```
correct rules ................................... you are 203.0.113.20
masquerade with no "oifname wan" ................ you are 10.1.0.1
forward chain without "ct status dnat accept" ... (timed out)
```

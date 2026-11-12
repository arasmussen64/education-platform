# Writing brief: `csa.net.transport` (topic 28), TCP and UDP

Design only. Nothing here is in the repository yet. Sources were read on 2026-11-11; each fact carries its URL and date. Lab mechanics marked **tried** were run in Docker on the owner's machine (Docker Desktop 29.8.2, kernel `6.18.33.2-microsoft-standard-WSL2`, 8 CPUs, cgroups v2) on 2026-11-11 (container clocks read 2026-11-12 UTC), and everything started was removed afterwards. The prototypes, scripts and real captures are in `scratchpad/cloud/m3-design/prototypes/transport-congestion/` (`idle/`, `sysd/`, `captures/`, `items/`); the appendix lists what was run and what it printed.

The companion brief is `csa.net.congestion.md` (topic 29). The two share the lab topologies of section 7 and one image layer, and topic 29 builds on this topic's windows, round trips and UDP.

## 1. What the learner will be able to do

1. Capture a TCP conversation they started themselves and read it line by line: the settings each side offers in its SYN (MSS, SACK, timestamps, window scale), bytes counted by sequence and acknowledgement numbers, the goodbye (FIN) and who said it first, a reset (RST) against a goodbye, retransmissions, keepalive probes, and a reset forged by a box in the middle, told apart by its TTL.
2. Explain flow control and the receive window, why window scaling exists and why a box that strips it caps a connection at about 64 KiB per round trip; work out a path's bandwidth-delay product and the most one connection can carry with a given window.
3. Say how long TCP waits before it gives up (a connection attempt, an unanswered retransmission, an idle connection), what the application is told each time, and why applications set their own, shorter timeouts.
4. Explain why idle connections get cut in a cloud: every stateful box on the path (NAT gateway, load balancer, firewall connection tracking) forgets a flow that has been quiet too long, and the endpoints aren't told. Name the defaults on the three clouds, recognise the two symptoms (an immediate reset, or a hang ending in a timeout), and fix it with keepalives below the smallest idle timer on the path, switched on by the application and made to survive a reboot.
5. Explain how UDP differs: no handshake, no acknowledgement, no retransmission; what a closed port and a firewall drop look like; why middleboxes give UDP short timers; and how a client that waits for pushes keeps its NAT mapping alive.

**The six-month core.** What should still be there half a year on, and what the review pool is built around:

- A capture tells the story: SYN's options, bytes by `seq`/`ack`, `[F.]` is goodbye and `[R]` is a slammed door; the side that says goodbye first sits in TIME-WAIT. A reset whose TTL doesn't match the server's packets came from a box in the middle.
- One connection carries at most one window per round trip: **throughput ≤ window ÷ RTT**. The window the path needs is the **bandwidth-delay product, rate × RTT**. Without window scaling the window stops at 65,535 bytes.
- Every stateful box forgets quiet flows: **AWS NAT gateway and NLB 350 s, Azure load balancer and NAT gateway 4 minutes, Google Cloud NAT 20 minutes, Google's firewall 10 minutes, AWS Nitro v6 instances' connection tracking 350 s.** Keepalive must start below the smallest timer on the path, and only sockets that switch keepalive on send any.
- Linux's defaults are far too long for a cloud: keepalive after **2 hours**; a connection attempt to a silent host gives up after **about 2 minutes**; a connection whose peer vanished mid-transfer after **about 15 minutes**.
- UDP has no connection; boxes invent one with a short timer (often 30 s), so a UDP client that waits for pushes sends keepalives.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.net.nat]`. The module's order makes NAT (topic 27) the topic before this one, and through it the chain reaches layers, CIDR and routing. The module brief should keep "every Module 3 topic depends on `csa.m2.checkpoint` directly or through another Module 3 topic" (the rule Module 2 kept). This topic's labs also lean on `csa.net.layers` (TTL, ICMP, MTU, encapsulation) and `csa.net.routing` (a router namespace forwarding between two networks).

**What the track already taught, which this topic builds on and never repeats** (from `csa.linux.net-tools`, read in full 2026-11-11):

| From | Already taught | This topic adds |
| --- | --- | --- |
| `csa.linux.net-tools` | `tcpdump -nn -i IF filter`, `-w`; the handshake's flags `[S]`, `[S.]`, `[.]`, `[P.]`; `[R.]` to a SYN is refused; a SYN repeated with no answer is dropped | the SYN's **options**, `seq`/`ack` as byte counts, the **teardown** (`[F.]`), RST in an open connection, keepalive probes, `-v` and the TTL |
| `csa.linux.net-tools` | `ss -ltnp`, `ss -tan`, states `ESTAB`, `TIME-WAIT` (60 s on Linux), `CLOSE-WAIT`; ephemeral ports | `ss -o` timers (`keepalive`, `timewait`, `on`), `ss -i` (`wscale`, `rtt`, `cwnd`) |
| `csa.linux.net-tools` | connection tracking (`ct state established,related accept`), `conntrack -L`; network namespaces and veth pairs; `from-office` | conntrack's **idle timers** and what happens when an entry expires mid-conversation |
| `csa.linux.services`, `csa.linux.scripting` | units, `systemctl restart`, files under `/etc` that survive a reboot, `awk`, `grep -o` | `/etc/sysctl.d/` and `sysctl` (one sentence each if no Module 1 or 3 topic has taught them; see below) |
| `csa.net.layers` (assumed; confirm in the module merge) | packet, segment, datagram; TTL; ICMP and "port unreachable"; MTU | MSS as the payload a segment may carry (one sentence: MTU minus the IP and TCP headers) |
| `csa.net.nat` (assumed; confirm) | source NAT and masquerade, the mapping table, SNAT ports and exhaustion | the mapping's **idle timeout**, and what the NAT does when a packet arrives for a forgotten mapping |

**Terms this topic must define itself** (searched: no earlier lesson uses them, or uses them without defining them):

- **Sequence number, acknowledgement number** (each byte is numbered; `ack N` means "I have everything before byte N"), **relative numbering** in tcpdump (`-S` shows the raw numbers), **segment length**.
- **MSS** (maximum segment size), **SACK** (selective acknowledgement), **timestamps option**, **window scale option** and its **shift count**.
- **Receive window, flow control, bandwidth-delay product (BDP), round-trip time (RTT)**. Net-tools said "fifteen milliseconds between the first two packets is the round trip" once, without the term.
- **FIN, graceful close, half-close; RST, abort; TIME-WAIT** is net-tools'; this topic says who ends up in it and why.
- **Retransmission timeout (RTO), exponential backoff, `ETIMEDOUT`, `ECONNREFUSED`, `ECONNRESET`** (the errors the application sees: "Connection timed out", "Connection refused", "Connection reset by peer").
- **Keepalive** (TCP's empty probe, off by default), **`SO_KEEPALIVE`** (the per-socket switch), **`tcp_keepalive_time` / `_intvl` / `_probes`** (the system's defaults), **`TCP_KEEPIDLE` / `TCP_KEEPINTVL` / `TCP_KEEPCNT`** (per-socket overrides), **application heartbeat** (a message the application sends for the same purpose, which crosses proxies).
- **Idle timeout** of a stateful box; **load balancer** (one sentence: a box that spreads connections across servers; topic 33 teaches it), **security group** (one sentence: a cloud's per-machine firewall that tracks connections; Module 11 teaches it), **connection pool** (an application keeping a few connections open and reusing them).
- **Datagram** if `csa.net.layers` hasn't defined it; **UDP mapping** in a NAT; **keepalive datagram**.
- **`sysctl`, `/etc/sysctl.d/`** (the kernel's tunable settings, and the folder whose files set them at every boot, read in name order, later files winning). No Module 1 or Module 2 file mentions `sysctl` (every `csa.*` file searched, 2026-11-11). If an earlier Module 3 topic teaches it (routing's `net.ipv4.ip_forward` is the natural first use), this topic builds on that; otherwise it teaches both in one paragraph.
- **Mbit/s against MB/s, KiB against KB**: one line, because every rate in this topic is in bits a second and every window in bytes.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `read-a-capture` | Read a TCP conversation in `tcpdump -nn` text: the SYN's options (`mss`, `sackOK`, `TS`, `wscale`), relative `seq` and `ack` as byte counts, data and its acknowledgement, the FIN exchange and who closed first, RST against FIN, retransmissions and their growing gaps, keepalive probes (empty segments re-acknowledging old data), and a reset forged by a box in the middle, found with `-v` by its TTL |
| `window-math` | Flow control and the receive window; window scaling (a shift count in the SYN only, both sides must offer it, a box that strips it caps the window at 65,535 bytes); the bandwidth-delay product; throughput ≤ window ÷ RTT; the window field times 2 to the shift |
| `tcp-timers` | How long TCP waits and what the application hears: a connection attempt to a silent host (about 2 minutes on Linux), a refused one (at once), retransmissions doubling until about 15 minutes, TIME-WAIT, keepalive's defaults (2 hours, then 9 probes 75 s apart) and how long a dead peer takes to notice; why applications set shorter connect and read timeouts |
| `idle-cuts` | Why idle connections get cut: stateful boxes' idle timers and the three clouds' defaults; the two symptoms (a reset, or a hang ending in a timeout); keepalive below the smallest timer on the path, switched on by the application, with the idle time from the socket or the system default, kept after a reboot; application heartbeats where a proxy sits in the path; what raising a box's timer costs |
| `udp-behaviour` | UDP's datagrams with no handshake, acknowledgement, retransmission or order; a closed port answers with ICMP port unreachable, a firewall drop answers nothing, and `nc -u` can't tell them apart; middleboxes' short UDP timers; keepalive datagrams for a client that waits for pushes; when UDP is the right choice (DNS, QUIC, voice and video, VPNs) |

Five skills. `window-math`, `tcp-timers` and `idle-cuts` are calculation skills (at least three estimate items each, ADR-0024 rule 6; they have 4, 5 and 3). Every skill has at least four questions that can come back (counted in section 9).

## 4. Lesson plan

The lesson is `<Intro>` (what to watch for, plus the explanations no resource gives a beginner), the main resource, and `<Recap>`. The order of ideas, each with the resource section it leans on and what the lesson itself must supply:

**4.1 What TCP promises, and how it counts.** TCP turns packets that can be lost, duplicated or reordered into a byte stream that arrives complete and in order. Every byte has a number; the receiver acknowledges "everything before byte N". *Resource:* HPBN chapter 2, "Three-Way Handshake". *The lesson supplies* the picture, which no resource draws for a beginner:

> A long letter sent as numbered postcards. The reader writes back "I've got everything up to card 7; send 7 next" (`ack 7`). Cards that go missing are sent again; cards that arrive out of order wait in a pile until the gap is filled. tcpdump shows the card numbers counted from the start of this conversation (`seq 1:4` is bytes 1 to 3, `length 3`), because the real numbers start at a random value (the SYN's `seq 4030549266`); `tcpdump -S` shows the real ones.

Then the capture the learner will make, read line by line: the captured conversation in section 7.2 (`captures/keepalive-probes-and-teardown.txt`). Client sends 3 bytes (`seq 1:4`), server answers 6 (`seq 1:7`), each acknowledges the other.

**4.2 The SYN carries the connection's settings.** In `options [mss 1460,sackOK,TS val … ecr 0,nop,wscale 10]`: **MSS** is the largest payload this side will accept in one segment (the link's MTU minus 40 bytes of IP and TCP headers, which `csa.net.layers` explains); **sackOK** offers selective acknowledgement (the receiver can say "I have 1–4 and 9–12", so only the gap is resent); **TS** is the timestamps option, used to measure round trips and to tell old segments from new ones (RFC 7323); **wscale 10** offers to multiply this side's window by 2^10. `nop` is padding. Each option is offered in the SYN and only counts if both sides offer it.

**4.3 Saying goodbye, and slamming the door.** Each side closes its direction with a FIN, and each FIN is acknowledged; often it takes three packets (`[F.]`, `[F.]`, `[.]`), as in the capture. The side that sends the first FIN waits in TIME-WAIT (net-tools taught the state; the lesson adds *who*): our client closed first, so the client has the TIME-WAIT socket. A FIN is a goodbye; an **RST** is a slammed door: no goodbye, the socket is gone at once, and the application is told "Connection reset by peer". Who can send one: the peer's kernel (a closed port; an application that aborted), **or any box in the middle that pretends to be the peer**. *The lesson supplies* how to tell them apart, from the lab's own capture (`captures/forged-reset-ttl.txt`): with `tcpdump -v` every packet shows its TTL; the database's real packets arrive with `ttl 63` (64 minus the one router, the NAT gateway, they crossed), and the reset that claims to be from the database arrives with `ttl 64`: it was made one hop closer, by the gateway.

**4.4 Flow control, the window and the round trip.** The receiver says in every segment how much more it can take (`win`). The sender may have at most that much unacknowledged data in flight, so in one round trip it can send at most one window: **throughput ≤ window ÷ RTT**. *Resource:* HPBN chapter 2, "Flow Control", "Window Scaling (RFC 1323)" and "Bandwidth-Delay Product". *The lesson supplies* two worked numbers and a picture:

> The window is how many postcards may be in the post at once. If the reader allows 45 cards and a card takes 50 ms to arrive and its answer 50 ms to come back, the writer can send 45 cards every 100 ms, however fast the post could carry them.

- The window field is 16 bits, so at most 65,535 bytes. Over a 100 ms round trip that's 65,535 × 8 ÷ 0.1 = 5.2 Mbit/s, on any link. Measured in the lab with scaling switched off at the receiver: 5.05 Mbit/s on a 50 Mbit/s link (appendix A5).
- **Window scaling** multiplies the field by 2^shift; the shift is agreed in the SYNs only, so a capture that misses the handshake can't tell what `win 63` means. In the lab's capture `win 63` with `wscale 10` is 63 × 1,024 = 64,512 bytes.
- **The bandwidth-delay product** is how many bytes are "on the wire" when a path is full: 50 Mbit/s × 100 ms = 625,000 bytes. A connection needs a window at least that large to fill the path.
- **A box that strips the option** (old firewalls' "TCP normalisation") leaves both sides without scaling: in the lab, the SYN leaving `lab` says `wscale 10` and the same SYN arriving at `dr` says `nop,nop,nop,nop`, and the transfer falls to 5 Mbit/s (appendix A6). Comparing captures on both sides of a box is how it's found.

**4.5 How long TCP waits.** *Resource:* Cloudflare, "When TCP sockets refuse to die", sections "SYN-SENT", "Idle ESTAB is forever", "Busy ESTAB socket is not forever". *The lesson supplies* one table, measured or read from the kernel's own documentation (facts F6, F21):

| Situation | What TCP does | What the application hears, and when |
| --- | --- | --- |
| Connect to a port with nothing listening | the host answers RST | "Connection refused", at once |
| Connect to a host whose firewall drops the SYN | resends the SYN: 1 s apart five times, then doubling (current Linux) | "Connection timed out" after about 2 minutes (131 s on current kernels, 127 s on older ones; 134 s measured) |
| Data sent, peer vanished | resends with a doubling gap, from 0.2 s, never more than 120 s apart | "Connection timed out" after about 15 minutes (at least 924.6 s) |
| Connection idle, peer vanished, no keepalive | nothing at all | nothing, ever, until it next sends |
| Connection idle with keepalive on, Linux defaults | first probe after 2 hours, then 9 probes 75 s apart | "Connection timed out" after 2 h 11 min |

Then the habit: **applications set their own connect and read timeouts** (a few seconds), because two minutes of a hung connect is an outage.

**4.6 Keepalives.** RFC 9293 lets an implementation send keepalives, insists they be **off by default** for each connection and start no sooner than **two hours** of quiet (fact F1). Linux follows it: a socket sends keepalives only if its program switched them on with `SO_KEEPALIVE`; the program may set its own idle time, probe gap and probe count (`TCP_KEEPIDLE`, `TCP_KEEPINTVL`, `TCP_KEEPCNT`); otherwise the system's `net.ipv4.tcp_keepalive_time`, `_intvl` and `_probes` apply. *The lesson supplies* what a probe looks like on the wire, from the lab's capture: every 10 s of quiet, the client sends an empty segment (`length 0`) acknowledging the same byte as before (`ack 7`), and the server answers with an empty acknowledgement. And the trap, said twice: **the system setting does nothing for a program that never switches keepalive on**, and many libraries' "keepalive = true" only switches it on, leaving Linux's two hours (the AWS blog's PostgreSQL and Redis examples, resource R5). Time to notice a dead peer = idle time + gap × probes.

**4.7 Why idle connections get cut.** *Resources:* AWS NAT gateway troubleshooting, "Internet connection drops after 350 seconds" (R3); Azure, "Load Balancer TCP Reset and idle timeout" (R4); Google Cloud NAT's timeouts table (R7). *The lesson supplies* the picture and the table:

> A cloakroom that throws out any coat not collected within six minutes. Your ticket still looks fine in your pocket. Only when you come back do you find out: either the attendant tells you straight away (a reset), or nobody is at the counter and you wait until you give up (a silent drop).

Every NAT gateway, load balancer and stateful firewall keeps a table entry for each flow and throws out entries that stay quiet too long. The endpoints are never told. The next packet then meets either a **reset** (AWS's NAT gateway resets the inside end; Azure's NAT gateway resets whoever sends on a forgotten flow; Azure's load balancer with "TCP reset on idle" resets both ends) or a **silent drop** (Azure's load balancer by default), and the sender retransmits until its own timeout. The fix, in order of preference: **keepalives starting below the smallest idle timer on the path** (the AWS blog suggests 240 s idle, 60 s gap, 3 probes, under AWS's 350 s); an **application heartbeat** where a proxy sits in the path, because TCP keepalives only reach the proxy (Azure's page; AWS's ALB doesn't even count HTTP/2 PING frames); a **connection pool** that closes connections before they've been idle that long; and, where a box allows it, a longer timer, which costs (Azure's NAT gateway holds the SNAT port for the whole timer and advises against raising it).

**Where the three clouds differ** (facts F9 to F18; the lesson's table):

| Box | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| NAT gateway, TCP | 350 s, fixed; RST to the inside end on the next packet | 4 min default, 4 to 120 min; RST to whoever sends on a forgotten flow | 1,200 s (20 min) established, configurable; 30 s while opening or closing |
| NAT gateway, UDP | not stated on the page read | 4 min, fixed | 30 s, configurable |
| Layer 4 load balancer | NLB: 350 s default, 60 to 6,000 s (TLS listeners 350 s fixed) | 4 min default, 4 to 100 min (outbound rules to 120); drops silently unless "TCP reset on idle" is on | (passthrough load balancers: not read; leave out) |
| Layer 7 load balancer | ALB: 60 s default, 1 to 4,000 s; HTTP/2 PING doesn't count | Front Door: HTTP keep-alive 90 s, fixed (Application Gateway: not read; leave out) | external Application LB: client keepalive 610 s (5 to 1,200), backend keepalive 600 s fixed |
| The machine's own firewall | security group tracking: 350 s on Nitro v6 instances, 5 days on others; 60 s to 5 days per network interface | (not stated on the pages read) | VPC firewall: a flow stays tracked while it sends at least one packet every 10 minutes |

The writer leaves a cell out rather than filling it from memory; the four "not read" cells can be read and added on the day of writing.

**4.8 UDP.** *Resource:* HPBN chapter 3, "Null Protocol Services", "UDP and Network Address Translators", "Connection-State Timeouts", "TCP Timeouts and NATs". UDP sends one datagram and forgets it: no handshake, no acknowledgement, no resending, no order, and each datagram arrives whole or not at all. *The lesson supplies* what it looks like, from the lab's capture (`captures/udp-closed-and-dropped.txt`): a datagram to a closed port is answered by ICMP "udp port 5301 unreachable"; a datagram a firewall drops is answered by nothing; and `nc -u` exits 0 either way, because there is nothing to wait for. Middleboxes invent a "connection" for UDP and give it a short timer: Linux's connection tracking keeps an unanswered flow 30 s and a two-way one 120 s (observed, fact F19); Google Cloud NAT 30 s; Azure's NAT gateway 4 minutes and says a keepalive must be sent from both sides; AWS security groups 30 s and 180 s. So a client that subscribes and then waits for pushes must send its own keepalive datagrams (RFC 9000 says experience shows "every 30 seconds"; WireGuard's documentation's familiar 25 s is the same idea; the lesson names the RFC, not WireGuard, unless the writer reads WireGuard's page). When UDP is chosen: DNS (one question, one answer), voice and video (late is as bad as lost), VPN tunnels, and QUIC, the next topic.

**Recap.** One bullet per idea above, with the commands: `tcpdump -nn [-v] [-S]`, `ss -tno` (timers), `ss -tni` (`wscale`, `rtt`, `cwnd`), `sysctl net.ipv4.tcp_keepalive_time`, `/etc/sysctl.d/`, `conntrack -L`, the table of timers, the formula.

## 5. Verified facts

Each read on 2026-11-11 unless marked **measured** (run in the lab on the date above). Where sources disagree it says so.

| # | Fact | Source |
| --- | --- | --- |
| F1 | Keep-alives are optional; if implemented the application must be able to turn them on or off per connection and they must default to off; they are sent only after an interval with no data that must be configurable and default to no less than two hours; a probe "generally contains SEG.SEQ = SND.NXT-1"; one missing answer must not be taken as a dead connection | RFC 9293 §3.8.4, https://www.rfc-editor.org/rfc/rfc9293.txt |
| F2 | The window field is 16 bits; it is shifted when window scaling is used [RFC 7323]; TIME-WAIT lasts 2×MSL, MSL taken as 2 minutes in the RFC. Linux uses 60 s for TIME-WAIT (Module 1's figure) | RFC 9293 §3.1, §3.4.2, §3.6.1 (same URL) |
| F3 | Window scale shift ≤ 14, allowing windows of 2^30 = 1 GiB; sent only in a SYN; both sides must send it to enable scaling in either direction; without it both shifts are zero. Timestamps are for RTT measurement and protection against wrapped sequence numbers (PAWS) | RFC 7323 §2.1 to 2.3, https://www.rfc-editor.org/rfc/rfc7323.html |
| F4 | Initial RTO 1 second; a computed RTO below 1 s "SHOULD be rounded up to 1 second". Linux uses a lower minimum: the kernel's `tcp_retries2` text counts from `TCP_RTO_MIN`, and its 924.6 s is exactly what a start of 0.2 s doubling to a cap of 120 s gives over 16 waits (derived here, not stated on the page; the lesson says "from 0.2 s" with that caveat in the writer's notes) | RFC 6298 §2, https://www.rfc-editor.org/rfc/rfc6298.txt; kernel ip-sysctl (F6) |
| F5 | `tcp_keepalive_time` default 2 hours; `tcp_keepalive_probes` 9; `tcp_keepalive_intvl` 75 s, "connection will be aborted after ~11 minutes of retries"; `tcp_syn_retries` 6 "corresponds to 67seconds (with tcp_syn_linear_timeouts = 4) till the last retransmission … the final timeout for an active TCP connection attempt will happen after 131seconds"; `tcp_synack_retries` 5, 63 s; `tcp_retries2` 15 "yields a hypothetical timeout of 924.6 seconds and is a lower bound"; `tcp_fin_timeout` 60 s; `tcp_window_scaling` 1; `ip_local_port_range` 32768 to 60999 | https://docs.kernel.org/networking/ip-sysctl.html and https://www.kernel.org/doc/html/v6.8/networking/ip-sysctl.html (the v6.8 page carries the same `tcp_syn_retries` text). **Disagreement:** older texts, and pre-linear-timeout kernels, say 63 s and 127 s; Cloudflare's 2019 post says about 130 s |
| F6 | Keep-alives are sent only when `SO_KEEPALIVE` is enabled; `TCP_KEEPIDLE`, `TCP_KEEPINTVL`, `TCP_KEEPCNT` override per socket; `TCP_USER_TIMEOUT` overrides keepalive's count when both are set | tcp(7), man-pages 6.19 (2026-04-19), https://man7.org/linux/man-pages/man7/tcp.7.html |
| F7 | `ss -o` prints `timer:(<name>,<expire_time>,<retrans>)` with names `on`, `keepalive`, `timewait`, `persist`, `unknown`; `-i` prints `wscale:<snd>:<rcv>` (the binary prints `wscale:10,10`), `rtt:<rtt>/<rttvar>` in ms, `cwnd` | ss(8), https://man7.org/linux/man-pages/man8/ss.8.html |
| F8 | Defaults in Docker Desktop's kernel 6.18: keepalive 7200/75/9, `tcp_syn_retries` 6, `tcp_syn_linear_timeouts` 4, `tcp_retries2` 15, `tcp_rmem` 4096 131072 33554432, conntrack TCP established 432000 s, UDP 30 s, UDP stream 120 s; the conntrack timers are per network namespace | **measured** (appendix A1) |
| F9 | AWS NAT gateway: "If a connection that's using a NAT gateway is idle for 350 seconds or more, the connection times out"; it "returns an RST packet to any resources behind the NAT gateway that attempt to continue the connection (it does not send a FIN packet)"; fix: more traffic, or "TCP keepalive on the instance with a value less than 350 seconds"; each IPv4 address supports up to 55,000 concurrent connections (topic 27's) | https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-troubleshooting.html |
| F10 | AWS NLB: TCP idle timeout default 350 s, settable 60 to 6,000 s; TLS listeners 350 s, not modifiable; above 350 s, targets' ENI connection tracking timeout must be at least as long, because on Nitro v6 it defaults to 350 s and "a mismatch causes the target's network interface to silently drop connection state" | https://docs.aws.amazon.com/elasticloadbalancing/latest/network/update-idle-timeout.html |
| F11 | AWS ALB: connection idle timeout default 60 s, range 1 to 4,000 s; "Application Load Balancers do not support HTTP/2 PING frames. These do not reset the connection idle timeout"; set the application's idle timeout larger than the load balancer's, or it may get 502s; HTTP client keepalive duration default 3,600 s | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html |
| F12 | AWS security group connection tracking: TCP established idle default 350 s on Nitro v6 instance types, 432,000 s on others, settable 60 to 432,000 s per network interface; UDP 30 s (30 to 60); UDP stream 180 s (60 to 180); NLB flows 350 s TCP and 120 s UDP; "configure TCP keep alives to be sent at intervals of less than 5 minutes" | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html |
| F13 | AWS blog, 22 May 2026: Nitro V6 (launched June 2025) defaults connection tracking to 350 s, down from 5 days, matching NLB, NAT gateway and GWLB; suggests `tcp_keepalive_time = 240`, `tcp_keepalive_intvl = 60`, `tcp_keepalive_probes = 3`; connection pools: `maxIdleTime`, `maxLifetime`; PostgreSQL `tcp_keepalives_*`, Redis `tcp-keepalive` default 300 s | https://aws.amazon.com/blogs/networking-and-content-delivery/best-practices-for-tcp-connection-management-on-ec2/ |
| F14 | Azure Load Balancer: default "silently drop flows when the idle timeout of a flow is reached"; "TCP Reset on Idle" sends bidirectional RSTs; idle timeout 4 to 100 min for load-balancing and inbound NAT rules, 4 to 120 for outbound rules, default 4 min; keepalives aren't recommended for mobile apps (battery); application-layer keepalives when a proxy is in the path; idle timeout isn't supported for UDP rules (ms.date 2024-07-31, updated 2026-08-19) | https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-tcp-reset |
| F15 | Azure NAT Gateway: TCP idle timeout 4 min default, 4 to 120 min; UDP 4 min, not configurable; a TCP reset is sent when traffic arrives for a flow that doesn't exist, unidirectional; doesn't recommend raising the TCP timeout (SNAT port held); "TCP keepalives appear as duplicate acknowledgements (ACKs)"; UDP keepalives must be enabled on both sides; FIN hold-down 65 s, RST 16 s, half-open 30 s; "These timer settings are subject to change" (ms.date 2025-11-04, updated 2026-10-13) | https://learn.microsoft.com/en-us/azure/nat-gateway/nat-gateway-resource |
| F16 | Google Cloud NAT defaults: UDP mapping idle 30 s, ICMP 30 s, TCP established 1,200 s, TCP transitory 30 s, TIME_WAIT 30 or 120 s depending on gateway creation date (30 s after 2026-09-30); all configurable; expiry "can occur up to five seconds early or late" | https://docs.cloud.google.com/nat/docs/tune-nat-configuration (redirected from cloud.google.com) |
| F17 | Google Cloud VPC firewall: "A firewall rule's tracking state is considered active if at least one packet is sent every 10 minutes"; over the tracked-connection limit, the longest-idle are dropped first | https://docs.cloud.google.com/firewall/docs/firewalls |
| F18 | Google Cloud external Application LB: client HTTP keepalive default 610 s, configurable 5 to 1,200 s; backend keepalive "fixed at 10 minutes (600 seconds)"; backend service timeout default 30 s; backend software's keepalive should be greater than 600 s | https://docs.cloud.google.com/load-balancing/docs/https/request-distribution |
| F18a | Azure Front Door: "a 90-second HTTP keep-alive timeout … You can't configure this timeout value"; a 5-second timeout for receiving a request's headers (ms.date 2026-11-02) | https://learn.microsoft.com/en-us/azure/frontdoor/front-door-faq |
| F19 | Linux conntrack: a UDP flow seen in one direction is kept 30 s, one with replies 120 s (Docker Desktop's kernel defaults) | **measured** (A1) |
| F20 | "sending packets every 30 seconds is necessary to prevent the majority of middleboxes from losing state for UDP flows" | RFC 9000 §10.1.2, https://www.rfc-editor.org/rfc/rfc9000.txt |
| F21 | A connect to a host that drops SYNs: SYNs at 0, 1, 2, 3, 4, 5, 7, 11, 19, 35.5 and 68.5 s; `ETIMEDOUT` after 134.1 s | **measured** (A3) |
| F22 | Window scaling off at the receiver: 5.05 Mbit/s on a 50 Mbit/s, 100 ms path (65,535 × 8 ÷ 0.1 = 5.24); receiver's `tcp_rmem` max 131,072: 7.25 Mbit/s | **measured** (A5) |
| F23 | `nft … tcp flags syn reset tcp option window` in a forwarding namespace replaces the option with four `nop`s; both sides then run without scaling; 5.05 Mbit/s | **measured** (A6) |
| F24 | A reset forged by the NAT gateway (`reject with tcp reset`) arrives with `ttl 64`; the database's real packets, one hop further, with `ttl 63` | **measured** (A2) |
| F25 | UDP to a closed port: one datagram, then ICMP "udp port 5301 unreachable"; to a dropped port: datagrams, no answer; `nc -u -w1` exits 0 in both cases; a connected UDP socket's next send after the ICMP fails with "Connection refused" | **measured** (A4) |

## 6. Resources

Fetched on 2026-11-11 unless noted. Minutes are the assigned parts at about 130 words a minute.

| # | Title | URL | Type | Licence (as the source states it) | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 (main) | High Performance Browser Networking, ch. 2 "Building Blocks of TCP", by Ilya Grigorik: read "Three-Way Handshake", "Flow Control" with "Window Scaling (RFC 1323)", and "Bandwidth-Delay Product" (about 1,700 of its 5,000 words) | https://hpbn.co/building-blocks-of-tcp/ | reading | CC BY-NC-ND 4.0 (page footer: "Copyright © 2013 Ilya Grigorik. Published by O'Reilly Media, Inc. Licensed under CC BY-NC-ND 4.0"); linked, not copied | 15 | `read-a-capture`, `window-math` | 2026-11-11 |
| R2 | "When TCP sockets refuse to die", Marek Majkowski, Cloudflare blog, 2019-09-20: read "SYN-SENT", "Idle ESTAB is forever", "Busy ESTAB socket is not forever", "Summary" | https://blog.cloudflare.com/when-tcp-sockets-refuse-to-die/ | reading | No licence stated on the page (© Cloudflare); linked, not copied | 12 | `tcp-timers`, `idle-cuts` | 2026-11-11 |
| R3 | Troubleshoot NAT gateways (AWS): the section "Internet connection drops after 350 seconds" | https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-troubleshooting.html | reading | Copyright Amazon Web Services; linked, not copied | 1 | `idle-cuts` | 2026-11-11 |
| R4 | Load Balancer TCP Reset and idle timeout (Azure) | https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-tcp-reset | reading | CC BY 4.0 (MicrosoftDocs/azure-docs, as the windows-ad topic records); linked, not copied | 7 | `idle-cuts` | 2026-11-11 |
| R5 | Best Practices for TCP Connection Management on EC2 (AWS Networking blog, 2026-05-22): optional, the whole post | https://aws.amazon.com/blogs/networking-and-content-delivery/best-practices-for-tcp-connection-management-on-ec2/ | reading | Copyright Amazon Web Services; linked, not copied | 15 | `idle-cuts`, `tcp-timers` | 2026-11-11 |
| R6 | High Performance Browser Networking, ch. 3 "Building Blocks of UDP": read "Null Protocol Services" and "UDP and Network Address Translators" up to "NAT Traversal" | https://hpbn.co/building-blocks-of-udp/ | reading | CC BY-NC-ND 4.0 (same footer); linked, not copied | 8 | `udp-behaviour`, `idle-cuts` | 2026-11-11 |
| R7 | Tune NAT configuration (Google Cloud): the default timeouts table | https://docs.cloud.google.com/nat/docs/tune-nat-configuration | reading | CC BY 4.0 (Google Cloud documentation, as the spec's "Before authoring" says; the writer confirms the page footer) | 2 | `idle-cuts`, `udp-behaviour` | 2026-11-11 |
| R8 | ip-sysctl (Linux kernel documentation): the entries `tcp_keepalive_time`, `_probes`, `_intvl`, `tcp_syn_retries`, `tcp_retries2`: reference | https://docs.kernel.org/networking/ip-sysctl.html | reference | GPL-2.0 (kernel documentation); linked | 3 | `tcp-timers` | 2026-11-11 |
| R9 | tcp(7): `TCP_KEEPIDLE`, `TCP_KEEPINTVL`, `TCP_KEEPCNT`, `TCP_USER_TIMEOUT`: reference | https://man7.org/linux/man-pages/man7/tcp.7.html | reference | Linux man-pages project (no licence printed on the page; Module 1 records man-pages as "free documentation; linked, not copied") | 3 | `idle-cuts` | 2026-11-11 |
| R10 | RFC 9293 §3.8.4 "TCP Keep-Alives" and §3.1 header picture: optional | https://www.rfc-editor.org/rfc/rfc9293.html | reference | IETF Trust Legal Provisions; linked, not copied | 4 | `tcp-timers`, `read-a-capture` | 2026-11-11 |
| R11 | RFC 7323 §2 "TCP Window Scale Option": optional | https://www.rfc-editor.org/rfc/rfc7323.html | reference | IETF Trust Legal Provisions; linked, not copied | 5 | `window-math` | 2026-11-11 |

Assigned reading: 48 minutes; optional 24 more. No video was found and verified for this topic's specifics; the writer may add one only after watching it.

## 7. The labs' shape, and what they need from the network-lab base

### 7.1 Topologies (all inside one lab container, as Module 2's `dc1` is)

- **A, "the gateway path"** (worked example, fill-in, build): `lab` (eth1 10.0.1.10) — `nat` (10.0.1.1 | 10.0.2.1, masquerade, connection tracking with a short idle timer, a forward chain that accepts new TCP only with SYN and either resets or drops the rest) — `db` (10.0.2.20, the managed database; in the fill-in also `supplier` 10.0.2.30 with a stateful firewall of its own). Services in the far namespaces run as systemd units with `NetworkNamespacePath=/run/netns/db` (**tried**: boots in 3 s, units active).
- **B, "the long path"** (worked example, debug): `lab` (eth2 10.0.5.1) — `wan` (netem: 50 Mbit/s, 50 ms each way, no loss in this topic) — `dr` (10.0.6.20, the far site, `iperf3 -s` as a unit). In the debug an `edge` namespace (the site's firewall with masquerade and a connection-tracking idle timer) sits between `lab` and `wan`.

The **lab's clock runs fast**: idle timers are 10 to 20 seconds instead of 350 s or 4 minutes, so a check can wait one out. Each prompt says what the number stands for ("the gateway forgets a quiet flow after 15 seconds; AWS's waits 350"). Tried at 30 s; every result in the appendix holds with any timer, and shorter timers keep CI cheap (section 11).

### 7.2 What these labs need from the network-lab base

1. **Machines as namespaces**, with a wrapper to run a command on each (`on-nat`, `on-db`, `on-dr`, `on-edge`, or the base's general `on HOST COMMAND`), as `on-dc` does.
2. **Per-machine settings that survive a reboot**: files under `/etc/netns/HOST/` (an `nftables.conf`, a `sysctl.d/` folder, a `hosts` file), applied by the base's boot script with `ip netns exec HOST nft -f /etc/nftables.conf` and `ip netns exec HOST sysctl --system`. **Tried:** a file written through `ip netns exec dr` to `/etc/sysctl.d/70-receive.conf` lands in `/etc/netns/dr/sysctl.d/` and `ip netns exec dr sysctl --system` applies it.
3. **Packages:** `iproute2` (with `tc`), `tcpdump`, `nftables`, `conntrack`, `python3` (for the stand-in services), all already in the systemd labs' shared first `RUN`; and **`iperf3`** (a 2.97 MB layer). Recommend the base adds `iperf3` to Module 3's shared layer, since topics 29 and 36 use it too. Topic 29's QUIC tools are a topic-only layer (see its brief).
4. **Kernel features** (all autoload on Docker Desktop's 6.18 kernel when first used from a privileged container; none confirmed on GitHub's runners): `sch_netem`, connection-tracking timers per namespace (`net.netfilter.nf_conntrack_tcp_timeout_established`, `…_udp_timeout`, `…_udp_timeout_stream`), nftables' TCP-option reset (`reset tcp option window`), per-namespace TCP sysctls (`tcp_window_scaling`, `tcp_rmem`, `tcp_keepalive_*`). Loading a module this way changes Docker's machine until Docker restarts; the lab page's sentence about privileged containers (ADR-0018 amendment) covers it.
5. **Things to avoid**, found while prototyping: an nftables chain named `fwd` (a keyword; the file fails to load and the ruleset is silently empty); `reject with tcp reset` without `meta l4proto tcp` before it (refused); UDP ports 7000 to 7009 (tcpdump prints them as the AFS protocol, `[|rx]`); `net.core.default_qdisc` (only the first namespace has it; `sysctl -p` fails on it inside a container).

## 8. Practice ladder

In ladder order. Recall items marked ● are also in the review pool; ◇ are review-only (section 10). Captured fixtures are labelled **captured** with their file in `captures/`; the rest **constructed**. Every multiple-choice item below has its four choices written out in full, of similar length, with the right answer not the longest in more than half (counted at the end of section 8).

### 8.1 `example-read-the-conversation` (worked example, systemd lab, topologies A and B), 30 minutes

Prompt: you're handed the shop's app server. `shop-api` keeps one connection to the cloud's managed database through the NAT gateway, and the nightly replication goes to the DR site over a long private link. Type each line and read what it prints. Steps:

1. **"The settings in the SYN"**: `sudo tcpdump -nn -i eth1 -c 10 'tcp port 5432' > ~/example/one-order.txt &`, then `printf 'order 1\n' | nc -N -w 3 10.0.2.20 5432`, `wait`, `cat`. Note: MSS 1460, sackOK, TS, wscale 10 on both SYNs.
2. **"Bytes and their acknowledgements"**: the client's `seq 1:9, length 8`, the server's `ack 9`, its reply `seq 1:12`; relative numbers, and `tcpdump -S -r` isn't needed: the lesson's postcards.
3. **"Who said goodbye first"**: the first `[F.]` is the client's; `ss -tno state time-wait '( dport = :5432 )'` shows the TIME-WAIT socket on the client with `timer:(timewait,…)`.
4. **"A quiet connection is cut"**: `curl -s localhost:8080/order`, `sleep 20`, `curl -s localhost:8080/order` → `"ok": false … Connection reset by peer`; `journalctl -u shop-api -n 3`.
5. **"Who sent that reset?"**: the same with `sudo tcpdump -nn -v -i eth1 'tcp port 5432 and tcp[tcpflags] & (tcp-rst|tcp-syn) != 0' > ~/example/reset.txt &` running: the SYN-ACK from the database has `ttl 63`, the RST that claims to be from it has `ttl 64`.
6. **"The gateway's timer"**: `on-nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established` → 15 (the lab's stand-in for AWS's 350 s); `on-nat conntrack -L -p tcp --dport 5432` shows the entry and its seconds left.
7. **"Keepalives keep it"**: `sudo nano /etc/shop/api.conf`, set `db_keepalive = on` and `db_keepalive_idle = 5`, `sudo systemctl restart shop-api`, an order, then `ss -tno '( dport = :5432 )'` shows `timer:(keepalive,…)`; a capture on `nat`'s outside for 20 s shows empty segments every 5 s; the order after 20 s of quiet works on the same port.
8. **"Window scaling over a long path"**: `iperf3 -c 10.0.6.20 -t 5` → about 45 Mbit/s; `ss -tni dst 10.0.6.20` during it shows `wscale:10,10`; `on-dr sudo sysctl -w net.ipv4.tcp_window_scaling=0`, again → about 5 Mbit/s, and the window arithmetic; `on-dr sudo sysctl -w net.ipv4.tcp_window_scaling=1` to put it back.

Checks (worked examples never open or close a follow-up, ADR-0011 amendment): `one-order.txt` holds both SYNs with `wscale`; `reset.txt` holds an RST with `ttl 64`; `shop-api`'s config has keepalive on with an idle below the gateway's timer; dr's window scaling is back on. Wrong fixes: `scaling-left-off.sh`, `no-ttl-capture.sh` (capture without `-v`), `keepalive-idle-too-long.sh`.

### 8.2 Recall on reading a capture

1. ● **`cap-bytes-each-way`** (`predict_shell`, `read-a-capture`). **Captured** `cap.txt` = the 19 lines of `captures/keepalive-probes-and-teardown.txt` without its comment lines. Prompt: the command adds up the bytes each side sent (the last number on each line is the segment's length), keyed by the sender's port. Command: `awk '{split($3, s, "."); bytes[s[5]] += $NF} END {for (p in bytes) print p, bytes[p]}' cap.txt | sort -n`. Expected (run in Git Bash's gawk 5.4; run again on CI's `awk`):

   ```
   5432 12
   57146 6
   ```

   Explanation: the client sent `seq 1:4` and `4:7`, 6 bytes; the server `1:7` and `7:13`, 12 bytes; its last `ack 14` counts the FIN as one byte. The empty segments every 10 s carry nothing: they're keepalive probes and their answers.
2. **`mcq-who-closed-first`** (`read-a-capture`). Prompt shows the capture's last three lines (`[F.]` from 10.0.1.10.57146, `[F.]` from 10.0.2.20.5432, `[.]` from the client). "Which machine has a socket in TIME-WAIT for the next minute?"
   - "The client, 10.0.1.10: it sent the first FIN, and the side that closes first waits" ✔
   - "The server, 10.0.2.20: it sent the second FIN, so it waits for late copies of the ACK"
   - "Both of them: each sent a FIN, and every side that sends a FIN waits in TIME-WAIT"
   - "Neither: the FINs were answered at once, so both sockets close the moment the ACK lands"
   Explanation: the active closer waits (net-tools taught the minute); the server passes through LAST-ACK and is gone when the final ACK arrives.
3. ● **`mcq-who-sent-the-reset`** (`read-a-capture`). Prompt: three **captured** `tcpdump -v` lines from `captures/forged-reset-ttl.txt` (the SYN with `ttl 64` from 10.0.1.10, the SYN-ACK with `ttl 63` from 10.0.2.20, and 35 s later an `[R]` "from" 10.0.2.20 with `ttl 64`); 10.0.1.1 is the NAT gateway between them. "Who most likely sent the reset?"
   - "The NAT gateway, one hop away, pretending to be the database" ✔
   - "The database's kernel, because the database closed its socket"
   - "A router beyond the database, which forwarded the reset onward"
   - "The client's own kernel, which reset its socket after a timeout"
   Explanation: TTL drops by one per router; the database's packets cross one router and arrive with 63; a packet arriving with 64 started one hop closer. A box in the middle that has forgotten a flow answers in the server's name (AWS's NAT gateway does exactly this, F9). The database's own reset would carry `ttl 63`; the client's kernel's reset would never arrive at its own interface.
4. ● **`mcq-fin-or-reset`** (`read-a-capture`, `idle-cuts`). "An application logs `Connection reset by peer` on the first query after lunch. Which capture fits?"
   - "An `[R]` arrives in answer to the query, with no FIN anywhere before it" ✔
   - "An `[F.]` arrives from the server, the client answers with an `[F.]` of its own"
   - "The query is sent again at 0.2, 0.4 and 0.8 s and nothing at all comes back"
   - "A `[S]` goes out, an `[R.]` comes back, and no data is ever sent on the wire"
   Explanation: a reset in an open connection is the abort; FINs are a goodbye (the app would read end-of-file, not a reset); silent retransmissions end in "timed out"; a reset to a SYN is "refused".
5. **`mcq-what-are-these`** (`read-a-capture`, `idle-cuts`). Prompt: four captured lines, 10 s apart, `Flags [.], ack 7, win 63, … length 0` from the client, each answered by `Flags [.], ack 4 … length 0`. "What are they?"
   - "Keepalive probes: empty segments that make the other side answer" ✔
   - "Retransmissions of bytes the server never acknowledged in time"
   - "Window updates telling the server the client's buffer has room"
   - "Delayed acknowledgements of data that arrived ten seconds before"
   Explanation: no new data, the same `ack` every time, exactly every 10 s of quiet: `TCP_KEEPIDLE=10`. Retransmissions carry data (`length 3`) and their gaps grow.

### 8.3 Recall on windows

6. ● **`est-bdp-cross-region`** (estimate, `window-math`). Prompt: "A replication link between two regions carries 200 Mbit/s and has a round-trip time of 80 ms. How many bytes must one TCP connection be allowed to have in flight to fill it? Within 2%." Unit: bytes. `given: { rate: 200, rtt: 80 }`; `working: rate * 1000000 / 8 * rtt / 1000`; answer 2000000; tolerance `{ percent: 2 }`. Mistakes: `bits-not-bytes` 16000000 (`rate * 1000000 * rtt / 1000`: "that's bits; a window counts bytes, so divide by 8"); `one-way` 1000000 (`rate * 1000000 / 8 * rtt / 2000`: "the data must still be in flight until its acknowledgement comes back: use the whole round trip"). Explanation: 200,000,000 ÷ 8 = 25,000,000 bytes a second × 0.08 s.
7. ● **`est-unscaled-ceiling`** (estimate, `window-math`). Prompt: "A firewall strips the window scale option, so the receiver's window can't exceed 65,535 bytes. The round trip is 40 ms. What's the most one connection can carry, in Mbit/s? Within 2%." `given: { window: 65535, rtt: 40 }`; `working: window * 8 / (rtt / 1000) / 1000000`; answer 13.107. Mistakes: `bytes-a-second` 1.638 (`window / (rtt / 1000) / 1000000`: "that's megabytes a second; a link is sold in megabits"); `seconds-not-ms` 0.013 (`window * 8 / rtt / 1000000`: "40 ms is 0.04 s").
8. ● **`est-scaled-window`** (estimate, `window-math`). Prompt: "In a capture, a receiver's SYN-ACK offered `wscale 7`, and a later segment from it shows `win 1465`. How many bytes may the sender have in flight? Exactly." `given: { shift: 7, field: 1465 }`; `working: field * 2 ** shift`; answer 187520. Mistakes: `ignored-scale` 1465 ("the field is multiplied by 2 to the power of the shift agreed in the SYNs"); `times-shift` 10255 (`field * shift`: "the shift is a power of two: 2^7 is 128").
9. ● **`mcq-stripped-scale`** (`window-math`, `read-a-capture`). Prompt: the two **captured** SYN lines (`at-lab.txt`, `at-dr.txt` of `items/`; the SYN leaving `lab` has `nop,wscale 10`, the SYN arriving at `dr` has `nop,nop,nop,nop`), and "replication runs at 5 Mbit/s on a 50 Mbit/s link with a 100 ms round trip". "What explains both?"
   - "A box between them removes the window scale option from SYNs" ✔
   - "dr's receive buffer is too small for a 100 ms round trip"
   - "The link loses packets, so the sender keeps halving its rate"
   - "lab's congestion control is the wrong one for long paths"
   Explanation: the option leaves `lab` and doesn't arrive, so something in between rewrote it; without it both shifts are zero (RFC 7323) and the window stops at 65,535 bytes: 65,535 × 8 ÷ 0.1 = 5.2 Mbit/s. A small buffer would leave the option in the SYN; loss and congestion control are topic 29's, and neither changes a SYN.
10. ◇ **`est-dr-ceiling`** (estimate, `window-math`). Prompt: "A receiver's SYN-ACK arrives without `wscale`, and its window field reads 65,160. The round trip is 100 ms. At most how many Mbit/s can it receive on one connection? Within 3%." `given: { field: 65160, rtt: 100 }`; `working: field * 8 / (rtt / 1000) / 1000000`; answer 5.2128 (written 5.21). Mistakes: `megabytes` 0.6516.

### 8.4 Recall on timers

11. ● **`est-syn-classic`** (estimate, `tcp-timers`). Prompt: "An older Linux client connects to an address whose firewall drops SYNs. It waits 1 s before resending the SYN, doubles the wait each time, resends 6 times, then waits once more, twice as long as the last wait, and gives up. How many seconds after the first SYN does `connect()` fail? Exactly." `given: { first: 1, resends: 6 }`; `working: 1 + 2 + 4 + 8 + 16 + 32 + 64`; answer 127. Mistakes: `last-resend` 63 (`1 + 2 + 4 + 8 + 16 + 32`: "that's when the last SYN goes out; it then waits 64 s more"); `count` 6 ("that's how many SYNs were resent, not the seconds"). Explanation adds: current kernels resend the first few at 1 s gaps, then double, and give up after 131 s (the lab measured 134); either way, about two minutes, which is why apps set a connect timeout.
12. ● **`est-dead-peer-keepalive`** (estimate, `tcp-timers`, `idle-cuts`). Prompt: "A server uses AWS's suggested keepalive: first probe after 240 s of quiet, then a probe every 60 s, giving up after 3 unanswered probes. Its peer's machine loses power. How many seconds after the last packet does the server close the connection? Exactly." `given: { idle: 240, gap: 60, probes: 3 }`; `working: idle + gap * probes`; answer 420. Mistakes: `idle-only` 240; `one-probe` 300 (`idle + gap`).
13. ● **`est-default-keepalive`** (estimate, `tcp-timers`). Prompt: "With Linux's defaults (first probe after 7,200 s, then up to 9 probes 75 s apart), how many minutes after the last packet does a socket with keepalive on notice its peer is gone? Within 1 minute." `given: { idle: 7200, gap: 75, probes: 9 }`; `working: (idle + gap * probes) / 60`; answer 131.25. Mistakes: `idle-only` 120; `probes-only` 11.25.
14. **`mcq-which-error`** (`tcp-timers`). "A connect takes 2 minutes and then fails. Which message did the application most likely get, and why?"
   - "Connection timed out: SYNs were sent again and again and never answered" ✔
   - "Connection refused: the host answered each SYN with a reset at once"
   - "Connection reset by peer: the host accepted, then aborted the socket"
   - "Network is unreachable: the client has no route to that address"
   Explanation: refused is instant (a reset), reset by peer needs an open connection, unreachable is the client's routing table and is also instant. Two minutes is the SYN retries running out.
15. ● **`mcq-idle-forever`** (`tcp-timers`). "A client holds an idle connection, without keepalive, to a server whose machine is switched off. What does the client's socket do?"
   - "Stays ESTAB until the client next sends; only then do resends start" ✔
   - "Closes after 2 hours, when the system's keepalive timer runs out"
   - "Moves to TIME-WAIT for a minute, then disappears from `ss -tan`"
   - "Gets a reset from the server's network card as the machine powers off"
   Explanation: R2's "Idle ESTAB is forever"; the system's keepalive timer only applies to sockets that switched keepalive on; TIME-WAIT follows a FIN; a powered-off machine sends nothing.
16. ◇ **`est-retries-ceiling`** (estimate, `tcp-timers`). Prompt: "A connection's peer vanishes while data is unacknowledged. The kernel resends after 0.2 s, doubles the wait each time but never waits more than 120 s, and gives up at the end of the 16th wait. How many seconds is that? Within 1 second." `given: { start: 0.2, cap: 120 }`; `working: start * (1 + 2 + 4 + 8 + 16 + 32 + 64 + 128 + 256 + 512) + 6 * cap`; answer 924.6. Mistakes: `no-cap` 13107 (`start * (2 ** 16 - 1)`: "the wait stops growing at 120 s"); `fifteen-waits` 804.6.

### 8.5 Recall on idle cuts

17. ● **`est-smallest-idle`** (estimate, `idle-cuts`). Prompt: "An app's database connection crosses an Azure NAT gateway (TCP idle timeout 4 minutes), a firewall appliance (forgets idle flows after 300 s) and arrives at a database in another network whose firewall tracks a flow while it sends at least one packet every 10 minutes. Below how many seconds must the keepalive's first probe come? Exactly." `given: { nat: 4, appliance: 300, far: 10 }`; `working: min(nat * 60, appliance, far * 60)`; answer 240. Mistakes: `largest` 600 ("every box on the path must remember it: the smallest timer wins"); `minutes` 4 ("the question asks for seconds").
18. ● **`mcq-sysctl-alone`** (`idle-cuts`). "A team set `net.ipv4.tcp_keepalive_time = 240` on every server, but database connections are still cut behind a 350-second NAT. What's the likely reason?"
   - "The database client never switches keepalive on for its sockets" ✔
   - "The setting only takes effect after the database server restarts"
   - "Keepalive probes are dropped by the NAT gateway as empty packets"
   - "240 seconds is too close to 350 for a probe to arrive in time"
   Explanation: the system value is only the default for sockets with `SO_KEEPALIVE`; the fix is the driver's switch (PostgreSQL's `keepalives=1`, F13). The sysctl is read when the timer is armed, not at a database restart; the NAT counts probes as traffic (F15: they look like duplicate ACKs); 240 leaves 110 s.
19. **`mcq-reset-or-hang`** (`idle-cuts`). "After a quiet hour, the first query fails at once with a reset on AWS but hangs for the app's whole 30-second timeout on Azure. Which change would make Azure's behave like AWS's?"
   - "Turn on TCP reset on idle for the Azure load balancer's rule" ✔
   - "Raise the Azure load balancer's idle timeout from 4 to 30 minutes"
   - "Lower the client's `tcp_syn_retries` so it gives up sooner"
   - "Send the query over UDP so that no connection has to be kept"
   Explanation: Azure's default drops silently (F14) and the client retransmits into the void; with TCP reset both ends hear at once. A longer idle timeout moves the problem, doesn't change the symptom; SYN retries are for new connections; UDP doesn't fix a database protocol.
20. **`mcq-proxy-in-the-path`** (`idle-cuts`). "Clients reach an API through AWS's ALB. Clients enable TCP keepalives every 30 s; long-polling requests still end after 60 s of silence. Why?"
   - "The ALB ends the client's TCP connection there, so probes stop at it" ✔
   - "TCP keepalives are only sent on connections that carry no requests"
   - "The ALB counts only HTTP/2 PING frames as activity, not TCP probes"
   - "A 30-second gap is too long for the ALB's 60-second idle timeout"
   Explanation: a layer 7 load balancer terminates TCP (topic 33 says more); its idle timer counts data, not TCP probes, and the AWS page says it doesn't count HTTP/2 PING either (F11). Send at least a byte of data in the response, or raise the idle timeout (1 to 4,000 s).
21. ● **`ss-keepalive-timers`** (`predict_shell`, `idle-cuts`). **Constructed** `ss.txt` in `ss -tno`'s layout (the `119min` and `10sec` forms were seen in the lab; `4min59sec` is the documented form): four ESTAB connections, `timer:(keepalive,119min,0)`, `timer:(keepalive,9.6sec,0)`, no timer, `timer:(keepalive,4min59sec,0)`. Command: `awk 'NR > 1 {k = "off"; if (match($0, /keepalive,[^,]*/)) k = substr($0, RSTART + 10, RLENGTH - 10); print $5, k}' ss.txt`. Expected:

   ```
   10.0.2.20:5432 119min
   10.0.2.20:5432 9.6sec
   10.0.2.20:5432 off
   10.0.2.30:6000 4min59sec
   ```

   Explanation: which survive a 350-second NAT? The 9.6-second and 299-second timers come first; the 2-hour timer and the socket with none are cut. `ss -o` shows time *left* until the next probe; on a fresh or just-probed connection that's the idle setting.
22. ◇ **`mcq-raise-the-timer`** (`idle-cuts`). "Why does Azure advise against raising its NAT gateway's TCP idle timeout from 4 to 120 minutes to fix idle cuts?"
   - "Each idle flow holds its SNAT port longer, so ports run out sooner" ✔
   - "Flows idle for longer than 4 minutes are reset by the virtual network"
   - "The longer timer only applies to new connections made after a restart"
   - "Keepalives stop working once the timer is longer than an hour"
   Explanation: F15; topic 27's port exhaustion, met again.
23. ◇ **`est-probe-count`** (estimate, `idle-cuts`, `tcp-timers`). Prompt: "Keepalive starts after 200 s of quiet and probes every 20 s. You want a dead peer noticed no later than 300 s after the last packet. What's the largest probe count you can set? Exactly." `given: { idle: 200, gap: 20, limit: 300 }`; `working: (limit - idle) // gap`; answer 5. Mistakes: `whole-limit` 15 (`limit // gap`); `nat-instead` 7 (`(350 - idle) // gap`, "350 is the NAT's timer, not your limit").

### 8.6 Recall on UDP

24. ● **`udp-closed-or-dropped`** (`predict_shell`, `udp-behaviour`). **Captured** `udp.txt` = `captures/udp-closed-and-dropped.txt` (6 lines: two datagrams to 5301 each answered by ICMP unreachable, two to 5302 with no answer). Command: `grep -o '\.530[0-9]: UDP\|udp port [0-9]* unreachable' udp.txt | sort | uniq -c`. Expected:

   ```
         2 .5301: UDP
         2 .5302: UDP
         2 udp port 5301 unreachable
   ```

   Explanation: port 5301 has nothing listening and the host says so with ICMP; port 5302 is dropped by a firewall and nothing comes back; `nc -u` exited 0 for both (F25): a UDP sender can't tell unless it reads the ICMP or waits for an application's answer.
25. **`mcq-udp-what-it-gives`** (`udp-behaviour`). "Which of these does UDP do for an application?"
   - "Keeps each datagram whole: one send arrives as one receive, or not at all" ✔
   - "Resends a datagram once if no reply arrives within the round-trip time"
   - "Delivers datagrams in the order they were sent, holding back early ones"
   - "Tells the sender when a datagram was dropped by a firewall on the path"
   Explanation: message boundaries are the one thing UDP keeps; no resends, no ordering, no notice of a drop (ICMP only for a closed port, and only if nothing filters it).
26. ● **`mcq-udp-push-through-nat`** (`udp-behaviour`, `idle-cuts`). "A client behind Google Cloud NAT (UDP mappings kept 30 s) subscribes once to a feed that pushes an update every 60 s. What happens, and what fixes it?"
   - "No update arrives; the client sends a small datagram every 20 s or so" ✔
   - "Every update arrives; a UDP mapping lasts as long as the subscription"
   - "Only the first update arrives; the NAT resets the flow after it passes"
   - "Updates arrive late; raise the client's receive buffer so none are lost"
   Explanation: the mapping expires 30 s after the subscription; the push 60 s later finds no mapping and the NAT drops it. Keepalive datagrams from the client refresh the mapping (and Cloud NAT may expire it 5 s early, F16). A NAT doesn't reset UDP, and buffers don't help packets that never arrive. The build lab does exactly this.
27. ◇ **`mcq-when-udp`** (`udp-behaviour`). "Which workload is UDP the right choice for?"
   - "A video call, where a frame that arrives late is no better than one lost" ✔
   - "A database's replication stream, where every change must arrive in order"
   - "A file download, where the user waits for the last byte before using it"
   - "An API call that must not be applied twice if the network repeats it"
   Explanation: real-time media would rather drop than wait for a resend; the others need TCP's guarantees (or QUIC's, next topic).

### 8.7 `fill-keepalive-under-the-timeout` (fill-in, systemd lab, topology A with `supplier`), 25 minutes, skills `idle-cuts`, `tcp-timers`

Story: `stock-sync` on `lab` holds one connection to the supplier's API (10.0.2.30:6000) through the shop's NAT gateway (`nat`: forgets a quiet flow after 20 s, resets the inside end) and the supplier's own firewall (`supplier`: forgets after 12 s, drops silently). After a quiet spell, the next sync fails. Starter files, `...` in each gap:

```
# /etc/sysctl.d/60-keepalive.conf
# Keepalive timers for every program on this machine that switches keepalive on.
net.ipv4.tcp_keepalive_time = ...
net.ipv4.tcp_keepalive_intvl = ...
net.ipv4.tcp_keepalive_probes = 3

# /etc/stock-sync.conf
supplier = 10.0.2.30:6000
keepalive = ...
```

Prompt (the fill-in's rules): find each box's timer yourself (`on-nat sysctl …`, `on-supplier sysctl …`, as the worked example showed); fill the gaps so that the connection survives any quiet spell, a supplier that goes dark is noticed within 45 s of the last packet, and it all lasts after a reboot. Say which gaps make the file unreadable (a `...` in a sysctl file is an invalid value: `systemd-sysctl` logs it and ignores the line, so nothing changes until it's filled). Checks:

| Check | What it tests |
| --- | --- |
| `quiet-spell` (`timeout: 45`) | a sync, 17 s of quiet, a sync: the second succeeds on the same local port, at least 2 empty segments and no data crossed `nat`'s outside during the quiet (the `check-quiet.sh` pattern, **tried**) |
| `from-the-files` | each live `net.ipv4.tcp_keepalive_*` equals what `systemd-sysctl --cat-config` says the files set (so `sysctl -w` alone fails) |
| `noticed-in-time` | live time < 12 and time + intvl × probes ≤ 45 |
| `switched-on` | `ss -tno` shows a `keepalive` timer on stock-sync's connection, and `/etc/stock-sync.conf` says `keepalive = on` |
| `boxes-as-they-were` | `nat`'s and `supplier`'s rulesets equal their shipped files loaded into a throwaway namespace, and their timers still read 20 and 12 |

Wrong fixes (each fails the check in brackets): `beats-nat-only.sh` (time 18: under 20, over 12 [`quiet-spell`, `noticed-in-time`]); `switch-left-off.sh` [`quiet-spell`, `switched-on`]; `runtime-only.sh` (`sysctl -w`, starter file untouched [`from-the-files`]); `slow-to-notice.sh` (time 10, intvl 30 [`noticed-in-time`]); `supplier-timer-raised.sh` (`on-supplier sysctl …=3600` plus a time of 18 [`boxes-as-they-were`]). Restart trial: `docker restart`, the five checks pass again (the **tried** persistence result in A7 says they will).

### 8.8 `write-syn-check` (write, plain lab), 35 minutes, skills `read-a-capture`, `window-math`

Prompt: when a long transfer is slow, an engineer captures the same connection's SYN on both sides of a box. Write `~/bin/syn-check BEFORE AFTER` (two files of `tcpdump -nn` text) that prints one line for each of `mss`, `sackOK`, `TS` and `wscale`: the option's name, its value before and after the box (`none` where it's missing; `yes` for `sackOK` and `TS` when present), and nothing else. For a box that strips window scaling: `wscale 10 none`. With anything other than two files, a usage line and a non-zero exit. Write it from a blank file with `nano`, try it on the three pairs in `/srv/captures/`, then run the checks, which also try it on pairs it hasn't seen.

Hints (the practice ladder may hint): the SYN is the line with `Flags [S],`; `grep -o 'wscale [0-9]*'` pulls one option out; `sed -n 's/.*mss \([0-9]*\).*/\1/p'` is another way; a function called once for each file keeps the script short.

Checks: on each of `/srv/captures/{clean,stripped,clamped}` the output equals the check's own `grep -o` over the same files; and on three hidden pairs (root-only under `/usr/local/lib/lab/hidden/`, as `write-steal-pct` does): one where `sackOK` was removed, one where MSS was clamped from 1460 to 1360, one with both window scaling and timestamps removed. Usage check as in `write-steal-pct`.

The pairs are **captured**, made by the author with the lab of appendix A6 and nftables' `reset tcp option window`, `reset tcp option sack-perm`, `reset tcp option timestamp` and `tcp option maxseg size set 1360`. Only the first was tried; the author tries the other three before writing the lab (open question 6). Wrong fixes: `before-only.sh` (reads one file twice), `first-line-not-syn.sh` (takes line 1, which in two of the pairs is an ARP line), `no-none.sh` (prints an empty value), `hard-coded-clean.sh`.

### 8.9 Ladder order for `topic.yaml`

`example-read-the-conversation`, `cap-bytes-each-way`, `mcq-who-closed-first`, `mcq-who-sent-the-reset`, `mcq-fin-or-reset`, `mcq-what-are-these`, `est-bdp-cross-region`, `est-unscaled-ceiling`, `est-scaled-window`, `mcq-stripped-scale`, `est-syn-classic`, `est-dead-peer-keepalive`, `est-default-keepalive`, `mcq-which-error`, `mcq-idle-forever`, `est-smallest-idle`, `mcq-sysctl-alone`, `mcq-reset-or-hang`, `mcq-proxy-in-the-path`, `ss-keepalive-timers`, `udp-closed-or-dropped`, `mcq-udp-what-it-gives`, `mcq-udp-push-through-nat`, `fill-keepalive-under-the-timeout`, `write-syn-check`.

That is 22 recall items in practice (3 `predict_shell`, 7 estimates, 12 multiple choice) and 5 review-only (◇). Multiple choice: 14 items in all. Measured on the choices as drafted above (characters as the page shows them, backticks removed; `items/mcqlen.py`-style count run 2026-11-11): the right answer is the longest choice in 3 of 14 (`mcq-which-error`, `mcq-proxy-in-the-path`, `mcq-udp-what-it-gives`; three more tie), and the largest ratio of right to longest wrong is 1.04. The writer counts again after editing, since the validator holds the line (content/README, "Tips for questions").

## 9. Proofs

### 9.1 Build: `build-quiet-path` (systemd lab, topology A plus a feed), 50 minutes, skills: `idle-cuts`, `tcp-timers`, `udp-behaviour`

From a written brief on a fresh app server, no starter files to fill. The brief states only goals:

1. **The order connection survives every quiet spell.** `shop-api` keeps one pooled connection to `orders-db` (10.0.2.20) through the NAT gateway and the database subnet's firewall. Find both boxes' idle timers (lab numbers: `nat` 18 s with resets, `db` firewall 11 s with silent drops: different from every practice item). Keepalive must be switched on for `shop-api`'s connection and start below the smaller timer, and a dead database must be noticed within 60 s of the last packet.
2. **The price feed keeps arriving.** `feed-client` subscribes once to the supplier's UDP feed (10.0.2.20:5005), which pushes an update every 25 s; the NAT forgets a UDP mapping after 10 s (the lab's stand-in for Cloud NAT's 30 s). Updates must keep arriving.
3. **A dead standby is reported in seconds.** `shop-api`'s health page tries the standby database (10.0.2.21, powered off: its firewall drops SYNs). It must report the standby down within 5 seconds, not after two minutes, using only `shop-api`'s own settings.
4. **Nothing weakened, nothing temporary.** The two boxes stay as they are (they stand for the cloud's); `shop-api` keeps one connection rather than opening one per order; the machine's other programs keep the system's connect behaviour; everything survives a reboot.

Checks and their `test_skills`-style mapping (the topic's skill each one tests):

| Check | Tests | Skill |
| --- | --- | --- |
| `orders-after-quiet` (`timeout: 45`) | order, 16 s quiet, order on the same port, only empty segments crossed `nat` | `idle-cuts` |
| `keepalive-under-both` | the effective idle (socket or system) < 11; the switch on in `/etc/shop/api.conf` | `idle-cuts` |
| `dead-db-noticed` | effective idle + gap × count ≤ 60 | `tcp-timers` |
| `feed-arrives` (`timeout: 60`) | a new update appears in `journalctl -u feed-client` within 30 s, and client datagrams cross `nat`'s outside at gaps under 10 s | `udp-behaviour` |
| `standby-in-seconds` (`timeout: 20`) | `curl localhost:8080/health/standby` answers "down" in ≤ 6 s | `tcp-timers` |
| `system-connects-unchanged` | `net.ipv4.tcp_syn_retries` is still 6 | `tcp-timers` |
| `one-connection` | `ss -tn dst 10.0.2.20:5432` shows exactly one ESTAB from `shop-api` before and after two orders | `idle-cuts` |
| `boxes-as-they-were` | `nat` and `db` rulesets and timers as shipped | `idle-cuts` |
| `lasts` | every setting the other checks read comes from a file (`systemd-sysctl --cat-config`, the two config files) | `idle-cuts` |

Wrong fixes (8): `keepalive-only-beats-nat.sh` (idle 15), `system-default-without-switch.sh`, `feed-keepalive-too-slow.sh` (12 s), `syn-retries-lowered.sh` (`tcp_syn_retries = 1` in `/etc/sysctl.d`, no app setting), `new-connection-per-order.sh` (sets the stand-in's `db_pool = off`), `nat-udp-timer-raised.sh`, `db-firewall-flushed.sh`, `runtime-only.sh`. Restart trial before `ready`.

Lab mechanics **tried**: the TCP part (A7: reference fix and an alternative pass; seven shortcuts each fail the intended check; the restart trial passes for the persistent fixes and fails the runtime-only one), the UDP part (A8: no updates without a keepalive datagram, every update with one). Not yet tried: the health page's standby probe (`shop-api` stand-in feature: `create_connection(timeout=db_connect_timeout)`), and the `db` namespace's own conntrack timer (the same mechanism as `nat`'s).

### 9.2 Debug: `debug-slow-replication` (systemd lab, topology B with `edge`), 45 minutes, skills `window-math`, `idle-cuts`, `read-a-capture`

Prompt (what the system is for, the symptom, the count; never what or where): every night `lab` replicates the shop's database to the DR site, `dr1` (10.0.6.20), over a private link of 50 Mbit/s with a 100 ms round trip, and `repl-agent` keeps a status connection open to dr1's API on port 8443. The site firewall, `edge`, sits between `lab` and the link: it lets `lab` reach out, lets nothing in, and translates `lab`'s address. Since a firewall replacement last month, replication runs at about a tenth of the link's speed, and the status connection drops after quiet spells. **There are three faults.** You may change `lab`, `edge` and `dr1`; `on-edge` and `on-dr` run commands there. The rules: `edge` keeps refusing connections from outside and keeps its 15-second idle timer (it stands for a managed firewall's); the link stays as it is; fixes last after a reboot. `iperf3 -c 10.0.6.20 -t 5` measures the link the way replication uses it; `journalctl -u repl-agent` shows the status connection.

The faults, for the writer:

1. **`edge` strips window scaling.** Its `/etc/netns/edge/nftables.conf` has a `normalise` chain with `tcp flags syn reset tcp option window` (**tried**, A6: 5.05 Mbit/s).
2. **dr1's receive buffer is capped.** `/etc/netns/dr/sysctl.d/60-tuning.conf` sets `net.ipv4.tcp_rmem = 4096 87380 174760`, copied from an old tuning guide (with scaling restored, about 7 Mbit/s: A5 measured 7.25 at a 131,072 cap).
3. **The status connection's keepalive is overruled at boot.** `/etc/sysctl.d/50-repl.conf` sets `tcp_keepalive_time = 10`, but `/etc/sysctl.d/99-vendor-tuning.conf` sets it back to 7200, and later files win; `repl-agent` switches keepalive on and relies on the system's time.

Checks (descriptions state end states only; the page lists them after a first try, #235):

| Check | End state | Fails for fault |
| --- | --- | --- |
| `replication-speed` (`timeout: 30`) | one `iperf3` connection, 6 s, receives at least 40 Mbit/s | 1, 2 |
| `scaling-reaches-dr` | a SYN captured on dr1's side carries `wscale` | 1 |
| `dr-buffers-last` | dr1's live `tcp_rmem` maximum is at least 1,000,000 and equals what its files set | 2 |
| `status-after-quiet` (`timeout: 45`) | the status connection survives 20 s of quiet on the same port, with only empty segments crossing `edge` | 3 |
| `keepalive-from-files` | the live keepalive time equals the files' final value, and is under 15 | 3 |
| `edge-still-guards` | from dr1, `nc -z -w 2` to listeners of the check's own on `lab` (ports 22, 8080, 9999) gets no answer for the whole timeout; `lab` still leaves as `edge`'s address; `edge`'s timer still reads 15 | shortcuts |
| `link-as-it-was` | `on-wan tc qdisc show` equals the shipped settings | shortcut |

Wrong fixes (9): `edge-flushed.sh` (scaling restored by deleting every rule), `edge-timer-raised.sh`, `link-shortened.sh` (netem delay removed), `dr-buffers-runtime-only.sh` (`sysctl -w` on dr1), `keepalive-runtime-only.sh`, `keepalive-in-50-only.sh` (`sysctl -p 50-repl.conf`, passes until the reboot the check imitates by comparing with the files), and three two-of-three fixes. Prove under `labcheck test` that each fault alone turns only its own checks red (the table's last column), as Module 2's plan asked of topic 17's debug.

### 9.3 Explain

Prompt: "A company moved an app from its data centre to a cloud. Two things broke. The first database query after a quiet lunch hour fails with 'Connection reset by peer', and a nightly copy to another region runs at a tenth of the link's speed. Explain, in your own words: how you'd read a capture of the database connection to find out who sent the reset, and how a box in the middle can send one that looks like the database's; why idle connections get cut in a cloud, what the NAT gateways and load balancers of two clouds do by default, and how keepalives fix it, including what has to be true of the application for the system's keepalive setting to matter; how the receive window and window scaling limit one connection over a long path, with the bandwidth-delay product worked for an example of your own; and, if you can, how a UDP flow through the same NAT differs."

Rubric rows: `capture` (required: SYN options, FIN against RST, TTL of the forged reset), `idle-cuts` (required: stateful boxes forget quiet flows, the endpoints aren't told, reset or silent drop), `keepalive-fix` (required: below the smallest timer on the path; the application must switch keepalive on; persist the setting; heartbeat where a proxy sits), `window` (required: throughput ≤ window ÷ RTT, BDP = rate × RTT with numbers, 65,535 bytes without scaling, a box that strips the option), `clouds-differ` (required: two correct defaults and behaviours, e.g. AWS NAT gateway 350 s with a reset to the inside, Azure load balancer 4 minutes with a silent drop unless TCP reset is on, Google Cloud NAT 20 minutes), `udp` (optional: short UDP timers, keepalive datagrams from the client).

## 10. Review pool

21 items; every skill has at least four.

| Skill | Items |
| --- | --- |
| `read-a-capture` | `cap-bytes-each-way`, `mcq-who-sent-the-reset`, `mcq-fin-or-reset` (and `mcq-stripped-scale`) |
| `window-math` | `est-bdp-cross-region`, `est-unscaled-ceiling`, `est-scaled-window`, ◇ `est-dr-ceiling` |
| `tcp-timers` | `est-syn-classic`, `est-dead-peer-keepalive`, `est-default-keepalive`, ◇ `est-retries-ceiling`, `mcq-idle-forever` |
| `idle-cuts` | `est-smallest-idle`, `mcq-sysctl-alone`, `ss-keepalive-timers`, ◇ `mcq-raise-the-timer`, ◇ `est-probe-count` |
| `udp-behaviour` | `udp-closed-or-dropped`, `mcq-udp-push-through-nat`, ◇ `mcq-when-udp` |

Mostly production, not recognition: 10 estimates and 3 `predict_shell` among 21. Estimate items per calculation skill, practice and review together: `window-math` 4, `tcp-timers` 5, `idle-cuts` 3 (ADR-0024 rule 6 asks for 3). Follow-up candidates per skill (recall plus fill-in and write): `read-a-capture` 7, `window-math` 6, `tcp-timers` 8, `idle-cuts` 12, `udp-behaviour` 4.

## 11. Platform work

Nothing new in the content model: `estimate` (ADR-0024), per-check `timeout:` (ADR-0018's second amendment) and `predict_shell` exist. What these labs need first:

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| T1 | The network-lab base (section 7.2) | the five items listed there; this topic's labs can carry their own `network.sh` until the base exists, as the windows-ad labs do | every lab here |
| T2 | **A CI spike on GitHub's runners** | one pull request with `example-read-the-conversation` and `debug-slow-replication`: does `tc qdisc add … netem` autoload `sch_netem` from a privileged container on `ubuntu-latest`? (Ubuntu may ship it in `linux-modules-extra-$(uname -r)`, not confirmed.) Does `reset tcp option window` work? If netem is missing, a step in `.github/workflows/labs.yml` installs the extra modules package and runs `sudo modprobe sch_netem` before the tests (free; the merging note for workflow files applies) | the debug, topic 29's labs |
| T3 | CI time | see section 12; no change to the shard count expected | — |

Decided against: a stand-in tool that prints made-up captures in the learner's shell (Module 2's 3.4); a real-cloud lab (section 12).

## 12. Cost and time

**Money: nothing.** Every lab is local. A real AWS NAT gateway would show the same 350-second cut, but it bills by the hour and by the gigabyte, and the local gateway reproduces the documented behaviour (a reset to the inside end) exactly; no cloud run is proposed, now or later.

**Learner's time:** lesson 15, assigned reading 48, 22 recall items at 1.5 minutes 33, worked example 30, fill-in 25, write 35, build 50, debug 45, explain 20: **about 300 minutes** (`estimated_minutes: 300`). If it runs long in the owner's first pass, `mcq-udp-what-it-gives` and `mcq-proxy-in-the-path` move to the review pool (−3 minutes) before anything else.

**CI time** (from the prototypes' timings: a systemd boot 3 to 8 s, a quiet-spell check its timer plus 5 s, an `iperf3` check 6 s):

| Lab | Runs (pristine + solution + wrong) | Seconds a run | Serial minutes |
| --- | --- | --- | --- |
| `example-read-the-conversation` | 5 | 60 | 5 |
| `fill-keepalive-under-the-timeout` | 7 | 40 | 5 |
| `write-syn-check` (plain) | 6 | 15 | 1.5 |
| `build-quiet-path` | 10 | 75 | 12.5 |
| `debug-slow-replication` | 11 | 50 | 9 |

About 33 serial minutes, 8 to 10 on one shard with four jobs. Image: the shared systemd layer plus 2.97 MB for `iperf3`; no topic-only layer.

## 13. Open questions, each with a recommendation under the owner's rule

1. **The lab's fast clock.** Timers of 10 to 20 s stand for 350 s and 4 minutes. *Recommend:* yes, said in every prompt with the real number beside it; it keeps each check under a minute and CI cheap, and the behaviour is identical (A7 at 30 s).
2. **`prerequisites:`** *Recommend* `[csa.net.nat]` (and the module's gate through it); topic 29 then depends on this topic.
3. **The SYN timeout fact.** Sources say 127 s (older kernels, most books) and 131 s (current kernel docs); the lab measured 134 s. *Recommend:* teach "about two minutes", state the schedule in every estimate item, and quote the kernel page's 131 s with its date.
4. **Teaching `sysctl` and `/etc/sysctl.d/`.** Modules 1 and 2 never mention them. *Recommend:* the routing topic (26) introduces them with `net.ipv4.ip_forward`, the first place a learner needs one; if it doesn't, this lesson gives them one paragraph (topic 29 and Module 4 need them again). The module merge decides.
5. **The write lab's hidden captures** need three nftables option rewrites not yet tried (`sack-perm`, `timestamp`, `maxseg size set`). *Recommend:* the author tries them before writing; if any fails, use a pair captured from a real MSS-clamping setup (MSS clamping on the `edge` namespace with `tcp option maxseg size set rt mtu`) or drop that pair; the write still has three seen and two hidden pairs.
6. **Checkpoint 3 part 2** asks for "an intermittent outage caused by three faults". *Recommend to the checkpoint designer:* one of the three is this topic's idle cut (a keepalive above a NAT's idle timer: fails only after quiet spells, which is what "intermittent" looks like in practice), with `test_skills` `csa.net.transport/idle-cuts`; this brief's `check-quiet.sh` pattern checks it.
7. **The QUIC idle timeout** (`max_idle_timeout`, 30 s from Caddy) is topic 29's; this topic mentions only that QUIC rides on UDP and so meets the same UDP timers.

## Appendix: what was tried in Docker (2026-11-11, Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2)

All containers were named `tcproto-*` and images `tcproto-*:1`; all were removed at the end (`docker ps -a` and `docker images` show none). Scripts are in `prototypes/transport-congestion/`.

- **A1 Kernel defaults** (privileged `ubuntu:24.04`): `tcp_available_congestion_control` "reno cubic" until first use; keepalive 7200 75 9; `tcp_syn_retries` 6, `tcp_syn_linear_timeouts` 4, `tcp_retries2` 15, `tcp_fin_timeout` 60; `tcp_rmem` 4096 131072 33554432; conntrack sysctls present per namespace, TCP established 432000, UDP 30, UDP stream 120; `net.core.default_qdisc` absent inside the container.
- **A2 The idle cut** (`idle/mech.sh`, `idle/client.py`, `idle/server.py`): `lab` → `nat` (masquerade, `nf_conntrack_tcp_timeout_established=30`, forward chain: established accept; new TCP from inside only with SYN; the rest `meta l4proto tcp reject with tcp reset`) → `db`. Keepalive off, 40 s idle: the second query fails at once, `[Errno 104] Connection reset by peer`; capture: the query `[P.] seq 4:7` answered by `[R]`. With `-v`: the SYN-ACK from 10.0.2.20 `ttl 63`, the RST "from" 10.0.2.20 `ttl 64`. Keepalive idle 10 s: probes every 10.2 s, each answered; the query after 40 s works; teardown `[F.]`, `[F.]`, `[.]` (the capture in `captures/`). Keepalive switched on with the system's 7200 s: `ss -tno` shows `timer:(keepalive,119min,0)` and the cut happens. With `drop` instead of the reset: the query is retransmitted at +0.21, 0.42, 0.85, 1.7, 3.3 s, the app times out after 8 s, the socket sits in FIN-WAIT-1 retransmitting. Also seen: lowering `tcp_keepalive_time` affects an existing socket's next timer (a script slip set it back to 7200 mid-test and the connection was then cut), so the timer reads the system value when it's armed. Masquerade kept the client's port.
- **A3 SYN timeout:** connect to a port the gateway drops: SYNs at 0, 1.0, 2.0, 3.0, 4.1, 5.1, 7.1, 11.2, 19.4, 35.5, 68.5 s; `Connection timed out` after 134.1 s. To an address with no host: `No route to host` after 3.1 s (the router's ICMP).
- **A4 UDP:** `nc -u -w1` to a closed port: one datagram, ICMP "udp port 5301 unreachable", exit 0; to a dropped port: datagrams, nothing back, exit 0; a connected Python socket's second send: `[Errno 111] Connection refused`. Ports 7001 and 7002 printed as `[|rx]` (AFS), so the lab avoids 7000 to 7009. UDP mapping (`nat` UDP timers 20 s, `idle/udpfeed.py`, pushes every 25 s): no updates at all without a client keepalive; with a keepalive datagram every 10 s, updates at 13.8, 38.8, 63.8 s.
- **A5 Windows** (`cc/wan.sh`: `lab` → `wan` netem → `dr`; 50 Mbit/s, 50 ms each way, limit 2000, no loss): CUBIC 44.6 Mbit/s; `dr` `tcp_window_scaling=0` (per namespace; the root namespace still 1): 5.05; `dr` `tcp_rmem` max 131072: 7.25.
- **A6 A box that strips the option:** in `wan`, `table inet strip { chain forward { type filter hook forward priority mangle; tcp flags syn reset tcp option window } }`: at `lab` the SYN has `nop,wscale 10` and the SYN-ACK none; at `dr` the SYN has `nop,nop,nop,nop`; 5.05 and 4.86 Mbit/s.
- **A7 The systemd lab** (`sysd/`: `lab-network.service` builds `nat`, `db`, `wan`, `dr`; `orders-db.service` and `backup-sink.service` with `NetworkNamespacePath=`; `shop-api` with `/etc/shop/api.conf`): started as `labcheck` starts a systemd lab (`--privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock … /sbin/init`), `running` after 3 s. `check-quiet.sh 38` (order, 38 s quiet with a capture on `nat`'s outside, order): pristine → reset; nine fixes in nine containers at once: reference (app keepalive on, idle 10, gap 5, count 3) **kept alive**; app switch on plus `/etc/sysctl.d/60-keepalive.conf` time 10 **kept alive**; idle 45 → reset; system time 10 with the switch off → reset; switch on with no time → reset; gateway timer raised to 3600 → "no keepalive probes crossed the gateway"; gateway forward chain flushed to accept → the same; a heartbeat loop of orders every 10 s → "orders or other data crossed the gateway during the quiet spell (6 packets)"; switch on with `sysctl -w` → kept alive. **Restart trial** (`docker restart`, boot about 8 s): reference kept alive; sysctl-file fix kept alive (`systemd-sysctl` applied `/etc/sysctl.d` at boot, time 10); `sysctl -w` fix → reset (time back to 7200).
- **A8** (see A4's UDP mapping result.)
- **Images:** the shared systemd layer was cached; the `iperf3` layer is 2.97 MB; image 328 MB in all.

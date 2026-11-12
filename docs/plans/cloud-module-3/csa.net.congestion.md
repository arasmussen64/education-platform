# Writing brief: `csa.net.congestion` (topic 29), Congestion control and QUIC

Design only. Nothing here is in the repository yet. Sources were read on 2026-11-11; each fact carries its URL and date. Lab mechanics marked **tried** were run in Docker on the owner's machine (Docker Desktop 29.8.2, kernel `6.18.33.2-microsoft-standard-WSL2`, 8 CPUs) on 2026-11-11, and everything started was removed. Prototypes, scripts and captures: `scratchpad/cloud/m3-design/prototypes/transport-congestion/` (`cc/`, `sysd/`, `quic/`, `quic-sysd/`, `captures/`, `items/`); the appendix lists what was run and what it printed.

Read with `csa.net.transport.md` (topic 28): this topic uses its windows, round trips, bandwidth-delay product and UDP, and shares its lab topologies (that brief's section 7).

**The question the task asked first: are throughput numbers reliable enough to check?** Yes, as thresholds placed in the middle of a wide gap, not as values. On a 50 Mbit/s path with a 50 ms round trip and 1% random loss, CUBIC delivered 3.3 to 7.2 Mbit/s and BBR 43.4 to 45.7 Mbit/s across 14 runs, including runs with four and nine lab containers measuring at once (appendix B2, B3). The gap is six-fold at its narrowest, so a check of "at least 25 Mbit/s" passes every BBR run by 1.7 times and fails every CUBIC run by 3.4 times. CUBIC's own numbers are noisy (8.9 to 45.7 Mbit/s at 0.1% loss), so no check ever compares a CUBIC number with a value. Window-limited and round-trip-limited numbers are exact (5.05 Mbit/s for a 64 KiB window; first byte at 0.305 s and 0.205 s at a 100 ms round trip, to the millisecond), and those are what estimate items and fine-grained checks use. Not yet confirmed on GitHub's runners (platform work C2).

## 1. What the learner will be able to do

1. Explain the two limits on how fast a sender may send: the receiver's window (topic 28) and the congestion window, the sender's guess at what the network can carry; read both in `ss -tni`.
2. Explain slow start, congestion avoidance and CUBIC, and why a loss-based algorithm slows down on a long path that loses packets at random; work out roughly what such a connection can carry from its round trip and loss rate, and what changes it.
3. Explain what BBR measures and does instead, show the difference on a lossy path, name its costs (retransmissions, fairness to CUBIC), and set a sender's congestion control so that it lasts, knowing that only the sending side's choice matters.
4. Explain what QUIC changes: one handshake for transport and encryption, streams that don't block each other, connection IDs that survive an address change, and an encrypted transport that boxes in the middle can't read or meddle with; read what a capture and a client's own log show of it.
5. Explain how HTTP/3 is found (Alt-Svc, HTTPS DNS records), what happens when UDP port 443 is blocked, when HTTP/3 helps and when it doesn't, and what the three clouds offer; turn it on for a server and its firewall.

**The six-month core.**

- A sender has at most **min(congestion window, receive window)** in flight. **Slow start** doubles the congestion window every round trip from 10 segments, so short transfers are counted in round trips, not bandwidth.
- **Loss-based** congestion control (Reno, CUBIC: the default almost everywhere) reads every loss as congestion. Its ceiling falls with the round trip and with the square root of the loss rate, about **1.2 × MSS ÷ (RTT × √p)**: twice the distance, half the speed; four times the loss, half the speed.
- **BBR** measures the bottleneck's delivery rate and the path's shortest round trip and sends at that rate. On a long, lossy path it can be many times faster (45 against 5 Mbit/s in the lab), at the cost of more retransmissions and an unfair share against CUBIC. **The sender chooses**; Linux's BBR is version 1.
- **QUIC** is TCP's job plus TLS 1.3 in one handshake over UDP: the first byte arrives **one round trip sooner**; one lost packet stalls only its own stream; a **connection ID** survives a new address; almost everything is encrypted.
- **HTTP/3** is advertised with **Alt-Svc** (or an HTTPS DNS record); with **UDP 443 blocked, browsers fall back to HTTP/2 without a word**. The clouds end HTTP/3 at their edge and speak HTTP/1.1 or HTTP/2 to backends.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.net.transport]`.

**Built on, never repeated:** topic 28's sequence and acknowledgement numbers, receive window and window scaling, RTT and the bandwidth-delay product, retransmissions, keepalives and idle timers, UDP and middleboxes' UDP timers, `ss -tni`, `/etc/sysctl.d/`, the "lab's fast clock". Module 1's `tcpdump`, nftables (`policy drop`, sets, `/etc/nftables.conf`, saved against running rules), `curl -I`, `systemctl reload`. Topic 23's MTU (QUIC's 1,200-byte minimum).

**Ordering note for the module merge.** Topic 31 (`csa.net.http-tls`) is where HTTP/1.1, 2 and 3 and the TLS handshakes are taught properly, after this topic. This topic says only what it needs: HTTP/2 runs many requests ("streams") over one TCP connection; TLS is the encryption layer, and TLS 1.3 needs one round trip before the first request; an HTTPS DNS record is a record a browser can look up to learn a site speaks HTTP/3 (topic 30 teaches records). Topic 31 then refers back here for QUIC instead of re-teaching it. The HTTP/3 designers should agree this split.

**Terms this topic must define itself:** congestion; **congestion window (cwnd)**; **slow start**, **slow-start threshold (ssthresh)**, **initial window**; **congestion avoidance**, **AIMD** (add a little each round trip, cut by a fraction on loss); **Reno**, **CUBIC**; **loss rate**; **bufferbloat** (queues that fill and add delay); **BBR**, **bottleneck bandwidth**, **minimum RTT** (the path's own delay without queues), **pacing** (spacing packets out instead of sending bursts); **congestion control as a sender's setting** (`net.ipv4.tcp_congestion_control`, `TCP_CONGESTION`, `iperf3 -C`); **QUIC**, **stream**, **head-of-line blocking**, **multiplexing**, **0-RTT** (resumed connections only), **connection ID**, **connection migration**, **ossification** (boxes that only let through what they recognise, so a protocol can't change; topic 28's stripped window scale is an example); **HTTP/3**, **Alt-Svc** and its `ma`, **HTTPS DNS record**, **fallback**; **netem** and **iperf3** (the lab's tools, one sentence each).

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `loss-based-cc` | The congestion window against the receive window; slow start from 10 segments doubling each round trip; congestion avoidance and AIMD; Reno halving and CUBIC's 0.7 cut and cubic regrowth; why random loss and long round trips slow loss-based algorithms; bufferbloat; reading `cwnd`, `ssthresh` and `retrans` in `ss -tni` |
| `bbr-model` | BBR's model (the highest recent delivery rate, the shortest recent round trip), pacing, its four states; Linux's BBR doesn't react directly to loss; its costs (retransmissions, an unfair share against CUBIC); version 1 in Linux, version 3 in the IETF draft; congestion control is the sender's choice, set for good in `/etc/sysctl.d/`, per socket, or for one test with `iperf3 -C` |
| `loss-latency-math` | Calculation: the loss-based ceiling 1.2 × MSS ÷ (RTT × √p) and its two scalings; a window in flight per round trip as a rate; slow start's growth; parallel connections; transfer time; which limit binds (link, window, loss) |
| `quic-changes` | QUIC's handshake (one round trip to the first request, against two for TCP with TLS 1.3), streams without cross-stream head-of-line blocking, connection IDs and migration, encryption of almost everything, the 1,200-byte first datagram and the three-times limit, QUIC's own idle timeout and middleboxes' UDP timers; what `tcpdump` shows (UDP lengths) and what a client's own log shows |
| `http3-in-practice` | Discovery through Alt-Svc (`h3=":443"; ma=…`) and HTTPS DNS records; silent fallback to HTTP/2 when UDP 443 is blocked; a firewall needs `udp dport 443`; when HTTP/3 helps (lossy, mobile, far away, many requests) and when it doesn't; the clouds' support, and that it ends at their edge |

`loss-latency-math` is the calculation skill (8 estimate items, counting the two it shares); `loss-based-cc`, `bbr-model` and `quic-changes` also have estimates (2, 1 and 1). Every skill has at least five questions that can come back.

## 4. Lesson plan

**4.1 Two limits, two windows.** Topic 28's receive window is the receiver saying how much it can take. The **congestion window** is the sender's own guess at how much the network between can take; the sender keeps at most the smaller of the two in flight. *Resource:* HPBN ch. 2, "Congestion Avoidance and Control" opening. *The lesson supplies* the picture:

> The receive window is the size of the warehouse at the far end; the congestion window is how many lorries the sender dares put on the motorway at once. A sender that doesn't know the motorway starts with a few lorries and adds more until some get stuck.

**4.2 Slow start.** A new connection starts with 10 segments (about 14,600 bytes, RFC 6928) and, for every segment acknowledged, adds one, which doubles the window each round trip (RFC 5681) until it sees a loss or reaches the slow-start threshold. *Resource:* HPBN "Slow-Start" with "Increasing TCP's Initial Congestion Window". *The lesson supplies* the consequence in numbers: after 5 round trips the window is 10 × 2^5 = 320 segments; in its first 4 round trips a connection can deliver at most (10 + 20 + 40 + 80) × 1,448 = 217,200 bytes; so a small web page's time is mostly round trips, which is why distance matters even on a fast link.

**4.3 Congestion avoidance, Reno and CUBIC.** After slow start the window grows slowly and is cut on a loss. Reno adds one segment a round trip and halves on a loss: the sawtooth. CUBIC, Linux's default since 2006 and the default in Windows and Apple's stacks too (RFC 9438), cuts to 0.7 of the window, then grows back along a cubic curve: fast at first, flat near where the last loss happened, then probing past it; its growth depends on time since the loss, not on the round trip. *Resource:* HPBN "Congestion Avoidance"; RFC 9438 §1 optional. *The lesson supplies* the central flaw in one line: **a loss-based algorithm treats every lost packet as a sign of congestion**, including the packet a noisy Wi-Fi link or a long-haul path loses at random. Its ceiling: standard TCP's average window is about 1.2 ÷ √p segments (RFC 3649), one window per round trip, so about **1.2 × MSS ÷ (RTT × √p)**. On the lab's path (1,448-byte segments, 50 ms, 1%) that's 2.8 Mbit/s for Reno; CUBIC measured 3.3 to 7.2, somewhat better, the same shape. Say plainly that CUBIC beats the formula and that the formula is for the shape, not the number.

**4.4 Bufferbloat.** With deep queues, a loss-based sender keeps adding until the queue overflows, so a full link also has a long queue: Google's measurement, median RTT 1,090 ms with CUBIC against 43 ms with BBR on a 10 Mbit/s, 40 ms path with a 1,000-packet buffer (S2). One paragraph; no lab.

**4.5 BBR.** *Resources:* Google Cloud's 2017 post (S2) and the header comment of Linux's `tcp_bbr.c` (S3). BBR keeps a model of the path, the highest delivery rate over the last ten round trips and the shortest round trip over the last ten seconds, sends at that rate (pacing), and keeps about one bandwidth-delay product in flight. It moves through STARTUP (doubling to find the rate), DRAIN (emptying the queue it made), PROBE_BW (most of its life) and PROBE_RTT (a brief dip to re-measure the round trip). Linux's own description: "The core algorithm does not react directly to packet losses or delays." *The lesson supplies* the lab's own numbers and their cost: on the 1%-loss path BBR delivered about 45 Mbit/s against CUBIC's 5, and retransmitted about 300 packets in 8 seconds against CUBIC's 30. Then the cautions: BBR (version 1, Linux's) can take more than a fair share from CUBIC flows on a shared link and causes steady loss behind traffic policers (S4); version 3, specified in the IETF draft (S11, intended Experimental), reacts once loss passes 2% a round trip; whether version 3 is in mainline Linux could not be confirmed, and the evidence says not (fact G9). Google uses BBR for google.com, YouTube, and traffic from its Cloud CDN and load balancers to users (S2).

**4.6 Who chooses, and how it's set.** Congestion control runs where data is **sent from**: switching a server that *receives* uploads to BBR changes nothing for those uploads (**tried**: BBR set on the receiver, 3.8 to 5.2 Mbit/s, the same as CUBIC). Set for good in `/etc/sysctl.d/` (`net.ipv4.tcp_congestion_control = bbr`; the kernel loads the module on first use and again at every boot), per program with `TCP_CONGESTION`, or for one test with `iperf3 -C bbr`. *The lesson supplies* the trap the lab hits: Google's and many guides' recipes also set `net.core.default_qdisc = fq`, which a container can't set (only the machine's first network namespace has it; `sysctl -p` prints an error and `systemd-sysctl` logs one and carries on). Linux's BBR paces by itself without `fq` ("otherwise TCP stack falls back to an internal pacing", S3), so the lab's fix leaves it out and the lesson says why.

**Where the three clouds differ on congestion control:** a VM's choice is its image's (CUBIC on Ubuntu, Debian and the other common Linux images; the lab's Ubuntu 24.04 image's default is `cubic`); Google's front ends use BBR toward users (S2); AWS and Azure publish nothing comparable in the pages read, so the lesson claims nothing for them.

**4.7 QUIC: why.** *Resource:* HTTP/3 explained (S5), "TCP head of line blocking", "Ossification", "TCP or UDP". *The lesson supplies* the picture of head-of-line blocking:

> Six images ride one TCP connection as six streams. TCP is one queue of numbered postcards (topic 28): if card 40 is lost, cards 41 to 60 wait in the pile even if they belong to other images, because TCP only hands over bytes in order. QUIC numbers each stream on its own, so only the stream that lost a packet waits.

And ossification, with the learner's own example: the firewall in topic 28 that stripped a TCP option. Boxes that read and rewrite TCP headers are why TCP can hardly change; QUIC encrypts almost all of its own headers so boxes can't.

**4.8 QUIC: what.** *Resource:* S5, "Fast handshakes", "Connections". QUIC runs over UDP, in the application rather than the kernel, with TLS 1.3 built into its handshake: one round trip and the first request can go (TCP needs one for its handshake and TLS 1.3 one more). A resumed connection can even send in its first flight (0-RTT), with a caveat that such data can be replayed, which topic 31 explains. Each connection has **connection IDs**, so when a phone's address changes the server still recognises it (only clients migrate, RFC 9000). *The lesson supplies* what the learner will see:

- **On the wire** (`tcpdump`, **captured**): only `UDP, length 1200`, `length 1252`, … The client's first datagram is padded to 1,200 bytes (RFC 9000 requires it); the server may send at most three times what it has received before the client's address is validated. Everything else is encrypted; Ubuntu 24.04's `tcpdump` doesn't even label it QUIC.
- **In the client's own log** (ngtcp2's `gtlsclient`, **captured**): `type=Initial` packets with `CRYPTO` and `PADDING` frames, then `type=Handshake`, the server's transport parameters (`max_idle_timeout=30000`: QUIC's own idle timer, the smaller of the two sides' values), "QUIC handshake has completed" at about one round trip, and `[:status: 200]` at about two.
- **Round trips, measured:** over a 100 ms path, `curl -w` shows TCP connected at 0.101 s, TLS done at 0.205 s and the first byte at 0.305 s; over HTTP/3 the handshake completed at about 0.101 s and the response arrived at 0.205 s.
- **Idle timers again:** QUIC rides on UDP, so a NAT's UDP timer (topic 28: often 30 s) can cut a quiet QUIC connection before QUIC's own timer; RFC 9000 says sending something every 30 seconds keeps most middleboxes' state, with PING frames.

**4.9 HTTP/3 in practice.** *Resources:* S5 "Bootstrap with Alt-svc"; the clouds' pages (S8, S9, S10). A browser first reaches a site over TCP; the response carries `alt-svc: h3=":443"; ma=2592000` (HTTP/3 on UDP port 443, remember it for 30 days; without `ma`, 24 hours, RFC 7838), and the browser tries HTTP/3 next time; or it learns it from an HTTPS DNS record (`alpn=h3`, RFC 9460) before connecting at all. If UDP 443 is blocked, the browser silently stays on HTTP/2: **tried**, the HTTP/3 client timed out while `curl` over TCP answered "hello over HTTP/2.0". So turning HTTP/3 on is two changes: the server must listen on UDP 443 and advertise it, and every firewall on the path must allow `udp dport 443`. When it helps: far-away and mobile users, lossy links, pages with many requests, phones changing networks. When it doesn't: clean links inside a data centre, one big download, networks that block UDP; and it costs servers more CPU than TCP (S5 "Common criticism", optional).

**Where the three clouds differ on HTTP/3** (facts G19 to G23): CloudFront offers HTTP/3 to viewers, with connection migration, and can use Route 53 HTTPS records; AWS's NLB passes QUIC through to targets untouched since 2025-11-13, keeping a connection on one target by its connection ID; Google's global external Application Load Balancer advertises HTTP/3 by default ("Automatic"), not on the regional one; Azure Application Gateway's HTTP/3 is in **preview** (front end only), and Azure Front Door's FAQ lists HTTP, HTTPS and HTTP/2 only. Every load balancer that terminates HTTP/3 speaks HTTP/1.1 or HTTP/2 to the backends.

**Recap:** the two windows; slow start's doubling; loss-based ceiling and its scalings; BBR's model, costs and version; who sets it and the `/etc/sysctl.d/` line; QUIC's five changes; Alt-Svc, fallback, `udp dport 443`; the clouds' table.

## 5. Verified facts

Read on 2026-11-11 unless marked **measured**.

| # | Fact | Source |
| --- | --- | --- |
| G1 | RFC 9438, August 2023, Standards Track, obsoletes RFC 8312: β_cubic SHOULD be 0.7 (Reno's 0.5); C SHOULD be 0.4; W_cubic(t) = C(t − K)³ + W_max; "CUBIC has been adopted as the default TCP congestion control algorithm by the Linux, Windows, and Apple stacks"; window growth independent of RTT outside the Reno-friendly region | https://www.rfc-editor.org/rfc/rfc9438.html |
| G2 | Slow start is used when cwnd < ssthresh; during it cwnd grows by at most SMSS per ACK of new data; congestion avoidance adds about SMSS×SMSS/cwnd per ACK; on loss ssthresh = max(FlightSize/2, 2×SMSS) | RFC 5681 §3.1, https://www.rfc-editor.org/rfc/rfc5681.txt |
| G3 | Initial window min(10×MSS, max(2×MSS, 14,600)): 10 segments, at most 14,600 bytes | RFC 6928, https://www.rfc-editor.org/rfc/rfc6928.txt |
| G4 | "the current Standard TCP's average congestion window is roughly 1.2/sqrt(p) segments" | RFC 3649 §1 and §5, https://www.rfc-editor.org/rfc/rfc3649.txt |
| G5 | Linux `tcp_bbr.c` header: bottleneck_bandwidth = windowed max of delivered/elapsed over 10 round trips; min_rtt = windowed min over 10 s; pacing_rate = pacing_gain × bandwidth; cwnd = max(cwnd_gain × bandwidth × min_rtt, 4); "The core algorithm does not react directly to packet losses or delays"; states STARTUP, DRAIN, PROBE_BW, PROBE_RTT; with fq "with pacing enabled, otherwise TCP stack falls back to an internal pacing"; SPDX GPL-2.0 OR BSD-3-Clause | https://raw.githubusercontent.com/torvalds/linux/master/net/ipv4/tcp_bbr.c |
| G6 | draft-ietf-ccwg-bbr-07, 2 November 2026, "specifies version 3 of the BBR algorithm, BBRv3"; intended status Experimental; authors Cardwell, Swett (Google), Beshay (Meta); BBR.LossThresh 2%; BBR.Beta 0.7; min_rtt filter 10 s | https://datatracker.ietf.org/doc/draft-ietf-ccwg-bbr/ |
| G7 | Google Cloud blog, Cardwell and Cheng, 2017-07-20: BBR models delivery rate and RTT; CUBIC about 3.3 Mbit/s against BBR over 9,100 Mbit/s on a 10 Gbit/s, 100 ms path with 1% loss; median RTT 1,090 ms against 43 ms on a 10 Mbit/s, 40 ms path with a 1,000-packet buffer; YouTube about 4% more throughput and 33% lower RTT; used for google.com, YouTube, Cloud CDN and Cloud Load Balancing traffic to users | https://cloud.google.com/blog/products/networking/tcp-bbr-congestion-control-comes-to-gcp-your-internet-just-got-faster |
| G8 | Huston, APNIC blog, 2017-05-09: BBR can push CUBIC back and keep the larger share on some paths; behind token-bucket policers BBR's probing causes continuous loss | https://blog.apnic.net/2017/05/09/bbr-new-kid-tcp-block/ |
| G9 | Mainline Linux's BBR is version 1: a bbr-dev thread of March 2025 says net-next and mainline still have BBR 1.x; Google's v3 is a separate branch (github.com/google/bbr, `v3`). **Not confirmed for November 2026**; consistent with G5's header text and with the lab's behaviour (hundreds of retransmissions at full rate) | https://groups.google.com/g/bbr-dev/c/4vwZGw0nxdQ (via search, 2026-11-11), https://github.com/google/bbr/blob/master/README.md |
| G10 | `tcp_congestion_control` sets the algorithm for new connections, default from the kernel's configuration; `tcp_available_congestion_control` lists registered ones, "More congestion control algorithms may be available as modules, but not loaded"; `tcp_allowed_congestion_control` limits unprivileged programs | https://docs.kernel.org/networking/ip-sysctl.html |
| G11 | `TCP_CONGESTION` sets the algorithm per socket; unprivileged processes are restricted to the allowed list | tcp(7), https://man7.org/linux/man-pages/man7/tcp.7.html |
| G12 | iperf3: `-C, --congestion` "Set the congestion control algorithm (Linux and FreeBSD only)"; `-t` duration (default 10 s); `-P` parallel streams; `-R` reverse; `-J` JSON; `-u` UDP. BSD-style licence (LBNL, repository LICENSE) | https://software.es.net/iperf/invoking.html, https://raw.githubusercontent.com/esnet/iperf/master/LICENSE |
| G13 | netem: delay, `loss random` ("Each packet loss is independent"), `rate` emulates a fixed link speed, `limit` caps the queue; rate accuracy depends on the kernel clock; "for TCP performance test results to be realistic netem must be placed on the ingress of the receiver host" (the labs put it on a separate router namespace, so it is neither sender nor receiver) | https://man7.org/linux/man-pages/man8/tc-netem.8.html |
| G14 | QUIC: clients pad datagrams carrying Initial packets to at least 1,200 bytes of UDP payload; before validation a server sends at most three times what it received; "QUIC MUST NOT be used if the network path cannot support a maximum datagram size of at least 1200 bytes"; at a 1,280-byte path, 1,252 bytes for IPv4 and 1,232 for IPv6; connection migration uses connection IDs and "Only clients are able to migrate in this version of QUIC"; the effective idle timeout is the minimum of both sides' `max_idle_timeout`; PING frames defer it; "sending packets every 30 seconds is necessary to prevent the majority of middleboxes from losing state for UDP flows" | RFC 9000 §1, §5.1, §8.1, §10.1, §14, https://www.rfc-editor.org/rfc/rfc9000.txt |
| G15 | HTTP/3 over QUIC; its example `Alt-Svc: h3=":50781"` | RFC 9114, https://www.rfc-editor.org/rfc/rfc9114.txt |
| G16 | An alternative service advertised by Alt-Svc "is considered fresh for 24 hours from generation of the message. This can be modified with the "ma" (max-age) parameter" | RFC 7838 §3.1, https://www.rfc-editor.org/rfc/rfc7838.txt |
| G17 | HTTPS records can carry `alpn=h3` (examples `@ 7200 IN HTTPS 1 . alpn=h3`) | RFC 9460, https://www.rfc-editor.org/rfc/rfc9460.txt |
| G18 | HTTP/3 explained is under CC BY 4.0 (the repository's LICENSE: "Attribution 4.0 International") | https://http3-explained.haxx.se/, https://raw.githubusercontent.com/bagder/http3-explained/master/LICENSE |
| G19 | CloudFront: for HTTP/3 viewers need TLS 1.3 and SNI; "CloudFront supports HTTP/3 connection migration"; Route 53 HTTPS records allow protocol negotiation in DNS | https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesGeneral.html |
| G20 | AWS NLB, 2025-11-13: QUIC in passthrough mode, "preserving session stickiness through QUIC Connection ID"; all commercial and GovCloud (US) regions; no extra charge, within UDP LCUs | https://aws.amazon.com/about-aws/whats-new/2025/11/aws-network-load-balancer-quic-passthrough-mode |
| G21 | Google Cloud: HTTP/3 on the global external Application LB and the classic one in Premium Tier, not the regional external or Standard Tier; "for connections between clients and the load balancer", not to backends; example `alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000`; `quicOverride` NONE (default, "Automatic"), ENABLE, DISABLE; a client's fallback "doesn't count as a load balancer failure" | https://docs.cloud.google.com/load-balancing/docs/https |
| G22 | Azure Application Gateway HTTP/3: "currently in preview"; "HTTP/3 applies only to frontend client connections. Backend connections continue to use HTTP/1.1"; needs a TLS 1.3 policy; no CLI, PowerShell or Terraform during preview (ms.date 2026-09-09) | https://learn.microsoft.com/en-us/azure/application-gateway/http3-quic-support |
| G23 | Azure Front Door FAQ: "Azure Front Door supports HTTP, HTTPS, and HTTP/2"; HTTP/2 to clients by default, HTTP/1.1 to origins (except gRPC preview routes) (ms.date 2026-11-02). **Disagreement:** a third-party article claims Front Door speaks HTTP/3; nothing official found; teach the FAQ | https://learn.microsoft.com/en-us/azure/frontdoor/front-door-faq |
| G24 | Caddy: `servers > protocols` accepts `h1 h2 h2c h3`, default `h1 h2 h3`; `local_certs` issues from Caddy's own CA; `skip_install_trust` stops it installing that CA. Apache-2.0 | https://caddyserver.com/docs/caddyfile/options, https://raw.githubusercontent.com/caddyserver/caddy/master/LICENSE |
| G25 | nginx's QUIC and HTTP/3 support "since 1.25.0"; the module isn't built by default; Ubuntu 24.04 ships nginx 1.24.0 | https://nginx.org/en/docs/quic.html; Ubuntu 24.04 `apt-cache policy nginx` (**measured**, A-packages) |
| G26 | Ubuntu 24.04 (noble) packages, 2026-11-11: `curl` 8.5.0, Features list without HTTP3; `caddy` 2.6.2 (universe); `python3-aioquic` 0.9.25; `ngtcp2-client` 0.12.1 (provides `/usr/bin/gtlsclient`); `iperf3` 3.16; `haproxy` 2.8.30 (QUIC support not checked); `tshark` 4.2.2; `tcpdump` 4.99.4 prints QUIC as "UDP, length N" and has no `-T quic` | **measured** (B6) |
| G27 | ngtcp2 is MIT-licensed; aioquic BSD-style ("Copyright (c) Jeremy Lainé. All rights reserved." with its LICENSE) | https://raw.githubusercontent.com/ngtcp2/ngtcp2/main/COPYING, https://raw.githubusercontent.com/aiortc/aioquic/main/LICENSE |
| G28 | BBR and netem autoload on Docker Desktop: before first use `reno cubic`; after `sysctl -w net.ipv4.tcp_congestion_control=bbr` in a privileged container, `reno cubic bbr`, and `tcp_bbr`, `sch_netem`, `sch_tbf`, `sch_fq`, `sch_htb` appear in `/proc/modules` | **measured** (B1) |
| G29 | Throughput, 50 Mbit/s with 25 ms each way: no loss CUBIC 46.4, BBR 46.1; 1% loss CUBIC 4.7 to 6.6, BBR 44.1 to 45.2; 50 ms each way, 1%: CUBIC 1.4 to 7.4, BBR 41.2 to 42.8; 25 ms each way, 0.1%: CUBIC 8.9 to 45.7, BBR 45.7 to 45.9 | **measured** (B2) |
| G30 | Round trips over a 100 ms path: HTTP/2 over TCP and TLS 1.3, connect 0.1007, TLS 0.2052, first byte 0.3059 s (three runs within 1 ms); HTTP/3 handshake complete at 101 to 103 ms and response at 205 ms (ngtcp2 log timestamps) | **measured** (B7) |

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 (main) | High Performance Browser Networking, ch. 2 "Building Blocks of TCP": read "Slow-Start" (with "Slow-Start Restart" and "Increasing TCP's Initial Congestion Window"), "Congestion Avoidance" and "Head-of-Line Blocking" (about 1,800 words) | https://hpbn.co/building-blocks-of-tcp/ | reading | CC BY-NC-ND 4.0 (page footer); linked, not copied | 14 | `loss-based-cc`, `loss-latency-math`, `quic-changes` | 2026-11-11 |
| S2 | "TCP BBR congestion control comes to GCP – your Internet just got faster", Cardwell and Cheng, Google Cloud blog, 2017-07-20 | https://cloud.google.com/blog/products/networking/tcp-bbr-congestion-control-comes-to-gcp-your-internet-just-got-faster | reading | No licence stated (Google's site terms); linked, not copied | 11 | `bbr-model`, `loss-based-cc` | 2026-11-11 |
| S3 | Linux kernel, `net/ipv4/tcp_bbr.c`: the comment at the top (about 450 words) | https://raw.githubusercontent.com/torvalds/linux/master/net/ipv4/tcp_bbr.c | reading | GPL-2.0 OR BSD-3-Clause (its SPDX line); linked, not copied | 4 | `bbr-model` | 2026-11-11 |
| S4 | "BBR, the new kid on the TCP block", Geoff Huston, APNIC blog, 2017-05-09: optional, sections "AIMD and TCP Reno", "CUBIC", "BBR", "Sharing" | https://blog.apnic.net/2017/05/09/bbr-new-kid-tcp-block/ | reading | No licence stated (© the author and APNIC); linked, not copied | 14 | `loss-based-cc`, `bbr-model` | 2026-11-11 |
| S5 | HTTP/3 explained, Daniel Stenberg: "TCP head of line blocking", "Ossification", "TCP or UDP", "Fast handshakes", "Connections", "Bootstrap with Alt-svc" (1,871 words); "Common criticism" optional (479) | https://http3-explained.haxx.se/ | reading | CC BY 4.0 (repository LICENSE); linked (could be quoted with attribution, but the platform's rule is to link) | 15 | `quic-changes`, `http3-in-practice` | 2026-11-11 |
| S6 | External Application Load Balancer overview (Google Cloud): the HTTP/3 section | https://docs.cloud.google.com/load-balancing/docs/https | reading | CC BY 4.0 (Google Cloud docs; confirm the footer) | 3 | `http3-in-practice` | 2026-11-11 |
| S7 | Distribution settings (CloudFront): "Supported HTTP versions" | https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesGeneral.html#DownloadDistValuesSupportedHTTPVersions | reading | Copyright Amazon Web Services; linked | 2 | `http3-in-practice` | 2026-11-11 |
| S8 | HTTP/3 support in Azure Application Gateway (Preview): optional | https://learn.microsoft.com/en-us/azure/application-gateway/http3-quic-support | reading | CC BY 4.0 (MicrosoftDocs/azure-docs); linked | 6 | `http3-in-practice` | 2026-11-11 |
| S9 | RFC 9438 (CUBIC) §1 and §4.1 to 4.6: optional | https://www.rfc-editor.org/rfc/rfc9438.html | reference | IETF Trust Legal Provisions; linked | 10 | `loss-based-cc` | 2026-11-11 |
| S10 | RFC 9000 (QUIC) §5.1, §9 (first page), §10.1, §14: optional reference | https://www.rfc-editor.org/rfc/rfc9000.html | reference | IETF Trust Legal Provisions; linked | 10 | `quic-changes` | 2026-11-11 |
| S11 | BBR Congestion Control, draft-ietf-ccwg-bbr-07: optional, the abstract and §1 | https://datatracker.ietf.org/doc/draft-ietf-ccwg-bbr/ | reference | IETF Trust Legal Provisions; linked | 5 | `bbr-model` | 2026-11-11 |
| S12 | Invoking iperf3 (ESnet): reference for `-C`, `-t`, `-P` | https://software.es.net/iperf/invoking.html | reference | © ESnet (page); iperf3's code is BSD-style | 2 | `bbr-model` | 2026-11-11 |

Assigned: S1, S2, S3, S5, S6, S7: 49 minutes. Optional: 45 more.

**Could not be opened, so not resources:** the BBR paper in ACM Queue (`queue.acm.org/detail.cfm?id=3022184`) and its CACM version both answered HTTP 403 to automated fetches on 2026-11-11, and Cloudflare's "What is HTTP/3?" learning page did too. They are well known and probably fine in a browser; a writer who opens one can add it, recording its licence (ACM's papers are © ACM). The Queue paper is cited by S3's header, which is how this brief refers to it.

## 7. The labs' shape

Topology **B** (topic 28 brief, 7.1) with loss: `lab` (eth2 10.0.5.1) — `wan` (netem on the data direction: `rate 50mbit delay 25ms loss 1% limit 2000`; on the return: `delay 25ms limit 2000`) — `dr` (10.0.6.20, `iperf3 -s` as `backup-sink.service` with `NetworkNamespacePath=/run/netns/dr`). And topology **C**: `lab` runs the shop's site with **Caddy** (Ubuntu's packaged `caddy.service`, **tried** under systemd in a booted lab) on `shop.test`; the office (`from-office`, Module 1's pattern) is the client, with `/etc/netns/office/hosts` naming `shop.test`, and in the worked example a netem delay on each side of its link so the round trip is 100 ms.

Needs beyond topic 28's list (that brief's 7.2):

1. A **topic-only second `RUN`**, identical in all five of this topic's labs: `caddy python3-aioquic ngtcp2-client ca-certificates` (63.3 MB layer, 44 s to build uncached on the owner's PC). Plus `iperf3` if the network-lab base hasn't taken it.
2. **`h3get`** (scenery, in `/usr/local/bin`): a 40-line Python program on aioquic that makes one HTTP/3 request and prints the status, headers and body (the prototype `quic/h3get.py`, **tried**). Needed because Ubuntu 24.04's `curl` can't speak HTTP/3. The lesson says what it is.
3. **`wan-set RATE DELAY LOSS`** (scenery, worked example only): the WAN's console, as Module 1's `lab-launch` stands in for a cloud console; it runs `tc qdisc change` in `wan` and always exits 0.
4. **The site's certificate trusted at boot:** a boot step copies Caddy's local root (`/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt` under the packaged service) into `/usr/local/share/ca-certificates/` and runs `update-ca-certificates`, so `curl` and `h3get` in the office verify without flags. Add `skip_install_trust` to the Caddyfile (without it Caddy logs "failed to install root certificate" at every start, harmless but alarming).
5. **Kernel:** `tcp_bbr` loaded on first use (from `/etc/sysctl.d` at boot as well: **tried** through a restart), `sch_netem`. Nothing special for QUIC (it's UDP); `quic-go` warns that it can't raise UDP buffer sizes in a container (`net.core.rmem_max` is the first namespace's), harmless at these speeds.

## 8. Practice ladder

● review pool too; ◇ review-only. Captured fixtures are in `captures/`; commands were run in Git Bash (gawk 5.4) with these exact outputs; run each again with CI's `awk` before committing.

### 8.1 `example-cubic-meets-loss` (worked example, systemd lab, topologies B and C), 40 minutes

1. **"Read the path"**: `on-wan tc qdisc show` (rate, delay, loss on `b0`; delay on `a0`), `ping -c 4 10.0.6.20` (about 50 ms).
2. **"A clean path first"**: `wan-set 50mbit 25ms 0%`; `iperf3 -c 10.0.6.20 -t 6` (about 46 Mbit/s); in a second shell during it, `ss -tni dst 10.0.6.20`: `cubic`, `cwnd`, `rtt`.
3. **"One packet in a hundred"**: `wan-set 50mbit 25ms 1%`; again (about 5 Mbit/s); the `Retr` column; `cwnd` near 23.
4. **"The same path, BBR"**: `iperf3 -c 10.0.6.20 -t 6 -C bbr` (about 45); `ss -tni` shows `bbr:(bw:…,mrtt:50,…)`; `sysctl net.ipv4.tcp_available_congestion_control` now lists `bbr`, loaded on first use.
5. **"Twice the distance"**: `wan-set 50mbit 50ms 1%`; both again (CUBIC lower and noisier, BBR about 42); then `wan-set 50mbit 25ms 1%` to put it back.
6. **"Write it down"**: `~/example/results.txt`, three lines `cubic-clean N`, `cubic-lossy N`, `bbr-lossy N`.
7. **"HTTP/3 on the same server"**: `from-office curl -sI https://shop.test/` (`alt-svc: h3=":443"; ma=2592000`); `from-office h3get https://shop.test/` ("hello over HTTP/3.0").
8. **"What the wire shows"**: `sudo tcpdump -nn -i eth1 -c 6 udp port 443 > ~/example/quic-wire.txt &`, `from-office h3get https://shop.test/ > /dev/null`, `wait`: lengths 1200, 1252, …
9. **"What the client sees"**: `from-office gtlsclient --exit-on-all-streams-close shop.test 443 https://shop.test/ 2> ~/example/quic.log`, then `grep -E 'type=(Initial|Handshake) |handshake has completed|max_idle_timeout|:status' ~/example/quic.log`. Say that `gtlsclient` is ngtcp2's example program and doesn't check certificates.
10. **"Count the round trips"**: `from-office curl -so /dev/null -w '%{time_connect} %{time_appconnect} %{time_starttransfer}\n' https://shop.test/ > ~/example/rtt.txt` (0.10, 0.20, 0.30); in `quic.log`, the `I00000…` numbers are milliseconds: handshake complete near 101, `:status` near 205.

Checks: `results.txt` has three numbers with `cubic-lossy` under half of `bbr-lossy` (the learner's own runs; a walkthrough never opens a follow-up); the WAN is back to 1% (the debug and build depend on it); `quic.log` has "QUIC handshake has completed" and `:status: 200`; `rtt.txt`'s three numbers are within 20% of 0.1, 0.2 and 0.3. Wrong fixes: `wan-left-clean.sh`, `no-quic-log.sh`, `rtt-on-the-server.sh` (`curl` run on `lab`, where the round trip is under 1 ms).

### 8.2 Recall on loss-based congestion control

1. ● **`est-slow-start-window`** (estimate, `loss-based-cc`). "A new connection starts with a congestion window of 10 segments and, in slow start, doubles it every round trip. If nothing is lost, how many segments is the window after 5 round trips? Exactly." `given: { start: 10, rounds: 5 }`; `working: start * 2 ** rounds`; answer 320. Mistakes: `added` 60 (`start + rounds * start`: "slow start doubles; adding 10 a round trip is congestion avoidance's shape, and even that adds one, not ten"); `one-short` 160 (`start * 2 ** (rounds - 1)`).
2. ● **`mcq-cubic-after-loss`** (`loss-based-cc`). "CUBIC sees a loss while its window is 100 segments. What does it do next?"
   - "Cuts the window to 70 segments, then regrows it on a curve that flattens near 100" ✔
   - "Cuts the window to 50 segments, then adds one segment for every round trip after"
   - "Cuts the window to 1 segment and starts slow start again, doubling every round trip"
   - "Keeps the window at 100 segments, since a single loss isn't proof of congestion"
   Explanation: β 0.7, then the cubic curve (G1); halving and one-a-round-trip is Reno; back to 1 segment is what follows a retransmission timeout, not a single loss; keeping the window is closer to BBR.
3. ● **`ss-read-cwnd`** (`predict_shell`, `loss-based-cc`, `bbr-model`). **Captured** `sstni.txt` = the two connection lines of `captures/ss-tni-cubic-bbr.txt` (each an `ESTAB` line and its indented detail line). Command: `awk '/wscale/ {cc = $1; for (i = 1; i <= NF; i++) {if ($i ~ /^cwnd:/) cw = substr($i, 6); if ($i == "delivery_rate") r = $(i + 1)} printf "%s cwnd %s, %.1f Mbit/s\n", cc, cw, r / 1000000}' sstni.txt`. Expected:

   ```
   cubic cwnd 23, 4.8 Mbit/s
   bbr cwnd 212, 46.7 Mbit/s
   ```

   Explanation: the same path (50 Mbit/s, 50 ms, 1% loss), four seconds into each transfer. CUBIC's window has been cut again and again to 23 segments; BBR's sits at 212, about the path's bandwidth-delay product (212 × 1,448 = 306,976 bytes; the BDP is 312,500). `awk` reads `4802840bps` as the number 4802840.
4. ● **`est-cwnd-to-rate`** (estimate, `loss-latency-math`). "`ss -tni` shows a connection with `cwnd:23`, `mss:1448` and `rtt:54.075`. If it sends one full window every round trip, how many Mbit/s is that? Within 3%." `given: { cwnd: 23, mss: 1448, rtt: 54.075 }`; `working: cwnd * mss * 8 / (rtt / 1000) / 1000000`; answer 4.93. Mistakes: `bytes` 0.62 (`cwnd * mss / (rtt / 1000) / 1000000`); `seconds` 0.005 (rtt not divided by 1000). Explanation: it's `ss`'s own `send 4927083bps` on the same line (captured), which is exactly this sum.
5. **`mcq-loss-on-wifi`** (`loss-based-cc`). "A laptop on Wi-Fi that loses 1% of packets at random downloads from a far-away server over an otherwise idle link. Why is a CUBIC download slow?"
   - "CUBIC takes each random loss as congestion, so it keeps cutting its window" ✔
   - "Wi-Fi's smaller MTU makes TCP send many more packets for the same bytes"
   - "The receive window can't grow beyond 64 KiB while losses are being repaired"
   - "Lost packets aren't resent until the next slow start begins after a timeout"
   Explanation: G1, and the ceiling formula; Wi-Fi's MTU is 1,500 like Ethernet's; window scaling isn't switched off by loss; fast retransmit resends a lost packet within a round trip, no timeout needed.
6. ◇ **`est-slow-start-bytes`** (estimate, `loss-based-cc`, `loss-latency-math`). "A connection starts with a window of 10 segments of 1,448 bytes and doubles it every round trip. At most how many bytes can it deliver in its first 4 round trips? Exactly." `given: { start: 10, mss: 1448 }`; `working: (start + 2 * start + 4 * start + 8 * start) * mss`; answer 217200. Mistakes: `last-round-only` 115840 (`8 * start * mss`); `no-doubling` 57920 (`4 * start * mss`). Explanation: why a 200 KB page takes four round trips whatever the bandwidth.

### 8.3 Recall on BBR

7. **`mcq-bbr-measures`** (`bbr-model`). "What does BBR measure to decide how fast to send?"
   - "The highest recent delivery rate and the shortest recent round trip" ✔
   - "How many packets each round trip lost, slowing down when any were"
   - "The receiver's advertised window, sending that much each round trip"
   - "The bottleneck router's queue length, from marks the router adds on"
   Explanation: G5; loss counting is CUBIC's signal; the receive window is a ceiling for every algorithm; router marks are ECN, which this topic doesn't teach (one sentence in the explanation is enough).
8. ● **`mcq-receiver-bbr`** (`bbr-model`). "Customers upload backups to your server across a long, lossy path. You set BBR in `/etc/sysctl.d` on the server and reboot it. Uploads are no faster. Why?"
   - "Congestion control runs at the sender, and for uploads the sender is the customer" ✔
   - "BBR only applies to connections made after the next kernel update is installed"
   - "BBR needs the fq queueing discipline as well, and the reboot didn't turn it on"
   - "BBR can't help on a lossy path, because each loss still halves its window there"
   Explanation: **tried** (B3: BBR on the receiver, CUBIC's speed). The setting applies to new connections at once; Linux's BBR paces without fq (G5); BBR doesn't halve on loss (the lab's 45 Mbit/s).
9. ● **`est-bbr-inflight`** (estimate, `bbr-model`, `loss-latency-math`). "`ss -tni` shows a BBR connection's model as `bbr:(bw:48087096bps,mrtt:50,…)`: 48,087,096 bits a second and a shortest round trip of 50 ms. How many bytes is one bandwidth-delay product of that path? Within 3%." `given: { bw: 48087096, mrtt: 50 }`; `working: bw / 8 * mrtt / 1000`; answer 300544. Mistakes: `bits` 2404355 (`bw * mrtt / 1000`); `one-way` 150272 (`bw / 8 * mrtt / 2000`). Explanation: the same line shows `cwnd:212`, 306,976 bytes: BBR keeps about one BDP in flight (G5's `cwnd_gain` allows up to two).
10. ● **`mcq-bbr-retransmits`** (`bbr-model`). "On the lab's 1%-loss path BBR retransmitted about 300 packets in 8 seconds and CUBIC about 30, yet BBR delivered eight times as much. Why?"
    - "BBR resends what was lost but keeps its rate; CUBIC slows down after each loss" ✔
    - "BBR's packets are smaller, so each one it loses costs less data to send again"
    - "CUBIC's retransmissions are hidden, since it waits out a timeout for each one"
    - "BBR asks the receiver to rebuild lost packets from extra data it sends ahead"
    Explanation: G5's "does not react directly to packet losses"; same MSS; CUBIC's are counted the same way; forward error correction isn't TCP's.
11. ◇ **`mcq-bbr-sharing`** (`bbr-model`). "A team moves its backup servers to Linux's BBR on a link it shares with other teams' CUBIC traffic. What's the risk?"
    - "Their BBR flows may take more than a fair share and squeeze the CUBIC flows" ✔
    - "BBR backs off whenever it detects CUBIC flows, so the backups will stall"
    - "Routers drop BBR's packets first, since BBR marks its packets low priority"
    - "Mixing algorithms on one link makes every flow fall back to Reno's rules"
    Explanation: G8; version 3 (G6) was designed partly to share better.

### 8.4 Recall on the arithmetic of loss and distance

12. ● **`est-loss-ceiling`** (estimate, `loss-latency-math`). "Standard TCP's average window is about 1.2 ÷ √p segments, where p is the share of packets lost, and it sends one window per round trip. With 1,460-byte segments, an 80 ms round trip and 1% loss, about how many Mbit/s can one connection carry? Within 10%." `given: { factor: 1.2, mss: 1460, rtt: 80, loss: 1 }`; `working: factor * mss * 8 / ((rtt / 1000) * (loss / 100) ** 0.5) / 1000000`; answer 1.75. Mistakes: `no-root` 17.52 (`… * (loss / 100)`: "the square root of 0.01 is 0.1; dividing by 0.01 is ten times too much"); `bytes` 0.22. Explanation: Reno's shape; CUBIC does somewhat better on the same path (the lab: about 2.8 by the formula at 50 ms against 3.3 to 7.2 measured).
13. ● **`est-double-rtt`** (estimate, `loss-latency-math`). "A loss-based connection gets 12 Mbit/s between two regions 40 ms apart. With the same loss rate, about how many Mbit/s would it get to a region 120 ms away? Exactly." `given: { speed: 12, near: 40, far: 120 }`; `working: speed * near / far`; answer 4. Mistakes: `halved` 6 ("three times the round trip divides it by three"); `unchanged` 12 ("one window per round trip: a longer round trip carries less a second").
14. **`est-quadruple-loss`** (estimate, `loss-latency-math`). "A loss-based connection gets 20 Mbit/s at 0.1% loss. At 0.4% loss on the same path, about how many Mbit/s? Exactly." `given: { speed: 20, before: 0.1, after: 0.4 }`; `working: speed * (before / after) ** 0.5`; answer 10. Mistakes: `linear` 5 (`speed * before / after`: "it falls with the square root of the loss rate").
15. ● **`est-parallel-streams`** (estimate, `loss-latency-math`). "One loss-limited connection gets 6 Mbit/s across a 100 Mbit/s path. A copy tool opens 8 such connections at once. About how many Mbit/s in all? Exactly." `given: { one: 6, streams: 8, link: 100 }`; `working: min(streams * one, link)`; answer 48. Mistakes: `link` 100; `one` 6. Explanation: why transfer tools open many connections, and why BBR on one connection is the other answer.
16. ◇ **`est-transfer-hours`** (estimate, `loss-latency-math`). "A 30 GB backup crosses a path where one connection gets 6 Mbit/s. How many hours does it take? Within 5%." `given: { size: 30, rate: 6 }`; `working: size * 1000000000 * 8 / (rate * 1000000) / 3600`; answer 11.1. Mistakes: `bytes` 1.39 (no × 8).

### 8.5 Recall on QUIC

17. ● **`quic-first-datagrams`** (`predict_shell`, `quic-changes`). **Captured** `quic.txt` = the first three lines of `captures/quic-on-the-wire.txt`. Command: `awk '{print ($3 ~ /\.443$/ ? "server" : "client"), $NF}' quic.txt`. Expected:

    ```
    client 1200
    server 1252
    server 282
    ```

    Explanation: the client's first datagram is padded to exactly 1,200 bytes (RFC 9000 requires at least 1,200), which proves the path carries datagrams that big and lets the server answer with up to three times as much (3,600 bytes) before it has checked the client's address; 1,252 + 282 = 1,534. Everything inside is encrypted: `tcpdump` shows only lengths.
18. ● **`est-rtt-saved`** (estimate, `quic-changes`). "A browser opens a new connection to an API whose round trip is 150 ms and sends one request. How many milliseconds sooner does the first byte of the answer arrive over HTTP/3 than over HTTP/2 on TCP with TLS 1.3? Exactly." `given: { rtt: 150 }`; `working: 3 * rtt - 2 * rtt`; answer 150. Mistakes: `h3-total` 300 (`2 * rtt`: "that's how long HTTP/3 waits; the question asks for the difference"); `h2-total` 450. Explanation: measured in the lab at a 100 ms round trip: 0.305 s against 0.205 s.
19. ● **`mcq-hol-blocking`** (`quic-changes`). "A page loads six images over one HTTP/2 connection on TCP, and one packet carrying part of the first image is lost. What happens to the other five?"
    - "They wait, because TCP hands on nothing past a gap until it's filled" ✔
    - "They carry on, because each image rides its own TCP connection in HTTP/2"
    - "They stop, because the browser restarts all six on a fresh connection"
    - "They carry on, because TCP hands later packets on and fills gaps later"
    Explanation: head-of-line blocking (S5); HTTP/2 deliberately uses one connection; nothing restarts; in-order delivery is TCP's promise (topic 28's postcards). Over QUIC only the first image waits.
20. ● **`mcq-migration`** (`quic-changes`). "A phone leaves Wi-Fi mid-download and switches to 5G with a new IP address. What happens to a QUIC connection, and to a TCP one?"
    - "QUIC carries on, found by its connection ID; the TCP one breaks" ✔
    - "Both break, since both are identified by the phone's address and port"
    - "Both carry on, since the phone's operating system moves its sockets"
    - "TCP carries on, found by its sequence numbers; the QUIC one breaks"
    Explanation: G14; CloudFront and AWS's NLB both mention connection IDs (G19, G20).
21. ◇ **`ngtcp2-idle`** (`predict_shell`, `quic-changes`). **Captured** `ngtcp2.txt`: three lines of `captures/ngtcp2-client-log.txt` (the first `type=Initial` line, `initial_max_streams_bidi=100`, `max_idle_timeout=30000`), each cut to 140 characters. Command: `awk -F= '/max_idle_timeout/ {print $NF / 1000, "seconds"}' ngtcp2.txt`. Expected: `30 seconds`. Explanation: QUIC's own idle timer, in milliseconds in the transport parameters, the smaller of both sides' values; a NAT may forget the UDP flow sooner (topic 28), so long-lived QUIC connections send PING frames.
22. **`mcq-capture-shows`** (`quic-changes`). "You capture an HTTP/3 request with `tcpdump`. What can you read?"
    - "Addresses, UDP ports and datagram lengths, but not the request" ✔
    - "The URL and headers, since QUIC encrypts only the body of a request"
    - "TCP's three handshake packets, then encrypted data like any HTTPS"
    - "Nothing at all, since QUIC encrypts the IP and UDP headers as well"
    Explanation: **captured** (B6); the IP and UDP headers must stay readable for routers and NATs to carry the packets.

### 8.6 Recall on HTTP/3 in practice

23. ● **`altsvc-read`** (`predict_shell`, `http3-in-practice`). **Captured** `headers.txt` (five header lines from `curl -sI https://shop.test/` against the lab's Caddy, line endings made plain): `HTTP/2 200`, `alt-svc: h3=":443"; ma=2592000`, `content-type: …`, `server: Caddy`, `content-length: 20`. Command: `grep -o 'h3=":[0-9]*"' headers.txt; awk -F'ma=' '/^alt-svc/ {print $2 / 86400, "days"}' headers.txt`. Expected:

    ```
    h3=":443"
    30 days
    ```

    Explanation: the answer came over HTTP/2 and says "HTTP/3 is on UDP port 443 of this same host; remember that for 2,592,000 seconds". Without `ma`, 24 hours (G16). Google's load balancer sends the same `ma` (G21).
24. ● **`mcq-udp-443-blocked`** (`http3-in-practice`). "An office firewall allows TCP 443 but drops UDP 443. What do users' browsers do on a site that offers HTTP/3?"
    - "Stay on HTTP/2 over TCP, and nobody is told" ✔
    - "Show a page saying the connection was refused"
    - "Retry HTTP/3 until the firewall lets one in"
    - "Ask the site for HTTP/3 carried on TCP 443"
    Explanation: **tried** (B8); HTTP/3 runs only on QUIC, so there's nothing to ask for over TCP; Google's page calls the fallback normal (G21). The site works, only slower on bad links: a fault nobody reports, which is why the debug lab has it.
25. **`mcq-h3-to-backends`** (`http3-in-practice`). "You turn on HTTP/3 on Google's global external Application Load Balancer. What do your backends receive?"
    - "Requests over HTTP/1.1 or HTTP/2, since HTTP/3 ends at the load balancer" ✔
    - "Requests over HTTP/3, so the backends must listen on UDP port 443 as well"
    - "The clients' QUIC packets, forwarded untouched and still fully encrypted"
    - "Nothing new: the load balancer uses HTTP/3 only for its own status pages"
    Explanation: G21 and G22; the third choice is what AWS's NLB does in QUIC passthrough mode (G20), a layer 4 box that doesn't end the connection.
26. ◇ **`mcq-when-h3-helps`** (`http3-in-practice`). "For which users is HTTP/3 most likely to make pages faster?"
    - "Mobile users far from the server, on links that lose packets" ✔
    - "Servers in one data centre, talking over a clean 25 Gbit/s link"
    - "Office users behind a firewall that drops UDP sent to port 443"
    - "Batch jobs downloading one large file with one long request"
27. ◇ **`mcq-three-clouds-h3`** (`http3-in-practice`). "Which statement about HTTP/3 at the three clouds' edges was true in November 2026?"
    - "CloudFront offers it; Azure Application Gateway's is a preview" ✔
    - "Front Door offers it; Google's load balancers don't support it yet"
    - "AWS's ALB offers it; CloudFront speaks HTTP/2 to viewers only"
    - "All three offer it, and all three speak HTTP/3 to the backends too"
    Explanation: G19 to G23, dated; this item's facts are the most likely in the topic to change, so it is review-only and carries its date in the prompt.

### 8.7 `fill-turn-on-http3` (fill-in, systemd lab, topology C), 25 minutes, skills `http3-in-practice`, `quic-changes`

Story: the shop's site runs on `lab` under Caddy; the office should get HTTP/3. Two files with gaps (`...`):

```
# /etc/nftables.conf (the input chain; the rest of the file is complete)
        iif lo accept
        ct state established,related accept
        tcp dport { 22, 80, 443 } accept
        ... dport ... accept

# /etc/caddy/Caddyfile (the global options)
{
        skip_install_trust
        servers {
                protocols h1 h2 ...
        }
}
```

Prompt: fill both, load the firewall file and reload Caddy (the commands are in the lesson), then check HTTP/3 from the office. The firewall must still let in nothing else. Which gaps stop the file loading: in `nftables.conf` both do (`nft -c -f` says so); in the Caddyfile, `...` is an unknown protocol and Caddy refuses to reload, keeping its old settings (the prompt says this, because the learner will see the reload fail). Checks:

| Check | Tests |
| --- | --- |
| `h3-from-the-office` (`timeout: 20`) | `from-office h3get https://shop.test/` prints `hello over HTTP/3.0` within 8 s |
| `advertised` | `from-office curl -sI https://shop.test/` has an `alt-svc` header naming `h3` on port 443 |
| `nothing-else-in` (`timeout: 20`) | listeners of the check's own on UDP 5000 and 9999 receive nothing from the office's datagrams in 3 s, and TCP 8080 gets no answer for the whole `nc -z -w 2` |
| `saved` | `/etc/nftables.conf` loaded into a throwaway namespace gives the same `nft -s list ruleset` as the running rules |
| `caddy-running` | `caddy.service` active and enabled |

Wrong fixes: `tcp-not-udp.sh` (gap filled `tcp dport 443`), `udp-wide-open.sh` (`meta l4proto udp accept`), `h3-not-listed.sh`, `not-saved.sh` (`nft add rule …` live only), `caddy-not-reloaded.sh` (file right, service never reloaded: the live server still has no UDP listener). Mechanics **tried** (B8, B9): `protocols h1 h2` plus `systemctl reload caddy` removes the UDP 443 listener and the Alt-Svc header; restoring `h3` and reloading brings both back.

### 8.8 `write-cc-compare` (write, systemd lab, topology B), 30 minutes, skills `bbr-model`, `loss-latency-math`

Prompt: write `~/bin/cc-compare HOST SECONDS` that measures one connection to `HOST` with CUBIC and then with BBR, each for `SECONDS`, and prints three lines: `cubic N`, `bbr N` (the receiver's rate in Mbit/s, one decimal) and `bbr/cubic R` (one decimal). Usage line and non-zero exit unless given two arguments. From a blank file with `nano`; try it on `dr1` (10.0.6.20); then run the checks.

Hints: `iperf3 -c HOST -t SECONDS -C cubic -f m` prints a summary line ending `receiver`, in Mbit/s whatever the speed (`-f m`; without it a slow run may print `Kbits/sec`); `awk '/receiver/ {print $7}'` picks the rate (the line is `[  5]   0.00-6.05  sec  3.86 MBytes  5.35 Mbits/sec  receiver`, so the seventh field); `awk "BEGIN {printf \"%.1f\", $b / $c}"` divides.

Checks:

| Check | Tests |
| --- | --- |
| `executable`, `usage` | as `write-steal-pct`'s |
| `numbers-are-the-receivers` (`timeout: 60`) | the check runs `cc-compare 10.0.6.20 4`, then reads `journalctl -u backup-sink` since it started: `iperf3 -s` logs `Accepted connection from …` and its own `receiver` summary line for each test (**tried**, B10), and the script's two numbers must each be within 10% of the two summaries, in order (the check converts the server's units). A script that prints numbers it didn't measure fails |
| `two-algorithms` | from the same run: `bbr` at least 3 times `cubic`, and `cubic` under 15 (both measured, above; the gap is six-fold at its narrowest, B2) |
| `ratio-right` | the third line equals `bbr ÷ cubic` from the script's own first two lines, to one decimal |

Wrong fixes: `hard-coded.sh` (prints `cubic 5.0`, `bbr 45.0`, `bbr/cubic 9.0`), `default-both-times.sh` (no `-C`: ratio near 1), `ratio-upside-down.sh`, `sender-line.sh` (picks the line ending `sender`, which on a lossy path reports bytes sent including those lost; the author confirms it differs by more than 10% under 1% loss, or drops this wrong fix), `no-usage.sh`.

### 8.9 Ladder order for `topic.yaml`

`example-cubic-meets-loss`, `est-slow-start-window`, `mcq-cubic-after-loss`, `ss-read-cwnd`, `est-cwnd-to-rate`, `mcq-loss-on-wifi`, `mcq-bbr-measures`, `mcq-receiver-bbr`, `est-bbr-inflight`, `mcq-bbr-retransmits`, `est-loss-ceiling`, `est-double-rtt`, `est-quadruple-loss`, `est-parallel-streams`, `quic-first-datagrams`, `est-rtt-saved`, `mcq-hol-blocking`, `mcq-migration`, `mcq-capture-shows`, `altsvc-read`, `mcq-udp-443-blocked`, `mcq-h3-to-backends`, `fill-turn-on-http3`, `write-cc-compare`.

21 recall items in practice (3 `predict_shell`, 8 estimates, 10 multiple choice) and 6 review-only. Multiple-choice length, measured with `items/mcqlen.py` on the choices as drafted: see section 8.10.

### 8.10 Multiple-choice lengths (measured)

Measured with `items/mcqlen.py` on this file on 2026-11-11 (characters as shown, backticks removed): 13 items; the right answer is the longest choice in 3 of them (`mcq-receiver-bbr`, `mcq-bbr-retransmits`, `mcq-bbr-sharing`; `mcq-bbr-measures` ties), and the largest ratio of right to longest wrong is 1.03. Two right answers were shortened to get there (`mcq-migration`, `mcq-capture-shows`). The writer re-counts after any edit.

## 9. Proofs

### 9.1 Build: `build-fast-far-site` (systemd lab, topologies B and C), 50 minutes, skills `bbr-model`, `http3-in-practice`, `quic-changes`, `loss-latency-math`

The shop's servers have moved to a far region. From a brief, on a server set up the way a new image comes (CUBIC; a default-deny firewall that lets in SSH, HTTP and HTTPS over TCP; Caddy serving `shop.test` with its defaults):

1. **The nightly archive reaches the DR site at least half as fast as the link.** `archive-push` (scenery, root-owned: one `iperf3` connection with the system's congestion control) sends to dr1 across 50 Mbit/s with a 100 ms round trip and 1% loss. It must deliver at least 25 Mbit/s on its one connection, every night, after reboots too. (The path is the one measured in B2: BBR 41.2 to 42.8, CUBIC 1.4 to 7.4 Mbit/s.)
2. **Office users get HTTP/3**, advertised by the site, through the firewall.
3. **The firewall still lets in only what the site serves**, and what's loaded is what's saved.
4. **The link and the archive job stay as they are** (they stand for the internet and another team's tool).

Checks (with the skill each tests):

| Check | Tests | Skill |
| --- | --- | --- |
| `archive-speed` (`timeout: 30`) | `archive-push` (6 s) receives at least 25 Mbit/s, read from dr1's `iperf3 -s` log | `bbr-model` |
| `sender-choice-lasts` | the live `net.ipv4.tcp_congestion_control` on `lab` is `bbr` and equals the final value `systemd-sysctl --cat-config` gives from the files | `bbr-model` |
| `h3-from-the-office` (`timeout: 20`) | `h3get` from the office answers over HTTP/3 | `http3-in-practice` |
| `advertised` | Alt-Svc names `h3` on port 443 | `http3-in-practice` |
| `nothing-else-in` (`timeout: 20`) | check listeners on UDP 4433, 5000, 9999 and TCP 8080 get nothing from the office | `http3-in-practice` |
| `saved` | saved firewall equals the running one | `http3-in-practice` |
| `job-and-link-as-they-were` | `archive-push`'s checksum, `on-wan tc qdisc show` as shipped | `bbr-model` |

Wrong fixes (8): `bbr-runtime-only.sh`, `bbr-on-dr1.sh`, `archive-parallel.sh` (edits the job to `-P 8`), `wan-loss-removed.sh`, `udp-wide-open.sh`, `firewall-not-saved.sh`, `tcp-443-only.sh`, `h3-off-in-caddy.sh`. Restart trial: **tried** for the BBR setting (B4: after `docker restart`, `bbr` from `/etc/sysctl.d`, 43.4 and 44.5 Mbit/s); Caddy's settings are files and come back with the service.

### 9.2 Debug: `debug-slow-from-far` (systemd lab, topologies B and C), 45 minutes, skills `bbr-model`, `http3-in-practice`

Prompt: the shop's site and its backups moved to a far region last month. The site runs Caddy on `lab` for the office and customers; the nightly archive goes from `lab` to the DR site, dr1, across a 50 Mbit/s link with a 50 ms round trip that loses about 1% of packets. Since the move, the archive takes about eight times longer than the link allows, and although the team "turned HTTP/3 on", no client ever uses it. **There are three faults.** You may change `lab` and dr1 (`on-dr`). The rules: the firewall keeps letting in only what the site serves; the link stays as it is; the archive keeps its one connection; fixes last after a reboot. `archive-push` runs the archive now and prints its speed; `from-office h3get https://shop.test/` tries HTTP/3.

The faults, for the writer:

1. **BBR was set on the wrong machine:** dr1's `/etc/netns/dr/sysctl.d/60-bbr.conf` sets it; `lab`, the sender, still runs CUBIC.
2. **The firewall opens the wrong UDP port:** `/etc/nftables.conf` has `udp dport 4433 accept` (typed from a test setup) instead of 443.
3. **Caddy's HTTP/3 is switched off:** the Caddyfile's global options keep `protocols h1 h2` from the migration.

Checks:

| Check | End state | Fails for |
| --- | --- | --- |
| `archive-speed` (`timeout: 30`) | at least 25 Mbit/s on one connection | 1 |
| `sender-choice-lasts` | `lab`'s live congestion control is `bbr` and comes from its files | 1 |
| `h3-from-the-office` (`timeout: 20`) | HTTP/3 answers from the office | 2, 3 |
| `advertised` | Alt-Svc names `h3` on 443 | 3 |
| `only-what-it-serves` (`timeout: 20`) | check listeners on UDP 4433, 5000, 9999 and TCP 8080 get nothing from the office | 2, shortcuts |
| `saved` | saved firewall equals the running one | shortcut |
| `link-as-it-was` | `on-wan tc qdisc show` as shipped | shortcut |

Wrong fixes (9): `bbr-runtime-only.sh`, `wan-loss-removed.sh`, `udp-wide-open.sh`, `extra-port-left.sh` (adds 443, leaves 4433 [`only-what-it-serves`]), `firewall-not-saved.sh`, `caddyfile-edited-not-reloaded.sh`, and three two-of-three fixes. Fault isolation as in the table's last column, to be proved under `labcheck test`.

### 9.3 Explain

Prompt: "A company is moving its shop's servers to a region on another continent: about 140 ms round trip from most customers, many of them on mobile networks that lose about 1% of packets. Its nightly backups will come back across the same distance. Explain, in your own words: how loss and distance together limit a TCP connection that uses CUBIC, with rough numbers; what BBR does differently, what it costs, and where it has to be configured to help the backups; what QUIC changes compared with TCP and TLS, and why that helps mobile customers in particular; how browsers find out that a site speaks HTTP/3 and what happens if a customer's network blocks it; and how the three clouds' load balancers or CDNs handle HTTP/3."

Rubric rows: `loss-and-distance` (required: loss-based algorithms cut on every loss; throughput falls with RTT and √loss; a worked rough number), `bbr` (required: models delivery rate and minimum RTT, paces, doesn't treat random loss as congestion; costs: retransmissions, fairness; set at the **sender**, persistently), `quic` (required: one handshake round trip instead of two, independent streams, connection IDs and migration, encrypted headers over UDP), `discovery-and-fallback` (required: Alt-Svc or an HTTPS record; UDP 443 blocked means a silent fallback to HTTP/2; firewall rule for UDP 443), `clouds` (required: two correct facts, e.g. CloudFront offers HTTP/3 with migration, Google's global external Application Load Balancer advertises it by default, Azure Application Gateway's is a preview, all end it at the edge), `queues` (optional: bufferbloat and BBR's smaller queues).

## 10. Review pool

22 items; every skill has at least four.

| Skill | Items |
| --- | --- |
| `loss-based-cc` | `est-slow-start-window`, `ss-read-cwnd`, `mcq-cubic-after-loss`, ◇ `est-slow-start-bytes` |
| `bbr-model` | `mcq-receiver-bbr`, `est-bbr-inflight`, `mcq-bbr-retransmits`, ◇ `mcq-bbr-sharing` (and `ss-read-cwnd`) |
| `loss-latency-math` | `est-cwnd-to-rate`, `est-loss-ceiling`, `est-double-rtt`, `est-parallel-streams`, ◇ `est-transfer-hours` |
| `quic-changes` | `quic-first-datagrams`, `est-rtt-saved`, `mcq-hol-blocking`, `mcq-migration`, ◇ `ngtcp2-idle` |
| `http3-in-practice` | `altsvc-read`, `mcq-udp-443-blocked`, ◇ `mcq-when-h3-helps`, ◇ `mcq-three-clouds-h3` |

Production over recognition: 9 estimates and 4 `predict_shell` among 22. Follow-up candidates per skill (recall, fill-in, write): `loss-based-cc` 5, `bbr-model` 7, `loss-latency-math` 9, `quic-changes` 7, `http3-in-practice` 6.

## 11. Platform work

| # | What | Smallest version | Blocks |
| --- | --- | --- | --- |
| C1 | The network-lab base, with topic 28's list and this brief's section 7 | as listed; the topic-only layer is ordinary Dockerfile work | all labs |
| C2 | **The CI spike** (topic 28's T2, extended) | in the same early pull request: does `sysctl -w net.ipv4.tcp_congestion_control=bbr` in a privileged container autoload `tcp_bbr` on `ubuntu-latest`? Do the thresholds hold with four labs at once (run `labcheck test` on `write-cc-compare` and `debug-slow-from-far` there)? If BBR can't load, the kernel module is in the runner's own `linux-modules` package and a workflow step `sudo modprobe tcp_bbr` loads it | all five labs |
| C3 | Image size | the 63.3 MB layer is built once per CI shard; five labs share it | — |
| C4 | `h3get` and `wan-set` as scenery | two small files in each lab that needs them, as Module 1's console stand-ins | the worked example, fill-in, build, debug |

No content-model work. Decided against: a QUIC dissector (`tshark` with key logs, a 100 MB-plus package) when `gtlsclient`'s own log shows the decrypted packets; downloading a static `curl` with HTTP/3 (not from `apt`, and a binary from outside the distribution); nginx (no QUIC in 1.24); measuring head-of-line blocking (too noisy to check; taught from S5 and one question).

## 12. Cost and time

**Money: nothing.** All local. A real HTTP/3 edge (Google's load balancer, CloudFront) isn't needed to see what this topic teaches, and Ubuntu's `curl` couldn't speak to it anyway.

**Learner's time:** lesson 15, assigned reading 49, 21 recall items 32, worked example 40, fill-in 25, write 30, build 50, debug 45, explain 20: **about 305 minutes** (`estimated_minutes: 300`; first to trim if the owner's pass runs long: step 5 of the worked example, −5).

**CI time:**

| Lab | Runs | Seconds a run | Serial minutes |
| --- | --- | --- | --- |
| `example-cubic-meets-loss` | 5 | 80 | 7 |
| `fill-turn-on-http3` | 7 | 30 | 3.5 |
| `write-cc-compare` | 7 | 40 | 4.5 |
| `build-fast-far-site` | 10 | 40 | 7 |
| `debug-slow-from-far` | 11 | 40 | 7.5 |

About 30 serial minutes; with topic 28's, about an hour serial for the two topics, 15 minutes of one shard at four jobs. Each lab's `timeout:`s add up to well under 600 s (the largest, the build: 30 + 20 + 20 + four checks at 30 = 190).

## 13. Open questions, each with a recommendation under the owner's rule

1. **An HTTP/3 client, since Ubuntu 24.04's `curl` has none.** *Recommend:* ngtcp2's `gtlsclient` (packaged, real, prints the decrypted packets: the best teaching view) for the handshake, said plainly to skip certificate checks; and `h3get` (aioquic, a 40-line scenery script) for ordinary requests and checks. Not a downloaded `curl`.
2. **Caddy for the server.** *Recommend:* Caddy 2.6.2 from Ubuntu's universe archive, HTTP/3 on by default and switchable with one line, **tried** as a packaged systemd service; nginx 1.24 has no QUIC.
3. **Which BBR to teach.** *Recommend:* "Linux's BBR, version 1 in the kernels these labs run" with version 3 as the IETF draft; on the day of writing, re-read `tcp_bbr.c`'s header and the bbr-dev list, and change one sentence if version 3 has landed.
4. **Throughput checks on CI.** *Recommend:* thresholds at the middle of the measured gap (25 Mbit/s against 3.3 to 7.2 and 41 to 46), confirmed by the spike (C2). If the runners overlap, the fallback is a deterministic check: `ss -tni` on the archive's own connection shows `bbr`, and the speed check moves to a 10-second run with a lower threshold.
5. **The `fq` qdisc.** *Recommend:* teach that Linux's BBR paces without it (S3) and that a container can't set the default qdisc; the solution omits it.
6. **The HTTP/3 split with topic 31.** *Recommend:* this topic owns QUIC, discovery and fallback; topic 31 owns HTTP versions' semantics and TLS. The module merge confirms with topic 31's designer.
7. **A real-cloud look at HTTP/3.** *Recommend:* none in this topic; Module 11's edge topic can, with a browser's developer tools, inside a free tier.
8. **Spec wording.** Optional: the topic 29 row could read "explain CUBIC and BBR, and how loss and latency interact; choose and set a sender's congestion control; explain what QUIC and HTTP/3 change, and when they help". *Recommend* the change, since the labs prove the setting, not only the explanation.

## Appendix: what was tried in Docker (2026-11-11)

Containers `tcproto-*`, images `tcproto-*:1`, all removed at the end.

- **B1 Kernel:** `reno cubic` available; after `sysctl -w net.ipv4.tcp_congestion_control=bbr` in a privileged container: `reno cubic bbr`; `tc qdisc add … netem`, `tbf`, `fq`, `htb` all worked; `/proc/modules` then listed `sch_htb sch_fq sch_tbf sch_netem tcp_bbr`. These modules stay loaded in Docker's machine until Docker restarts.
- **B2 The matrix** (`cc/wan.sh`, `cc/trial.sh`; `iperf3 -J`, 8 s each, one container): 50 Mbit/s, 25 ms each way, no loss: CUBIC 46.40, 46.44; BBR 45.93, 46.10. 1%: CUBIC 5.86, 4.69, 6.64 (34 to 48 retransmits); BBR 44.91, 44.11, 45.17 (300 to 403). 50 ms each way, 1%: CUBIC 7.38, 1.42, 2.07; BBR 42.29, 42.84, 41.15. 25 ms, 0.1%: CUBIC 45.71, 29.82, 8.86; BBR 45.88, 45.68, 45.67.
- **B3 Under load** (`sysd/cc-variant.sh`, four booted lab containers measuring at once, 8 s each): system CUBIC 7.2, 5.3 (and 3.3, 4.8 in a lone run); BBR in `/etc/sysctl.d` 45.0, 44.6; BBR plus `fq` 45.1, 45.7 (`sysctl: cannot stat /proc/sys/net/core/default_qdisc`); BBR set only on the receiver 5.2, 3.8. Earlier, nine containers ran topic 28's quiet-spell checks at once without a wrong result.
- **B4 Restart trial:** after `docker restart` of the BBR container, `net.ipv4.tcp_congestion_control = bbr`, 43.4 and 44.5 Mbit/s; `systemd-sysctl` logged "Couldn't write 'fq' to 'net/core/default_qdisc', ignoring" in the `fq` variant and finished.
- **B5 `ss -tni` during each** (the captured lines in `captures/ss-tni-cubic-bbr.txt`): CUBIC `cwnd:23`, `send 4927083bps`, `delivery_rate 4802840bps`; BBR `cwnd:212`, `bbr:(bw:48087096bps,mrtt:50,pacing_gain:1.25,cwnd_gain:2)`, `delivery_rate 46705144bps`.
- **B6 Packages and tools** (`ubuntu:24.04`, 2026-11-11): as in G26. Caddy 2.6.2 with `local_certs` served HTTP/2 with `alt-svc: h3=":443"; ma=2592000` and HTTP/3 ("hello over HTTP/3.0" via `quic/h3get.py`); `gtlsclient` worked against it and printed the decrypted packets. `tcpdump` showed `UDP, length 1200`, `1252`, `282`, `32`, …
- **B7 Round trips** (netem 50 ms on each side of the office's link): `ping` 100.3 ms; `curl -w` three runs: connect 0.1008, 0.1007, 0.1007; TLS 0.2052, 0.2044, 0.2048; first byte 0.3059, 0.3050, 0.3053. `gtlsclient` log: "QUIC handshake has completed" at I00000103, the response's `STREAM` frame and `[:status: 200]` at I00000205.
- **B8 UDP 443 blocked** (nftables `udp dport 443 drop` on `lab`): `h3get` timed out after 10 s; `curl` from the office over TCP: "hello over HTTP/2.0".
- **B9 Caddy under systemd** (`quic-sysd/`: Ubuntu's `caddy.service` in the booted lab image): enabled and active, listening on TCP 80, 443 and UDP 443; HTTP/3 worked; with `protocols h1 h2` and `systemctl reload caddy`: no UDP 443 listener, no `alt-svc`, `h3get` exit 124; restored: both back. Caddy logged "failed to install root certificate" (the lab adds `skip_install_trust`).
- **B10 iperf3's server log:** `iperf3 -s -1` printed `Accepted connection from 127.0.0.1, port 40034` and `[  5]   0.00-2.00   sec  10.0 GBytes  43.0 Gbits/sec   receiver` for a 2-second test; the client printed both a `sender` and a `receiver` line, the rate in field 7.
- **Images:** the QUIC tools layer 63.3 MB, 44 s uncached; the whole QUIC prototype image 412 MB.

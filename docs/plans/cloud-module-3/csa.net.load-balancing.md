# Writing brief: `csa.net.load-balancing` (topic 33), Load balancing

Design only. Nothing here is in the repository. Sources were read on 2026-11-11, each with its date below. Lab mechanics marked **tried** were run in Docker on the owner's PC (Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, cgroup v2) on 2026-11-11; the prototype, its exact commands, timings and captured outputs are in `prototypes/lb-ipsec/README.md` and `prototypes/lb-ipsec/lb/` beside this file, and everything started was removed.

**The decision in one paragraph.** The labs teach with **HAProxy 2.8** (Ubuntu 24.04's package), in both its modes: `mode http` (a layer 7 proxy) and `mode tcp` (a layer 4 proxy). It is the one free tool that does active health checks, draining, cookie stickiness and both layers, and its runtime API (`socat stdio /run/haproxy/admin.sock`) lets a check read the balancer's real state (`show stat`, `show servers state`) while it sends real traffic. Open-source nginx was ruled out because its active health checks are commercial only (nginx's own page, read 2026-11-11), and Ubuntu 24.04's nginx 1.24 predates the open-source `drain` and `sticky` of 1.29.6. Linux IPVS (the kernel's pass-through layer 4 balancer) was ruled out for the labs: it adds a kernel module the labs would depend on (present on both Docker Desktop and the runners, but a second moving part) and teaches one thing HAProxy can't, the pass-through balancer that keeps the client's address, which the lesson teaches from the clouds' own documentation instead, because every cloud layer 4 balancer is a managed service the learner never configures at that level.

## 1. What the learner will be able to do

1. For a given flow, choose layer 4 or layer 7, and a proxy or a pass-through balancer, and say what each can see and change: paths and headers, cookies, TLS, the client's address, protocols that aren't HTTP. Name each cloud's balancer families and which kind each is.
2. Configure HAProxy from a blank file: a frontend, backends, round robin, path routing, a TCP service, health checks, cookie stickiness, `X-Forwarded-For`, started at boot.
3. Design a health check: what to check (the server itself, not what it shares), how often, how many failures and successes before acting, and work out in seconds how long a dead or hung server keeps getting traffic and how long a recovered one waits. Say what each cloud does when every target fails at once.
4. Take a server out of service without hurting anyone: drain, wait for its connections to finish, then maintenance; say how stickiness and each cloud's draining settings change that.
5. Diagnose a misbehaving balancer from its own state and log: a whole fleet taken down by a check on a shared dependency, a server flapping in and out, a dead server still in rotation, a server taken out by hand that comes back at the next restart.

**The six-month core** (what the review pool is built to keep):

- Layer 7 reads the request (path, headers, cookies) and can terminate TLS; layer 4 sees addresses and ports only. A proxy hides the client's address unless told to pass it on (`X-Forwarded-For`, the PROXY protocol); a pass-through balancer keeps it.
- Check the server, not its dependencies. A check that fails on something every server shares fails on every server at once, and the balancer then has nothing to send traffic to.
- Time out ≈ failures needed × interval (+ the check's timeout for a server that hangs); time back ≈ successes needed × interval. The clouds' defaults are slow: an AWS ALB keeps sending to a hung target for about 65 s.
- One failure must never remove a server (hysteresis: more than one failure to go down, more than one success to come back); otherwise it flaps.
- Drain, wait, then stop. State changed through a balancer's API is gone at the next restart unless it's in the configuration.
- Losing one of N servers puts its load on the other N − 1: four at 60% become three at 80%.

## 2. Prerequisites and terms

**`prerequisites:`** `[csa.net.http-semantics, csa.net.nat]`. The table is for the writer: which earlier topic taught what this one uses. Module 3's topics 28 to 32 are being designed at the same time as this brief, so the Module 3 rows are what this brief **assumes** they teach; the critic should check them against those briefs.

| Topic | What this topic uses from it |
| --- | --- |
| `csa.linux.net-tools` | `curl -s`, `-I`, `-v`; `nc -z`; `ss -ltnp`; `tcpdump`; nftables; network namespaces and veth pairs; the `from-office` pattern. Every lab here uses them. |
| `csa.linux.services` | Units, template units (`shop-web@web1`), `systemctl enable`, `reload` against `restart`, `journalctl -u`. |
| `csa.linux.scripting`, `csa.linux.shell` | A script with arguments, a `while` loop with `sleep`, `awk -F,` over CSV, exit status. The write lab needs all of it. |
| `csa.linux.processes` | Signals; `kill -STOP` and `-CONT` (used by checks and by the worked example to make a server hang). |
| `csa.net.transport` (assumed) | The TCP handshake, a reset against a timeout, connection reuse (keep-alive), why a "connection" is a 5-tuple. |
| `csa.net.http-tls` (assumed) | An HTTP request and response, status codes (200, 500, 502, 503), headers, TLS termination, SNI, certificates. |
| `csa.net.http-semantics` (checked against `csa.net.http-semantics.md`, 2026-11-11) | Cookies: that brief's labs send `Cookie: session=alice` and its lesson explains why a response with `Set-Cookie` isn't cached, but its terms list names cookies only under CORS credentials. This topic still defines a cookie in one sentence (below) unless the module merge gives the definition to 32. |
| `csa.net.nat` | Source NAT: a device that opens connections in its own name hides the original address. The proxy here does exactly that, and the stickiness story needs "many people behind one NAT address". |
| `csa.net.dns` (assumed) | Names and TTLs, only for one sentence on DNS-based balancing (Route 53, Traffic Manager, Cloud DNS routing policies), which Module 11 teaches. |

**Terms this topic must define itself:** load balancer, frontend (listener), backend (target group, backend pool), server (target, backend instance), virtual IP (VIP); layer 4 and layer 7 balancing; **proxy** (two connections, the balancer in the middle of each) against **pass-through** (packets forwarded, one connection end to end); direct server return (one sentence, from HAProxy's guide); round robin, weighted round robin, least connections (least outstanding requests on AWS), hashing on the source address or the 5-tuple; slow start; **health check** (active) and passive health checking; liveness, local health and dependency checks (Yanacek's three words); interval, timeout, and the two thresholds (HAProxy `fall` and `rise`; AWS `UnhealthyThresholdCount` and `HealthyThresholdCount`; Azure "probe threshold"; Google "unhealthy/healthy threshold"); **fail open**; **flapping** and **hysteresis**; **draining** (connection draining, deregistration delay) and **maintenance**; **sticky sessions** (session affinity, persistence); `X-Forwarded-For`; the PROXY protocol; HAProxy's **runtime API** (its "stats socket") and `socat` (a tool that connects its input and output to a socket); N+1 capacity. **Cookie**, if topic 32 hasn't: a small named value a server asks the browser to store and send back with every later request to that site.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `choose-the-balancer` | Layer 4 or layer 7, proxy or pass-through, for a given flow; what each can see and do (paths, headers, cookies, TLS termination or passthrough, protocols that speak first, the client's address); balancing algorithms and when hashing on the source misbehaves; the clouds' families: AWS ALB, NLB, GWLB; Azure Load Balancer, Application Gateway, Front Door; Google's Application, proxy Network and passthrough Network Load Balancers |
| `health-checks` | What a check should test (the server, not a shared dependency); intervals, timeouts and the two thresholds; hysteresis against flapping; what each cloud and HAProxy do when every target fails (fail open, stop new flows, 503) |
| `failover-math` | The numbers: how long a dead or hung server keeps getting traffic, how long a recovered one waits, flaps an hour from a given failure rate, the load on the survivors when one fails, servers needed for N+1, how long a rolling deploy waits on draining |
| `drain-and-stick` | Drain, wait, maintenance; deregistration delay and connection draining on each cloud; sticky sessions by cookie or by source address, their cost (uneven load, users behind one NAT, lost sessions when a server dies) and how stickiness and draining interact |
| `read-the-balancer` | HAProxy's real state through its runtime API (`show stat`: `status`, `chkfail`, `chkdown`, `stot`; `show servers state`: operational and administrative state) and its log (DOWN and UP with their reasons, `<NOSRV>`, "no server available"); runtime state against the configuration, which wins at a restart |

Five skills. Each is practised before any proof needs it, and each has at least four questions that can come back (section 9).

## 4. Lesson plan

The lesson (`lesson.mdx`) is the intro, the main resource and the recap, as every topic's is. The order of ideas, with what the lesson itself must supply because no resource does it well for a beginner:

**4.1 What a balancer is, in the shop's terms** (HAProxy Starter Guide, section 2, the first third). Supply the picture in words that the labs use: the office laptops on one side, `10.0.9.1:80` on the balancer, three web servers `web1` to `web3` behind it on their own network, each a different machine. Every request reaches one server; the balancer decides which, and stops sending to one that is broken. Name the parts once with all three clouds' words beside HAProxy's: frontend = listener, backend = target group (AWS) / backend pool (Azure) / backend service (Google), server = target / backend instance.

**4.2 Two ways to balance** (Starter Guide section 2, the middle; Google's "Choose a load balancer", the proxy and passthrough section). The Starter Guide's two kinds, put plainly: one forwards **packets** and keeps one connection from the client to the server (a pass-through balancer, layer 4); the other is a **proxy** that accepts the client's connection and opens its own to the server, so it can read and change the request (layer 7, and HAProxy's `mode tcp` is a layer 4 *proxy*). A table the lesson must draw, because no resource puts it in one place:

| | Pass-through, layer 4 | Proxy, layer 4 (`mode tcp`) | Proxy, layer 7 (`mode http`) |
| --- | --- | --- | --- |
| Can route by path, host, header, cookie | no | no (in principle; see note) | yes |
| Terminates TLS | no (passes it through) | can, but usually passes it through | yes, usually |
| The server sees the client's address | yes | no, unless the PROXY protocol | no, unless `X-Forwarded-For` |
| Works for protocols that aren't HTTP | yes | yes | no |
| Examples | Azure Load Balancer, Google passthrough NLB, AWS NLB (instance targets keep the client's address by default) | HAProxy `mode tcp`, Google proxy NLB | AWS ALB, Azure Application Gateway and Front Door, Google Application LBs, HAProxy `mode http` |

Note for the writer, **tried**: HAProxy 2.8 accepts a path rule in a `mode tcp` frontend (it can inspect content), so never write "HAProxy can't read the path in TCP mode"; write "a layer 4 balancer decides on addresses and ports". The demonstration that works, and that the worked example uses: a service that **speaks first** (the shop's stock-sync service sends `STOCK-SYNC 1.0 ready` before the client says anything) hangs behind a `mode http` proxy, which waits for an HTTP request that never comes; behind `mode tcp` it works. The client's address: `X-Forwarded-For` is a header the proxy appends (HAProxy's manual: the server must use the last one, since a client can send its own); the PROXY protocol does the same job for any TCP protocol, and the server must expect it (AWS NLB uses version 2).

**Where the clouds differ (4.2):** AWS NLB keeps the client's address by default for instance targets and for UDP, and not for IP targets over TCP or TLS, where it offers PROXY protocol v2; ALB adds `X-Forwarded-For`. Azure Load Balancer is pass-through (5-tuple hash by default). Google says plainly that its proxy load balancers "don't preserve client IP addresses by default" and its passthrough ones do.

**4.3 Choosing a server** (Sam Rose, "Load Balancing", interactive, optional but recommended; HAProxy Starter Guide 3.3.5). Round robin, weighted, least connections (AWS calls it least outstanding requests), and hashing. The lesson supplies one warning no resource frames for this learner: hashing on the **source address** sends everyone behind one NAT address to one server (topic 27); AWS's NLB page and Azure's distribution-mode page both warn of it. Slow start in one sentence (a recovered server gets its share gradually).

**4.4 Health checks** (David Yanacek, "Implementing health checks", sections "Ways to measure health" to "Real things that have gone wrong"; then the three clouds' pages, selected sections). The order:

1. Active and passive checking. HAProxy's `check`, `option httpchk GET /livez`, `http-check expect status 200`.
2. What to check: Yanacek's liveness, local health, dependency health. The lesson tells the fleet story with the lab's own numbers (**tried**): every web server's `/health` asks the shared database; the database restarts for a few seconds; within 6 s all three servers fail their checks together; HAProxy has no server left and answers every request, even the front page that needs no database, with `503 No server is available to handle this request`. Yanacek's sentence is the moral: trouble comes when a check "fails for a non-critical reason and when that failure is correlated across servers".
3. The arithmetic, worked on the board (the lesson supplies it; no resource does): with checks every `inter` seconds, a server that refuses connections is out after about `fall × inter`; one that hangs, after about `fall × inter + timeout`; a recovered one is back after `rise × inter`. Then each cloud's defaults through the same sums (facts table): an ALB's hung target keeps getting traffic for about 2 × 30 + 5 = 65 s and a recovered one waits 5 × 30 = 150 s. AWS's ALB page says each check is independent and the time a target takes to answer doesn't move the next one, which is what makes the sum exact there.
4. **Fail open.** What happens when every target fails at once differs, and the lesson must lay it side by side (facts 6 to 9): AWS ALB and NLB fail open (send to all targets anyway); Azure Load Balancer sends no new flows and lets established TCP flows continue; Google's Application Load Balancers answer 503 (the classic one 502); Google's passthrough Network Load Balancers send to unhealthy backends "as a last resort"; HAProxy answers 503 unless a `backup` server exists. Fail open is why the same deep check that took the lab's shop down would, on an ALB, have kept it up, and why that is luck, not design.
5. **Flapping and hysteresis.** A check that fails now and then, with `fall 1 rise 1`, takes the server out and puts it back every few seconds (**tried**: 6 times in 30 s). More than one failure to go down, more than one success to come back. Azure's probe page adds that its balancer waits longer before putting back an endpoint whose probe fluctuates.
6. Two gotchas from the clouds' pages: Azure Load Balancer's HTTP probe marks an instance down at the first non-200 answer (its threshold applies only to timeouts); AWS NLB's checks run from many nodes ("targets receive more than the configured number of health checks"), so a check endpoint must be cheap.

**4.5 Draining and stickiness** (HAProxy configuration manual `cookie`, management guide `set server ... state`; AWS ALB target group attributes, sections "Deregistration delay" and "Sticky sessions"; Google "connection draining"). Drain (no new users, existing connections finish), wait until the server's sessions reach zero, then maintenance; patch; ready. Stickiness by cookie (HAProxy `cookie SHOPSRV insert indirect nocache` and `cookie web1` on each server; ALB's `AWSALB`, a non-configurable 7 days) or by source address (NLB; Azure "Client IP" and "Client IP and protocol"; Google `CLIENT_IP`). The costs: uneven load, everyone behind one NAT on one server, carts lost when a sticky server dies, and the fix that is architecture, not balancer settings (keep session state somewhere shared).

**Where the clouds differ (4.5):** how draining meets stickiness. HAProxy in `drain` still accepts *persistent* connections (its management guide), so a sticky visitor keeps reaching the draining server (**tried**); an ALB routes a new request for a draining target to a healthy one. Default drain time: AWS 300 s (ALB and NLB); Google none unless set (0 to 3,600 s, "as quickly as possible" when unset or 0); Azure Load Balancer lets established TCP flows continue when an instance's probe goes down, and its probe page suggests failing the probe on purpose to drain.

**4.6 Reading the balancer** (management guide 9.3, `show stat` fields 0 to 24, `show servers state`). The lesson shows the four `show stat` columns that matter (`status`, `chkfail`, `chkdown`, `stot`), the `awk -F,` one-liner that prints them, and the three log lines (DOWN with its reason, UP, `backend ... has no server available!`). Then **runtime against configuration**, **tried**: a server put in maintenance through the API is `UP` again after `systemctl reload haproxy`. What lasts is in `haproxy.cfg`: the `disabled` keyword (it shows as administrative state 4, "maintenance because of the configuration"), or the server line removed, or a server-state file.

**4.7 Capacity when one fails** (the lesson supplies it). N+1: if any one of N servers can fail, the other N − 1 must carry the peak within the policy. Worked once: four servers at 60% become three at 80%.

**Recap** bullets: the six-month core, then the commands: `socat stdio /run/haproxy/admin.sock` with `show stat`, `show servers state`, `set server BACKEND/SERVER state drain|maint|ready`; `haproxy -c -f /etc/haproxy/haproxy.cfg`; `systemctl reload haproxy`; `journalctl -u haproxy`.

## 5. Verified facts

Each read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | HAProxy `fall` defaults to 3 consecutive failed checks, `rise` to 2 consecutive successes, `inter` to 2000 ms; `fastinter` and `downinter` change the interval while a server is changing state or down | HAProxy 2.8 Configuration Manual, `fall`, `rise`, `inter`: https://docs.haproxy.org/2.8/configuration.html |
| 2 | Without `timeout check`, HAProxy uses `inter` as the whole check's timeout; with it, `min(timeout connect, inter)` to connect and `timeout check` to read | same, `timeout check` |
| 3 | `set server <backend>/<server> state drain` "only removes the server from load balancing but still allows it to be checked and to accept new persistent connections"; `maint` stops all traffic and checks | HAProxy 2.8 Management Guide, 9.3: https://docs.haproxy.org/2.8/management.html |
| 4 | `show stat` field 17 `status`, 21 `chkfail`, 22 `chkdown` ("number of UP->DOWN transitions"), 23 `lastchg`, 4 `scur`, 7 `stot` (numbered from 0); `show servers state` `srv_admin_state` is a mask: 0x01 forced maintenance, 0x04 maintenance because of the configuration, 0x08 forced drain | same, 9.1 and the server-state description |
| 5 | `option forwardfor` appends `X-Forwarded-For`; the server must use the last occurrence; `send-proxy` sends the PROXY protocol for any TCP connection | Configuration Manual, `option forwardfor`, `send-proxy` |
| 6 | ALB health check defaults (instance and IP targets): interval 30 s, timeout 5 s, healthy threshold 5, unhealthy threshold 2, path `/`, success code 200; each check is independent and the target's answer time doesn't move the next check; "If a target group contains only unhealthy registered targets, the load balancer routes requests to all those targets" (fails open) | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html |
| 7 | NLB defaults: protocol TCP, interval 30 s, timeout 10 s (TCP and HTTPS) or 6 s (HTTP), healthy 5, unhealthy 2, matcher 200-399; fails open when all targets fail in all enabled zones; sends a TCP RST on client connections to a target that becomes unhealthy (unless failing open); checks come from many nodes, so targets get more than the configured number | https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-health-checks.html |
| 8 | Azure Load Balancer (Standard): probe protocols TCP, HTTP, HTTPS; all probes down: no new flows, established TCP flows continue; interval default 5 s in the portal, 15 s through ARM, CLI and PowerShell (minimum 5); HTTP probes: an explicit non-200 marks down at once, the threshold applies only to timeouts; probes come from 168.63.129.16; a fluctuating probe makes the balancer wait longer before marking up (page dated 2026-09-04) | https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-custom-probe-overview |
| 9 | Google health checks: default interval 5 s, timeout 5 s, healthy and unhealthy thresholds 2; all backends unhealthy: Application LBs return 503 (classic 502), proxy NLBs end new connections, passthrough NLBs distribute among unhealthy backends as a last resort | https://docs.cloud.google.com/load-balancing/docs/health-check-concepts (no date shown) |
| 10 | Azure Application Gateway default probe: every 30 s, timeout 30 s, unhealthy threshold 3, healthy on 200-399, host 127.0.0.1 unless set (page dated 2026-08-03) | https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-probe-overview |
| 11 | ALB deregistration delay defaults to 300 s and completes early when a target has no in-flight requests; a new request to a draining target is routed to a healthy one; duration-based stickiness cookie `AWSALB`, expiry 7 days, not configurable; algorithms round robin (default), least outstanding requests, weighted random | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html |
| 12 | NLB: client IP preservation on by default for instance targets and UDP; off by default for IP targets over TCP and TLS; proxy protocol v2; deregistration delay 300 s by default (120 s or more recommended); source-IP stickiness warns that "all clients behind the same NAT device have the same source IP address" | https://docs.aws.amazon.com/elasticloadbalancing/latest/network/edit-target-group-attributes.html |
| 13 | Azure Load Balancer distribution: 5-tuple hash by default; session persistence Client IP (2-tuple) or Client IP and protocol (3-tuple); clients behind proxies "might be seen as one unique client" (dated 2026-05-19) | https://learn.microsoft.com/en-us/azure/load-balancer/distribution-mode-concepts |
| 14 | Google connection draining: 0 to 3,600 s; unset or 0 ends existing connections "as quickly as possible"; no new connections to a removed backend | https://docs.cloud.google.com/load-balancing/docs/enabling-connection-draining |
| 15 | Google: "Proxy load balancers terminate incoming client connections"; they "don't preserve client IP addresses by default"; passthrough ones "don't terminate client connections" | https://docs.cloud.google.com/load-balancing/docs/choosing-load-balancer |
| 16 | nginx's active health checks (`health_check`) are "available as part of our commercial subscription"; open source has passive `max_fails` (default 1) and `fail_timeout` (default 10 s); `drain` and the `sticky` learn method became open source in 1.29.6 | https://nginx.org/en/docs/http/ngx_http_upstream_hc_module.html, https://nginx.org/en/docs/http/ngx_http_upstream_module.html |
| 17 | Ubuntu 24.04 packages: haproxy 2.8.30-0ubuntu0.24.04.2, nginx 1.24.0-2ubuntu7.19, socat 1.8.0.0-4ubuntu0.1 | `apt-cache policy` in `ubuntu:24.04`, tried |
| 18 | The three kinds of check (liveness, local health, dependency) and fail open; "Trouble arises when the health check fails for a non-critical reason and when that failure is correlated across servers" (David Yanacek, 2019) | https://builder.aws.com/content/3Ev53O39izHCtWLzp4XU6t8PC1O/implementing-health-checks |
| 19 | HAProxy's own guide describes the packet-level (layer 4) and proxy (layer 7) balancers, direct server return, health checks and stickiness | HAProxy Starter Guide 2.8, section 2: https://docs.haproxy.org/2.8/intro.html |
| 20 | Tried: a deep check took all three servers DOWN 6 s after the database stopped, and the front page got 503; `fall 1 rise 1` with every fourth check failing flapped 6 times in 30 s, `fall 2` and `fall 3` not at all; a frozen server (`inter 2s fall 3`, `timeout check 1s`) was DOWN after 8.6 s; drain kept the sticky visitor and let an 8-s download finish; a reload undid `maint` set through the API; a server-speaks-first service hung behind `mode http` | `prototypes/lb-ipsec/README.md` |

Where sources disagree or I couldn't confirm: AWS's NLB page gives a 6-second HTTP timeout and a 10-second TCP and HTTPS one, so an item that quotes "the NLB default timeout" must say which protocol. Google's health-check page shows no date. The Builders' Library article moved from `aws.amazon.com/builders-library/` to `builder.aws.com` (a 301); link the new address.

## 6. Resources

Fetched on 2026-11-11 unless noted. Minutes are reading at about 130 words a minute for the assigned part.

| # | Title (as the topic should list it) | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 (main) | HAProxy Starter Guide, section 2: "Quick introduction to load balancing and load balancers" | https://docs.haproxy.org/2.8/intro.html | reading | GPL-2.0 (HAProxy's LICENSE: GPL for everything but its LGPL include files); linked, not copied | 17 (about 2,200 words) | choose-the-balancer, health-checks, drain-and-stick | 2026-11-11 |
| R2 | David Yanacek, "Implementing health checks" (Amazon Builders' Library): read "Ways to measure health" to the end of "Real things that have gone wrong" | https://builder.aws.com/content/3Ev53O39izHCtWLzp4XU6t8PC1O/implementing-health-checks | reading | © Amazon Web Services; linked, not copied | 25 (about 3,300 of its 4,000 words) | health-checks, failover-math | 2026-11-11 |
| R3 | Google Cloud, "Choose a load balancer": the section on proxy and passthrough load balancers | https://docs.cloud.google.com/load-balancing/docs/choosing-load-balancer | reading | CC BY 4.0 (Google Cloud documentation; the footer didn't come through my fetch: confirm on the day) | 6 | choose-the-balancer | 2026-11-11 |
| R4 | Sam Rose, "Load Balancing" (interactive essay): optional | https://samwho.dev/load-balancing/ | interactive | no licence stated on the page: link only | 15 (about 2,500 words with simulations) | choose-the-balancer | 2026-11-11 |
| R5 | AWS, "Health checks for Application Load Balancer target groups": the settings table and the fail-open paragraph | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | reading | © AWS; linked | 5 | health-checks, failover-math | 2026-11-11 |
| R6 | AWS, "Edit target group attributes for your Application Load Balancer": "Deregistration delay" and "Sticky sessions" only | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html | reading | © AWS; linked | 6 | drain-and-stick | 2026-11-11 |
| R7 | Azure, "Azure Load Balancer health probes": "Probe down behavior", "Probe interval & timeout", "Probe threshold" | https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-custom-probe-overview | reading | CC BY 4.0 (MicrosoftDocs/azure-docs, as recorded in `csa.hw.windows-ad`); linked | 5 | health-checks | 2026-11-11 |
| R8 | Google Cloud, "Health checks overview": the default settings and the table of what each load balancer does when all backends are unhealthy | https://docs.cloud.google.com/load-balancing/docs/health-check-concepts | reading | CC BY 4.0; linked | 5 | health-checks | 2026-11-11 |
| R9 | HAProxy 2.8 Management Guide, 9.3 "Unix Socket commands": `show stat`, `show servers state`, `set server` (lookup) | https://docs.haproxy.org/2.8/management.html | reference | GPL-2.0; linked | 8 | read-the-balancer, drain-and-stick | 2026-11-11 |
| R10 | HAProxy 2.8 Configuration Manual: `check`, `inter`, `fall`, `rise`, `option httpchk`, `http-check expect`, `cookie`, `option forwardfor`, `disabled` (lookup) | https://docs.haproxy.org/2.8/configuration.html | reference | GPL-2.0; linked | lookup, inside the labs | all | 2026-11-11 |

Reading assigned before the labs: R1, R2, R3, R5 to R8 = 69 minutes; R4 optional; R9 and R10 are opened during the labs. Considered and dropped: Matt Klein's "Introduction to modern network load balancing and proxying" (blog.envoyproxy.io) would be an excellent R1, but it did not answer from this machine (connection failed with curl and WebFetch); a resource that can't be opened isn't one. Cloudflare's learning pages returned 403.

## 7. Practice ladder

All labs are systemd labs on one scenery, called **the shop's balancer** below (it is what the network-lab base must provide; section 10):

```
office 10.0.9.2 -- eth1 10.0.9.1 [lab: HAProxy] br0 10.0.1.1 -- web1 10.0.1.11, web2 .12, web3 .13   (shop-web on 8080)
                                                              -- api1 10.0.1.21, api2 .22            (shop-web on 8081, build only)
                                                              -- stock1 10.0.1.31, stock2 .32        (stock-sync on 7000, build only)
                                                              -- db 10.0.1.20                        (shop-db on 5432)
```

Each backend machine is a network namespace with a veth into `br0`, and its program is a systemd template unit with `NetworkNamespacePath=/run/netns/%i` (**tried**). `shop-web` (Python, standard library, one file) answers `/` (the front page, needs nothing; names the server), `/orders` (needs the database), `/health` (deep: 200 only if `db:5432` answers), `/livez` (shallow), `/slow?s=N` (a download that takes N seconds), `/whoami` (prints the address it saw the request come from and any `X-Forwarded-For`), and sends `X-Served-By: NAME`. A **hiccup switch** for checks: while `/run/shop/hiccup-NAME` exists, every fourth `/livez` answers 503 at once (the prototype used a 1.5-s delay against `timeout check 1s`; switch to a fast 503 so that a longer `timeout check` can't hide it and only hysteresis fixes it). `stock-sync` (Python) sends `STOCK-SYNC 1.0 ready <name>` on connect and echoes a line back. The learner is in group `haproxy`, so `socat stdio /run/haproxy/admin.sock` works without `sudo`; HAProxy logs to `/dev/log` with no `chroot` line, so `journalctl -u haproxy` shows it.

### 7.1 `example-balance-the-shop` (worked example, systemd lab), skills `choose-the-balancer`, `health-checks`, `read-the-balancer`, `drain-and-stick`

Scenery: HAProxy already balances `web1` to `web3` (`balance roundrobin`, `option httpchk GET /livez`, `default-server inter 2s fall 3 rise 2`), plus a `listen stock` in `mode http` on 7000 in front of `stock1` (the mistake the example uncovers). About 35 minutes. The steps, each with a label and a note, as Module 1's examples:

1. **The servers, one by one.** `curl -s 10.0.1.11:8080/` and the other two from the lab: three machines, three answers.
2. **The balancer's configuration.** `cat /etc/haproxy/haproxy.cfg`: frontend, backend, servers, the check line read aloud.
3. **Through the balancer.** `for i in 1 2 3 4 5 6; do from-office curl -s http://10.0.9.1/; done`: round robin.
4. **Its real state.** `echo "show stat" | socat stdio /run/haproxy/admin.sock | awk -F, '$1 == "web" {print $2, $18, $23, $8}'`: name, status, times gone down, requests served. Then `show servers state`.
5. **A server dies.** `sudo systemctl stop shop-web@web3`; `journalctl -u haproxy -n 5` shows `Server web/web3 is DOWN, reason: Layer4 connection problem` (the writer captures the exact text); the stats show it; six office requests reach only web1 and web2. `sudo systemctl start shop-web@web3`; it's UP after two good checks.
6. **A server hangs.** `sudo systemctl kill -s STOP shop-web@web2`; time how long until `status` says DOWN (about `fall × inter`, plus the check's timeout); `kill -s CONT`.
7. **Who the server thinks you are.** `from-office curl -s http://10.0.9.1/whoami`: the server saw 10.0.1.1, the balancer. Add `option forwardfor` to the backend, `sudo haproxy -c -f /etc/haproxy/haproxy.cfg`, `sudo systemctl reload haproxy`, ask again: `X-Forwarded-For: 10.0.9.2`.
8. **Layer 4 for a protocol that speaks first.** `from-office nc -w 3 10.0.9.1 7000` prints nothing (the `mode http` proxy waits for an HTTP request); change that `listen` to `mode tcp`, reload, and the banner arrives.
9. **Drain.** Visit with a cookie jar after adding `cookie SHOPSRV insert indirect nocache` and `cookie webN` (given), see stickiness; `set server web/web1 state drain`; new visitors avoid web1, the sticky visitor doesn't; `set server web/web1 state ready`.
10. **Write down what you saw** into `~/example/`: `down.txt` (the reason HAProxy logged for web3), `hung-seconds.txt` (the number you timed), `xff.txt` (the header line), `banner.txt` (the banner through port 7000).

Checks: `down.txt` contains `Layer4` and `web3`; `hung-seconds.txt` is a number from 4 to 15; `xff.txt` contains `10.0.9.2`; `banner.txt` starts `STOCK-SYNC`; the running config has `option forwardfor` and the stock listener in `mode tcp` (read from `haproxy -c` passing and the file); every server is `UP` and ready at the end (`show servers state` admin 0, op 2). Wrong fixes: `left-stopped.sh` (web3 never started again), `left-draining.sh`, `banner-by-hand.sh` (the banner typed into the file from `nc` straight to `stock1`, while 7000 is still `mode http`).

### 7.2 Recall on choosing a balancer and on checks

Every multiple-choice item is written out in full, choices of one shape and within about 1.3 times of each other in length, the right answer the longest in no more than a third of the topic's items (content/README, Module 2 plan 3.1). Below, the scenario and the right answer; the writer writes the wrong choices as real, plausible claims (suggested in brackets).

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-route-by-path` | mcq | choose-the-balancer | `/api/` to two servers, everything else to three. Right: a layer 7 balancer, because the path is inside the HTTP request, which a layer 4 one never reads. [Wrong: a layer 4 balancer with two ports; DNS with two names for the same address; source-address hashing.] |
| `mcq-speaks-first` | mcq | choose-the-balancer | The stock-sync service hangs behind HAProxy `mode http` but works direct. Right: the HTTP proxy waits for an HTTP request before it talks to a server, and this protocol's server speaks first, so it needs `mode tcp`. [Wrong: the health check marks it down; port 7000 needs root; `timeout client` too short.] |
| `mcq-who-is-the-client` | mcq | choose-the-balancer | After the move behind HAProxy, the app's log shows every request from 10.0.1.1. Right: the proxy opens its own connection, so add `X-Forwarded-For` (or the PROXY protocol) and have the app read it. |
| `mcq-tls-stays-with-payments` | mcq | choose-the-balancer | Payments insists TLS ends on its own servers. Right: pass the TLS through at layer 4 (`mode tcp`, an NLB TCP listener), giving up path rules and cookies for that service. |
| `mcq-which-is-pass-through` | mcq | choose-the-balancer | Which pairs a cloud balancer with the right kind? Right: Azure Load Balancer passes packets through and keeps the client's address. [Wrong, each stating a real product with the wrong kind: ALB passes packets through; Application Gateway is layer 4; Google's Application LB keeps the client address by default.] |
| `predict-stat-columns` | predict_shell | read-the-balancer | File `stat.csv` and command in 7.6; output pinned there. |
| `mcq-deep-check` | mcq | health-checks | `/health` checks the shared database; the database restarts for 20 s at night. Right: every server fails its check together and HAProxy has nothing to send the front page to, so everything gets 503 for a while. [Wrong: only `/orders` fails; each server drops out in turn; nothing happens because 20 s is under the timeout.] |
| `mcq-what-to-check` | mcq | health-checks | The web servers' only dependency is the shared database. Right: check that the server itself answers (and its own disk and threads are fine), and let `/orders` fail on its own when the database is down. |
| `mcq-fail-open` | mcq | health-checks | Every target fails its checks at the same moment. Right: an AWS ALB sends to all of them anyway; Azure Load Balancer sends no new flows; Google's Application LB answers 503. (Write as three separate true/false-style choices, each naming one cloud; one is right.) |
| `mcq-azure-http-probe` | mcq | health-checks | Azure Load Balancer, HTTP probe, threshold 3; one probe gets a 500. Right: the instance is marked down at once (the threshold only counts timeouts). |
| `mcq-flapping` | mcq | health-checks | web2 goes DOWN and UP every few seconds; its check fails about one time in four; `fall 1 rise 1`. Right: require more than one failure to go down and more than one success to come back. [Wrong: remove the check from web2; lower `inter` to check faster; give web2 a bigger weight.] |
| `predict-down-reasons` | predict_shell | read-the-balancer | `haproxy.log` and command in 7.6. |
| `est-haproxy-dead-server` | estimate | failover-math | `inter 2s`, `fall 3`; a server stops right after a passing check and refuses connections at once. Seconds until HAProxy marks it DOWN? Exactly. **6** (`fall * inter`). Mistakes: 2 (one check), 4 (`rise * inter`). |
| `est-alb-hung-target` | estimate | failover-math | ALB defaults given in the prompt (interval 30 s, timeout 5 s, unhealthy threshold 2). A target hangs just after a passing check. Seconds until it's out of service? Exactly. **65** (`unhealthy * interval + timeout`). Mistakes: 60 (no timeout), 70 (`unhealthy * (interval + timeout)`), 35 (one check). |
| `est-capacity-after-loss` | estimate | failover-math | Four web servers each at 60% CPU at the peak; one fails and its share spreads evenly. Percent on each survivor? Exactly. **80**. Mistakes: 45 (`60 * 3 / 4`), 60. |

### 7.3 `fill-health-check` (fill-in, systemd lab), skills `health-checks`, `failover-math`

The backend section of `haproxy.cfg` is given with gaps, and the prompt states the shop's policy: "a server that stops answering is out of rotation within 15 seconds; one failed check never takes a server out; a database restart must not take the front page down; a recovered server is back after two good checks." Gaps: the check path (`/livez`), `http-check expect status ...`, and `default-server inter ... fall ... rise ...` (any values meeting the policy: `fall` 2 or more, `rise` 2, `fall × inter + timeout` at most 15). The prompt says the file is checked with `haproxy -c` and loaded with `systemctl reload haproxy`. About 25 minutes.

Checks (each makes its own inputs at check time; the server each acts on is picked at random from the three):

1. `config-valid`: `haproxy -c -f /etc/haproxy/haproxy.cfg` passes and the running worker started after the file's last change. A reload starts a new worker under the same master, so the unit's start time isn't enough: read the worker's uptime from the runtime API's `show info` (`Uptime_sec`) or the worker's start time from `/proc/PID/stat`, and compare with the file's modification time. Not tried: the writer confirms which of the two resets at a reload in 2.8.
2. `hung-server-out` (`timeout: 40`): the check freezes a random server (`systemctl kill -s STOP`), polls `show stat` every 0.5 s, and passes if it is DOWN within 15 s; then thaws it and waits for UP.
3. `hiccups-tolerated` (`timeout: 40`): creates `/run/shop/hiccup-NAME` for a random server for 20 s while sending traffic; passes if that server's `chkdown` didn't change. Removes the file. Deterministic: every fourth check fails, so `fall 1` always flaps and `fall 2` never does.
4. `db-restart-survived` (`timeout: 40`): stops `shop-db` for 15 s; passes if every one of 20 office requests to `/` during it got 200; starts the database again.
5. `back-after-two` : `show servers state` lists all three servers ready and UP at the end.

Wrong fixes: `deep-check.sh` (`/health`), `fall-one.sh` (`fall 1 rise 1`), `slow-detection.sh` (`inter 10s fall 3`), `file-not-loaded.sh` (the file right, no reload).

### 7.4 `write-drain-server` (write, systemd lab), skills `drain-and-stick`, `read-the-balancer`

From a blank file, `~/bin/drain-server NAME`: put `web/NAME` in drain through the runtime API, wait until its current sessions (`scur` in `show stat`) reach 0, checking every second for at most 60 s, then set it to maintenance and print `NAME drained in N s` (or, at 60 s, `NAME still had K sessions; set to maintenance anyway`), exit 0; with an unknown name, print an error to stderr and exit 1. Module 1's scripting topic taught every construct (arguments, `while`, `sleep`, `awk -F,`, exit codes); the prompt gives the whole `chmod +x` line and names the editor. About 35 minutes.

Checks (each picks NAME at random among web1 to web3 at check time, and puts every server back to ready afterwards, which leaves the machine as a correct script would):

1. `waits-for-the-download` (`timeout: 60`): a 10-second `/slow` download pinned to NAME by a cookie is started; 1 s later the learner's script runs; the check polls `show servers state` every 0.25 s throughout. Pass if: the state went to drain (admin 8) before maintenance (admin 1), the script returned after the download finished (timestamps), the download completed with all its bytes, and the server ended in maintenance.
2. `no-new-visitors` (`timeout: 30`): during a second run, 10 office requests without a cookie, sent while NAME drains, none served by NAME.
3. `says-how-long`: the printed line matches `^NAME drained in [0-9]+ s$` for the name given.
4. `gives-up-at-60` (`timeout: 90`): the check holds a sticky visitor on NAME who keeps making requests every half second; the script must still end within 75 s, print the "still had" line and set maintenance.
5. `unknown-name`: `drain-server web9` exits 1 and prints to stderr only.

Wrong fixes: `maint-at-once.sh` (sets maintenance straight away: never seen in drain, returns before the download ends), `no-wait.sh` (drain then maintenance with no loop), `hard-coded-web2.sh`, `waits-forever.sh` (no 60-s limit: fails check 4), `stops-the-service.sh` (`systemctl stop shop-web@NAME`: the download is cut).

### 7.5 More recall (practice), after the labs

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-drain-then-maint` | mcq | drain-and-stick | Patching web2 without dropping anyone. Right: drain, wait for its sessions to reach zero, then maintenance. [Wrong: maintenance first, then wait; stop the service, HAProxy will notice; lower its weight and restart it at once.] |
| `mcq-drain-keeps-sticky` | mcq | drain-and-stick | A visitor with a `SHOPSRV=web1` cookie keeps reaching web1 after `state drain`. Right: HAProxy's drain still accepts persistent connections; maintenance would move them. An ALB, by contrast, sends that visitor's new request to a healthy target. |
| `mcq-nat-and-source-hash` | mcq | drain-and-stick | 300 office staff behind one NAT address; the balancer uses source-address affinity across three servers. Right: one server gets all of them. |
| `mcq-draining-defaults` | mcq | drain-and-stick | The same rolling deploy cut long downloads on Google Cloud and not on AWS. Right: AWS waits 300 s by default before finishing deregistration; Google drains only if a timeout is set. |
| `predict-servers-state` | predict_shell | read-the-balancer | File and command in 7.6. |
| `mcq-maint-lost-at-restart` | mcq | read-the-balancer | web3 was put in maintenance with `socat` last week; after Sunday's restart it serves errors again. Right: state set through the runtime API isn't saved; mark it `disabled` in `haproxy.cfg` (or remove it). |
| `est-n-plus-one` | estimate | failover-math | The peak needs 420% of one server's CPU; with any one server failed the rest must stay at or under 70%. Fewest servers? Exactly. **7** (`ceil(load / policy) + 1`). Mistakes: 6 (no spare), 5 (no headroom). |

### 7.6 The predict-the-output items, pinned

Run on 2026-11-11 in Git Bash; the writer re-runs them in the validator. Files are constructed in HAProxy 2.8's formats from the prototype's captures (labelled constructed).

**`predict-stat-columns`** (`read-the-balancer`). Prompt: `stat.csv` is the first 24 columns of `show stat`; the command prints each web server's status, its UP-to-DOWN count and how many requests it has served. File:

```
# pxname,svname,qcur,qmax,scur,smax,slim,stot,bin,bout,dreq,dresp,ereq,econ,eresp,wretr,wredis,status,weight,act,bck,chkfail,chkdown,lastchg
shop,FRONTEND,,,0,3,262143,260,24120,49660,0,0,0,,,,,OPEN,,,,,,
web,web1,0,0,0,1,,96,8928,18336,,0,,0,0,0,0,UP,1,1,0,0,0,412
web,web2,0,0,0,1,,68,6324,12988,,0,,0,0,0,0,UP,1,1,0,9,9,1
web,web3,0,0,0,1,,96,8868,18336,,0,,0,0,0,0,UP,1,1,0,0,0,412
web,BACKEND,0,0,0,3,,260,24120,49660,0,0,,0,0,0,0,UP,3,3,0,,0,412
```

Command: `awk -F, '$1 == "web" && $2 != "BACKEND" {print $2, "status=" $18, "down-transitions=" $23, "requests=" $8}' stat.csv`. Output:

```
web1 status=UP down-transitions=0 requests=96
web2 status=UP down-transitions=9 requests=68
web3 status=UP down-transitions=0 requests=96
```

Explanation to write: web2 is UP *now* but has gone down nine times and last changed a second ago (`lastchg` 1): it is flapping, and it has served fewer requests than the others.

**`predict-down-reasons`** (`read-the-balancer`, `health-checks`). File `haproxy.log`: the three captured "is DOWN, reason: Layer7 wrong status, code: 503" lines for web1, web2 and web3 within six seconds, the captured `backend web has no server available!`, and one constructed httplog line with `web/<NOSRV>` and status 503. Command: `grep -o 'web/web[0-9] is DOWN, reason: [^,]*' haproxy.log; grep -c 'NOSRV' haproxy.log`. Output: the three `web/webN is DOWN, reason: Layer7 wrong status` lines, then `1`. Explanation: all three failed the same way within seconds, so look for what they share; `<NOSRV>` is a request HAProxy had nowhere to send.

**`predict-servers-state`** (`read-the-balancer`, `drain-and-stick`). File `servers-state.txt`: `show servers state` for web1 (op 2, admin 0), web2 (op 2, admin 8), web3 (op 0, admin 1). Command: `awk 'NR > 2 {s = "ready"; if ($7 == 8) s = "drain"; if ($7 == 1) s = "maint"; print $4, s}' servers-state.txt`. Output: `web1 ready`, `web2 drain`, `web3 maint`. The full file is in `prototypes/lb-ipsec/predict/lb3/`.

### 7.7 Ladder order for `topic.yaml`

`example-balance-the-shop`, `mcq-route-by-path`, `mcq-speaks-first`, `mcq-who-is-the-client`, `mcq-tls-stays-with-payments`, `mcq-which-is-pass-through`, `predict-stat-columns`, `mcq-deep-check`, `mcq-what-to-check`, `mcq-fail-open`, `mcq-azure-http-probe`, `mcq-flapping`, `predict-down-reasons`, `est-haproxy-dead-server`, `est-alb-hung-target`, `est-capacity-after-loss`, `fill-health-check`, `mcq-drain-then-maint`, `mcq-drain-keeps-sticky`, `mcq-nat-and-source-hash`, `mcq-draining-defaults`, `predict-servers-state`, `mcq-maint-lost-at-restart`, `est-n-plus-one`, `write-drain-server`. That is 22 quick items (5 + 1 + 5 + 1 + 3 + 4 + 1 + 1 + 1, of which 7 produce an answer: three predicts and four estimates) and three labs. Fifteen are multiple choice: the writer checks the "longest in more than half" rule across all of them, and the review-only ones.

## 8. Proofs

### 8.1 Build: `build-shop-balancer` (systemd lab, 60 minutes), skills all five

**Prompt (substance).** The shop's new balancer, from a nearly empty `/etc/haproxy/haproxy.cfg` (only `global` and `defaults`, the stats socket line included). Requirements, each a check:

- The web front end on `10.0.9.1:80`: everything under `/api/` goes to `api1` and `api2` (port 8081), everything else to `web1` to `web3` (port 8080), round robin.
- Each web visitor stays on one web server for their visit with a cookie named `SHOPSRV` (the cart lives in the server's memory). The office reaches the internet through one NAT address, so stickiness by address won't do.
- Every backend server sees the office laptop's address.
- The stock-sync service on `10.0.9.1:7000` is balanced across `stock1` and `stock2`. It speaks first.
- The health policy of the fill-in (out within 15 s when it stops answering; one failed check never removes a server; a database restart never takes the front page down), for the web and API servers.
- HAProxy starts at boot with this configuration.

The prompt names the rules of the fix ("don't change the servers or the database") and gives the four commands it may need (`haproxy -c -f`, `systemctl reload haproxy`, `socat stdio /run/haproxy/admin.sock`, `from-office curl`).

**Checks** (`test_skills` in parentheses; `timeout:` where given; total under 600 s):

1. `config-valid-and-running` (read-the-balancer): `haproxy -c` passes; `haproxy` active and enabled; the running worker started after the file's last change; its command line names `/etc/haproxy/haproxy.cfg`.
2. `web-round-robin` (choose-the-balancer): 30 office requests to `/` with no cookie: each web server serves at least 8; none from an API server.
3. `api-routed` (choose-the-balancer): 10 requests to `/api/whoami`: all from api1 or api2, both used.
4. `sticky-by-cookie` (drain-and-stick): with a cookie jar, 10 requests all on one server, and the jar holds `SHOPSRV`; a second visitor without a cookie is spread (covered by check 2, which fails source hashing, since every office request has one address).
5. `client-address-passed` (choose-the-balancer): `/whoami` through `/` and through `/api/` reports `X-Forwarded-For` ending in `10.0.9.2`.
6. `stock-sync-at-layer-4` (choose-the-balancer): 6 connections to `10.0.9.1:7000` from the office each get a `STOCK-SYNC 1.0 ready` banner within 3 s, from both stock servers.
7. `hung-server-out` (health-checks, failover-math, `timeout: 40`): as the fill-in's, on a random web server.
8. `hiccups-tolerated` (health-checks, `timeout: 40`): as the fill-in's, on a random web server **and** a random API server at once.
9. `db-restart-survived` (health-checks, `timeout: 40`): as the fill-in's.
10. `all-ready-at-the-end` (read-the-balancer): every server in every backend is UP and ready (no server left in drain or maintenance by the learner).

**Wrong fixes** (each must fail at least one check): `deep-check.sh` (`/health`: check 9), `no-checks.sh` (no `check`: check 7, because a frozen server keeps getting requests that hang, and its status is "no check"), `fall-one.sh` (check 8), `slow-detection.sh` (`inter 10s`: check 7), `source-affinity.sh` (`balance source` in place of the cookie: check 2), `no-forwardfor.sh` (check 5), `stock-in-http-mode.sh` (check 6), `no-api-route.sh` (check 3), `started-by-hand.sh` (the right config in `/tmp` run with `haproxy -f`, the service disabled: check 1). Nine wrong fixes, three of them shortcuts the prompt forbids (no checks, source affinity, by hand).

**Shortcuts and why each check stops it.** Removing health checks to stop flapping: check 7. Raising `fall` to 10 to stop flapping: check 7 (detection over 15 s). Pinning everyone to one server ("sticky") with `balance source`: check 2. Typing the banner or the address anywhere: checks 5 and 6 read live answers from servers the check picks. A config that only lives in a hand-started process: check 1 and the restart trial.

**Restart trial**: author applies `solution.sh`, `docker restart`s the container, runs the checks: every check must pass again (nothing here is runtime-only by design).

**Steps, versions** are a checkpoint's; topics have none.

### 8.2 Debug: `debug-errors-every-few-minutes` (systemd lab, 45 minutes), skills `health-checks`, `read-the-balancer`, `drain-and-stick`

**The story (scenery, made once at first boot by a `story.sh`, as Module 2's debug labs do).** The shop's balancer as in 7.1, configured by a colleague who has left. Three faults:

1. **A deep check.** The web backend checks `/health`, which asks the database. The database (scenery) restarts itself for 12 s every 60 s ("a nightly job that runs all day by mistake", which the prompt does not say), so every minute all three servers go DOWN together and customers get 503 for several seconds.
2. **No hysteresis.** `default-server inter 1s fall 1 rise 1`, and web2's check hiccups one time in four (the hiccup switch, permanently on for web2), so web2 flaps all the time; its `chkdown` climbs.
3. **Out by hand, back at restart.** web3's application is broken (every page answers 500; its `/livez` and `/health` still pass, as a broken deploy's often do). The story put it in maintenance through the runtime API. The configuration doesn't know; at every restart of HAProxy, web3 is back and one page in three fails.

**Prompt (substance, written to rule 5 of the house rules).** What the system is (the office, the balancer, three web servers, a database, the stock service not involved), the symptom ("several times an hour, every customer gets 'No server is available' for a few seconds; the shop is slower than it should be in between; and the on-call notes say that after every restart of the balancer about one page in three fails with an error until someone 'runs the usual command'"), three faults, and the rules of the fix: change only the balancer's configuration (not the servers' programs, not the database or its schedule, not web3); the balancer must still take a server that stops answering out within 15 s; every fix must last a restart. It names the commands that show the symptom (`from-office curl -s -o /dev/null -w '%{http_code}\n' http://10.0.9.1/` in a loop; `journalctl -u haproxy`; `show stat`) and the done criterion: a minute of requests with no error, and the same after `sudo systemctl restart haproxy`. Check descriptions are shown only after a first try (#235) and state end states only.

**Checks:**

1. `no-errors-for-a-minute` (health-checks, `timeout: 90`): 60 s of office requests, two a second, with and without a `SHOPSRV=web3` cookie: every answer 200, and none served by web3. (Fails while the deep check remains, because the database's 60-s cycle falls inside the window; fails while web3 is reachable through a cookie.)
2. `web2-steady` (health-checks, `timeout: 40`): web2's `chkdown` unchanged over 20 s of traffic, and web2 still serves a share (at least a fifth of 30 requests).
3. `web3-out-for-good` (read-the-balancer, drain-and-stick): in `show servers state`, web3 is absent or its administrative state has the configuration bit (0x04). This reads what the *running* process loaded from the file, so a file edit without a reload, or an API-only `maint` (0x01), fails.
4. `hung-server-out` (health-checks, `timeout: 40`): a random one of web1 and web2 frozen is DOWN within 15 s.
5. `left-alone` : checksums of `shop-web`, the database's unit and timer, and web3's files equal the story's; the hiccup switch for web2 is still there.

**Wrong fixes:** `checks-removed.sh` (no flapping, no fleet-down, but check 4 fails), `fall-ten.sh` (check 4), `maint-via-api.sh` (all else fixed, web3 out only through `socat`: check 3), `weight-zero.sh` (web3 `weight 0` in the file: a sticky visitor still reaches it, check 1), `db-schedule-stopped.sh` (the database's restart timer disabled: check 5), `health-made-shallow-in-app.sh` (the app edited so `/health` skips the database: check 5), `only-two-fixed-a.sh` and `-b.sh` (two of three faults fixed, each leaving a different one).

Confirm on CI that each fault alone turns only its own checks red (the Module 2 plan's caution for multi-fault labs). The writer captures the real log lines of all three faults in the lesson's recall items only where they don't give this lab away (the practice items above use the fleet-down lines; that's acceptable, because finding which of three faults causes which line is still the work).

### 8.3 Explain

**Prompt.** "A shop runs three web servers behind a load balancer. Last night a routine database restart took the whole shop offline for half a minute, although the front page doesn't use the database, and the on-call engineer saw one server 'blinking' in and out all week. Explain, in your own words: whether this shop's web traffic and its stock-sync service need a layer 4 or a layer 7 balancer, and why; what the health check should test and why the database restart took every server out at once; how long a dead or hung server keeps getting traffic with the settings you'd choose, with the numbers; why a server blinks in and out and how to stop it without blinding the balancer; how you'd take a server out for patching without hurting anyone, and how sticky sessions change that; and what any two of AWS, Azure and Google Cloud would have done differently when every server failed its check."

**Rubric** (ids, required unless noted):

- `l4-l7`: Layer 7 reads the HTTP request (paths, cookies, headers) and can terminate TLS, so the web traffic with path routing and cookie stickiness needs it; the stock-sync service speaks first and isn't HTTP, so it needs layer 4 (`mode tcp`); a proxy hides the client's address unless it adds `X-Forwarded-For` or the PROXY protocol, a pass-through balancer keeps it.
- `what-to-check`: Check the server itself (liveness or local health), not the shared database; a dependency check fails on every server at once when the shared thing blips, leaving nothing to send traffic to, so even pages that don't need the database fail.
- `timing`: A dead server is out after about failures-needed × interval (plus the check timeout if it hangs) and back after successes-needed × interval, with any correct numbers; for example 3 × 2 s + 1 s.
- `flapping`: A check that fails now and then, acted on after one failure, flaps; require several failures to go down and several successes to come up (hysteresis), rather than removing or slowing the checks.
- `drain`: Drain (no new users, existing ones finish), wait for its connections to reach zero, then maintenance; sticky visitors keep reaching a draining HAProxy server until maintenance; state set through the API must also go in the configuration to survive a restart.
- `clouds` : Any two correct, for example: an AWS ALB fails open and sends to all targets; Azure Load Balancer sends no new flows and lets established TCP flows continue; Google's Application LB returns 503; defaults differ (ALB 30 s × 2 down, 5 up; Google 5 s, 2 and 2; Azure probes every 5 or 15 s).
- `n-plus-one` (optional): when one of N servers fails, the rest carry its share, so size for N − 1 at the peak.

**Model answer**: the writer drafts it from the rubric, about 400 words, in the voice of the existing model answers.

## 9. Review pool

At least two per skill, mostly judgement and numbers. ● marks items already in the practice ladder.

| Skill | Items |
| --- | --- |
| `choose-the-balancer` | ● `mcq-speaks-first`, ● `mcq-who-is-the-client`, ● `mcq-which-is-pass-through`, review-only `mcq-l7-terminates-tls` (to route by cookie the balancer must see inside TLS, so it terminates it and holds the certificate), review-only `mcq-nlb-client-ip` (NLB with IP targets over TCP: the app sees the balancer's address unless client IP preservation or proxy protocol v2 is turned on) |
| `health-checks` | ● `mcq-deep-check`, ● `mcq-flapping`, ● `mcq-fail-open`, review-only `mcq-cheap-check` (NLB health checks come from many nodes; make the endpoint a cheap static answer) |
| `failover-math` | ● `est-alb-hung-target`, ● `est-capacity-after-loss`, ● `est-n-plus-one`; review-only `est-back-in-service` (ALB healthy threshold 5 × interval 30 = **150** s; mistakes 60, 30), `est-flaps-per-hour` (`fall 1`, checks every 2 s, one check in 50 fails at random: about **36** an hour, within 10%; mistakes 1800 (every check), 0.72 (what `fall 2` would give)), `est-rolling-deploy` (12 servers, one at a time, each waits a full 300-s deregistration delay plus 60 s to start: **72** minutes, exactly; mistakes 60, 6), `est-azure-probe-out` (Azure Load Balancer TCP probe deployed with the CLI's 15-s default interval and threshold 2: about **30** s; mistakes 10 (the portal's 5 s), 15) |
| `drain-and-stick` | ● `mcq-drain-then-maint`, ● `mcq-drain-keeps-sticky`, ● `mcq-nat-and-source-hash`, ● `mcq-draining-defaults` |
| `read-the-balancer` | ● `predict-stat-columns`, ● `predict-down-reasons`, ● `predict-servers-state`, ● `mcq-maint-lost-at-restart` |

`review_pool:` for `topic.yaml` (16): `mcq-speaks-first`, `mcq-which-is-pass-through`, `mcq-l7-terminates-tls`, `mcq-deep-check`, `mcq-flapping`, `mcq-fail-open`, `est-alb-hung-target`, `est-n-plus-one`, `est-back-in-service`, `est-flaps-per-hour`, `est-rolling-deploy`, `mcq-drain-keeps-sticky`, `mcq-nat-and-source-hash`, `predict-stat-columns`, `predict-servers-state`, `mcq-maint-lost-at-restart`. Seven of them produce an answer (estimates and predicts).

## 10. What needs platform work first

**None new.** Everything here uses what exists or is already agreed: systemd labs, the estimate type (ADR-0024), the per-check `timeout:` (ADR-0018's second amendment), the debug page that hides check descriptions until a first try (#235).

**What the labs need from the network-lab base** (smallest version):

1. The systemd lab image with the shared first `RUN`, and a Module 3 network layer that includes `haproxy socat` (6.3 MB here). One layer for all Module 3 labs is the recommendation (`frr frr-pythontools strongswan-swanctl charon-systemd libstrongswan-standard-plugins haproxy socat` plus what the other topics need, about 35 MB; `frr-labs-common.md` N1 asks for FRR on the same shared line), so every Module 3 image shares it.
2. A boot script that makes the office (Module 1's veth on `eth1`) and a backend bridge `br0` with named hosts, each a namespace with one address, from a small table (`web1 10.0.1.11`, ...), and a template unit `NAME@.service` pattern with `NetworkNamespacePath=/run/netns/%i` for the programs on them. **Tried** as `network.sh` and `shop-web@.service`. This fits the routing labs' proposal of one shared script reading a declarative topology file (`frr-labs-common.md` N2) if that script can attach hosts to a bridge as well as to point-to-point veths; their `on NAME COMMAND` (N7) serves here too.
3. `shop-web`, `shop-db` and `stock-sync` stand-ins with the endpoints and switches in section 7, and `/run/shop/` for the hiccup switch.
4. HAProxy's config without `chroot` (so `/dev/log` reaches journald) and the learner in group `haproxy`.

**Kernel:** nothing beyond what Module 1's networking labs already use (veth, bridge, network namespaces). No module loads.

## 11. Cost and time

**Money:** none. Everything is local; no cloud account is touched.

**Learner's time**, worked out: lesson 15; assigned reading 69 (R1 17, R2 25, R3 6, R5 5, R6 6, R7 5, R8 5); 22 quick items at 1.5 = 33; worked example 35; fill-in 25; write 35; build 60; debug 45; explain 20. **Total 337 minutes**, which is over Module 2's 240 to 300. Two ways down, in the order I'd take them: make R6 to R8 "More resources" and have the lesson carry their numbers in its own table (−16), and cut `mcq-azure-http-probe` and `mcq-tls-stays-with-payments` to review-only (−3). That gives **about 315**; `estimated_minutes: 315`. See open question 1.

**CI:** five labs, 29 wrong fixes, so 39 container runs. From the prototype: boot 4 to 5 s; checks with windows take 20 to 40 s each; a passing build run takes about 3 minutes, a failing one about the same (all checks run). Estimate: example 5 runs × 1 min, fill 6 × 2.5, write 7 × 3.5, build 11 × 3, debug 10 × 3 = about **110 minutes of runs, about 28 minutes on one shard at `--jobs 4`**. To keep it down: the hiccup window is 20 s, not longer; checks 7 to 9 share their traffic generator; the debug's 60-s window is the one long wait and is needed (the database's cycle is 60 s). Image: 334 MB, of which 6.3 MB is this topic's layer; build 18 s with the base cached.

## 12. Open questions, each with a recommendation

1. **The topic is long (337 minutes as designed).** Split it into "Load balancers" (choosing, algorithms, checks) and "Running a balancer" (draining, stickiness, failure stories)? Recommendation: **don't split**; trim to about 315 as in section 11. The proofs need all five skills together (the fleet-down story is a health-check story told through draining and runtime state), and the reading cut costs nothing because the lesson carries the cloud numbers.
2. **IPVS in a lab?** It would show a real pass-through balancer keeping the client's address. Recommendation: **no**; teach pass-through from the clouds' pages (every cloud layer 4 balancer is managed) and keep the labs to one tool whose state the checks can read. Revisit in Module 19 (Kubernetes uses IPVS or nftables for Services).
3. **Should a check restart HAProxy?** The debug's check 3 reads the configuration bit instead, so no check restarts the service. Recommendation: keep it that way; the done criterion asks the learner to restart it themselves.
4. **TLS termination in the build?** It would need a certificate (topic 31 teaches issuing one). Recommendation: **leave it out** of the labs and keep it in the lesson and two recall items; the build is already 60 minutes. If topic 31's labs leave a certificate tool in the network layer, a later revision can add an HTTPS frontend as a fresh version.
5. **The hiccup as a fast 503 rather than a slow answer.** Recommendation: **fast 503**, so only hysteresis fixes it and a longer `timeout check` can't hide it (tried with the slow version; the fast one is a one-line change in `shop-web`, not yet run).

## For the checkpoint designer: Checkpoint 3, part 2

Checkpoint 3's debug is "a local network of routers, a DNS server and an app" with "an intermittent outage caused by three faults". A flapping or correlated health check is the textbook intermittent fault, and this topic's scenery provides it cheaply: an HAProxy in front of the app with a deep check on a dependency that blips, or `fall 1` on a hiccupping server. If the checkpoint's app sits behind a balancer, one of its three faults can be that, with `test_skills` `csa.net.load-balancing/health-checks` or `/read-the-balancer`. The checks above (`no-errors-for-a-minute`, `web2-steady`) are the pattern; their 60-s windows are what "intermittent" costs in CI.

## Appendix: what was tried

See `prototypes/lb-ipsec/README.md`, section "Load balancing". In short: the scenery boots in 4 to 5 s and survives `docker restart`; the fleet-down, flapping, frozen-server, stickiness, drain, maint-lost-at-reload and speaks-first behaviours all reproduce, with the numbers quoted in section 5, fact 20. Not yet tried: the hiccup as a fast 503, the `stock-sync` stand-in, the API backend, the write lab's checks as code, and anything on a GitHub runner (nothing here needs more than Module 1's networking labs did).

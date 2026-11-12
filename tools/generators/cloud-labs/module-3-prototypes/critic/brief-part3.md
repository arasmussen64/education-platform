### 31. `csa.net.http-tls`, HTTP and TLS (new scope; designer material: [csa.net.http-tls.md](csa.net.http-tls.md), the HTTP-versions and handshake parts)

- **Title:** HTTP and TLS. **Prerequisites:** `csa.net.dns`, `csa.net.congestion`.
- **Skills:** `http-versions` (HTTP/1.1 against HTTP/2: connections, multiplexing, HPACK, ALPN; HTTP/3 named as topic 29's; the round-trip sums, three estimates: `est-rtt-tls12`, `est-rtt-tls13`, `est-hundred-connections`), `tls-handshake` (reading 1.2 and 1.3 in `s_client -trace`, what an observer sees, SNI in clear and ECH), `tls-server-config` (new: which versions to allow, SNI and a default server that refuses unknown names, HTTP/2 on, OCSP stapling set up and read with `-status`).
- **Removed, because topic 29 owns them:** lesson idea 2 (how a client finds HTTP/3) and the HTTP/3 cloud list, the worked example's Caddy step, `alt-svc-parse`, `mcq-h3-udp-blocked`, `mcq-when-h3-helps` (the same id and question as topic 29's) and `est-h3-saving` (topic 29's `est-rtt-saved` with the same 150 ms). The lesson says "HTTP/3 runs on QUIC, topic 29" in one sentence. No Caddy or `ngtcp2-client` in this topic's labs.
- **Practice ladder:** `example-two-handshakes` (the designer's example steps 1, 3 and 4, plus a stapling step against the lab's OCSP responder and an SNI step comparing two names' certificates); recall: `alpn-from-curl-v`, `mcq-h2-hol`, `est-rtt-tls12`, `est-rtt-tls13`, `trace-13-messages`, `trace-12-in-clear`, `mcq-what-observer-sees`, `mcq-sni-why`, `mcq-tls-versions`, `stapling-status`, `mcq-first-handshake-no-staple`, `mcq-ocsp-today`; **`fill-nginx-tls`** (new: gaps for `ssl_protocols`, the `http2` flag on `listen` (nginx 1.24), `ssl_stapling on` with its `resolver`, and the second site's `server_name`; checks read the live server with `openssl s_client` and `curl -w %{http_version}`; wrong fixes `tls11-allowed`, `no-http2`, `stapling-without-resolver`, `wrong-server-name`); **`write-handshake-report`** (new, from the designer's `write-cert-report`: `~/bin/handshake-report HOST PORT [NAME]` prints `protocol`, `alpn`, `certificate-name` (the leaf's first SAN for that SNI) and `stapled yes|no`, against throwaway `openssl s_server` processes the checks start on 127.0.0.1 with random names and settings; plain lab).
- **Proofs (new, designed here, not prototyped):** build **`build-two-sites-one-address`**: on `web`, `www.shop.test` and `api.shop.test` on one address, each with its own certificate (given as files from the lab CA), chosen by SNI; TLS 1.2 and 1.3 only; HTTP/2; OCSP stapling for www against the lab's responder (`openssl ocsp`, scenery, as the designer's prototype ran on port 8888); an unknown name refused (`ssl_reject_handshake on` in a default server) rather than given another site's certificate; HTTP redirected to HTTPS; saved and `nginx@web` enabled. Checks: `sni-each`, `unknown-name-refused`, `versions`, `h2`, `stapled` (second handshake), `full-chain`, `redirect`, `lasts`. Wrong fixes: `one-cert-for-both`, `tls11-allowed`, `no-http2`, `no-stapling`, `unknown-gets-www`, `not-reloaded`. Debug **`debug-handshake-failures`**: the shop's partner integration (an old client limited to TLS 1.2, scenery) fails, a monitoring probe that sends no SNI reports a name mismatch, and stapling never appears; three faults (versions limited to 1.3, the default server is api's, the stapling resolver missing), each found from `s_client` output and nginx's error log. Rules: keep 1.0 and 1.1 off, don't hand the probe another site's certificate, no client told to skip verification. Explain: the designer's prompt without the certificate and ACME clauses, plus "what SNI is for and what an observer still sees". Both labs are proved under `labcheck test` before writing (they reuse mechanisms the designer tried: verify codes, `-trace`, stapling from the second handshake).
- **Review pool:** `est-rtt-tls13`, `est-hundred-connections` (review-only), `trace-12-in-clear`, `keylog-decrypted` (review-only), `mcq-what-observer-sees`, `mcq-first-handshake-no-staple`, `mcq-tls-versions`.
- **Resources:** MDN "Evolution of HTTP", The Illustrated TLS 1.3 Connection (MIT), Cloudflare's "What happens in a TLS handshake?", the nginx SSL module. Cloudflare's page refuses automated fetches (critic, 2026-11-11, HTTP 403): the writer confirms it in a browser; if it can't, The Illustrated TLS 1.3 Connection becomes `resources[0]`. Facts re-read: TLS 1.3 is RFC 9846 (July 2026, Proposed Standard, obsoleting RFC 8446 and 5246 among others); ECH is RFC 9849 (March 2026).
- **Minutes:** 175.

### 32. `csa.net.certificates`, Certificates and mutual TLS (new topic; designer material: [csa.net.http-tls.md](csa.net.http-tls.md), the chain, ACME and mTLS parts)

- **Prerequisites:** `csa.net.http-tls`. **Skills:** `cert-chains`, `acme-and-rotation`, `mutual-tls` (as designed; `acme-and-rotation` keeps its four estimates).
- **Practice ladder:** `example-issue-and-rotate` (the designer's example steps 5 to 7, plus reading the chain served); the chain, ACME and mTLS recall rows of sections 7.5 to 7.7; `fill-local-ca` and `write-cert-report` (its `protocol` line dropped: topic 31's report has it) as designed.
- **Proofs:** build `build-shop-tls` and debug `debug-padlock-trouble` as designed (its `versions` and `h2` checks stay as retrieval of topic 31). Neither was built end to end; the untried pieces (the TLS 1.1 refusal check, nginx rejecting a client certificate without `clientAuth`, an already-expired certificate made with `faketime`, the certbot drop-in for `REQUESTS_CA_BUNDLE`) are tried first, each with the designer's fallback.
- **Labs on the base:** `web` (nginx@web), `ca` (step-ca as `step-ca@ca`, its files in ca's state folder), `office`, `partner`. certbot runs **inside `web`**: `certbot@web.service` and `certbot@web.timer` (B9), so its `/etc/letsencrypt` is web's and its deploy hook is `systemctl reload nginx@web`. The prompts say so; the masked plain `nginx` unit refuses the habit-typed `systemctl reload nginx` with a clear message.
- **Review pool:** the designer's chain, ACME and mTLS rows.
- **Resources:** Let's Encrypt's "How It Works", "Challenge Types" and "Ending OCSP Support in 2025" (re-read: Must-Staple failing from 2025-01-30, OCSP URLs dropped 2025-05-07, responders off 2025-08-06, for privacy), "From 90 to 45" optional, Cloudflare's mTLS page (confirm in a browser). The CA/Browser Forum schedule: 200 days from 2026-03-15, 100 from 2027-03-15, 47 from 2029-03-15 (BR v2.3.1 as the designer read it; the ballot's page confirms "398 days to 47 days", March 2026 to March 2029).
- **Minutes:** 230.

### 33. `csa.net.http-semantics` (designer: [csa.net.http-semantics.md](csa.net.http-semantics.md))

- **Skills:** as designed (four). **Prerequisites:** `csa.net.http-tls`.
- **Owns the cookie** (one sentence, in the CORS credentials paragraph), which topic 34 uses.
- **Labs on the base:** `origin` (nginx@origin, the learner's `/etc/nginx/sites-available/shop` inside it; `shop-app` and `order-board` as machine-level units), `edge` (nginx@edge, sealed scenery), `office`. `cors-verdict` lives in the base's `checklib.sh` with its test table (B7). The write lab is a plain lab whose throwaway servers listen on 127.0.0.1.
- **Practice ladder, proofs:** as designed; the debug's WebSocket fault is scaled down (board ping 45 s, faulty timeout 30 s, check 75 s with `timeout: 100`), as the designer recommends. `est-ping-interval` is written as a deliberate retrieval of topic 28's rule (the smallest timer on the path wins), in a new story.
- **Review pool, resources:** as designed (re-read: MDN caching's sections and its `no-cache` sentence; `Access-Control-Max-Age` 5 s default, Firefox 86,400, Chromium 7,200 since v76; RFC 9111 §5.2.2.4, §5.2.2.7 and the 10% heuristic; nginx's WebSocket page, `proxy_http_version` "before version 1.29.7", 60 s; grpc.io's four RPC kinds and deadlines).
- **Minutes:** 315 (the designer's 321 with RFC 6455 §1 moved to the recap and `mcq-idempotency-key` already review-only).

### 34. `csa.net.load-balancing` (designer: [csa.net.load-balancing.md](csa.net.load-balancing.md))

- **Skills:** as designed (five). **Prerequisites:** `csa.net.http-semantics`.
- **Labs on the base:** `lb` (haproxy@lb, `/etc/haproxy/haproxy.cfg` inside it, the stats socket at lb's `/run/haproxy/admin.sock`), `web1` to `web3`, `api1`, `api2`, `stock1`, `stock2`, `db` with their stand-ins as machine-level units, `office`. Commands become `on lb socat …`, `systemctl reload haproxy@lb`, `journalctl -u haproxy@lb`.
- **Practice ladder, proofs, review pool:** as designed, with the designer's trims (R6 to R8 to "More resources"; `mcq-azure-http-probe` and `mcq-tls-stays-with-payments` review-only). Untried pieces tried first: the hiccup as a fast 503, the `stock-sync` stand-in, the API backend, and which of `show info`'s `Uptime_sec` or the worker's `/proc` start time resets at a reload in 2.8. Google's "all backends unhealthy" row is worded from the page as it is (re-read 2026-11-11): Application Load Balancers answer 503 (classic 502); passthrough Network Load Balancers may drop all traffic if their failover policy says so, otherwise send to unhealthy backends as a last resort, and the global external type fails over to the next region.
- **Resources:** as designed (re-read: HAProxy's Starter Guide section 2; Yanacek's article and its correlated-failure sentence; ALB defaults 30/5/5/2 and fail-open; Google's 5/5/2/2; nginx's active checks commercial only).
- **Minutes:** 315.

### 35. `csa.net.bgp` (designer: [csa.net.bgp.md](csa.net.bgp.md); shared: [frr-labs-common.md](frr-labs-common.md))

- **The split is accepted;** this is the first half. **Skills, prerequisites:** as designed (four; `csa.net.routing`).
- **Labs on the base:** `edge`, `ispa`, `ispb`, `transit`, `cloud`, `office`, `shopweb`, `web`; `looking-glass` and `bgp-best` from the base; the far routers sealed and checked with `intact` and `frr_saved` (R6).
- **Practice ladder, proofs, review pool, resources:** as designed (re-read: FRR 8.4's "enabled by default for the traditional configuration", the MED wording "received from the same AS", the import check "for versions 7.4 and beyond").
- **Minutes:** 285.

### 36. `csa.net.bgp-steering` (new id; designer: [csa.net.bgp-steering.md](csa.net.bgp-steering.md))

- **Skills, prerequisites:** as designed (four; `csa.net.bgp`). `route-reflection` and `failure-detection` are calculation skills with three and four estimates.
- **Labs:** as designed, on the base, with BFD through `bfdd=yes` and `netlab link … silent` for the silent cut.
- **Practice ladder, proofs, review pool, resources:** as designed (re-read: Direct Connect's `7224:7100/7200/7300` "evaluated before any AS_PATH attribute", the associated-Region medium preference, "AWS does not recommend using MED"; the 100-route default per private or transit VIF, raisable to 1,000, the session going idle; hold 90 s, keepalive 30 s, BFD 300 ms × 3, graceful restart not with BFD).
- **Minutes:** 295.

### 37. `csa.net.ipsec` (designer: [csa.net.ipsec.md](csa.net.ipsec.md))

- **Skills:** as designed (five). **Prerequisites:** `csa.net.bgp`, `csa.net.http-tls`.
- **The tunnel is a VTI,** as the designer built it; the base gets the `forecast` fix (B1), which the critic confirmed makes VTI work between two base machines. The fallback, if a runner refuses `ip_vti`, is the base designer's GRE inside a tunnel-mode SA (its contract kept), switched by the topology's `tunnel` lines and the `children` block.
- **Labs on the base:** the learner's gateway is machine `vpn` (`strongswan@vpn`, `frr@vpn`, `nftables@vpn`); the provider is `cloud` (sealed; `strongswan@cloud`, `frr@cloud`, ordered to start before `vpn`'s); `internet` and `office` are machines. `vti0` lasts in vpn's `/etc/network/up` (B3), so the fill-in's gaps move from `vti0.service` to that file, and the build's `comes-back-at-boot` check reads it through `netlab verify`. `cloud-vpn-status` and `cloud-vpn-log` stay as read-only wrappers for the provider's view.
- **Practice ladder, proofs:** as designed; `keyingtries = 0` in every learner connection (the critic's restart trial failed without it, as the designer's first did). ECP-384 untried: the writer runs it first and falls back to `modp3072`.
- **Review pool, resources:** as designed. strongSwan's documentation is CC BY 4.0 (its page footer, re-read 2026-11-11), not "not stated" as the base brief has it. Re-read: AWS's MTU table (AES-GCM 1446/1406, with NAT-T 1438/1398, AES-CBC SHA1/SHA2-256 1438/1398), the virtual private gateway's default ASN 64512 fixed after creation, the inside `/30` from `169.254.0.0/16` and default `0.0.0.0/0` selectors.
- **Minutes:** 310.

### 38. `csa.net.troubleshooting` (designer: [csa.net.troubleshooting.md](csa.net.troubleshooting.md))

- **Skills, prerequisites:** as designed (six; `csa.net.load-balancing`, `csa.net.ipsec`).
- **Faults checked against the final topic briefs** (the designer's open question 1): the debug's three (provider loss with a rate-limited hop, a duplicate service address announced by gratuitous ARP, a backend's egress filter blocking its database) appear in no topic's debug; topic 23's pinned-MAC fault is a neighbour of the duplicate address but a different mechanism. The worked example's stale more-specific static route resembles routing's stale blackhole (debug fault 3): it is practice, chosen so the example spends its effort on the method, and the prompt says it is a routing fault met before. The casebook uses other topics' debug faults as recorded cases on purpose (retrieval after those proofs).
- **Practice ladder, proofs, review pool:** as designed, with the designer's trim (a): R1's core sections only and five multiple-choice items to review-only. The debug's checks and wrong fixes are run under `labcheck test` before writing; `calls-succeed` with 8% loss runs three times in the CI spike, and drops to 5% loss if it ever fails for the solution. The casebook's plain `RUN` is the shared Module 3 plain line (3.5), without `gawk`.
- **Resources:** as designed (re-read: the SRE chapter's CC BY-NC-ND 4.0 and its sections; Gregg's anti-methods and problem-statement questions, no licence stated; Akamai's guide, including the "small amounts of loss in the neighborhood of 10%, there is no cause for real concern" line the lesson corrects). Everything curl's and nginx's documentation licences are confirmed before they are listed.
- **Minutes:** 300.

## 6. Checkpoint 3: the address plan, the outage and the cloud link (designer: [csa.m3.checkpoint.md](csa.m3.checkpoint.md))

**Prerequisites:** the sixteen topics. **`estimated_minutes`: 240.** Objectives as designed (no cause of part 2 named). The proof block as designed:

```yaml
prove:
  build: build-the-address-plan              # part 1, plain lab
  debug: debug-the-outage                    # part 2, network lab
  more:
    - id: build-the-cloud-link               # part 3, network lab
      versions: [build-the-cloud-link-clinic]
  explain: ...                               # opens once part 1 passes
unstuck:
  example: example-address-plan-print-shop
  steps: [step-size-the-blocks, step-place-and-summarise, step-the-ipv6-plan, step-the-whole-plan]
  versions: [build-the-address-plan-clinic, build-the-address-plan-bakery]
```

**Part 1, `build-the-address-plan`** (60 minutes): as designed and prototyped (the checker passes the reference plan and each of 14 wrong plans fails only its own check, identically under Python 3.14 and Ubuntu's 3.12). Its rules are the CIDR and IPv6 topics' builds' rules, so it brings in nothing new; the cloud facts it uses were re-read (AWS and Azure reserve 5, Google 4; Azure IPv6 subnets exactly /64; Google's `fd20::/20` with a /48 per network; RIPE-690's /48 for businesses and nibble boundaries). The image uses the shared plain `RUN`.

**Part 2, `debug-the-outage`, version 2** (60 minutes): as designed (nine machines; the zone edited without a new serial, a filter on one of two ECMP tunnels, an app firewall that only knows the old network). Version 1 isn't used: its three faults repeat topics 30, 23 and 26's debugs, and a checkpoint's debug is unfamiliar work. Fault 1 shares its symptom (a stale secondary) with topic 30's debug but not its cause or evidence (the same serial and different answers, and "zone is up to date" in ns2's log, against a refused transfer); the primary is unsigned, so unlike topic 30's inline-signed primary it loads the edit. `test_skills` corrections: `both-tunnels` names `csa.net.troubleshooting/locate-on-the-path` and `csa.net.routing/find-the-black-hole` (where topic 26's new ECMP item lives). **Before writing:** a full contract run with the two redesigned checks (`both-tunnels-carry`, the office half of `app2-web-for-the-shop`) and the restart trial.

**Part 3, `build-the-cloud-link`** (60 minutes, in `prove.more`), with fresh version `-clinic`: as designed, with **a VTI** for the tunnel (the base's B1), so the machines and checks follow topic 37's. It retrieves CIDR (the summary), BGP (sessions, filters, local preference), BGP steering (prepending, failover) and IPsec (the sheet, PFS, a private key) in one task weeks after the topics. It overlaps topic 36's build (circuits and a VPN backup) and topic 37's (a tunnel from a sheet), deliberately, in a new story with new numbers, and with the scenery's cloud comparing AS paths so prepending (not communities) is the tool. **Not prototyped end to end:** build it first from the critic's VTI variant of the base's `proto-bgp-over-ipsec` plus a `dx` link and a second session, and time `fails-over` on the CI spike's runner with four labs at once.

**The explain** (20 minutes): as designed.

**Support:** solved sibling, four steps and two fresh versions for part 1 as designed; one fresh version for part 3 (a build part needs one); none for part 2. The map already lists a checkpoint's further parts (`MapPage.tsx` reads `partsPassed`), so the designer's C5 is done.

**Time:** 60 + 60 + 60 + 20 = 200 minutes of work; with three labs' starts and the slower checks, `estimated_minutes: 240`.


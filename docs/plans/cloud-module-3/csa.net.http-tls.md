# Writing brief: `csa.net.http-tls` (topic 31), HTTP and TLS

Design only. Nothing here is in the repository. Sources were read on 2026-11-11, and each fact carries its URL. Lab mechanics marked **tried** were run that day in Docker Desktop on the owner's PC: `ubuntu:24.04`, with these versions:

- nginx 1.24.0-2ubuntu7.19, OpenSSL 3.0.13, curl 8.5.0-2ubuntu10.16;
- certbot 2.9.0, lego 4.9.1;
- Pebble 2.4.0 (Ubuntu); step-ca 0.30.2 and step-cli 0.31.0 (GitHub release `.deb`s);
- Caddy 2.6.2, ngtcp2-client, tshark 4.2.2.

Everything started was removed. Prototype files are in `prototypes/dns-http/tls/` and `stepca/`, and captured output (full `openssl s_client -trace` runs for TLS 1.2 and 1.3, `-status` output) is in `prototypes/dns-http/captured/`.

**One choice shapes every lab here. The ACME labs use step-ca, not Pebble.** Pebble regenerates its root and intermediate on every start (its README says so, fact 13, and it was tried: the root changed from `Pebble Root CA 7f37de` to `20c02f` across one restart, and the issued certificate no longer verified). So no Pebble lab can pass the restart trial. step-ca keeps its CA on disk (tried: the same root fingerprint after `docker restart`), speaks ACME, and issues 24-hour certificates by default, which suits teaching rotation. See open question 2.

## 1. What the learner will be able to do

1. Say what HTTP/1.1, HTTP/2 and HTTP/3 change: connections, multiplexing, head-of-line blocking, header compression, and HTTP/3 riding QUIC on UDP. Read `curl -v` to see which version ALPN chose. Know that HTTP/3 is discovered (through `Alt-Svc` or a DNS HTTPS record) and silently skipped when UDP 443 is blocked. Work out what each handshake costs in round trips.
2. Read a TLS 1.2 and a TLS 1.3 handshake message by message in `openssl s_client -trace`. Say what an observer on the wire sees: the ClientHello with SNI in clear, then encrypted records in 1.3. Say what SNI, ALPN and OCSP stapling are for, and read `-status` output.
3. Build and read a certificate chain: root, intermediate, leaf, SANs, validity, and serving the full chain. Name the verify failures by their codes: 20 untrusted root, 21 missing intermediate, 10 expired, 62 wrong name.
4. Issue a certificate with ACME (certbot, HTTP-01) from a private ACME CA, renew it automatically, and make the server load each renewal (deploy hook, `live/` paths). Say why lifetimes are shrinking (200 days now, 47 days in 2029) and what replaced OCSP at the largest public CA.
5. Require client certificates (mutual TLS) from a separate client CA on one service and not on another. Say how the three clouds' load balancers do it.

**The six-month core:**

- A TLS 1.3 handshake costs one round trip on top of TCP's one; TLS 1.2 costs two. HTTP/3 on QUIC needs one in all. After ServerHello, everything in 1.3 is encrypted, the certificate included. SNI still shows the name (unless ECH).
- A client trusts a leaf if it can build a chain to a root it holds, the name is in the SANs and the dates are good. Serve the leaf plus intermediates. Code 21 means the intermediate is missing.
- Certificates expire on purpose and soon: 200 days at most since 2026-03-15, 100 days from 2027-03-15, 47 days from 2029-03-15. Automate with ACME, renew at about two-thirds of the lifetime, and make sure the server reloads.
- mTLS: the server asks for a client certificate and trusts only the CA you name for clients. `optional` isn't required.
- HTTP/2 multiplexes on one TCP connection. HTTP/3 removes TCP's head-of-line blocking. h3 needs UDP 443 open, or clients quietly fall back.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.net.dns, csa.net.congestion]`.

- `csa.net.dns`: certificates name DNS names; HTTP-01 needs the name to resolve; CAA (introduced in `csa.net.dns`'s `mcq-which-record`) limits which CA may issue; SNI is a DNS name; HTTPS records (one line in topic 30) advertise h3.
- `csa.net.congestion` (topic 29): QUIC and "what HTTP/3 changes" belong to it (its spec row: "explain what QUIC and HTTP/3 change, and when they help"). This topic uses QUIC as known and adds HTTP/3's discovery (`Alt-Svc`), its UDP firewall need, and its round-trip count against HTTP/2's. **For topic 29's designer:** this topic expects 29 to define QUIC, a UDP datagram, a stream, head-of-line blocking at the transport, and 0-RTT. If 29 doesn't, this topic's lesson adds a paragraph (idea 2).

Topic 28 (`csa.net.transport`) is reached through both, for RTT and the TCP handshake.

**Builds on (for the writer):** `csa.linux.net-tools` (curl `-v`/`-I`, status lines, `tcpdump -nn`, `ss`, nftables and `from-office`), `csa.linux.services` (`systemctl reload` against `restart`, timers, `journalctl`), `csa.linux.hardening` (if it covers SSH keys: the public/private key idea is reused here; otherwise this topic defines it), `csa.linux.shell` and `csa.linux.scripting`.

**Terms this topic must define itself:** HTTP request and response, method, header, status line (Module 1 read status lines and `Location`, and this topic takes them as known); persistent connection; head-of-line blocking at the HTTP level; multiplexing and stream (HTTP/2 meaning); HPACK and QPACK (one line); ALPN; `Alt-Svc`. Encryption (symmetric against public-key, one paragraph); key exchange (ECDHE) and forward secrecy (one sentence each); cipher suite; TLS record; handshake; ClientHello and ServerHello; EncryptedExtensions; Certificate, CertificateVerify and Finished; session resumption and 0-RTT (one line each). Certificate (X.509), subject, SAN, issuer, CA, root, intermediate, chain, trust store, validity, EKU (serverAuth and clientAuth), CSR. Revocation, CRL, OCSP, OCSP stapling, Must-Staple (one line). ACME, account key, order, challenge (HTTP-01, DNS-01, TLS-ALPN-01), ARI (one line). Certificate Transparency (one sentence). mutual TLS, client certificate. SNI, ECH.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `http-versions` | HTTP/1.1, 2, 3: connections, multiplexing, head-of-line blocking at each layer, ALPN, `Alt-Svc`. What to open in a firewall. When each version helps. Round-trip sums. **A calculation skill: four estimate items.** |
| `tls-handshake` | Reading 1.2 and 1.3 handshakes in `s_client -trace`. What's encrypted and what isn't (SNI, and ECH). Versions to allow (1.2 and 1.3; 1.0 and 1.1 deprecated). OCSP stapling as a handshake extension, read with `-status`. |
| `cert-chains` | Root, intermediate, leaf. SAN against CN. Validity. Serving the full chain. Verify return codes. A local CA with `openssl`. |
| `acme-and-rotation` | ACME flow and challenge types. certbot with webroot. Timers and deploy hooks, `live/` against `archive/`. Lifetimes (BR schedule, Let's Encrypt profiles). Renewal timing (two-thirds, ARI). Why short lifetimes replace revocation (the end of OCSP at Let's Encrypt). **A calculation skill: four estimate items.** |
| `mutual-tls` | Client certificates; `ssl_verify_client on` against `optional`; a separate client CA. Where mTLS is used (partner APIs, service meshes). The three clouds' load balancer options. |

## 4. Lesson plan

The lesson is about 2,000 words (16 minutes).

1. **HTTP in one connection, then many streams (MDN "Evolution of HTTP", the HTTP/1.1, HTTP/2 and HTTP/3 sections).** The lesson's picture in words: HTTP/1.1 is a single-lane road where each car (response) must arrive before the next leaves, so browsers open six lanes. HTTP/2 paints many lanes on one road (streams on one TCP connection), but one pothole (a lost TCP packet) stops every lane, because TCP delivers bytes in order. HTTP/3 gives each lane its own road surface (QUIC streams over UDP): a lost packet holds up only its own stream. Tried: `curl -v` against nginx printed `ALPN: server accepted h2` and `curl -w %{http_version}` printed `2`. Ubuntu 24.04's curl has HTTP2 but no HTTP3 (its feature list, tried).
2. **How a client finds HTTP/3 (lesson only, tried).** The first connection is over TCP. The server's response carries `alt-svc: h3=":9443"; ma=2592000` (Caddy, tried), and the next connection tries QUIC. RFC 9460's HTTPS record can carry the same hint in DNS (one line, back to topic 30). If UDP 443 is blocked, nothing errors: the client stays on HTTP/2 (tried: with UDP blocked by nftables, the HTTP/3 client got nothing, while `curl` still got `hello over HTTP/2.0`). That is why "we enabled HTTP/3 and nothing changed" is usually a firewall or a security group. **Where the clouds differ:**
   - Google's global external Application Load Balancer advertises HTTP/3 by default (`quicOverride` NONE) and speaks it to clients only.
   - Azure Application Gateway's HTTP/3 is in preview (page dated 2026-09-09), frontend only.
   - CloudFront has supported HTTP/3 since August 2022. Nothing read says the AWS Application Load Balancer does.
3. **Round trips (lesson only).** Count RTTs before the first request byte leaves:
   - TCP 1, then TLS 1.2 adds 2 (3 in all) or TLS 1.3 adds 1 (2 in all);
   - QUIC with TLS 1.3 built in: 1;
   - resumption with 0-RTT: 0, with the replay caveat from RFC 8446 §2.3, "no guarantees of non-replay between connections".

   The estimate items drill this.
4. **The TLS handshake, two versions side by side (main resource: Cloudflare, "What happens in a TLS handshake?", then "The Illustrated TLS 1.3 Connection", the Client Hello, Server Hello and server encrypted-record sections).** The lesson's own material is the lab's real trace, reduced to one line each by `awk` (tried):
   - TLS 1.3: `ClientHello ServerHello EncryptedExtensions Certificate CertificateVerify Finished Finished NewSessionTicket NewSessionTicket`
   - TLS 1.2: `ClientHello ServerHello Certificate ServerKeyExchange ServerHelloDone ClientKeyExchange Finished NewSessionTicket Finished`

   Then the key moment: in the 1.3 trace, the record carrying the Certificate has outer `Content Type = ApplicationData (23)` and `Inner Content Type = Handshake (22)`, so on the wire it's encrypted (RFC 8446 §1.2: "All handshake messages after the ServerHello are now encrypted"). In 1.2 the certificate crosses in clear. The odd `ChangeCipherSpec` in a 1.3 trace is there "for middlebox compatibility" only. **Spec status:** TLS 1.3 is now RFC 9846 (July 2026), which obsoletes RFC 8446 (and RFC 5246, TLS 1.2's spec). TLS 1.0 and 1.1 have been deprecated since RFC 8996 (2021). nginx's default `ssl_protocols` is `TLSv1.2 TLSv1.3`.
5. **What the wire still shows (lesson only, tried).** A `tcpdump -A` of the same connection shows `www.shop.test` once, in the ClientHello: that's SNI. One address can host many sites, and the server needs the name to pick a certificate before anything is encrypted. ECH (RFC 9849, March 2026) encrypts the ClientHello. Name it, and say it needs support at both ends and a DNS record. Decrypting a capture needs the session keys: `SSLKEYLOGFILE` with curl writes them, and Wireshark or tshark then shows EncryptedExtensions, Certificate, CertificateVerify and the HTTP/2 headers (tried; recall items use the captured output, and the labs don't ship tshark's 147 MB).
6. **Certificates and chains (lesson, plus Let's Encrypt's "How It Works").** A certificate binds names (the SAN list; browsers ignore the CN) to a public key, signed by an issuer. A client walks leaf → intermediate → a root in its trust store. The server must send the intermediates; the root it may leave out. The four verify codes, each tried with `openssl s_client -verify_return_error`-style runs:
   - `0 (ok)`;
   - `20 (unable to get local issuer certificate)`: root not trusted;
   - `21 (unable to verify the first certificate)`: intermediate not sent;
   - `62 (hostname mismatch)`.

   curl reports the first two as `(60) SSL certificate problem`. Why browsers sometimes work anyway: some cache or fetch missing intermediates, which hides a broken chain until a stricter client (an API client, a phone) fails. That's why the debug lab's partners fail while "it works in my browser".
7. **Revocation, then and now (Let's Encrypt, "Ending OCSP Support in 2025").** OCSP lets a client ask the CA "is this certificate revoked?", and stapling has the server fetch that answer and attach it to the handshake (RFC 6066 `status_request`). Tried with nginx: the first handshake after a start carries no staple, because nginx fetches it lazily, and later ones show `OCSP Response Status: successful … Cert Status: good`. Then the honest current picture:
   - Let's Encrypt removed OCSP URLs from certificates on 2025-05-07 and turned its responders off on 2025-08-06, for privacy (fact 9). It publishes CRLs.
   - Short lifetimes are the industry's answer: Let's Encrypt's 160-hour `shortlived` profile since 2026-01-15, and 45-day certificates (opt-in from 2026-05-13, default from 2028-02-16).

   So stapling is taught as something you'll still meet with private and enterprise CAs and read in `-status`, not as the future.
8. **ACME (Let's Encrypt "Challenge Types"; the lesson adds the moving parts on a real server).** An account key, an order, a challenge, the CSR, the certificate.
   - HTTP-01 needs port 80 and can't do wildcards. DNS-01 can, and needs DNS API credentials on the server.
   - certbot keeps every version in `archive/` and points `live/` at the newest. A server must read `live/…/fullchain.pem`, or it never sees a renewal.
   - certbot installs a timer (tried: `certbot.timer` active, twice a day). Renewal changes files, not the running server, so `--deploy-hook "systemctl reload nginx"`.
   - Non-interactive `certbot renew` sleeps a random time first (tried: 239 s) unless `--no-random-sleep-on-renew`, which the labs' checks use.

   The lifetime schedule (CA/B Forum Baseline Requirements v2.3.1): 200 days from 2026-03-15, 100 from 2027-03-15, 47 from 2029-03-15. Renew at about two-thirds of a lifetime, or follow ARI (RFC 9773), which Let's Encrypt recommends. **Where the clouds differ:** each has a managed certificate service tied to its load balancers (AWS Certificate Manager, Azure Key Vault certificates and App Service managed certificates, Google-managed certificates). The lesson names them in one line each and makes no claim about their lifetimes or renewal (not read; Module 11 owns them).
9. **Mutual TLS (Cloudflare, "What is mutual TLS?").** In the trace a server that wants a client certificate sends `CertificateRequest`, listing the CAs it accepts. Tried: `Acceptable client certificate CA names: CN = Shop Partners CA`. The client answers with its own Certificate and CertificateVerify. In nginx:
   - `ssl_client_certificate` names the client CA (and sends its name to clients); `ssl_trusted_certificate` doesn't send it.
   - `ssl_verify_client on` refuses without a valid certificate: tried, HTTP 400 "No required SSL certificate was sent", and "The SSL certificate error" for a certificate from the wrong CA.
   - `optional` lets anonymous clients through: tried, `verified=NONE` and a 200.

   Use a separate CA for clients. If the server CA also signs client certificates, anyone holding any certificate from your server CA gets in. **Where the clouds differ:**
   - AWS ALB: passthrough or verify mode, a trust store, and the certificate details passed to targets in `X-Amzn-Mtls-*` headers.
   - Google's Application Load Balancers: a TrustConfig, with `REJECT_INVALID` or `ALLOW_INVALID_OR_MISSING_CLIENT_CERT`.
   - Azure Application Gateway calls it mutual authentication. Its HTTP/3 page lists it as unsupported on HTTP/3 listeners; the mutual-authentication page itself wasn't read.
10. **The labs (lesson only).** `lab` is the shop's web server (nginx); `ca` runs the company's private ACME CA (step-ca) at `ca.shop.test:9000`; `office` is a customer's laptop that trusts that CA's root; `partner` is the warehouse's server with its client certificate.

**Read now:** Cloudflare's handshake page (main). The Illustrated TLS 1.3 Connection: Client Hello, Server Hello, "Server Handshake Keys Calc" skimmed, "Server Encrypted Extensions" and "Server Certificate", about 15 minutes; open the 1.2 one if curious. MDN's "Evolution of HTTP", the HTTP/1.1, HTTP/2 and HTTP/3 sections. Let's Encrypt's "How It Works" and "Challenge Types". The OCSP post. Cloudflare's mTLS page.

## 5. Verified facts

All read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | TLS 1.3 is RFC 9846 (July 2026), obsoleting RFC 8446, RFC 5246 and others. | https://www.rfc-editor.org/rfc/rfc9846.json |
| 2 | RFC 8446 §1.2: "All handshake messages after the ServerHello are now encrypted". EncryptedExtensions is new. ChangeCipherSpec is kept only for middlebox compatibility. §2.3: 0-RTT has "no guarantees of non-replay between connections". (Read from RFC 8446; RFC 9846 keeps the handshake. A writer re-reads RFC 9846 §1.2 and §2.3 and cites it.) | https://www.rfc-editor.org/rfc/rfc8446.html |
| 3 | TLS 1.0 and 1.1 are deprecated (RFC 8996, March 2021, BCP). | https://www.rfc-editor.org/rfc/rfc8996.json |
| 4 | ECH is RFC 9849, March 2026, Proposed Standard. | https://www.rfc-editor.org/rfc/rfc9849.json |
| 5 | HTTP/2 RFC 9113, HTTP/3 RFC 9114, HTTP/1.1 RFC 9112, HTTP Semantics RFC 9110, all June 2022. Alt-Svc RFC 7838 (April 2016). SVCB/HTTPS RR RFC 9460 (November 2023). ALPN RFC 7301. SNI and `status_request` in RFC 6066. | rfc-editor.org JSON metadata for each |
| 6 | ACME RFC 8555 (March 2019). ARI RFC 9773 (June 2025). | rfc-editor.org JSON |
| 7 | Let's Encrypt challenge types: HTTP-01 on port 80, no wildcards; DNS-01 needs a TXT record at `_acme-challenge.<domain>`, allows wildcards, and needs DNS API credentials; TLS-ALPN-01 on 443, "not suitable for most people". Page updated 2026-02-12. | https://letsencrypt.org/docs/challenge-types/ |
| 8 | Baseline Requirements v2.3.1: maximum subscriber certificate validity 200 days from 2026-03-15, 100 days from 2027-03-15, 47 days from 2029-03-15; domain validation reuse 200 then 100 days on the same dates. | https://raw.githubusercontent.com/cabforum/servercert/main/docs/BR.md (lines 190–205); ballot SC-081v3, https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/ |
| 9 | Let's Encrypt: Must-Staple requests fail from 2025-01-30; OCSP URLs dropped from certificates 2025-05-07; responders off 2025-08-06; reason privacy; CRLs since 2022. | https://letsencrypt.org/2024/12/05/ending-ocsp/ |
| 10 | Let's Encrypt lifetimes: `tlsserver` profile 45 days from 2026-05-13 (opt-in); `classic` 64 days from 2027-02-10, 45 days from 2028-02-16; ARI recommended, or renewal at about two-thirds of the lifetime. | https://isrg.org/post/from-90-to-45/ (2025-12-02) |
| 11 | Let's Encrypt `shortlived` profile: 160 hours, generally available 2026-01-15. | https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability.html |
| 12 | Let's Encrypt's "How It Works": account key pair, challenges checked from several network perspectives, CSR, Certificate Transparency logs, revocation published in CRLs. Updated 2025-08-02. | https://letsencrypt.org/how-it-works/ |
| 13 | Pebble "is NOT INTENDED FOR PRODUCTION USE"; root and intermediate "are regenerated on every launch" (`/roots/0` on the management port 15000); `PEBBLE_VA_NOSLEEP`, `PEBBLE_VA_ALWAYS_VALID`, `PEBBLE_WFE_NONCEREJECT` (default rejects 5% of nonces), `PEBBLE_AUTHZREUSE` (50%); HTTP-01 port 5002 and TLS-ALPN-01 port 5001 by default; `-dnsserver`; MPL-2.0. Latest upstream v2.10.3 (2026-11-11); Ubuntu 24.04 ships 2.4.0. | https://github.com/letsencrypt/pebble and the GitHub releases API |
| 14 | Tried: Pebble 2.4.0 issued a certificate offline over HTTP-01 to lego in 7 s (`PEBBLE_VA_NOSLEEP=1`, `-dnsserver 127.0.0.1:53`, `httpPort: 80`); certificates valid 5 years; after a restart the root changed and the old certificate failed `openssl verify`. | prototype |
| 15 | step-ca supports ACME `http-01`, `dns-01`, `tls-alpn-01` and short-lived certificates; Apache-2.0; v0.30.2 released 2026-03-23; step-cli v0.31.0 released 2026-09-25. | https://github.com/smallstep/certificates; GitHub releases API |
| 16 | Tried: `step ca init --acme` took 1.1 s; lego and certbot each issued over HTTP-01 (0.2 s and 3 s); default lifetime 24 hours (`notAfter` = `notBefore` + 24 h + 1 min backdate); same root fingerprint after `docker restart`. Installed size 99 MB (`.deb` sha256: step-ca 0.30.2-1 `f8e43f0f2ba1e37121b75623993ea0bece5cc3a02b73eefc16e414d41c9fec71`, step-cli 0.31.0-1 `dbea61cba1854e07625d8f064d83441c7f9232edd9440bc08a78614dcc8232fc`). smallstep.com's docs returned 503 on the day, so the lifetime claims rest on the run, not the docs. | prototype |
| 17 | Tried: non-interactive `certbot renew` printed `random delay of 239.12 seconds`; `--no-random-sleep-on-renew` renewed in 2.5 s; `archive/` held `cert1.pem` and `cert2.pem`; `certbot.timer` was active after install. lego 4.9.1 has `--no-random-sleep`. | prototype |
| 18 | nginx: the `http2` directive appeared in 1.25.1 (Ubuntu 24.04's 1.24 needs `listen 443 ssl http2;`, tried); default `ssl_protocols TLSv1.2 TLSv1.3`; stapling needs the issuer known (in the chain or `ssl_trusted_certificate`) and a `resolver` for a responder named by host name; `ssl_verify_client on \| off \| optional \| optional_no_ca`; `ssl_client_certificate` sends its CA list to clients, `ssl_trusted_certificate` doesn't; non-standard codes 495 (certificate error), 496 (no certificate), 497 (HTTP to HTTPS port). | https://nginx.org/en/docs/http/ngx_http_ssl_module.html, https://nginx.org/en/docs/http/ngx_http_v2_module.html |
| 19 | Tried: nginx answered a missing client certificate with `400 No required SSL certificate was sent` and a wrong-CA certificate with `400 The SSL certificate error` (the docs give 495/496 for `error_page`; what the client sees is a 400 page); `optional` passed `verified=NONE`. | prototype |
| 20 | Tried: verify codes 0, 20, 21 and 62 as listed in the lesson; curl `(60)`. | prototype |
| 21 | Tried: stapling absent on the first handshake after a restart, present from the second (one worker; with eight workers, absent on three tries). | prototype |
| 22 | Tried: tcpdump showed the SNI name in clear; tshark with an `SSLKEYLOGFILE` decrypted handshake types 8, 11, 15, 20 and HTTP/2 headers, and without it showed only types 1 and 2. | prototype |
| 23 | Tried: Caddy 2.6.2 serves HTTP/3 and sends `alt-svc: h3=":9443"; ma=2592000`; ngtcp2's `gtlsclient` printed `[:status: 200]` over QUIC and exits 0 even when UDP is dropped (after about 10 s), so checks read its output, never its exit status. | prototype |
| 24 | Google's global external ALB and classic ALB (Premium) support HTTP/3, client side only; `NONE` (default) and `ENABLE` both advertise it. | https://docs.cloud.google.com/load-balancing/docs/https |
| 25 | Azure Application Gateway HTTP/3 is in preview; frontend only, backend HTTP/1.1; needs a TLS 1.3 policy; mutual authentication not supported on HTTP/3 listeners. ms.date 2026-09-09. | https://learn.microsoft.com/en-us/azure/application-gateway/http3-quic-support |
| 26 | CloudFront supports HTTP/3 (announced 2022-08-15). Seen in search results only; the What's New page wasn't opened. | https://aws.amazon.com/about-aws/whats-new/2022/08/amazon-cloudfront-supports-http-3-quic |
| 27 | ALB: idle timeout default 60 s; `routing.http2.enabled` default true; mutual TLS passthrough or verify, trust stores, `X-Amzn-Mtls-Clientcert*` headers. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html, …/mutual-authentication.html |
| 28 | Google ALBs: mTLS on the target HTTPS proxy with a TrustConfig; modes `ALLOW_INVALID_OR_MISSING_CLIENT_CERT` and `REJECT_INVALID`. | https://docs.cloud.google.com/load-balancing/docs/mtls |

**Not confirmed:**

- Whether Let's Encrypt stopped issuing certificates usable for client authentication. A secondary source says its `tlsclient` profile closes in 2026; no Let's Encrypt page was opened. The lesson says only "use a private CA for client certificates", which is right either way.
- Azure's mutual-authentication page and Front Door's HTTP/3 status weren't read.
- The ACM, Key Vault and Google-managed certificate lifetimes weren't read.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | "What happens in a TLS handshake?" (Cloudflare Learning Center) | https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/ | reading | © 2026 Cloudflare. Linked | 9 (about 1,150 words of body) | tls-handshake | 2026-11-11 |
| 1 | "The Illustrated TLS 1.3 Connection: Every byte explained": the sections named in the lesson | https://tls13.xargs.org/ | interactive reading | MIT (repository `syncsynchalt/illustrated-tls13`). Linked | 15 of a long page (15,000 words) | tls-handshake | 2026-11-11 |
| 2 | "The Illustrated TLS 1.2 Connection", optional | https://tls12.xargs.org/ | interactive reading | MIT. Linked | optional | tls-handshake | 2026-11-11 |
| 3 | "Evolution of HTTP" (MDN): HTTP/1.1, HTTP/2, HTTP/3 sections | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Evolution_of_HTTP | reading | CC BY-SA 2.5 or later (prose), CC0 (code). Linked | 9 of 19 (2,410 words) | http-versions | 2026-11-11 |
| 4 | "HTTP/2", High Performance Browser Networking (Ilya Grigorik): "Binary Framing Layer" to "Request and Response Multiplexing", optional | https://hpbn.co/http2/ | reading | CC BY-NC-ND 4.0. Linked | 15 of 47 | http-versions | 2026-11-11 |
| 5 | "How It Works" (Let's Encrypt) | https://letsencrypt.org/how-it-works/ | reading | © 2026 ISRG. Linked | 5 (638 words) | acme-and-rotation | 2026-11-11 |
| 6 | "Challenge Types" (Let's Encrypt) | https://letsencrypt.org/docs/challenge-types/ | reading | © 2026 ISRG. Linked | 9 (1,184 words) | acme-and-rotation | 2026-11-11 |
| 7 | "Ending OCSP Support in 2025" (Let's Encrypt) | https://letsencrypt.org/2024/12/05/ending-ocsp/ | reading | © ISRG. Linked | 6 (747 words) | tls-handshake, acme-and-rotation | 2026-11-11 |
| 8 | "From 90 to 45" (ISRG), optional | https://isrg.org/post/from-90-to-45/ | reading | © ISRG. Linked | 7 (873 words) | acme-and-rotation | 2026-11-11 |
| 9 | "What is mutual TLS (mTLS)?" (Cloudflare) | https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/ | reading | © 2026 Cloudflare. Linked | 9 (about 1,200 words of body) | mutual-tls | 2026-11-11 |
| 10 | nginx `ngx_http_ssl_module`: `ssl_verify_client`, `ssl_stapling`, reference | https://nginx.org/en/docs/http/ngx_http_ssl_module.html | reference | nginx documentation (BSD-2-Clause, with nginx). Linked | 5 | mutual-tls, tls-handshake | 2026-11-11 |

## 7. Practice ladder

The network-lab base (topic 30's section 10, D1) plus this topic's layer: a second `RUN` with `nginx certbot faketime ngtcp2-client caddy` (Caddy disabled at build; tried sizes: nginx with lego 43 MB, certbot 20 MB, ngtcp2-client with Caddy 47 MB; faketime is small). Labs that need the ACME CA add a third `RUN` that installs step-ca and step-cli from the pinned `.deb`s with `curl`, checks the sha256 and deletes the files (99 MB; open question 2). tshark is **not** installed (147 MB); its decrypted view appears in recall items as captured output.

Machines:

| Machine | Address | Role |
| --- | --- | --- |
| `lab` | 10.0.9.1 | nginx for `www.shop.test` and `api.shop.test`; certbot; dnsmasq names the lab |
| `ca` | 10.0.9.5 | step-ca, `ca.shop.test:9000`, ACME provisioner, CA files under `/var/lib/lab/ca` |
| `office` | 10.0.9.2 | a customer: trusts the CA's root (a file `/etc/lab/office-trust.pem`, used with `--cacert`) |
| `partner` | 10.0.9.3 | the warehouse: a client certificate from "Shop Partners CA" |

### 7.1 `example-issue-and-inspect` (worked example, systemd lab), skills `http-versions`, `tls-handshake`, `acme-and-rotation`

Labelled steps:

1. **Which HTTP?** `curl -sv --cacert … https://www.shop.test/ -o /dev/null 2>&1 | grep -E 'ALPN|HTTP/'`, then with `--http1.1`.
2. **HTTP/3 is offered:** `curl -sI https://www.shop.test:9443/ | grep -i alt-svc` (Caddy on 9443 for this step), then `gtlsclient --exit-on-all-streams-close www.shop.test 9443 https://www.shop.test:9443/ 2>&1 | grep status`.
3. **Two handshakes:** `openssl s_client … -tls1_3 -trace` and `-tls1_2 -trace`, each reduced with `grep -E '^    [A-Z][A-Za-z]+, Length' | awk '{print $1}' | tr -d , | tr '\n' ' '`. Save the 1.3 line to `~/example/tls13.txt`.
4. **What the wire sees:** `sudo tcpdump -i eth1 -nn -A -c 20 port 443` in the background while `from-office curl` runs; `grep -c www.shop.test`.
5. **Ask the CA for a certificate:** `sudo certbot certonly --server https://ca.shop.test:9000/acme/acme/directory --webroot -w /var/www/html -d www.shop.test -m ops@shop.test --agree-tos --no-eff-email` (with `REQUESTS_CA_BUNDLE` set in `/etc/environment` by the image). `ls -l /etc/letsencrypt/live/www.shop.test/`.
6. **Serve it:** point nginx at `live/…/fullchain.pem` and `privkey.pem`, then `sudo systemctl reload nginx`. Check from the office: `Verify return code: 0`.
7. **Make renewal reach nginx:** `sudo certbot reconfigure --deploy-hook "systemctl reload nginx"`, or the `renew_hook` line in the renewal file. Then `sudo certbot renew --force-renewal --no-random-sleep-on-renew` and watch the served serial change. Save both serials to `~/example/serials.txt`.

Checks:
- `tls13.txt` starts `ClientHello ServerHello EncryptedExtensions`.
- The served certificate's issuer is the CA's intermediate, and `notAfter − notBefore` is at most 25 hours.
- `serials.txt` holds two different serials, and the second is the one served now.
- A deploy hook is configured: `grep -E '^(renew_hook|deploy_hook)' /etc/letsencrypt/renewal/www.shop.test.conf`.

Wrong fixes:
- `no-reload.sh`: renews without a hook and writes the same serial twice.
- `self-signed.sh`: `openssl req -x509` in place of certbot.

About 35 minutes.

### 7.2 Recall on HTTP versions

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `alpn-from-curl-v` | predict_shell | http-versions | Captured `curl -v` lines. `grep -o 'ALPN: server accepted [a-z0-9/.]*'` prints `ALPN: server accepted h2`. |
| `alt-svc-parse` | predict_shell | http-versions | Captured headers with `alt-svc: h3=":443"; ma=86400`. `grep -i '^alt-svc' h.txt \| grep -o 'ma=[0-9]*'` prints `ma=86400`; the explanation converts it to a day. |
| `mcq-h2-hol` | mcq | http-versions | On a lossy mobile link, why can HTTP/2 be slower than expected? Right: a lost TCP packet stalls every stream on the connection until it is resent. Distractors: HTTP/2 opens six connections; HPACK must re-send headers; ALPN renegotiates. |
| `mcq-h3-udp-blocked` | mcq | http-versions | HTTP/3 was enabled, `Alt-Svc` is sent, and dashboards show 0% HTTP/3. Right: UDP 443 is blocked between clients and the server (a firewall or security group), so clients stay on HTTP/2. |
| `mcq-when-h3-helps` | mcq | http-versions | Which workload gains most from HTTP/3? Right: mobile users on lossy, changing networks. Distractors cover service-to-service calls inside one data centre, large one-off downloads on fibre, and an internal admin page. |
| `est-rtt-tls12` | estimate | http-versions | RTT 80 ms. A new HTTPS connection with TCP and TLS 1.2 (full handshake). How many milliseconds before the request can be sent? Exactly. **240** (`3 * rtt`). Mistakes: 160 (TLS 1.3), 80. |
| `est-rtt-tls13` | estimate | http-versions | RTT 120 ms, TCP and TLS 1.3. Exactly. **240** (`2 * rtt`). Mistakes: 360, 120. |
| `est-h3-saving` | estimate | http-versions | RTT 150 ms. How many milliseconds does a new HTTP/3 connection save over HTTP/2 on TLS 1.3, before the first request? Exactly. **150** (`2*rtt - rtt`). Mistakes: 300, 0. |
| `est-hundred-connections` | estimate | http-versions | A client opens 50 new TLS 1.2 connections one after another at RTT 40 ms, against reusing one. How many seconds of handshakes does reuse save? Within 5%. **5.88** (`49 * 3 * rtt / 1000`). Mistakes: 6 (counts all 50), 1.96 (one RTT each). |

### 7.3 Recall on handshakes

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `trace-13-messages` | predict_shell | tls-handshake | A trimmed captured `-trace` (from `captured/openssl-trace-tls13.txt`; keep the message header lines). The lesson's `awk` one-liner prints the 1.3 sequence. |
| `trace-12-in-clear` | predict_shell | tls-handshake | The 1.2 capture. `grep -B3 'Certificate, Length' t12.txt \| grep 'Content Type'` prints `Content Type = Handshake (22)`. The same command on the 1.3 capture prints `ApplicationData (23)`. Two files, one command each, a two-line output. |
| `mcq-what-observer-sees` | mcq | tls-handshake | On the wire, in TLS 1.3 without ECH, which can an observer read? Right: the server name in the ClientHello. Distractors: the certificate's subject, the URL path, the session cookie. |
| `mcq-sni-why` | mcq | tls-handshake | Why does the client send SNI? Right: many sites share one address, and the server must pick a certificate before anything is encrypted. |
| `mcq-tls-versions` | mcq | tls-handshake | Which versions should a public server allow in 2026? Right: TLS 1.2 and 1.3 (1.0 and 1.1 deprecated by RFC 8996). Distractors cover 1.3 only, which cuts off some older clients the brief's story names; 1.1 to 1.3; and "whatever the library defaults to", which is wrong on old builds. |
| `stapling-status` | predict_shell | tls-handshake | The captured `s_client -status` output (`captured/s_client-status.txt`). `grep -E 'OCSP Response Status\|Cert Status'` prints the two lines. |
| `mcq-first-handshake-no-staple` | mcq | tls-handshake | Right after `systemctl restart nginx`, `-status` says `no response sent`, and a second try shows a staple. Right: nginx fetches the OCSP response when the first handshake asks, so the first one goes without it. |
| `keylog-decrypted` | predict_shell | tls-handshake | Two captured tshark outputs, with and without the key log (fact 22), as handshake-type columns. The command counts the distinct types in each. Without keys `1 2`; with keys `1 2 4 8 11 15 20`. The explanation maps the numbers to names. |

### 7.4 `fill-local-ca` (fill-in, systemd lab), skills `cert-chains`, `mutual-tls`

`~/bin/make-shop-certs` with gaps. Fixed: the root `openssl req -x509` line with `basicConstraints=critical,CA:TRUE`. Gaps:

- the intermediate's extension file (gap: `CA:TRUE,pathlen:0`);
- the leaf's `subjectAltName` (gap: `DNS:api.shop.test`);
- the leaf's `extendedKeyUsage` (gap: `serverAuth`);
- the full-chain file's order (gap: which file first);
- the partners' client CA, a separate root (fixed);
- the warehouse's client certificate EKU (gap: `clientAuth`).

`/etc/nginx/sites-available/partner-api` with gaps: `ssl_certificate` (which file), `ssl_client_certificate` (which CA), `ssl_verify_client` (the value).

Checks:
- `chain-verifies`: from the office, `openssl s_client -connect api.shop.test:8443 -servername api.shop.test -CAfile root.pem -cert …warehouse…` gives `Verify return code: 0`, and the chain served has 2 certificates.
- `names`: the leaf's SANs include `api.shop.test`.
- `partner-in`: `from-partner curl --cert …` returns 200, with `$ssl_client_verify=SUCCESS` echoed by the location.
- `anonymous-out`: no certificate gives 400.
- `server-ca-cert-out`: a client certificate the check signs at check time with the server intermediate gives 400.

Wrong fixes:
- `leaf-only.sh`: fails `chain-verifies` (21).
- `cn-only.sh`: SAN missing, so hostname mismatch (62).
- `chain-reversed.sh`: intermediate first, so nginx won't start (`key values mismatch`) and `chain-verifies` fails.
- `verify-optional.sh`.
- `server-ca-trusted-for-clients.sh`.
- `client-eku-missing.sh`: nginx rejects a certificate without clientAuth. **Not tried:** OpenSSL checks the purpose during verification, so confirm it fails before keeping this one; if it passes, drop it and teach EKU in recall only.

About 35 minutes.

### 7.5 Recall on chains

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `verify-code-meaning` | predict_shell | cert-chains | Four captured `Verify return code:` lines in a file. `cut -d'(' -f2 \| tr -d ')' \| sort` prints the four reasons. The explanation maps each to its cause. |
| `mcq-code-21` | mcq | cert-chains | `curl` from a server fails with `unable to verify the first certificate`, while a laptop browser shows the padlock. Right: the server sends its certificate without the intermediate; the browser had the intermediate already. |
| `mcq-san-not-cn` | mcq | cert-chains | The certificate's CN is `www.shop.test` and its SANs are `shop.test` only. A browser visiting `www.shop.test`: right, a name error, because browsers match only the SANs. |
| `x509-dates` | predict_shell | cert-chains | A captured `openssl x509 -noout -subject -issuer -dates -ext subjectAltName` output. `grep -E 'notAfter\|DNS:'` prints two lines. |
| `est-days-left` | estimate | cert-chains | `notAfter=Mar 30 12:00:00 2027 GMT` and today is 2027-03-02 12:00 GMT. Whole days left? Exactly. **28**. Mistakes: 29 (counting both ends), 30 (assuming 30-day months). |
| `mcq-ship-the-root` | mcq | cert-chains | Must the server send the root? Right: no. The client must already trust it, so sending it only adds bytes. |

### 7.6 Recall on ACME and rotation

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `mcq-wildcard-challenge` | mcq | acme-and-rotation | A wildcard `*.shop.test`. Which challenge? Right: DNS-01. |
| `mcq-port-80-closed` | mcq | acme-and-rotation | The server only opens 443. Which challenge still works without DNS credentials? Right: TLS-ALPN-01 (with the "limited client support" caveat). Distractors: HTTP-01 on 443, DNS-01 without an API, re-using last year's authorisation. |
| `mcq-live-not-archive` | mcq | acme-and-rotation | nginx points at `/etc/letsencrypt/archive/www.shop.test/cert1.pem`. What happens at renewal? Right: certbot writes `cert2.pem` and moves `live/` to it; nginx keeps serving `cert1` until it expires. |
| `mcq-deploy-hook` | mcq | acme-and-rotation | Renewal succeeds every 2 months, yet the site serves an expired certificate. Right: nothing reloads nginx after renewal; it needs a deploy hook. |
| `mcq-why-short` | mcq | acme-and-rotation | Why are lifetimes shrinking? Right: revocation is unreliable, so a stolen key stays useful until expiry, and a shorter life bounds the damage and forces automation. |
| `mcq-ocsp-today` | mcq | acme-and-rotation | A certificate from Let's Encrypt issued in November 2026. Is there an OCSP URL to staple? Right: no; OCSP URLs were dropped in May 2025, and revocation is published in CRLs. |
| `est-renew-at-two-thirds` | estimate | acme-and-rotation | A 45-day certificate renewed at two-thirds of its life. On which day after issue does renewal start? Exactly. **30** (`45 * 2 / 3`). Mistakes: 15, 45. |
| `est-renewals-a-year` | estimate | acme-and-rotation | 47-day maximum validity, renewing every 30 days. How many renewals in 365 days? Within 1. **12** (`365 / 30`, 12.17). Mistakes: 8 (365/47), 4 (90-day thinking). |
| `est-200-days` | estimate | acme-and-rotation | A certificate issued on 2026-04-01 with the maximum validity allowed then. In how many days does it expire? Exactly. **200**. Mistakes: 398, 100. The working is the plain 200, a number to know. |
| `est-24h-two-thirds` | estimate | acme-and-rotation | step-ca's 24-hour certificates, renewed at two-thirds. How many renewals a day? Within 0.1. **1.5** (`24 / 16`). Mistakes: 1, 3. |

### 7.7 Recall on mutual TLS

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mtls-curl-outcomes` | predict_shell | mutual-tls | Three captured curl results (no cert, the right cert, a server-CA cert). The command prints each `<title>` or body line: `400 No required SSL certificate was sent`, `partner CN=warehouse.partners.test verified=SUCCESS`, `400 The SSL certificate error`. |
| `mtls-trace-request` | predict_shell | mutual-tls | The captured mTLS trace sequence (fact 19's run): `CertificateRequest` appears after EncryptedExtensions, and the client sends `Certificate CertificateVerify Finished`. Count the Certificate messages: 2. |
| `mcq-optional` | mcq | mutual-tls | Right: `ssl_verify_client optional` lets clients without a certificate through, so the API is open. |
| `mcq-separate-client-ca` | mcq | mutual-tls | Why not trust the server CA for client certificates? Right: then any certificate it ever issued, such as a web server's, would open the partner API. |
| `mcq-alb-mtls-modes` | mcq | mutual-tls | ALB passthrough against verify. Right: passthrough forwards the client chain in a header for the targets to check; verify has the load balancer check it against a trust store. |

### 7.8 `write-cert-report` (write, plain lab is enough), skills `cert-chains`, `tls-handshake`

`~/bin/cert-report HOST PORT [NAME]` connects (with SNI = NAME, default HOST) and prints exactly six lines:

```
names: <the SANs, comma-separated, sorted>
issuer: <issuer CN>
days-left: <whole days until notAfter, rounded down>
chain: <number of certificates the server sent>
protocol: <TLSv1.3 or TLSv1.2>
verify: <ok, or the reason in brackets from Verify return code>
```

The trust file is fixed by the prompt: `/etc/lab/trust.pem`. The prompt names `openssl s_client -showcerts`, `openssl x509 -noout -ext subjectAltName -enddate -issuer`, `date -d … +%s` and `$(( ))`.

Checks make their own inputs. Each check generates a fresh CA, intermediate and leaf with `openssl`, with **random** SAN labels and a random lifetime of 3 to 60 days plus 12 hours (so rounding down and rounding up always differ). It starts throwaway `openssl s_server` processes on random high ports, then runs the script and compares field by field. Three servers each run: full chain over TLS 1.3; leaf only, over `-tls1_2` only; and one whose SNI name differs from the default certificate (served by two `-servername`/`-cert2` pairs), checked with and without NAME. The check stops its servers afterwards (`pkill -f 'openssl s_serve[r]'`, the bracket rule).

Wrong fixes:
- `hard-coded.sh`;
- `rounds-up.sh`;
- `cn-not-sans.sh`;
- `no-sni.sh`: ignores NAME, so the third case fails;
- `counts-root.sh`: counts the trust file's root in `chain`.

About 35 minutes.

### 7.9 Ladder order

`example-issue-and-inspect`, `alpn-from-curl-v`, `alt-svc-parse`, `mcq-h2-hol`, `mcq-h3-udp-blocked`, `est-rtt-tls12`, `est-rtt-tls13`, `est-h3-saving`, `trace-13-messages`, `trace-12-in-clear`, `mcq-what-observer-sees`, `mcq-sni-why`, `mcq-tls-versions`, `stapling-status`, `mcq-first-handshake-no-staple`, `verify-code-meaning`, `mcq-code-21`, `mcq-san-not-cn`, `x509-dates`, `est-days-left`, `fill-local-ca`, `mtls-curl-outcomes`, `mcq-optional`, `mcq-separate-client-ca`, `mcq-wildcard-challenge`, `mcq-live-not-archive`, `mcq-deploy-hook`, `mcq-ocsp-today`, `est-renew-at-two-thirds`, `est-renewals-a-year`, `write-cert-report`.

That's 26 quick items (39 minutes), a worked example, a fill-in and a write. Review-only: `mcq-when-h3-helps`, `est-hundred-connections`, `keylog-decrypted`, `mcq-ship-the-root`, `mcq-port-80-closed`, `mcq-why-short`, `est-200-days`, `est-24h-two-thirds`, `mtls-trace-request`, `mcq-alb-mtls-modes`.

Practised before proven:

| Skill | Practised in |
| --- | --- |
| http-versions | the example, 7 items |
| tls-handshake | the example, 7 items, the write |
| cert-chains | the fill-in, 5 items, the write |
| acme-and-rotation | the example (issue, serve, hook, renew), 6 items |
| mutual-tls | the fill-in, 3 items |

## 8. Proofs

### 8.1 Build: `build-shop-tls` (systemd lab, 60 minutes), skills: all but http-versions

**Brief to the learner:**

1. `www.shop.test` serves HTTPS with a certificate from the company CA's ACME service (`https://ca.shop.test:9000/acme/acme/directory`), obtained with certbot over HTTP-01. It renews automatically, and every renewal reaches nginx without anyone touching it.
2. Port 80 only redirects to HTTPS, except for ACME's challenge path.
3. TLS 1.2 and 1.3 only. HTTP/2 on.
4. `api.shop.test` on port 8443, the same address, is the partners' API. It needs its own certificate, from the same ACME service. It admits only clients with a certificate from the Shop Partners CA (`/etc/lab/partners-ca.pem`), and the public site asks no one for a certificate.
5. Each name gets its own certificate, chosen by SNI. One certificate covering both names is also accepted (open question 3).

**Checks:**

| Id | What it proves |
| --- | --- |
| `www-trusted` | From the office with only the CA root: `Verify return code: 0`, SAN contains `www.shop.test`, issuer is the CA's intermediate, lifetime ≤ 25 h (so it came from ACME, not a hand-made CA). |
| `renewal-reaches-nginx` | `timeout: 120`. Reads the served serial, runs `certbot renew --force-renewal --no-random-sleep-on-renew`, then within 10 s the served serial differs and matches `live/` (this is what the timer would do at two-thirds of a life). |
| `timer-on` | `systemctl is-enabled certbot.timer` and `is-active`. |
| `redirect` | `curl -sI http://www.shop.test/` gives 301 to `https://www.shop.test/`; a challenge-path file the check writes to the webroot and then removes is served over HTTP. |
| `versions` | `s_client -tls1_2` and `-tls1_3` succeed; `-tls1_1 -cipher 'DEFAULT@SECLEVEL=0'` fails. **Not tried:** OpenSSL 3's client refuses 1.1 at the default security level whatever the server says, hence the cipher string. Prove that this check fails against a server allowing 1.1 before relying on it. |
| `h2` | `curl -w '%{http_version}'` gives `2`. |
| `partner-in` | From `partner`, with its certificate: 200 on `https://api.shop.test:8443/`. |
| `partner-api-closed` | No certificate gives 400. A client certificate signed by the server CA at check time gives 400. A certificate from a throwaway CA gives 400. |
| `public-site-open` | `www.shop.test` with no client certificate gives 200, and the handshake has no CertificateRequest (`-trace`). |
| `sni` | `-servername api.shop.test` gets a certificate whose SANs include `api.shop.test`; `-servername www.shop.test` gets one with `www.shop.test`. |

**Wrong fixes:**

1. `self-signed.sh`
2. `leaf-only.sh`
3. `no-deploy-hook.sh`
4. `archive-path.sh`
5. `timer-disabled.sh`
6. `tls11-allowed.sh` (with `ssl_ciphers DEFAULT@SECLEVEL=0`)
7. `verify-optional.sh`
8. `client-ca-is-server-ca.sh`
9. `mtls-on-www.sh`
10. `no-redirect.sh`
11. `redirect-breaks-acme.sh`: redirects the challenge path too. It passes once issued, so the check's challenge-path probe catches it.

The time limits add up to 120 + 9 × 30 = 390 s, under 600.

### 8.2 Debug: `debug-padlock-trouble` (systemd lab, 45 minutes), skills `cert-chains`, `acme-and-rotation`, `mutual-tls`

**Prompt.** The shop's web server runs nginx for two sites:

- `www.shop.test`, the public shop, whose certificate comes from the company CA's ACME service through certbot, renewed by its timer;
- `api.shop.test:8443`, the partners' API, whose server certificate comes from the company's internal CA (`/etc/ssl/shop/`), and which admits only clients holding a certificate from the Shop Partners CA.

Since the weekend's maintenance:

- customers' browsers say the shop's certificate has expired, though `sudo certbot certificates` shows one valid for another 23 hours;
- the warehouse's nightly sync, which runs on `partner`, fails: run it with `from-partner /usr/local/bin/warehouse-sync` and read what it prints.

There are three faults. Rules of the fix:

- the warehouse's certificate and key are theirs: don't replace them;
- the API must keep refusing everyone without a valid partner certificate;
- no client may be told to skip verification;
- whatever you do must survive the next renewal and a reboot.

**Faults** (story script):

1. nginx's `www` server reads `/etc/nginx/certs/www.pem` and `www.key`, a copy someone made by hand. It expired yesterday: the story issues it with a short lifetime through `faketime` and the internal CA. certbot's `live/` holds a fresh one, and the renewal configuration has no deploy hook.
2. The API's server certificate is served without its intermediate. The warehouse's client (curl with `--cacert` of the internal root) fails with `(60) … unable to get local issuer certificate`.
3. Once the chain is fixed, the next error appears: `ssl_client_certificate` points at the internal server CA bundle, "tidied up" over the weekend, so the warehouse's certificate is refused with `400 The SSL certificate error`.

The learner finds 2 and 3 in sequence, the way `csa.hw.windows-ad`'s debug lab works.

**Checks:**
- `www-valid`: the office verifies OK; the certificate isn't expired; its issuer is the ACME intermediate.
- `renewal-reaches-nginx`: as in the build.
- `sync-works`: `warehouse-sync` prints `synced 42 orders` (a fixed scenery output, once its HTTPS call returns 200).
- `api-chain`: 2 certificates served, verify 0.
- `api-still-closed`: no certificate gives 400; a server-CA client certificate made at check time gives 400.
- `warehouse-cert-unchanged`: sha256 of `partner`'s certificate and key match the image.
- `no-skip`: `warehouse-sync`'s file unchanged, so no `-k` was added.

**Wrong fixes:**
1. `copied-fresh-cert.sh`: copies `live/` over `/etc/nginx/certs/`. Passes today, fails `renewal-reaches-nginx`.
2. `reload-only.sh`.
3. `verify-off.sh`.
4. `trust-both-cas.sh`: puts both CAs in `ssl_client_certificate`, so the server-CA client certificate is accepted.
5. `new-warehouse-cert.sh`.
6. `sync-insecure.sh`: adds `-k` to the sync script.
7. One "two of three fixed" variant per fault.

**Not built.** The ACME, chain and mTLS mechanics were each tried. The `faketime` issue of an already-expired certificate wasn't; `faketime` is in Ubuntu and `csa.hw.windows-ad`'s labs already install it. Prove the contract first.

### 8.3 Explain

**Prompt.** "A colleague says HTTPS is 'just encryption, the certificate is a formality'. Explain, in your own words: what a TLS 1.3 handshake does and what an observer on the network can still see; how a client decides to trust a server's certificate, and the two most common ways that goes wrong in production; why certificates now last weeks rather than years, and what you must build so that this causes no outages; what OCSP stapling was for and what is replacing it; when you would require client certificates, and the one setting that most often leaves mTLS open; and what HTTP/2 and HTTP/3 change, with one reason HTTP/3 might not be used even when it's switched on."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `handshake` | yes | Key exchange and the server proves possession of the certificate's key (CertificateVerify). 1.3 encrypts everything after ServerHello, in 1 RTT. SNI (and so the site's name) is visible unless ECH. |
| `trust` | yes | Chain to a trusted root; SAN matches; within dates. Failures: missing intermediate (21), expired, wrong name. |
| `lifetimes-automation` | yes | 200 → 100 → 47 days; ACME with renewal at about two-thirds or ARI; the server must load the renewal (`live/` paths, reload hook); monitor expiry. |
| `revocation` | no | Stapling put the CA's status in the handshake; Let's Encrypt ended OCSP in 2025; CRLs and short lifetimes. |
| `mtls` | yes | Partner and service-to-service APIs; a separate client CA; `optional` or a broad trust store leaves it open. |
| `http-versions` | yes | h2 multiplexes on one TCP connection (TCP head-of-line); h3 on QUIC/UDP removes it and saves a round trip; UDP 443 blocked means silent fallback. |

## 9. Review pool

- http-versions: `est-rtt-tls13`, `est-hundred-connections`, `mcq-h3-udp-blocked`, `mcq-when-h3-helps`.
- tls-handshake: `trace-12-in-clear`, `keylog-decrypted`, `mcq-what-observer-sees`, `mcq-first-handshake-no-staple`.
- cert-chains: `verify-code-meaning`, `est-days-left`, `mcq-code-21`, `mcq-ship-the-root`.
- acme-and-rotation: `est-renew-at-two-thirds`, `est-200-days`, `est-24h-two-thirds`, `mcq-live-not-archive`, `mcq-why-short`.
- mutual-tls: `mtls-curl-outcomes`, `mtls-trace-request`, `mcq-separate-client-ca`, `mcq-alb-mtls-modes`.

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| T1 | The network-lab base (see `csa.net.dns` D1). Here it needs four machines: `lab`, `ca`, `office`, `partner`. The `ca` machine needs a persistent directory for step-ca (`/var/lib/lab/ca`) and its unit started after the network. | as in topic 30 |
| T2 | **The first lab image that downloads a binary from outside Ubuntu's archive.** step-ca and step-cli `.deb`s from GitHub releases, pinned by version and sha256, verified in the same `RUN`. | One `RUN` line: `curl -fsSLo … && echo "<sha256>  <file>" \| sha256sum -c && apt-get install -y ./… && rm …`. No ADR needed, but record it in the devlog's author notes, because the image's build now depends on GitHub as well as the archive. |
| T3 | `REQUESTS_CA_BUNDLE` set system-wide for certbot (in `/etc/environment` and certbot's timer service as a drop-in). Otherwise certbot can't trust the private CA's HTTPS endpoint. | A drop-in for `certbot.service` with `Environment=REQUESTS_CA_BUNDLE=/etc/lab/ca-root.pem`. Tried by environment variable only; the drop-in isn't tried. |
| T4 | None in the app. | |

## 11. Cost and time

- **Money:** none. No cloud lab. A real Let's Encrypt certificate needs a public name and port 80 reachable from the internet, which the owner's machine doesn't offer. The private ACME CA teaches the same protocol.
- **Learner minutes:** lesson 16, reading 47 (Cloudflare 9, Illustrated TLS 15, MDN 9, Let's Encrypt 5 + 9, OCSP 6, mTLS 9; HPBN and ISRG optional), 26 quick items 39, worked example 35, fill-in 35, write 35, build 60, debug 45, explain 20. **Total 332.**
- **Labs and CI:** five labs. Images: base, plus the topic layer (about 70 MB), plus step-ca (99 MB) on three of them, built once per shard. Contract runs: the example about 2 minutes, the fill-in about 3, the write about 2, the build about 7 (13 containers, with renewals), the debug about 6. **About 20 minutes for the topic**, about 5 minutes of wall time at four jobs.

## 12. Open questions, each with a recommendation

1. **332 minutes is over the 300 at which Module 2 split topics.** Split it along the seam "TLS on the wire" (`http-versions`, `tls-handshake`: the example's steps 1 to 4, sections 7.2 and 7.3, a new build "serve two sites on one address with TLS 1.2 and 1.3, HTTP/2 and HTTP/3 through Caddy with UDP open", and a new debug with a version mismatch, a default-server SNI mistake and blocked UDP 443) and "certificates" (`cert-chains`, `acme-and-rotation`, `mutual-tls`: everything else, the build and debug above). That would give about 170 and 230 minutes. **Recommendation: split,** as Module 2's critic did, for the same reason: shorter topics reach their proofs and first reviews sooner. The second topic's id would be `csa.net.certificates`, "Certificates, ACME and mutual TLS". Spec and checkpoint prerequisites change. If the critic prefers one topic, keep this brief as written. The two proofs above already test every skill except `http-versions`, which recall and the explain cover.
2. **step-ca rather than Pebble.** Pebble is Let's Encrypt's own test CA and in Ubuntu's archive. But its root changes every start, which breaks the restart trial, and its 5-year certificates hide rotation. step-ca keeps its CA and issues 24-hour certificates, at 99 MB and a GitHub download. **Recommendation: step-ca.** The lesson names Pebble in one line as what ACME client authors test against.
3. **One certificate for both names, or one each?** **Recommendation: accept either** in the build. Both are correct practice. The `sni` check accepts any certificate whose SANs contain the name asked for.
4. **certbot or lego?** lego is smaller (3 packages against 36). certbot is what most guides and distributions use, and it installs its own timer. **Recommendation: certbot,** for the timer and the deploy-hook lesson, at 20 MB.
5. **tshark in a lab?** **Recommendation: no** (147 MB). Recall items carry its decrypted output, captured, and `openssl -trace` shows the same structure from the endpoint.

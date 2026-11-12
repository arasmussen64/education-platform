# Writing brief: `csa.net.http-semantics` (topic 32), HTTP semantics

Design only. Nothing here is in the repository. Sources were read on 2026-11-11, and each fact carries its URL. Lab mechanics marked **tried** were run that day in Docker Desktop on the owner's PC (`ubuntu:24.04`, nginx 1.24.0, curl 8.5.0, Python 3.12, python3-websockets 10.4). Everything started was removed. Prototype files are in `prototypes/dns-http/http-semantics/`:

- `app/app.py`, a stdlib shop backend;
- `app/board.py`, a WebSocket order board;
- `nginx-sites/shop`, an origin plus an edge cache;
- `nginx-sites/api`, CORS;
- `nginx-sites/board`, WebSocket proxying.

**How a lab can check CORS without a browser.** CORS is a rule that browsers enforce, using headers the server sends. A lab can't run a browser cheaply (a headless Chromium would add hundreds of megabytes to every image), but it doesn't need one. It sends the browser's own requests with `curl` (the preflight `OPTIONS` with `Origin`, `Access-Control-Request-Method` and `Access-Control-Request-Headers`, then the real request with `Origin`). Then it applies the browser's decision rules to the server's answers: the Fetch standard's "CORS check" (§4.10) and its preflight rules. Those rules are short and public: a dozen lines of Python, `cors-verdict`, living in the check's directory, not in the learner's shell, so no stand-in tool prints answers at the learner (Module 2's rule 3.4). The learner reads the same `curl` output and reasons like a browser. The write lab asks them to code the rule in bash themselves.

## 1. What the learner will be able to do

1. Set `Cache-Control` for each kind of response and say what a browser and a shared cache (a CDN or reverse proxy) will do with it:
   - fingerprinted assets: a long `max-age` plus `immutable`;
   - HTML: `no-cache` with an `ETag`, so revalidation gives a 304;
   - personal pages: `private` (or `no-store`);
   - API answers: usually `no-store`.

   Work out freshness from `max-age`, `s-maxage`, `Age`, and the heuristic for responses that carry no caching headers.
2. Explain CORS: what the same-origin policy protects (the user's data in their browser, against other sites' scripts). Know which requests are preflighted, and what the server's answer must contain, including the credentials rules (no `*`, `Access-Control-Allow-Credentials: true`, `Vary: Origin`). Know that CORS is not server-side access control.
3. Use methods and status codes as contracts: safe and idempotent methods; why only idempotent requests are retried automatically; conditional requests (304, 412); and 502 against 504 at a proxy.
4. Choose between REST over HTTP, WebSockets, server-sent events and gRPC over HTTP/2 for a given flow, and name what each asks of proxies and load balancers: the WebSocket upgrade and idle timeouts, and HTTP/2 end to end with trailers for gRPC (and gRPC-Web for browsers).

**The six-month core:**

- A fingerprinted file is cached for a year with `immutable`. HTML is `no-cache` (store it, but ask before reusing it), and an `ETag` turns the asking into a cheap 304. Anything personal is `private`. A shared cache that stores a personal page shows it to the next person (Steam, Christmas 2015).
- Freshness is `max-age` (or `s-maxage` for shared caches) minus `Age`. With no caching headers, caches may guess, typically 10% of the time since `Last-Modified`.
- A browser preflights anything beyond GET, HEAD or POST with simple headers. The answer must name the exact origin, never `*`, when credentials are sent; must say `Allow-Credentials: true`; and must carry `Vary: Origin` when it varies. Reflecting any origin, or matching on a suffix, opens the API to every site.
- PUT, DELETE and the safe methods are idempotent; POST isn't, so a retry can buy twice.
- WebSockets need the `Upgrade` and `Connection` headers passed through, and a ping more often than the smallest idle timeout on the path. gRPC needs HTTP/2 all the way.

## 2. Prerequisites and terms

**Recommended `prerequisites:`** `[csa.net.http-tls]` (HTTP versions, HTTP/2 streams for gRPC, and TLS for `https` origins). It reaches `csa.net.dns` and `csa.linux.net-tools` through that.

**Builds on (for the writer):**

- `csa.linux.net-tools`: `curl -I`, `-v`, `-H`, `-X`, `-w`; status lines; the `Location` header;
- `csa.net.http-tls`: HTTP/2 streams, ALPN, and HTTPS on nginx (this topic's labs serve plain HTTP inside the lab, to keep the image small and the focus on semantics; the prompts say so, and the CORS origins are written `https://…` because origins include the scheme);
- `csa.net.dns`: the topic's `TTL` caching picture, which the lesson calls on ("the same idea as DNS TTLs, one layer up");
- `csa.linux.services`: `systemctl reload nginx`, `journalctl`.

**Terms this topic must define itself:**

- origin (scheme, host, port) and same-origin policy; cross-origin request; preflight; simple request (Fetch calls it a "CORS-safelisted" method or header); credentials (cookies, HTTP authentication) and `credentials: include`;
- cache, private cache and shared cache; fresh and stale; freshness lifetime; validator (`ETag`, `Last-Modified`); conditional request (`If-None-Match`, `If-Modified-Since`, `If-Match`); revalidation; cache key and `Vary`; fingerprinted (versioned) URL; CDN (one line, taught in Module 11);
- safe method, idempotent method; idempotency key (one line); gateway and proxy in RFC 9110's sense (inbound server, upstream);
- REST (resources and methods, one paragraph, not a style war), WebSocket and the HTTP upgrade, `101 Switching Protocols`, ping and pong frames, idle timeout, server-sent events (one line), RPC, gRPC, protocol buffers, the four RPC kinds, trailers, gRPC-Web.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `caching` | `Cache-Control` directives (`max-age`, `s-maxage`, `no-cache`, `no-store`, `private`, `public`, `must-revalidate`, `immutable`, `stale-while-revalidate`); validators and 304; `Age` and freshness arithmetic; heuristic freshness; `Vary`; what a shared cache must never store. **A calculation skill: four estimate items.** |
| `cors` | Same-origin policy; simple against preflighted requests; the preflight answer; credentials and wildcards; `Vary: Origin`; `Access-Control-Max-Age` and browser caps; allow-list mistakes (reflection, suffix match, `null`); CORS isn't authentication. |
| `methods-and-status` | Safe and idempotent; retries; conditional requests (304, 412); status classes; 502 against 504; 405 and 429 (one line each). |
| `api-styles` | REST, WebSockets, SSE and gRPC (unary and streaming) for given flows; what each needs from nginx and cloud load balancers (upgrade headers, `proxy_read_timeout`, idle timeouts, HTTP/2 and `grpc_pass`, gRPC-Web). |

## 4. Lesson plan

The lesson is about 1,800 words (14 minutes).

1. **HTTP's verbs are promises (MDN "HTTP request methods" and "Idempotent").** RFC 9110 §9.2.1: a safe method is "essentially read-only". §9.2.2: "PUT, DELETE, and safe request methods are idempotent", and that is why a request "can be repeated automatically if a communication failure occurs". The lesson's picture: a lift button (pressing it twice changes nothing more) against a vending machine (pressing twice buys two). Consequences for an architect: a load balancer or client library may retry GET and PUT on a dropped connection, never POST; payment APIs add an idempotency key. Status classes in one table, then the two that matter most in operations, quoted from RFC 9110:
   - **502** "received an invalid response from an inbound server": the app crashed or closed the connection;
   - **504** "did not receive a timely response from an upstream server": the app is slow, or the proxy's timeout is short.
2. **Caching, the picture (MDN "HTTP caching", main resource: "Types of caches" to "Validation", then "Common caching patterns").** The lesson supplies the map:
   - the browser's private cache, the shared caches in between (a CDN, a company proxy, a reverse proxy like nginx), and the origin;
   - the same TTL idea as DNS, one layer up: `max-age` is a TTL, `Age` is how long the copy has already sat in a shared cache, and fresh means `max-age − Age > 0`;
   - stale isn't broken: a stale copy is revalidated with `If-None-Match`, and a 304 is a few hundred bytes.

   Tried, real output: `/assets/app.3f9a.js` through the edge gave `X-Cache-Status: MISS`, then `HIT`, and the origin answered `If-None-Match: "6af5239a-e"` with `304`.
3. **The four patterns (MDN's "Common caching patterns"; web.dev's article as a second explanation).**
   - fingerprinted assets: `public, max-age=31536000, immutable` (RFC 8246's `immutable` means "don't even revalidate on reload");
   - HTML: `no-cache`, which RFC 9111 §5.2.2.4 defines as "MUST NOT be used to satisfy any other request without forwarding it for validation". It doesn't mean "don't store"; that's `no-store`. This is the most commonly misread directive;
   - personal pages: `private`, because RFC 9111 §5.2.2.7 says "a shared cache MUST NOT store the response";
   - shared-cache-specific lifetime: `s-maxage` overrides `max-age` for shared caches (§5.2.2.10).

   With no caching headers at all, a cache may use a heuristic: "a typical setting of this fraction might be 10%" of the time since `Last-Modified` (§4.2.2). That's why "we never set cache headers" still caches.
4. **The day the cache shared a page (lesson; tried in the lab).** With `public, max-age=60` on `/account`, alice's request through the edge cache was stored, and bob's request a moment later got `X-Cache-Status: HIT` and alice's page. Steam's Christmas 2015 incident was this kind of mistake at scale: a caching configuration deployed during a traffic spike served some users other users' pages for about 90 minutes. Valve's statement as reported by the press: about 34,000 accounts. This is a secondary source, so the lesson says "as reported". `private` or `no-store` is the fix. The lab's nginx edge also refuses to store any response with `Set-Cookie` (nginx's docs say so).
5. **nginx specifics the labs need (lesson only, tried).**
   - `add_header` adds headers to what *this* nginx sends. A cache in front obeys the origin's headers, and nginx's own `proxy_cache` obeys what *its* upstream sent, not headers it adds itself. In the prototype, putting `add_header Cache-Control` on the same nginx that caches didn't make it cache (MISS, MISS).
   - So the labs have an **origin** nginx that sets headers and an **edge** nginx that caches, as real CDNs work.
   - `add_header … always` is needed for the header to appear on error responses too.
6. **Same origin and CORS (MDN "Cross-Origin Resource Sharing", from the top to "Requests with credentials", then the Fetch standard §4.10 read alongside).** The lesson's framing, which MDN doesn't foreground:
   - the browser holds the user's cookies for every site, so a page from `evil.test` running in the same browser must not be able to *read* the user's account at `api.shop.test`;
   - CORS is the API telling the browser which other origins may read its answers;
   - it protects users from other websites, not the server from attackers: `curl` ignores CORS entirely, so the API must still check who is calling.

   Then the mechanics:
   - simple requests (GET, HEAD, POST with safelisted headers, and `Content-Type` only `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`) go straight out. A JSON `PUT` doesn't: the browser first sends `OPTIONS` with `Access-Control-Request-Method` and `-Headers`;
   - the server's answer must allow that origin, method and headers. With credentials, the origin must be named exactly and `Access-Control-Allow-Credentials: true` sent, and `*` isn't allowed in the origin, methods or headers;
   - `Access-Control-Max-Age` lets the browser cache the preflight: default 5 seconds, capped at 7,200 by Chromium (since v76) and 86,400 by Firefox.

   Tried: nginx with a `map` allow-list answered the preflight from `https://www.shop.test` with the origin echoed back and `Vary: Origin`, and from `https://evil.test` with no `Access-Control-Allow-Origin`.
7. **Allow-list mistakes (lesson only).**
   - reflecting whatever `Origin` arrives (every site allowed, credentials included);
   - a regular expression ending `shop\.test$` without anchoring the dot before it, so `https://evilshop.test` matches;
   - allowing the origin `null` (sandboxed frames and local files send it);
   - forgetting `Vary: Origin`, so a shared cache hands one origin's CORS answer to another.

   The labs' checks try made-up origins of each kind.
8. **WebSockets (RFC 6455 §1 "Introduction"; nginx's "WebSocket proxying" page).** One HTTP request asks to upgrade (`Connection: Upgrade`, `Upgrade: websocket`, a key), and the server answers `101 Switching Protocols` with `Sec-WebSocket-Accept`. After that it's a two-way message channel on the same TCP connection.
   - Tried: RFC 6455's own example key `dGhlIHNhbXBsZSBub25jZQ==` produced `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=` through nginx, exactly as the RFC shows.
   - `Upgrade` is hop-by-hop, so a proxy must pass it explicitly (`proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";`, and `proxy_http_version 1.1` before nginx 1.29.7). Ubuntu 24.04's 1.24 needs it. Tried: without these lines the upgrade got `400 Bad Request`.
   - Every hop has an idle timeout: nginx's `proxy_read_timeout` is 60 s by default. Tried with 5 s: an idle WebSocket closed after exactly 5.0 s. AWS ALB's idle timeout is 60 s by default.
   - The fix is a ping more often than the smallest timeout on the path, plus, where the product allows, a longer timeout.
9. **gRPC (grpc.io "Introduction" and "Core concepts"; the gRPC-over-HTTP/2 protocol note).** A service defined in protocol buffers; unary, server-streaming, client-streaming and bidirectional RPCs; deadlines. On the wire: HTTP/2, `content-type: application/grpc`, and the status in **trailers** ("Status must be sent in Trailers even if the status code is OK"). Clients send `te: trailers` "to detect incompatible proxies". So every hop must speak HTTP/2 and pass trailers.
   - nginx does it with `grpc_pass`, which "requires the ngx_http_v2_module".
   - Browsers can't speak gRPC directly: grpc.io's web guide puts an Envoy proxy in front ("gRPC-Web").
   - **Where the clouds differ:** Google's load balancers proxy WebSockets with no configuration and apply their own timeouts, by load balancer type. Deeper cloud gRPC and WebSocket support is Module 11's.
10. **Choosing (lesson only, as a table the learner keeps).**

    | Flow | Choice |
    | --- | --- |
    | Product catalogue a browser reads | REST plus caching |
    | Live order board pushed to staff screens | WebSockets, or SSE if it only flows one way |
    | Chat both ways | WebSockets |
    | Internal service-to-service calls with a strict contract and streaming | gRPC |
    | Public partner API | REST (tooling, caching, CORS) |
    | Mobile app that must survive network changes | REST over HTTP/3, or gRPC with deadlines |

    The rule under it: pick the simplest style that carries the flow's direction and latency, then check every proxy on the path can carry it.

**Read now:** MDN's caching guide (main): "Types of caches" to "Validation", and "Common caching patterns". MDN's CORS guide to "Requests with credentials". RFC 6455's §1.2 and §1.3. grpc.io's "Core concepts". The nginx WebSocket page. Optional: web.dev's "HTTP Cache".

## 5. Verified facts

All read on 2026-11-11.

| # | Claim | Source |
| --- | --- | --- |
| 1 | Safe methods are "essentially read-only". "PUT, DELETE, and safe request methods are idempotent". Idempotent requests "can be repeated automatically if a communication failure occurs". | RFC 9110 §9.2.1, §9.2.2, https://www.rfc-editor.org/rfc/rfc9110.txt |
| 2 | 502: a gateway or proxy "received an invalid response from an inbound server". 504: it "did not receive a timely response from an upstream server". | RFC 9110 §15.6.3, §15.6.5 |
| 3 | RFC 9111 directives: `no-cache` (§5.2.2.4), `no-store` (§5.2.2.5), `private` (§5.2.2.7: "a shared cache MUST NOT store"), `s-maxage` (§5.2.2.10), `must-revalidate` (§5.2.2.2). Heuristic freshness "might be 10%" of the time since Last-Modified (§4.2.2). Vary joins the cache key (§4.1). | https://www.rfc-editor.org/rfc/rfc9111.html |
| 4 | `immutable` is RFC 8246 (September 2017). `stale-while-revalidate` is RFC 5861 (May 2010, Informational). | rfc-editor.org JSON |
| 5 | Fetch §4.10 CORS check: no `Access-Control-Allow-Origin` fails; `*` succeeds only when credentials mode isn't "include"; otherwise the value must equal the serialised origin; with credentials, `Access-Control-Allow-Credentials` must be `true`. CORS-safelisted methods are GET, HEAD and POST. Licence CC BY 4.0. Last updated 19 October 2026. | https://fetch.spec.whatwg.org/ (#cors-check, #cors-safelisted-method) |
| 6 | MDN: simple requests (methods, safelisted headers, three Content-Type values); the preflight's headers; with credentials no `*` in Allow-Origin, -Headers, -Methods or -Expose-Headers; `Vary: Origin` when the origin is chosen from a list. Page modified 2026-10-28. | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS |
| 7 | `Access-Control-Max-Age` default 5 s; caps: Firefox 86,400 s, Chromium 7,200 s (600 before v76). | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Max-Age |
| 8 | MDN prose is CC BY-SA 2.5 or later; code samples CC0. | https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Attrib_copyright_license |
| 9 | RFC 6455: Sec-WebSocket-Accept is base64 of SHA-1 of the key followed by `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`. The example key `dGhlIHNhbXBsZSBub25jZQ==` gives `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=`. The upgrade answer is 101. A Ping may serve "as a keepalive". | https://www.rfc-editor.org/rfc/rfc6455.html |
| 10 | nginx WebSocket proxying: Upgrade and Connection are hop-by-hop and must be passed explicitly. `proxy_http_version 1.1` is needed "before version 1.29.7". The connection closes after 60 s with no data unless `proxy_read_timeout` is raised or the server pings. | https://nginx.org/en/docs/http/websocket.html |
| 11 | nginx `proxy_read_timeout` default 60 s. Caching parameters come from `X-Accel-Expires`, `Expires` or `Cache-Control`. A response with `Set-Cookie` isn't cached. `Vary: *` isn't cached; another `Vary` keys on those request headers. The page does **not** list which `Cache-Control` values stop caching. | https://nginx.org/en/docs/http/ngx_http_proxy_module.html |
| 12 | nginx `ngx_http_grpc_module` passes requests to a gRPC server and "requires the ngx_http_v2_module". `grpc_read_timeout` defaults to 60 s. | https://nginx.org/en/docs/http/ngx_http_grpc_module.html |
| 13 | gRPC: unary, server streaming, client streaming and bidirectional RPCs; protocol buffers by default; deadlines (`DEADLINE_EXCEEDED`). grpc.io content is CC BY 4.0 (its repository's LICENSE). | https://grpc.io/docs/what-is-grpc/core-concepts/; https://github.com/grpc/grpc.io (LICENSE) |
| 14 | gRPC over HTTP/2: `content-type` starting `application/grpc`; status in trailers "even if the status code is OK"; `te: trailers` "Used to detect incompatible proxies". | https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md |
| 15 | gRPC-Web reaches gRPC services from browsers; grpc.io's example uses an Envoy proxy, and CORS setup may be needed. | https://grpc.io/docs/platforms/web/basics/ |
| 16 | AWS ALB idle timeout default 60 s. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html |
| 17 | Google's HTTP(S) load balancers support WebSocket with no configuration, over HTTP/1.1 or HTTP/2 to backends. Timeouts depend on the load balancer type. | https://docs.cloud.google.com/load-balancing/docs/https |
| 18 | web.dev "Prevent unnecessary network requests with the HTTP Cache" (Ilya Grigorik, Jeff Posnick): last updated 2018-11-05; CC BY 4.0, code Apache 2.0 (page footer). | https://web.dev/articles/http-cache |
| 19 | Tried: through an nginx edge cache, `public, max-age=31536000, immutable` gave MISS then HIT. `no-cache` gave MISS, MISS (nginx doesn't store it; RFC 9111 would allow storing with revalidation: the lesson flags the difference). `public, max-age=60` on `/account` gave bob alice's page (HIT). The origin answered `If-None-Match` with 304. | prototype |
| 20 | Tried: `add_header Cache-Control` on the caching nginx itself didn't make its own `proxy_cache` store (MISS, MISS). | prototype |
| 21 | Tried: a `map`-based allow-list echoed allowed origins with `Vary: Origin` and sent no `Access-Control-Allow-Origin` to others (nginx omits a header whose value is empty). | prototype |
| 22 | Tried: the WebSocket upgrade through nginx without the Upgrade and Connection lines gave 400; with them, 101 and the RFC's accept value. `proxy_read_timeout 5s` closed an idle socket after 5.0 s. | prototype |
| 23 | Steam, 25 December 2015: a caching configuration during a DoS-driven traffic spike served some users others' account pages for about 90 minutes; about 34,000 accounts (Valve's statement, as reported). | secondary: https://www.gameinformer.com/b/news/archive/2015/12/30/valve-provides-more-information-on-steams-troubled-christmas-that-affected-34000.aspx (found by search, not opened) |

**Not confirmed:** whether nginx's edge refuses to store `private` responses wasn't tried (fact 11's page is silent). The build's `account-private` check tests the behaviour (bob never sees alice's page), so either way the check is honest. A writer tries `private` in the prototype before writing a recall item that claims nginx's behaviour.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | "HTTP caching" (MDN): "Types of caches" to "Validation", and "Common caching patterns" | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | reading | CC BY-SA 2.5+ (prose). Linked | 22 of 40 (5,211 words) | caching | 2026-11-11 |
| 1 | "Cross-Origin Resource Sharing (CORS)" (MDN): from the top to "Requests with credentials" | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS | reading | CC BY-SA 2.5+. Linked | 18 of 29 (3,816 words) | cors | 2026-11-11 |
| 2 | "HTTP request methods" and "Idempotent" (MDN) | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods, https://developer.mozilla.org/en-US/docs/Glossary/Idempotent | reading | CC BY-SA 2.5+. Linked | 7 (430 + 484 words) | methods-and-status | 2026-11-11 |
| 3 | RFC 6455 §1.2 "Protocol Overview" and §1.3 "Opening Handshake" | https://www.rfc-editor.org/rfc/rfc6455.html | reading | IETF Trust Legal Provisions. Linked | 10 | api-styles | 2026-11-11 |
| 4 | "Core concepts" (grpc.io) | https://grpc.io/docs/what-is-grpc/core-concepts/ | reading | CC BY 4.0. Linked | 11 (1,491 words) | api-styles | 2026-11-11 |
| 5 | "WebSocket proxying" (nginx) | https://nginx.org/en/docs/http/websocket.html | reading | nginx documentation. Linked | 4 | api-styles | 2026-11-11 |
| 6 | "Prevent unnecessary network requests with the HTTP Cache" (web.dev), optional second explanation | https://web.dev/articles/http-cache | reading | CC BY 4.0 (text), Apache 2.0 (code). Linked | 16 (2,163 words; updated 2018-11-05, still right) | caching | 2026-11-11 |
| 7 | Fetch standard §4.10 "CORS check", optional, for the curious and for the writer of `cors-verdict` | https://fetch.spec.whatwg.org/#cors-check | reference | CC BY 4.0. Linked | 3 | cors | 2026-11-11 |
| 8 | "HTTP response status codes" (MDN), reference | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status | reference | CC BY-SA 2.5+. Linked | reference only | methods-and-status | 2026-11-11 |

## 7. Practice ladder

The network-lab base (topic 30's D1) plus this topic's layer: a second `RUN` with `nginx python3-websockets` (python3 is in the base; nginx is shared with topic 31's layer if the critic aligns the lines). Machines:

| Machine | Address | Role |
| --- | --- | --- |
| `lab` | 10.0.9.1 | the **origin**: nginx on 80 serving `/srv/www` (index.html, `assets/app.<hash>.js`, `news.html`); proxies `/account` and `/api/` to `shop-app` (Python, 127.0.0.1:8080) and `/board/` to `order-board` (Python websockets, 127.0.0.1:8090). The learner edits `/etc/nginx/sites-available/shop`. |
| `edge` | 10.0.9.10, `edge.shop.test` | a shared cache: a second nginx (`ip netns exec edge nginx -c /etc/lab/edge/nginx.conf`) with `proxy_cache` in front of the origin, adding `X-Cache-Status`. Scenery: the learner doesn't edit it, as with a CDN you don't run. |
| `office` | 10.0.9.2 | customers (`from-office curl …`) |

`shop-app` answers `/account` with the cookie's user name and a timestamp. It answers `/api/basket` (GET, PUT, DELETE) as JSON and sets no CORS headers itself (the origin nginx owns them). `news.html` is rewritten by a timer every 10 seconds with a new version number, so a stale copy can be detected without the check changing anything.

### 7.1 `example-follow-a-cache` (worked example, systemd lab), skills `caching`, `cors`, `api-styles`

Labelled steps:

1. **Through the edge twice:** `from-office curl -sI http://edge.shop.test/assets/app.3f9a.js`, twice. MISS then HIT; read `Cache-Control` and `Age`.
2. **Ask before reusing:** `curl -sI http://edge.shop.test/news.html`, then the conditional request straight to the origin with the `ETag` gives 304. Save the status to `~/example/conditional.txt`.
3. **The personal page:** `curl -s -H 'Cookie: session=alice' …/account`, then as bob. Each sees their own (the origin sends `private`). Read the header.
4. **A preflight by hand:** `curl -si -X OPTIONS -H 'Origin: https://www.shop.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://edge.shop.test/api/basket`. Save the `Access-Control-Allow-Origin` value to `~/example/acao.txt`. Then from `https://evil.test`: no such header.
5. **The upgrade:** `curl -si --max-time 3 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' http://edge.shop.test/board/`. Gives `101` and the RFC's accept value. Save the status line to `~/example/upgrade.txt`.

Checks: the three files hold `304`, `https://www.shop.test` and a line starting `HTTP/1.1 101`. Wrong fixes: `asked-the-edge.sh` (the conditional request sent to the edge without the ETag, saving 200), `evil-origin.sh` (step 4 with the wrong origin, so the file is empty). About 25 minutes.

### 7.2 Recall on methods and status

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-retry-which` | mcq | methods-and-status | A client library retries automatically when a connection drops before the response. For which request is that safe? Right: `PUT /basket/items/42` with the full new quantity. Distractors: `POST /orders`; `POST /payments`; `PATCH /basket` with "add one" (PATCH isn't idempotent by definition). |
| `mcq-idempotency-key` | mcq | methods-and-status | Why do payment APIs ask for an `Idempotency-Key` header on POST? Right: so a retried POST can be recognised and not charged twice. |
| `mcq-502-or-504` | mcq | methods-and-status | nginx in front of an app returns 504 after exactly 60 s on a slow report. Right: nginx's `proxy_read_timeout` (60 s default) ran out waiting for the app; a 502 would mean the app answered badly or closed the connection. |
| `status-classes` | predict_shell | methods-and-status | An access log excerpt (constructed, labelled so). `awk '{print substr($9,1,1)"xx"}' access.log \| sort \| uniq -c` counts the classes. The explanation reads the 5xx as the server's fault and the 4xx as the client's. |
| `conditional-304` | predict_shell | methods-and-status | Two captured `curl -sI` outputs (the first with an ETag; the second, sent with `If-None-Match`, gives 304). `head -n1` on each. |

### 7.3 Recall on caching (calculation skill: four estimates)

| Id | Type | Skill | Scenario and right answer (tolerance; mistakes) |
| --- | --- | --- | --- |
| `cache-control-parse` | predict_shell | caching | Captured headers `Cache-Control: public, max-age=31536000, immutable` and `Age: 120`. `grep -i '^cache-control' h.txt \| grep -o 'max-age=[0-9]*' \| cut -d= -f2` prints `31536000`. |
| `est-fresh-remaining` | estimate | caching | `Cache-Control: max-age=600` and `Age: 420` from the CDN. For how many more seconds is it fresh? Exactly. **180**. Mistakes: 600 (ignores Age), 1020 (adds). |
| `est-heuristic` | estimate | caching | No `Cache-Control` or `Expires`. `Last-Modified` is 10 days before `Date`. With the typical 10% heuristic, for how many hours may a cache treat it as fresh? Exactly. **24**. Mistakes: 240 (100%), 2.4. The 10% is a number to know, so it goes in `working` and not in the prompt. |
| `est-s-maxage` | estimate | caching | `Cache-Control: max-age=60, s-maxage=3600`. For how many seconds may the CDN serve its copy without asking? Exactly. **3600**. Mistake: 60. |
| `est-origin-load` | estimate | caching | An asset with `max-age=300` is requested 10,000 times a minute through 20 CDN locations, each keeping its own copy and refetching when stale. About how many requests reach the origin in an hour? Within 10%. **240** (`20 * 60 / 5`). Mistakes: 600000 (no caching), 12 (one location). |
| `mcq-no-cache-means` | mcq | caching | Right: store it, but check with the origin before every reuse. Distractors: never store it (that's `no-store`); store only in the browser (`private`); cache for zero seconds and then forever. |
| `mcq-account-cache` | mcq | caching | `/account` sent `public, max-age=60`, and bob saw alice's page. Right: the shared cache stored a personal page and served it to the next requester; send `private` (or `no-store`). |
| `mcq-fingerprint` | mcq | caching | Why can `app.3f9a.js` be cached for a year? Right: a new build has a new name, so the old URL's content never changes. |
| `mcq-vary` | mcq | caching | An API answers differently by `Accept-Language`. What must it send so a CDN doesn't mix languages? Right: `Vary: Accept-Language`. |

### 7.4 `fill-cache-policy` (fill-in, systemd lab), skills `caching`

`/etc/nginx/sites-available/shop` with `add_header Cache-Control "...";` gaps in four `location` blocks: `/assets/`, `= /news.html` and `= /index.html`, `/account`, `/api/`. ETags are on by default for static files, and the prompt says so.

Checks (through the edge, from the office):
- `assets-cached`: the second request is `HIT`, with `max-age` at least 31536000 and `immutable`.
- `html-fresh`: fetch `news.html` through the edge, wait 11 s (`timeout: 30` is enough), fetch again: the version number must have changed. It must also send a validator, so a conditional request gives 304.
- `account-private`: alice then bob within 2 s; each body names its own user. The header contains `private` or `no-store`.
- `api-not-stored`: two `GET /api/basket` with different cookies, each its own, and the header contains `no-store`.

Wrong fixes:
- `no-store-everywhere.sh`: fails `assets-cached`.
- `long-cache-html.sh`: `max-age=86400` on HTML, so the version never changes. Fails `html-fresh`.
- `public-account.sh`: fails `account-private`.
- `assets-short.sh`: `max-age=60`. Fails `assets-cached`.

About 25 minutes.

### 7.5 Recall on CORS

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `mcq-preflight-when` | mcq | cors | Which call from `https://www.shop.test` to `https://api.shop.test` makes the browser send OPTIONS first? Right: `PUT` with `Content-Type: application/json`. Distractors: a `GET` with no custom headers; a form `POST` with `application/x-www-form-urlencoded`; a `HEAD`. |
| `mcq-star-credentials` | mcq | cors | The API sends `Access-Control-Allow-Origin: *` and the page calls it with `credentials: "include"`. Right: the browser refuses the response, because with credentials the origin must be named exactly. |
| `mcq-cors-not-auth` | mcq | cors | "We set CORS to our own origin, so nobody else can call our API." Right: CORS only controls which web pages a browser lets read the answers; `curl` or a server ignores it, so the API must still authenticate. |
| `mcq-suffix-regex` | mcq | cors | The allow-list is the regex `shop\.test$` against the Origin's host. Which origin wrongly passes? Right: `https://evilshop.test`. Distractors: `https://shop.test.evil.example` (the `$` stops this one), `https://api.shop.test` (allowed on purpose), `null`. |
| `preflight-read` | predict_shell | cors | The captured preflight answers (tried output, section 4 idea 6). The command prints the `Access-Control-Allow-Origin` line for each origin, or `none`. Output: `https://www.shop.test` and `none`. |
| `est-preflights` | estimate | cors | A page sends a JSON `PUT` to the API every 10 s for an hour. The API sends `Access-Control-Max-Age: 600`; the browser is Chromium. How many preflights? Exactly. **6**. Mistakes: 360 (no caching), 1 (taking Chromium's 7,200 s cap as the lifetime). |
| `mcq-vary-origin` | mcq | cors | Why must an API that echoes an allowed origin also send `Vary: Origin`? Right: otherwise a shared cache may give one origin's CORS answer to another origin's page. |

### 7.6 `write-cors-audit` (write, plain lab), skills `cors`

`~/bin/cors-audit URL ORIGIN METHOD [HEADER] [--credentials]`. It sends the preflight a browser would send for that request, if one is needed: methods outside GET, HEAD and POST, or a header outside the safelist (for this lab, any header other than `Accept`, `Accept-Language`, `Content-Language`, and `Content-Type` with one of the three simple values; the prompt gives this list). It then prints `allowed`, or `blocked: <reason>` with one of a fixed set of reasons:

- `no allow-origin`;
- `origin not allowed`;
- `wildcard with credentials`;
- `credentials not allowed`;
- `method not allowed`;
- `header not allowed`.

The prompt names `curl -si -X OPTIONS`, `grep -i`, `tr -d '\r'`, and case-insensitive header names.

Checks make their own inputs. Each check starts a throwaway Python HTTP server on a random port (in a scratch namespace) whose CORS answers it chooses **at random** from a table of cases:

- exact allow;
- `*`;
- `*` with credentials;
- allow without `Allow-Credentials`;
- missing method;
- missing header;
- a different origin.

Each case uses random origins and method names from a list. The check compares the script's verdict with `cors-verdict` on the same answers. Every run covers all seven cases (seven calls), so no rule goes unchecked by chance. A last check runs it against the lab's real API from two origins.

Wrong fixes:
- `ignores-credentials.sh`: treats `*` as always allowed.
- `case-sensitive.sh`: misses `access-control-allow-origin` in lower case. The throwaway server sends lower-case names in half the cases, always including one per run.
- `no-preflight-check.sh`: says `allowed` whenever the actual GET has ACAO.
- `hard-coded.sh`.

About 35 minutes.

### 7.7 Recall on API styles

| Id | Type | Skill | Scenario and right answer |
| --- | --- | --- | --- |
| `ws-accept-compute` | predict_shell | api-styles | `printf '%s' "$key"258EAFA5-E914-47DA-95CA-C5AB0DC85B11 \| openssl sha1 -binary \| base64` with RFC 6455's example key. Prints `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=`. Git Bash has openssl; confirm the command runs in the validator's bash on Linux and Git Bash. |
| `mcq-board-style` | mcq | api-styles | Staff screens show orders the moment they arrive; screens never send anything back. Right: server-sent events, or WebSockets. Distractors: polling every minute, gRPC unary per order, a cached REST list. Write each as a full claim; the explanation contrasts SSE and WebSockets. |
| `mcq-internal-streaming` | mcq | api-styles | Two internal services exchange a contract-checked stream of stock updates both ways. Right: gRPC bidirectional streaming over HTTP/2. |
| `mcq-browser-grpc` | mcq | api-styles | Why can't a browser page call the gRPC service directly? Right: browser APIs don't give pages control of HTTP/2 framing and trailers, so a gRPC-Web proxy translates. Phrase the right answer from fact 15 only ("needs gRPC-Web and a proxy such as Envoy"); the explanation names trailers (fact 14). |
| `mcq-ws-drops-60s` | mcq | api-styles | The order board's WebSocket drops after exactly a minute of quiet, behind nginx. Right: `proxy_read_timeout` (60 s by default) closes an idle upstream connection; ping more often, or raise the timeout. |
| `mcq-ws-400` | mcq | api-styles | Through nginx the upgrade gets 400; straight to the app it gets 101. Right: nginx isn't passing the hop-by-hop `Upgrade` and `Connection` headers. |
| `est-ping-interval` | estimate | api-styles | Path: ALB idle timeout 60 s, nginx `proxy_read_timeout` 300 s. What is the longest gap between messages (in seconds) the connection survives? Exactly. **60** (`min(60, 300)`). Mistakes: 300, 360. |

### 7.8 Ladder order

`example-follow-a-cache`, `mcq-retry-which`, `mcq-502-or-504`, `status-classes`, `conditional-304`, `cache-control-parse`, `est-fresh-remaining`, `est-heuristic`, `est-s-maxage`, `mcq-no-cache-means`, `mcq-account-cache`, `mcq-fingerprint`, `fill-cache-policy`, `mcq-preflight-when`, `mcq-star-credentials`, `mcq-cors-not-auth`, `mcq-suffix-regex`, `preflight-read`, `est-preflights`, `write-cors-audit`, `ws-accept-compute`, `mcq-board-style`, `mcq-internal-streaming`, `mcq-ws-drops-60s`, `mcq-ws-400`, `est-ping-interval`.

That's 23 quick items (35 minutes), a worked example, a fill-in and a write. Review-only: `mcq-idempotency-key`, `est-origin-load`, `mcq-vary`, `mcq-vary-origin`, `mcq-browser-grpc`.

Practised before proven:

| Skill | Practised in |
| --- | --- |
| caching | the example, 8 items, the fill-in |
| cors | the example, 6 items, the write |
| methods-and-status | 4 items |
| api-styles | the example (upgrade), 6 items |

The build's WebSocket part (upgrade headers and `proxy_read_timeout`) is practised in the example and two items. The writer may add the upgrade lines as a fifth gap to the fill-in, if the cold review finds the build's step too big. Recommended.

## 8. Proofs

### 8.1 Build: `build-shop-edge` (systemd lab, 60 minutes), skills `caching`, `cors`, `api-styles`

The origin's site file is given with the `location` blocks and their `proxy_pass` lines only. Brief:

1. **Caching:** assets for a year and immutable; HTML always revalidated, with validators; `/account` never stored by a shared cache; `/api/` never stored at all.
2. **CORS for `/api/`:** only `https://shop.test` and `https://www.shop.test` may call it from a browser, with credentials, using GET, PUT and DELETE with a JSON body. The browser may cache the preflight for 10 minutes. No other origin may read its answers. A preflight is answered 204 without reaching the app.
3. **The order board** `/board/` works through nginx as a WebSocket and survives five minutes of quiet. The board pings every 30 s; the brief states the path's idle limit as "the load balancer in front drops connections idle for more than 120 s", so the learner needs nginx's limit above 30 s and the ping below 120 s (given).

Checks:

| Id | What it proves |
| --- | --- |
| `assets-cached`, `html-fresh`, `account-private`, `api-not-stored` | as in 7.4 |
| `preflight-allowed` | For each of the two allowed origins: OPTIONS `PUT` with `content-type` and credentials passes `cors-verdict`, gets 204, and `Max-Age` is 600. The app's access log shows no OPTIONS (it never reached the app). |
| `actual-allowed` | The real `PUT` from an allowed origin with a cookie passes the CORS check (ACAO exact, ACAC true). |
| `others-blocked` | Fresh, random origins of five kinds: a random domain, `https://<random>shop.test`, `https://shop.test.<random>.example`, `http://shop.test` (wrong scheme), `null`. Each fails `cors-verdict` on both the preflight and the actual request. |
| `vary-origin` | Answers carrying ACAO also carry `Vary: Origin`. |
| `board-upgrades` | A Python websockets client through the edge: upgrade 101, a message echoed. |
| `board-survives-quiet` | `timeout: 100`. An idle connection with pings switched off on the client for 75 s, then a message: still open. (75 s is past nginx's default 60 s; the five-minute requirement is also read from `nginx -T`: `proxy_read_timeout` at least 300 s in the `/board/` block.) |

Wrong fixes:

1. `wildcard-with-credentials.sh`
2. `reflect-any-origin.sh` (`$http_origin` unconditionally)
3. `suffix-regex.sh` (`~shop\.test$`)
4. `no-vary.sh`
5. `methods-star.sh` (`Access-Control-Allow-Methods: *` with credentials)
6. `preflight-to-app.sh` (OPTIONS passed through to the app, which 405s)
7. `no-store-everywhere.sh`
8. `public-account.sh`
9. `no-upgrade-headers.sh`
10. `default-timeout.sh`
11. `null-allowed.sh`

Timeouts: 100 + 30 + 10 × 30 = 430 s, under 600.

### 8.2 Debug: `debug-stale-and-blocked` (systemd lab, 45 minutes), skills `caching`, `cors`, `api-styles`

**Prompt.** The shop's origin is nginx on `lab`, behind the edge cache (`edge.shop.test`, not yours to change). It serves the storefront, the static assets, the account pages, the basket API (which the storefront at `https://www.shop.test` calls with the customer's cookie, using `PUT` with a JSON body), and the staff order board, a WebSocket at `/board/`.

After Tuesday's deploy:

- customers see yesterday's prices on the storefront for hours;
- the new checkout page on `https://www.shop.test` can't update the basket, and the browser's console says the CORS request was refused (no browser here: use `curl` the way a browser would);
- the order board on the staff screens disconnects after a minute of quiet.

There are three faults. Rules: assets stay cached for a year; account pages and the API are never stored by the edge; the API admits no browser origin beyond `https://shop.test` and `https://www.shop.test`; the edge isn't yours to change.

Faults:
1. `news.html` and `index.html` carry `public, max-age=86400`.
2. The preflight answer's `Access-Control-Allow-Headers` lists `X-Requested-With` but not `Content-Type`, so JSON `PUT`s are refused. A visible symptom with an exact reason under `curl -si -X OPTIONS …`.
3. `/board/` passes the upgrade but sets `proxy_read_timeout 60s` while the board pings every 90 s (the board's ping interval is in `/etc/order-board.conf`, which the prompt names as the board's settings).

The fix may raise nginx's timeout or shorten the ping; both pass if the connection survives 150 s of quiet. That check has `timeout: 200`, the slowest in Module 3. Alternatively, scale it down: board ping 45 s, faulty timeout 30 s, check 75 s, `timeout: 100`. **Recommended: scale down,** stated in the prompt.

Checks:
- `html-fresh`;
- `checkout-preflight` (`PUT` plus `content-type` with credentials from `https://www.shop.test` passes `cors-verdict`);
- `others-blocked` (as in the build, random origins);
- `assets-cached`;
- `account-private`;
- `api-not-stored`;
- `board-survives-quiet`.

Wrong fixes:
- `no-store-everywhere.sh`;
- `cors-wildcard.sh`;
- `reflect-origin.sh`;
- `allow-headers-star-with-credentials.sh`;
- `board-timeout-too-short.sh` (raises `proxy_read_timeout` to 40 s, still under the board's 45 s ping);
- `edge-edited.sh` (a config checksum check);
- one "two of three fixed" variant per fault.

### 8.3 Explain

**Prompt.** "The shop is adding a CDN in front of its site, a partner-facing JavaScript widget that calls the basket API from partners' pages, and a live order board for warehouse staff. Explain, in your own words: which caching headers you'd send for the HTML, the versioned assets, the account pages and the API, and what goes wrong with each if you get it wrong; what CORS protects, what a browser checks before letting a partner's page read the basket, and why CORS doesn't stop anyone calling the API from a script on a server; which methods your API can let clients retry safely, and why; and whether the order board should use REST, WebSockets, server-sent events or gRPC, and what the CDN, the load balancer and nginx must each allow for it to stay connected."

**Rubric:**

| Id | Required | Description |
| --- | --- | --- |
| `cache-policy` | yes | assets: long `max-age` plus `immutable` because the name changes; HTML: `no-cache` with an ETag so a deploy shows at once; account: `private` or `no-store`, or a shared cache shows one customer's page to another; API: `no-store`; `s-maxage` for the CDN where wanted |
| `cors-purpose` | yes | the same-origin policy protects users' data in their browser from other sites; the server lists origins that may read; preflight for non-simple requests; exact origin plus `Allow-Credentials` with cookies; `Vary: Origin`; never reflect or suffix-match |
| `cors-not-auth` | yes | non-browser clients ignore CORS; the API still authenticates and authorises every call |
| `idempotency` | yes | GET, PUT and DELETE are idempotent, so retries are safe; POST isn't; idempotency keys |
| `board-choice` | yes | push to many screens: SSE or WebSockets (justified); every hop must pass the upgrade (for WebSockets) and keep idle connections longer than the ping interval |
| `grpc` | no | for internal service-to-service calls, gRPC over HTTP/2 end to end; browsers need gRPC-Web |

## 9. Review pool

- caching: `est-fresh-remaining`, `est-heuristic`, `est-origin-load`, `mcq-account-cache`, `mcq-no-cache-means`, `mcq-vary`.
- cors: `mcq-star-credentials`, `mcq-suffix-regex`, `est-preflights`, `mcq-vary-origin`, `mcq-cors-not-auth`.
- methods-and-status: `mcq-retry-which`, `mcq-502-or-504`, `mcq-idempotency-key`, `conditional-304`.
- api-styles: `est-ping-interval`, `mcq-ws-drops-60s`, `mcq-board-style`, `mcq-browser-grpc`.

## 10. Platform work needed first

| # | What | Smallest version |
| --- | --- | --- |
| H1 | The network-lab base (topic 30's D1), with machines `lab`, `edge` and `office`, and a way to run a second nginx in the `edge` namespace with its own config and pid file. | `ip netns exec edge nginx -c /etc/lab/edge/nginx.conf -g 'pid /run/edge-nginx.pid;'` as a unit |
| H2 | `cors-verdict`: a check-side helper of about 40 lines of Python implementing Fetch §4.10 and the preflight's method and header checks, with its own small test (a table of headers and verdicts) run by the validator, or by `labcheck test`, before any lab uses it. Keep it in each lab's folder (labs are self-contained) or in a shared location the labs copy, as the base decides. | New. Not yet written; the rules are short and quoted in fact 5. |
| H3 | None in the app. | |

## 11. Cost and time

- **Money:** none.
- **Learner minutes:** lesson 14, reading 47 (MDN caching 22, CORS 18, methods 7) plus about 25 (RFC 6455 10, gRPC 11, nginx 4) = 72; 23 quick items 35; worked example 25; fill-in 25; write 35; build 60; debug 45; explain 20. **Total 331.** Trimming the readings to the caching and CORS sections plus gRPC core concepts (dropping RFC 6455 §1 to the recap) gives 321. See open question 1.
- **Labs and CI:** five labs; image layer small (nginx and python3-websockets, about 15 MB). Contract runs: the example about 1 minute; the fill-in about 2 (one 11 s wait a run); the write about 2; the build about 9 (13 containers; the 75 s quiet check only on the solution and two wrong fixes); the debug about 6. **About 20 minutes for the topic**, 5 minutes of wall time at four jobs.

## 12. Open questions, each with a recommendation

1. **331 minutes.** Over 300, mainly because the spec gives this topic three distinct subjects. Option: move REST-against-WebSockets-against-gRPC to Module 5's distributed systems, or to Module 17's integration topics. **Recommendation: keep them here,** because the spec puts them here and the debug lab's WebSocket fault is a networking fault. Trim the reading as in section 11, and accept about 320.
2. **HTTPS in these labs?** **Recommendation: no.** Plain HTTP inside the lab keeps the image small and the topic on semantics. Origins are still written `https://…`, because CORS compares scheme, host and port, and the lesson says the browser does this over HTTPS in real life.
3. **`cors-verdict`, a model of a browser in the checks.** It applies Fetch's published rules to real server answers and never prints anything in the learner's shell. **Recommendation: yes,** with its own test table, and the lesson says how the checks decide.
4. **Align the nginx `RUN` line with topic 31's,** so the two topics share a layer. **Recommendation: yes;** the critic sets one line for topics 31, 32 and 33 (load balancing will want nginx or HAProxy too).

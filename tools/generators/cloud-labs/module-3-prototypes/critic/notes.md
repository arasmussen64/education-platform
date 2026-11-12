# Critic notes (working file)

## base
- base: VTI fails on DD; IPsec designer says VTI works -> resolve (check lb-ipsec README)
- base frr@M vs frr-common frr@NAME (/etc/frr/NAME, router cmd, lab-link, UTS drop-in). base form wins; base has UTS per machine already, /etc/netns/M/frr.
- R3 (frr-common): "no route whose protocol is boot" -- iproute2 omits protocol for boot unless -d; base says absent. Must check w/o -d => check "protocol missing" or use -d. VERIFY.
- base: no per-machine learner-editable network file; layers N-A asks for one (/etc/netns/M/<file> of ip cmds). base open q5 says don't invent; troubleshooting says nothing needed for t36. layers/cidr/ipv6 need it (faults in pinned ARP, link down, tunnel). DECIDE.
- base: no radvd (FRR RA); ipv6 designer wants radvd. DECIDE.
- base: netlab verify (fresh-build check) proposed by layers.
- transport: /etc/netns/HOST/sysctl.d applied at boot -- base's netlab sets sysctls from topology only. Need persistent learner sysctl home (keepalive in t28 debug: /etc/sysctl.d/99 overrides). 
- dns-http used own network.sh/ns@.service; lb-ipsec own cloud-enter/on-cloud; frr own router/on/lab-link; all must adapt to base.
- tshark: base keeps (125MB); dns-http says no tshark (147MB). 

## layers (t23)
- prereq csa.m1.checkpoint. 6 skills. 321->300 min.
- build: firewall-strict: listeners on r3 & branch from isp. ok. 
- fill-tunnel-up uses per-machine file (N-A) w/ `___` gaps; "apply with sudo systemctl restart netlab" 
- write-why-not: random port states per boot, root-only file; 
- debug d23 prototyped & contract kept.
- est-gre-mtu mistake 1476 has working "1476" fine.
- est-mss-from-mtu: mistake list includes 1500 with no working? check.
- hdr-hex-ttl `${5:0:2}` substring - bash ok.
- explain prompt ok.
- MCQ lengths: check mcq-icmp-related right ans long?

## cidr (t24) 
- prereq layers. 5 skills, 15 est. 295 min. bash $(( )) "in code". plain labs need python3 (P-4) -> start from base layer1.
- debug-new-warehouse NOT built (contract not run). needs per-machine network file (N-A) + plan.txt.
- F8 Google peering & F9 AWS default VPC unconfirmed -> I verify.
- est-binary-octet contrived given (ones:4); fine-ish. est-smallest-prefix working "32 - 9" ok.
- validator P-1 dotted quad reading: small validator change.
- build: AWS web 254 x2 +5=513 -> /22. ok.

## ipv6 (t25)
- prereq cidr. 5 skills. 308->300.
- needs radvd (base has FRR RA instead!), per-machine sysctl file (debug fault 2), web-svc test server, DAD override.
- debug d25 prototyped, contract kept, restart ok.
- Azure IPv6 egress translated: spec line change.
- mcq-azure-ipv6 right answer claim: verify F21/F22.
- mcq-rs-ra-order: shuffled-line MCQ, ok.

## routing (t26)
- prereq cidr. 5 skills. 297/295. 21 recall, 5 labs, 27 wrong.
- R3 bug everywhere (protocol boot w/o -d).
- debug fault 2: default via 198.51.100.254 (on-link /24, nonexistent) "FRR doesn't install it" -- likely FALSE: on-link nexthop resolves via connected route -> installed; ARP FAILED. VERIFY w/ docker.
- review-only est-loop-crossings-ttl128 wording ambiguous ("any loop link").
- sysctl: never taught in M1/M2 (grep: 0 hits). routing must define sysctl, ip_forward, rp_filter, /etc/sysctl.d (NAT brief wrongly says M1 taught /etc/sysctl.d).
- write-next-hop awk; accept bash or awk; point to cidr recap.
- uses router/lab-link (frr-common) -> base: `on r1 vtysh`, base needs link cut helper (lab-link) -> add to base as `netlab link`? 
- mcq-distance-255 relies on FRR doc conflict; prototype F7 confirmed. ok.

## nat (t27)
- prereq routing, ipv6. 5 skills, 9 est. 293/290. 
- claims M1 hardening taught /etc/sysctl.d -> FALSE.
- gateway in main namespace -> conflicts w/ base (lab machine on no lab net). DECIDE: machine `gw` with nftables@gw + per-machine sysctl.d (new base feature, /etc/netns/gw/sysctl.d overlay; netlab applies net.* keys only; NOT sysctl --system which touches global keys).
- DEBUG INCONSISTENT: fault 2 "masquerade without oifname" would also translate office traffic -> fault 3 (stale office prefix) invisible. Fix: fault 2 = `iifname "wan" masquerade` (in/out confusion) or similar that hits inbound only.
- holdconns/holdserver -> base.
- AWS NAT Ohio price verify. 
- build check forwarding-lasts reads sysctl.d order -> adapt to gw machine files.

## transport (t28)
- prereq nat. 5 skills (3 calc). 300 min. MCQ measured (right longest 3/14).
- uses `lab` main ns as app server + on-nat/on-db wrappers + own network.sh; /etc/sysctl.d in main ns -> must become machine `app` (base) w/ per-machine sysctl.d; shop-api stand-in runs as unit via `ip netns exec app lab-enter app ...`.
- fast clock (10-20 s timers) fine.
- write-syn-check hidden pairs need 3 untried nft option rewrites.
- teaches sysctl if routing doesn't -> routing does (decide).
- CI spike: netem, reset tcp option window.
- transport `sysctl --system` inside netns: applies /usr/lib/sysctl.d global keys -> danger to Docker VM. Base must apply only machine's files, net.* keys.

## congestion (t29)
- prereq transport. 5 skills. 305/300. MCQ measured 3/13.
- `lab` main ns = Caddy server + sender -> machine `shop`; needs caddy@M unit, topic layer caddy+python3-aioquic+ngtcp2-client (63MB), h3get, wan-set (-> base `netlab netem` console?).
- HTTP/3 split w/ t31: t29 owns QUIC + HTTP/3 discovery/fallback + lab; t31 owns versions semantics + TLS. CHECK http-tls brief overlap (it has Caddy/gtlsclient HTTP/3 too).
- thresholds 25 Mbit/s CI unverified -> spike.
- debug: BBR on dr, udp 4433, protocols h1 h2. ok.

## dns (t30)
- prereq transport. 5 skills. 318 (323 w/ step 8). Keep one topic, trim to ~305.
- MODULE 3 depends on m1 only (outline prereq csa.m1.checkpoint); m2's windows-ad DNS terms can't be assumed (dns brief correct; ipv6 brief WRONG to lean on windows-ad for DNS/record/AAAA; base brief cites windows-ad for resolver/zone; transport brief says m2.checkpoint gate WRONG).
- uses own ns@ units, /var/lib/lab/dns, `lab` as resolver host -> adapt to base named@M, unbound@M, /etc/netns/M/bind; resolver machine. base proto-services already proved hierarchy.
- est-forgot-to-lower: fetched 08:59 -> exact 3.983; reword "just before the change".
- debug & build not built end to end (move-watch, broken.test, allow-transfer story).
- tshark: dns-http says no; base keeps.

## http-tls (t31)
- prereq dns, congestion. 5 skills. 332. designer recommends split -> csa.net.http-tls (http-versions, tls-handshake ~170) + csa.net.certificates (cert-chains, acme, mtls ~230).
- DUPLICATES congestion's HTTP/3: idea 2 (discovery/fallback/clouds), example step 2 (Caddy), alt-svc-parse, mcq-h3-udp-blocked, mcq-when-h3-helps (same id!), est-h3-saving (== congestion est-rtt-saved, same 150 ms!). Remove from t31; drop caddy+ngtcp2 from t31 layer.
- step-ca from GitHub .deb pinned sha256 (first non-archive download). 
- versions check (TLS1.1 refusal) untried; client-eku-missing untried; faketime expired cert untried; REQUESTS_CA_BUNDLE drop-in untried.
- verify: RFC 9846 TLS1.3 (Jul 2026), RFC 9849 ECH (Mar 2026), BR 200/100/47 days, LE OCSP end 2025-08-06.
- DECISION split: yes (clean seam; tls-handshake gets own proofs; certs half fully designed). New t31 build/debug to specify (nginx SNI two sites, TLS1.2+1.3, h2, stapling w/ local OCSP responder?) -> check tls prototype for OCSP responder.

## http-semantics (t32)
- prereq http-tls (after split: still csa.net.http-tls; certificates not needed - plain HTTP labs). 4 skills. 331->321. Keep; trim reading (RFC6455 to recap) & move 2 items to review -> ~315.
- `lab` main ns = origin nginx; edge 2nd nginx; -> base machines origin/edge with nginx@M (base has nginx@).
- cors-verdict helper (check-side) w/ own tests -> base checklib? store in content/lab-bases/net/ (shared) - decide.
- nginx already in base layer 2; topic layer just python3-websockets.
- debug scale-down WS (45 s ping/30 s timeout) recommended -> accept.
- MDN licence CC BY-SA 2.5 verify.

## load-balancing (t33)
- prereq http-semantics, nat. 5 skills. 337->315 (designer trims). keep one topic.
- `lab` main ns = HAProxy + br0 + from-office -> base machine `lb` with haproxy@lb; shop-web@ machine units.
- hiccup fast-503 untested; worker-start-vs-file check untested; stock-sync, API backend untested.
- solid. 29 wrong fixes; CI ~28 min one shard (high) -> trim? debug 60-s window needed.

## ipsec (t35 -> 37)
- prereq layers, nat, http-tls, bgp. 5 skills. 318->310.
- VTI works end-to-end in IPsec proto (lab main ns, single initiator, disable_policy, install_routes=no). base says VTI fails (both in netns; its earlier trap-on-both-sides issue -> duplicate SAs? ). CRITIC TEST: base proto switched to VTI.
- `lab` main ns = VPN gw w/ default frr.service -> base machine `vpn` w/ frr@vpn, strongswan@vpn; vti0 lasting home = per-machine /etc/network/up (N-A).
- cloud-enter/on-cloud -> base `on cloud`; cloud-vpn-status/log helpers = `on cloud swanctl --list-sas` / journalctl -u strongswan@cloud (read-only?) -> provider views as helper scripts.
- facts to verify: AWS VGW ASN 64512, MTU 1446/1406, Azure 65515/4000 prefixes/60-180 timers.
- ECP-384 untested.

## CRITIC PROBES (done)
- VTI: works between base machines once strongSwan `forecast` plugin not loaded (base's libstrongswan-extra-plugins pulls it). Root cause found. -> VTI for ipsec & checkpoint part 3; GRE-in-IPsec dropped to fallback. Restart needs keyingtries=0 + ordering. RESULT.md written.
- iproute2: `ip -j route` w/o -d omits protocol for hand-made (boot) routes; -d shows "boot". frr-common R3 wording wrong -> use `ip -d -j route`, reject protocol boot.
- FRR static via on-link nonexistent nexthop: shown resolved "via dummy0" (not inactive) -> routing debug fault 2 claim "FRR doesn't install it" likely false; evidence is FAILED neighbour.

## bgp (t34->35) + bgp-steering (->36)
- split accepted (365 -> 285 + 295). bgp prereq routing; steering prereq bgp.
- adapt router/looking-glass/lab-link/bgp-best to base (`on edge vtysh`, base frr helper; add `netlab link` + `looking-glass` + `bgp-best` helpers to base checklib/bin).
- paths /etc/frr/edge/frr.conf -> inside-machine /etc/frr/frr.conf.
- steering: estimates verified arithmetically ok. AWS facts to verify (private VIF 100, communities, hold 90).
- routing debug & checkpoint might overlap w/ bgp debug? check.

## troubleshooting (t36->38)
- prereq load-balancing, ipsec. 6 skills. 320->300 (trim a). method topic, good.
- example fault (stale more-specific static) resembles routing debug fault 3 (stale blackhole /17) -> example is practice, ok, but say so.
- casebook uses other topics' debug faults as recorded cases (retrieval after the fact) ok.
- debug-branch-api checks not run; netem CI.
- estimates verified.
- base pattern for machine-level custom units (ip netns exec M lab-enter M PROG) -> base README.

## checkpoint
- 3 parts (plan / outage v2 / cloud link). 240 min. accept part 3 (spec change). part 3 -> VTI (critic decided) not GRE.
- part 2 fault 1 (serial not bumped, unsigned primary) is cousin of DNS debug fault 1 (stale secondary via allow-transfer) - same symptom, different cause; acceptable but note.
- part 2 fault 2 ECMP filter: ECMP practiced only in t36 (mcq-another-port, ports-and-paths) + routing lesson para -> ok; add routing recall item on ECMP? (routing has none) -> add 1 recall item in routing.
- part 3 overlaps bgp-steering build (circuits+VPN backup) + ipsec build -> acceptable combo, different story/numbers, prepend not communities.
- v2 contract w/ redesigned checks not run; restart not tried v2; part 3 not prototyped.
- verify test_skills ids: csa.linux.shell/navigate?

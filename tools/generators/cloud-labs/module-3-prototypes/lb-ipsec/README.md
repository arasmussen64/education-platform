# Prototypes for topics 33 (load balancing) and 35 (IPsec)

Run on 2026-11-11 (evening; container clocks read 2026-11-12 UTC) on the owner's PC: Docker Desktop 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2, cgroup v2. Every container and image made here carried the label `m3design=lb-ipsec` and was removed at the end (see the last section). Containers were started the way `tools/labcheck.py` starts a systemd lab: `docker run -d --hostname lab --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock IMAGE /sbin/init` (in Git Bash, with `MSYS_NO_PATHCONV=1`, or Git Bash rewrites `/run`).

## Folders

- `ipsec/`: a route-based IPsec tunnel (strongSwan 5.9.13, VTI) with BGP over it (FRR 8.4.4) between the lab machine and a "cloud" namespace, through an "internet" namespace, with an "office" namespace behind the lab. `solution.sh` is the build's reference shape. `try-fault.sh` re-initiates with one change and prints both sides' logs. `log-*.txt` are the captured outputs (real, from this run).
- `lb/`: HAProxy 2.8.30 in front of three web servers (`web1` to `web3`, namespaces on a bridge) and a database stand-in (`db`), with an office namespace as the client. `log-*.txt` are captured outputs.
- `downloads/`: the HAProxy 2.8 manuals (configuration, management, starter guide) and RFCs 7296, 4303, 4555, fetched to read and grep. Untrusted data; nothing in it is run.

## Exact images and packages

Both start `FROM ubuntu:24.04` (image `fe81560990fa`, two weeks old on the day) with the shared systemd first `RUN` line copied unchanged from Module 1's labs (153 MB layer).

| Lab | Second `RUN` (the topic layer) | Layer | Image | Build (base layer cached) |
| --- | --- | --- | --- | --- |
| IPsec | `strongswan-swanctl charon-systemd libstrongswan-standard-plugins frr` (5.9.13-2ubuntu4.24.04.5; 8.4.4-1.1ubuntu6.8) | 27.6 MB | 361 MB | 17 to 23 s |
| Load balancing | `haproxy socat` (2.8.30-0ubuntu0.24.04.2; 1.8.0.0-4ubuntu0.1) | 6.3 MB | 334 MB | 18 s |

Other candidates checked in the same archive: nginx 1.24.0, keepalived 2.2.8, ipvsadm 1.31, wireguard-tools 1.0.20210914.

## What the kernel had to give

Docker Desktop's kernel config (`/proc/config.gz`), read from a privileged container:

- `CONFIG_XFRM_USER=m`, `CONFIG_INET_ESP=m`, `CONFIG_NET_IPVTI=m`, `CONFIG_CRYPTO_GCM=y`, `CONFIG_CRYPTO_AES=y`, `CONFIG_IP_VS=m`, `CONFIG_NET_SCH_NETEM=m`, `CONFIG_WIREGUARD=m`, `CONFIG_NETFILTER_XT_TARGET_TCPMSS=y`.
- **`CONFIG_XFRM_INTERFACE` is not set.** XFRM interfaces (`ip link add ... type xfrm`) fail with `Error: Unknown device type.` VTI works.
- Modules load on demand from a privileged container: creating a VTI loaded `ip_vti` and `tunnel4`; adding an ESP state loaded `esp4`; `ip link add wg0 type wireguard` worked too. `/lib/modules` doesn't exist inside the container; the kernel asks Docker Desktop's own machine.
- Side effect: once `ip_vti` (and `ip6_vti`) are loaded, every new network namespace on that Docker machine gets fallback devices `ip_vti0` and `ip6_vti0` (seen in fresh, unrelated containers afterwards, beside `gre0`, `sit0`, `tunl0`, `ip6tnl0` that something else had loaded). They stay until Docker Desktop restarts. Checks must never assume the full list of interfaces in a namespace.

GitHub's `ubuntu-24.04` runner (image 20261101.360.1, kernel 7.0.0-1017-azure, read from actions/runner-images on 2026-11-11): the package `linux-modules-7.0.0-1017-azure` (not the -extra one) lists `esp4.ko.zst`, `ip_vti.ko.zst`, `tunnel4.ko.zst`, `xfrm_user.ko.zst`, `xfrm_algo.ko.zst`, `xfrm_interface.ko.zst`, `ip_vs.ko.zst`, `sch_netem.ko.zst` (packages.ubuntu.com file list, read 2026-11-11). Not tried on a runner: whether a privileged container there loads them on demand as Docker Desktop does. The first pull request with an IPsec lab is the test.

## IPsec: commands and timings

Topology (made at boot by `network.sh`):

```
office 192.168.10.10 -- lan0 192.168.10.1 [lab] eth1 198.51.100.10 -- 198.51.100.1 [internet] 203.0.113.1 -- 203.0.113.10 [cloud] vpc0 10.20.1.10/16
                                          vti0 169.254.21.2/30  ======= ESP =======  vti0 169.254.21.1/30
```

The cloud's strongSwan runs in the cloud namespace and a mount namespace of its own (`cloud-enter` binds `/srv/cloud/swanctl` over `/etc/swanctl` and `/srv/cloud/strongswan.conf` over `/etc/strongswan.conf`; its vici socket is `/run/cloud/charon.vici`, and `swanctl.socket` in that strongswan.conf points `swanctl` at it), the pattern of Module 2's `dc-enter`. Its FRR is FRR's own pathspace feature: `/etc/frr/cloud/daemons` with `watchfrr_options="--netns"`, started by `/usr/lib/frr/frrinit.sh start cloud`, queried with `vtysh -N cloud`. A Python `http.server` on 10.20.1.10:80 serves `index.html` and a 303,030-byte `report.txt`.

| Step | Result |
| --- | --- |
| Boot to `running` | 3 s; cloud's charon, FRR and app up |
| `solution.sh` as the learner, until `10.20.0.0/16` is in the kernel by BGP | 7 to 8 s |
| `swanctl --list-sas` | `AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048`, CHILD `ESP:AES_GCM_16-256`, TS `0.0.0.0/0 === 0.0.0.0/0`, IKE on port 4500 (MOBIKE floats to 4500 with no NAT; ESP stays plain protocol 50, seen in `tcpdump`) |
| Office to the cloud app | `curl` gets the page and the 303,030-byte report |
| Restart trial (`docker restart`) | booted in 6 to 7 s; BGP route back 11 s after the restart command |
| The cloud gateway restarted (`systemctl restart lab-cloud`) | app reachable again after 4 to 6 s, **with** `close_action = start`; **not back within 45 s** without it (tried with and without `dpd_action = restart`) |
| A prefix advertised from the cloud at check time | in the lab's kernel by BGP after 0.3 s; a 172.16.x.0/24 and 0.0.0.0/0 advertised with it were dropped by the lab's in-filter; withdrawal removed it |
| CHILD_SA rekey started from the cloud | new CHILD shows `ESP:AES_GCM_16-256/MODP_2048` (the PFS group is visible only after a rekey) |

Found on the way (each becomes teaching):

1. **The first restart trial failed.** The lab's charon started before the cloud's had loaded its connection, got `NO_PROPOSAL_CHOSEN`, and with `keyingtries` at its default of 1 never tried again. Fixed by ordering the scenery (`Before=strongswan.service frr.service` on the cloud's units) and by `keyingtries = 0` in the solution. strongSwan retries timeouts with `keyingtries = 0`, not "permanent errors" such as `NO_PROPOSAL_CHOSEN` (swanctl.conf reference).
2. `charon.install_routes = no` is needed for a VTI with `0.0.0.0/0` selectors (strongSwan's route-based page says so); the lab ships it in `/etc/strongswan.d/charon-lab.conf` as scenery.
3. `swanctl` prints 13 "plugin ... failed to load" lines on Ubuntu 24.04 unless `/etc/strongswan.d/swanctl.conf` names the plugins it loads (`load = pem pkcs1 pkcs8 x509 revocation constraints pubkey openssl random`). Ship that file.
4. After the tunnel is torn down and rebuilt, FRR's BGP waited for its connect-retry timer (120 s default) before reconnecting; in the run where it happened the session sat in `Active` for about two minutes (1 min 39 s when first read, then 25 s more) before the route came back. The cloud's scenery should say `neighbor ... timers connect 10`.
5. With `local_ts = 192.168.10.0/24` and `remote_ts = 10.20.0.0/16` on the lab, the cloud (configured `0.0.0.0/0`) **narrowed** to those selectors and the tunnel came up; BGP between 169.254.21.1 and .2 never established (`Active`), because those addresses aren't in the selectors, so no routes, so nothing works. A tunnel that is "up" while nothing passes.
6. A PFS mismatch (lab `esp_proposals = aes256gcm16`, cloud `aes256gcm16-modp2048`) **establishes** (the first CHILD_SA takes its keys from IKE_AUTH and negotiates no DH group) and fails at the first rekey: `CHILD_SA rekeying failed, trying again in 14 seconds`. With default lifetimes the tunnel would die about 66 minutes after it came up.
7. MTU: with the internet namespace's links at 1400 and its outgoing ICMP "destination unreachable" dropped, `index.html` loaded and `report.txt` stalled at 0 bytes (outer ESP headers carry DF, copied from TCP). MSS clamping on the lab fixed it, both directions needed:

| Clamp on the lab's forward chain | 303,030-byte download | 400,000-byte upload |
| --- | --- | --- |
| none | 0 bytes (hangs) | 0 bytes (hangs) |
| `oifname "vti0" tcp flags syn tcp option maxseg size set 1300` | complete | 0 bytes |
| that, plus the same with `iifname "vti0"` | complete | complete |
| both, but `set 1460` | 0 bytes | 0 bytes |

Captured logs, both sides, in `ipsec/log-*.txt`: IKE proposal mismatch, wrong PSK, wrong identity, ESP proposal mismatch, narrowed selectors, `TS_UNACCEPTABLE` (cloud configured with specific selectors), UDP 4500 dropped on the path, PFS failure at rekey, MTU, the cloud restart variants, the BGP probe, the BGP summary. From the lab's side a wrong PSK and a wrong identity look the same (`received AUTHENTICATION_FAILED notify error`); only the responder's log tells them apart (`tried 1 shared key ... but MAC mismatched` against `no matching peer config found`).

## Load balancing: commands and timings

Topology: `office` 10.0.9.2 -- `eth1` 10.0.9.1 [lab, HAProxy] `br0` 10.0.1.1 -- `web1` .11, `web2` .12, `web3` .13 (each `shop-web` on 8080 in its own namespace, a systemd template unit with `NetworkNamespacePath=/run/netns/%i`), `db` .20 (`shop-db` on 5432). `shop-web` serves `/` (needs nothing), `/orders` (needs the database), `/health` (deep: 200 only if the database answers), `/livez` (shallow), `/slow?s=N`; `FLAKY=N` in `/etc/shop/<name>.env` makes every Nth `/livez` take 1.5 s. HAProxy logs to `/dev/log` with the `chroot` line removed, and `journalctl -u haproxy` shows both its log lines and its warnings. The learner is in group `haproxy`, so `socat stdio /run/haproxy/admin.sock` works without `sudo`.

| Step | Result |
| --- | --- |
| Boot | 4 s; round robin across three servers at once |
| Deep check (`option httpchk GET /health`, `inter 2s fall 3 rise 2`), then `systemctl stop shop-db` | all three DOWN after 6 s; the front page, which needs no database, answered `503` "No server is available to handle this request."; log: `Server web/web3 is DOWN, reason: Layer7 wrong status, code: 503` then `backend 'web' has no server available!` |
| `/livez` with `timeout check 1s`, web2 `FLAKY=4`, `inter 1s fall 1 rise 1`, 30 s of traffic | web2 marked DOWN 6 times (`chkdown`), served 69 of 260 requests |
| the same with `inter 2s fall 3 rise 2` / `inter 1s fall 2 rise 2` | 0 flaps; 87 of 261 / 88 of 263 |
| web3 frozen (`kill -STOP`), `inter 2s fall 3`, `timeout check 1s` | DOWN after 8.6 s |
| Cookie stickiness (`cookie SHOPSRV insert indirect nocache`) | one visitor 6 of 6 requests on one server |
| `set server web/web1 state drain` during an 8-second download pinned to web1 | the download completed (200, all bytes); new visitors went to web2 and web3; the sticky visitor stayed on web1 (status `DRAIN`, `scur` 1) |
| `set server web/web1 state maint` | the sticky visitor moved to other servers |
| `systemctl reload haproxy` | web1 back to `UP`: state set through the runtime API doesn't survive a reload |
| Restart trial | boot 5 s, `haproxy` enabled, config kept, all UP |

Two claims tested and dropped: HAProxy 2.8 **accepts** `use_backend api if { path_beg /api }` in a `mode tcp` frontend (`Configuration file is valid`), so the lesson must not say "HAProxy can't read paths in TCP mode"; and a server-speaks-first protocol behind a `mode http` proxy gives the client nothing (it timed out waiting for the banner), which is the clean lab demonstration of choosing layer 4.

`show stat` fields used by checks (0-based in the manual, so `awk -F,` columns are one more): `status` $18, `chkfail` $22, `chkdown` $23 (UP to DOWN transitions), `lastchg` $24, `scur` $5, `stot` $8.

## Clean-up

Removed: containers `m3lbipsec-ipsec`, `m3lbipsec-lb` and the short-lived `m3lbipsec-kcheck*`/`-pkg` ones (run with `--rm`); images `m3proto-ipsec:dev`, `m3proto-lb:dev`. No networks were created. Left behind, and not removable without a prune (not run): BuildKit's cache of the two topic layers (about 34 MB), and the kernel modules the tests loaded into Docker Desktop's machine (`ip_vti`, `ip6_vti`, `tunnel4`, `esp4`, `wireguard`), which go when Docker Desktop restarts.

# FRR prototypes for Module 3 (topics 26, 27, 34)

Scratch prototypes behind `../../csa.net.routing.md`, `csa.net.nat.md`, `csa.net.bgp.md`, `csa.net.bgp-steering.md` and `frr-labs-common.md`. Not lab content: no checks.yaml, no wrong fixes. They prove the mechanisms and give the timings.

| Folder | What it is | Image |
| --- | --- | --- |
| `base/` | `ubuntu:24.04`, Module 1's shared systemd layer byte for byte, then `frr frr-pythontools` from Ubuntu (8.4.4-1.1ubuntu6.8) | `frrproto-base:ubuntu`, 355 MB, FRR layer 24 MB, 10.5 s to build |
| `bgp/` | edge (AS 65001) dual-homed to ispa (65010) and ispb (65020), both to cloud (65100); office and web hosts; one FRR instance per network namespace (`frr@NAME`) | `frrproto-bgp` |
| `routing/` | three sites in a triangle of routers r1, r2, r3, static routes in FRR's staticd | `frrproto-routing` |
| `circuits/` | edge (65001) and cloud (64512) over two links dx1, dx2; the cloud honours AWS-style local-preference communities | `frrproto-circuits` |
| `rr/` | AS 65001 with r1, r2, r3 (r2 becomes a route reflector), cloud 64512 | `frrproto-rr` |
| `nat/` | office and app behind gw (a namespace here), the "internet" with srv and client; `holdconns` and `holdserver` helpers | `frrproto-nat` |
| `timeit.sh` | starts a container the way `tools/labcheck.py` does for a systemd lab and times boot and BGP convergence | |
| `CAPTURES.md` | real output captured from these prototypes, for recall items | |
| `docs/` | downloaded documentation pages used to check facts (not for publishing) | |

Run as `labcheck` would: `docker run -d --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock IMAGE /sbin/init` (Git Bash needs `MSYS_NO_PATHCONV=1`).

All containers and images made here were removed at the end of the design session; rebuild with `docker build -t frrproto-base:ubuntu base/` first, then the others.

# Plan: Cloud Solutions Architect, Module 3

The writing plan for Module 3, "Networking", made on 2026-11-11 before any of it was written. Seven designers each briefed part of the module (one of them the shared lab base every network lab starts from), researching and checking their facts and resources and trying their labs in Docker; a critic then checked the briefs against each other, the house rules and their sources, ran the disputed experiments again, and wrote one plan.

**Start with [MODULE-3-BRIEF.md](MODULE-3-BRIEF.md).** It decides; the designers' briefs hold the detail. Where they disagree, the brief wins.

| File | What it is |
| --- | --- |
| [MODULE-3-BRIEF.md](MODULE-3-BRIEF.md) | The final plan: sixteen topics and their order, the network-lab base in its final form, each topic's changes to its designer's brief, Checkpoint 3, the platform work, the writing waves, CI time, decisions for the owner queue, what to look up again, and the replacement text for the spec |
| [CRITIQUE.md](CRITIQUE.md) | Every problem the critic found in the briefs and what was done about it, the facts and resources re-checked, and what is still unverified |
| [network-lab-base.md](network-lab-base.md) | The shared base: machines as network namespaces built by `netlab` from a topology file, per-machine services, the `labcheck` change, what works in Docker Desktop's kernel |
| [frr-labs-common.md](frr-labs-common.md) | What the routing, NAT and BGP labs share: findings from their prototypes, check recipes, rules for writers (its R3 is corrected in the brief, section 3.5) |
| `csa.net.*.md`, `csa.m3.checkpoint.md` | The designers' briefs, one per topic. `csa.net.bgp-steering.md` is the second half of the spec's BGP topic; `csa.net.http-tls.md` also covers the new `csa.net.certificates`, which the plan split out |
| `prototypes/` | What the designers and the critic ran: `network-lab-base/` (the base and two labs that keep their contracts under the real `labcheck`), `layers-cidr-ipv6/` (two debug labs with contracts and restart trials, the CIDR write lab's generator), `frr/` (routing, NAT and BGP mechanisms and captured output), `transport-congestion/` (idle cuts, windows, CUBIC against BBR, QUIC), `dns-http/` (BIND, Unbound, DNSSEC, nginx, step-ca, captures), `lb-ipsec/` (HAProxy behaviours, a VTI tunnel with BGP and eight captured IKE failures), `troubleshooting-checkpoint/` (the checkpoint's plan checker and outage networks), `critic/` (the VTI experiment that settled the base, and the critic's working notes) |

The prototypes are in [`tools/generators/cloud-labs/module-3-prototypes/`](../../../tools/generators/cloud-labs/module-3-prototypes/); the plan's `prototypes/…` paths mean that folder. They are an archive, like the rest of that folder: nothing runs them in CI, and a lab is only real once it is written under `content/topics/` and passes `tools/labcheck.py test`. Left out on the way in: the scratch downloads (fetched RFCs and web pages), files over 150 KB, and the two prototypes' full copies of `tools/labcheck.py` and `tools/content_model.py` (the change to `labcheck` is kept as `network-lab-base/labcheck-shared-base.diff`).

**This is a plan, not the source of truth.** Once a topic is written, its files under `content/topics/` are what counts. Prices, limits, product names and package versions in these files were true on the dates they give and must be checked again when a topic is written (the brief's section 11).

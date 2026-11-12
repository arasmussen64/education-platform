#!/usr/bin/python3
"""plancheck CHECK [PLAN] [REQUIREMENTS-DIR]: one check of an address plan.

Prototype of the checker for Checkpoint 3, part 1. Prints "ok" or one
sentence saying what is wrong, and always exits 0 (the lab checker compares
the output). Works everything out from the requirements (sites.csv and
policy.txt), so a plan copied from another story fails.
"""

import csv
import ipaddress
import math
import sys

CHECK = sys.argv[1]
PLAN = sys.argv[2] if len(sys.argv) > 2 else "/home/learner/plan/plan.csv"
REQ = sys.argv[3] if len(sys.argv) > 3 else "/srv/plan"


def say(text):
    print(text)
    sys.exit(0)


def read_policy():
    policy, in_use = {}, []
    for line in open(f"{REQ}/policy.txt", encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        if key == "in_use":
            block, label = value.split(None, 1)
            in_use.append((ipaddress.ip_network(block), label))
        else:
            policy[key] = value
    return policy, in_use


def read_sites():
    with open(f"{REQ}/sites.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


policy, in_use = read_policy()
sites = read_sites()
clouds = sorted({s["cloud"] for s in sites if s["kind"] == "region"})
regions = [s for s in sites if s["kind"] == "region"]
dcs = [s for s in sites if s["kind"] == "dc"]
summaries = clouds + ["onprem"]
names = []
for c in clouds:
    names.append(c)
    names += [s["site"] for s in regions if s["cloud"] == c]
names.append("onprem")
names += [s["site"] for s in dcs]
dc_v4 = {label: block for block, label in in_use if label in {d["site"] for d in dcs}}


def pow2_at_least(n):
    return 1 << math.ceil(math.log2(n))


def need_v4(site):
    """Addresses a region's block must hold in five years."""
    hosts = int(site["hosts_per_subnet_today"]) * int(policy["host_growth"])
    subnet = pow2_at_least(hosts + int(policy[f"reserved_{site['cloud']}"]))
    return pow2_at_least(int(site["subnets_today"]) * int(policy["subnet_growth"]) * subnet)


def read_plan():
    rows = {}
    try:
        lines = [ln for ln in open(PLAN, encoding="utf-8") if ln.strip() and not ln.lstrip().startswith("#")]
    except OSError:
        say("there is no plan at ~/plan/plan.csv")
    reader = csv.reader([ln.replace("\r", "") for ln in lines])
    header = [h.strip() for h in next(reader, [])]
    if header != ["name", "ipv4", "ipv6"]:
        say("the plan's first line is not the header name,ipv4,ipv6")
    for row in reader:
        row = [c.strip() for c in row] + ["", ""]
        if row[0] in rows:
            say(f"the plan has two rows for {row[0]}")
        rows[row[0]] = (row[1], row[2])
    return rows


def parse(text, family, where):
    """A block, None for "-", or BAD. Only the complete check reports a
    cell it can't read; the others skip it, so one mistyped block fails one
    check and not all of them."""
    if text == "-":
        return None
    if CHECK != "complete":
        try:
            net = ipaddress.ip_network(text, strict=True)
            return net if net.version == family else BAD
        except ValueError:
            return BAD
    try:
        net = ipaddress.ip_network(text, strict=True)
    except ValueError:
        try:
            ipaddress.ip_network(text, strict=False)
        except ValueError:
            say(f"{where}: [{text}] is not an address block")
        say(f"{where}: [{text}] is not written as its network address")
    if net.version != family:
        say(f"{where}: [{text}] is not an IPv{family} block")
    return net


BAD = "bad"


def plan_nets():
    rows = read_plan()
    for n in names:
        if n not in rows:
            say(f"the plan has no row for {n}")
    extra = set(rows) - set(names)
    if extra:
        say(f"the plan has a row the requirements don't name: {sorted(extra)[0]}")
    v4 = {n: parse(rows[n][0], 4, f"{n}'s IPv4") for n in names}
    v6 = {n: parse(rows[n][1], 6, f"{n}'s IPv6") for n in names}
    if CHECK != "complete":
        # The complete check reports what can't be read; here it is skipped.
        v4 = {n: (None if b is BAD else b) for n, b in v4.items()}
        v6 = {n: (None if b is BAD else b) for n, b in v6.items()}
    return v4, v6


v4, v6 = plan_nets()
space4 = ipaddress.ip_network(policy["ipv4_space"])
space6 = ipaddress.ip_network(policy["ipv6_space"])
gcp_pool = ipaddress.ip_network(policy["ipv6_gcp_pool"])

if CHECK == "complete":
    for n in names:
        if v4[n] is None:
            say(f"{n} has no IPv4 block")
        gcp_region = any(s["site"] == n and s["cloud"] == "gcp" for s in regions)
        if gcp_region and v6[n] is not None:
            say(f"{n}'s IPv6 is chosen by Google Cloud, so the plan leaves it as -")
        if not gcp_region and v6[n] is None:
            say(f"{n} has no IPv6 block")
    say("ok")


def both(a, b):
    return a is not None and b is not None


if CHECK == "v4-sizes":
    for s in regions:
        b = v4[s["site"]]
        if b is not None and b.num_addresses != need_v4(s):
            say(f"{s['site']}'s IPv4 block isn't the smallest that holds its five-year need")
    say("ok")

if CHECK == "v4-dcs":
    for d in dcs:
        if v4[d["site"]] != dc_v4[d["site"]]:
            say(f"{d['site']} doesn't keep the addresses it has")
    blocks = [dc_v4[d["site"]] for d in dcs]
    on = v4["onprem"]
    if on is None or not all(b.subnet_of(on) for b in blocks):
        say("onprem doesn't hold both data centers")
    if any(all(b.subnet_of(h) for b in blocks) for h in on.subnets(prefixlen_diff=1)):
        say("onprem isn't the smallest block that holds both data centers")
    say("ok")

if CHECK == "v4-apart":
    sites_all = [s["site"] for s in sites]
    for n in sites_all + summaries:
        if v4[n] is not None and not v4[n].subnet_of(space4):
            say(f"{n}'s IPv4 block is outside the shop's space, {space4}")
    for i, a in enumerate(sites_all):
        for b in sites_all[i + 1:]:
            if both(v4[a], v4[b]) and v4[a].overlaps(v4[b]):
                say(f"{a} and {b} overlap")
    for s in regions:
        for block, label in in_use:
            if v4[s["site"]] is not None and v4[s["site"]].overlaps(block):
                say(f"{s['site']} overlaps addresses already in use ({label})")
    for i, a in enumerate(summaries):
        for b in summaries[i + 1:]:
            if both(v4[a], v4[b]) and v4[a].overlaps(v4[b]):
                say(f"the summaries {a} and {b} overlap")
    for c in clouds:
        for block, label in in_use:
            if v4[c] is not None and v4[c].overlaps(block):
                say(f"the summary {c} overlaps addresses already in use ({label})")
    say("ok")

if CHECK == "v4-summaries":
    for c in clouds:
        if v4[c] is None:
            say(f"the summary {c} has no IPv4 block to check")
        mine = [s for s in regions if s["cloud"] == c]
        for s in mine:
            if v4[s["site"]] is not None and not v4[s["site"]].subnet_of(v4[c]):
                say(f"{s['site']} is outside its cloud's summary, {c}")
        want = pow2_at_least(sum(need_v4(s) for s in mine) * int(policy["summary_room"]))
        if v4[c].num_addresses != want:
            say(f"the summary {c} isn't the smallest block with the room for growth the policy asks for")
    say("ok")

if CHECK == "v6-sizes":
    for n in names:
        if v6[n] is not None and v6[n].prefixlen % 4:
            say(f"{n}'s IPv6 block doesn't end on a nibble boundary")
    for s in regions + dcs:
        b = v6[s["site"]]
        if b is not None and b.prefixlen != int(policy["ipv6_region"]):
            say(f"{s['site']}'s IPv6 block isn't the size the policy gives a site")
    for c in summaries:
        if c != "gcp" and v6[c] is not None and v6[c].prefixlen != int(policy["ipv6_summary"]):
            say(f"the summary {c}'s IPv6 block isn't the size the policy gives a summary")
    if "gcp" in clouds and v6["gcp"] is not None and v6["gcp"].prefixlen != int(policy["ipv6_gcp_network"]):
        say("gcp's IPv6 network isn't the size Google Cloud gives a network")
    say("ok")

if CHECK == "v6-apart":
    own = [c for c in summaries if c != "gcp"]
    for c in own:
        if v6[c] is not None and not v6[c].subnet_of(space6):
            say(f"the summary {c}'s IPv6 block is outside the shop's IPv6 space, {space6}")
    for i, a in enumerate(own):
        for b in own[i + 1:]:
            if both(v6[a], v6[b]) and v6[a].overlaps(v6[b]):
                say(f"the IPv6 summaries {a} and {b} overlap")
    for s in regions + dcs:
        mine, parent = v6[s["site"]], v6[s["cloud"]]
        if both(mine, parent) and not mine.subnet_of(parent):
            say(f"{s['site']}'s IPv6 block is outside its summary, {s['cloud']}")
    six = [s["site"] for s in regions + dcs if v6[s["site"]] is not None]
    for i, a in enumerate(six):
        for b in six[i + 1:]:
            if v6[a].overlaps(v6[b]):
                say(f"the IPv6 blocks of {a} and {b} overlap")
    if "gcp" in clouds and v6["gcp"] is not None and not v6["gcp"].subnet_of(gcp_pool):
        say(f"gcp's IPv6 network isn't one Google Cloud can give it (inside {gcp_pool})")
    say("ok")

say(f"plancheck: no check called {CHECK}")

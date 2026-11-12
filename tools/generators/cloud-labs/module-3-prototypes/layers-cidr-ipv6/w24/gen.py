"""Check-side generator for write-cidr-overlaps (prototype).

Makes a plan of named IPv4 blocks with every case the script must get
right present every time (so no wrong script can pass by luck), with
random numbers inside each case, writes it, and prints the expected
output. Usage: python3 gen.py SEED PLANFILE > expected
"""
import ipaddress
import random
import sys

seed, path = int(sys.argv[1]), sys.argv[2]
rnd = random.Random(seed)
blocks = []  # (name, network)


def net(addr_int, prefix):
    return ipaddress.ip_network((addr_int, prefix), strict=False)


def fresh_base():
    # a random /16 inside 10.0.0.0/8 or 172.16.0.0/12, used once per case
    while True:
        a = rnd.choice([(10 << 24) | (rnd.randrange(256) << 16),
                        (172 << 24) | ((16 + rnd.randrange(16)) << 16)])
        if all(not net(a, 16).overlaps(n) for _, n in blocks):
            return a


names = iter(f"{w}-{i}" for i, w in enumerate(rnd.sample(
    ["web", "app", "db", "cache", "queue", "mgmt", "vpn", "lab", "dmz", "batch",
     "edge", "data", "logs", "dev", "test", "prod", "ops", "hr"], 18)))
cases = []
# 1. outer then inner (nested, the big one first), crossing an octet boundary
b = fresh_base(); p = rnd.choice([19, 20, 21])
outer = net(b | (rnd.randrange(4) << 13), p)
inner = net(int(outer.network_address) + (rnd.randrange(1, 2 ** (32 - p) // 256) << 8), 24)
cases.append([outer, inner])
# 2. inner then outer (nested, the small one first)
b = fresh_base(); p = rnd.choice([22, 23])
outer = net(b | (rnd.randrange(16) << 10), p)
inner = net(int(outer.network_address) + rnd.randrange(1, 2 ** (32 - p) // 32) * 32, 27)  # never the first /27
cases.append([inner, outer])
# 3. identical blocks written differently (host bits set in one)
b = fresh_base(); p = rnd.choice([24, 25, 26])
a = net(b | (rnd.randrange(256) << 8), p)
cases.append([a, ipaddress.ip_network(f"{a.network_address + rnd.randrange(1, a.num_addresses)}/{p}", strict=False)])
# 4. adjacent blocks that touch but don't overlap (both orders across the file)
b = fresh_base(); p = rnd.choice([25, 26, 27])
x = net(b | (rnd.randrange(256) << 8), p - 1)
lo, hi = list(x.subnets(new_prefix=p))[:2]
cases.append([hi, lo])
# 5. a /32 inside a block, and a /32 just outside it
b = fresh_base(); p = rnd.choice([28, 29])
blk = net(b | (rnd.randrange(256) << 8) | (rnd.randrange(8) << 5), p)
cases.append([blk, net(int(blk.network_address) + rnd.randrange(blk.num_addresses), 32),
              net(int(blk.broadcast_address) + 1, 32)])
# 6. same first three octets, different blocks (string-compare trap)
b = fresh_base(); c = b | (rnd.randrange(256) << 8)
cases.append([net(c, 26), net(c + 128, 26)])
# 7. far apart
cases.append([net(fresh_base(), 16), net(fresh_base() | (rnd.randrange(256) << 8), 24)])

flat = [n for case in cases for n in case]
rnd.shuffle(flat)
# Each nested pair keeps the order its case gives (big-then-small for
# case 1, small-then-big for case 2), wherever the shuffle put them, so a
# script that only looks one way round always fails one of the two.
for first, second in (cases[0], cases[1]):
    i, j = flat.index(first), flat.index(second)
    if i > j:
        flat[i], flat[j] = flat[j], flat[i]
plan = []
for n in flat:
    shown = str(n)
    if n == blk or (n.prefixlen <= 30 and rnd.random() < 0.3):
        shown = f"{n.network_address + 1}/{n.prefixlen}"  # host bits set: still that block
    plan.append((next(names), shown, n))
with open(path, "w") as f:
    f.write("# name  block\n")
    for name, shown, _ in plan:
        f.write(f"{name} {shown}\n")
for i in range(len(plan)):
    for j in range(i + 1, len(plan)):
        if plan[i][2].overlaps(plan[j][2]):
            print(plan[i][0], plan[j][0])

#!/bin/bash
# lab (sender) eth1 10.0.5.1 -- [wan: a0 10.0.5.2 | b0 10.0.6.2] -- dr (receiver) eth0 10.0.6.20
# Usage: wan.sh RATE DELAY_EACH_WAY LOSS LIMIT_PKTS
set -u
RATE=${1:-50mbit}; DELAY=${2:-25ms}; LOSS=${3:-0%}; LIMIT=${4:-1000}
ip netns add wan 2>/dev/null; ip netns add dr 2>/dev/null
ip link add eth1 type veth peer name a0 netns wan
ip -n wan link add b0 type veth peer name eth0 netns dr
ip addr add 10.0.5.1/24 dev eth1; ip link set eth1 up
ip route add 10.0.6.0/24 via 10.0.5.2
ip -n wan addr add 10.0.5.2/24 dev a0; ip -n wan link set a0 up
ip -n wan addr add 10.0.6.2/24 dev b0; ip -n wan link set b0 up
ip -n wan link set lo up
ip netns exec wan sysctl -qw net.ipv4.ip_forward=1
ip -n dr addr add 10.0.6.20/24 dev eth0; ip -n dr link set eth0 up; ip -n dr link set lo up
ip -n dr route add default via 10.0.6.2
# the WAN: towards dr (data): rate + delay + loss; back towards lab (acks): delay only
ip netns exec wan tc qdisc add dev b0 root netem rate $RATE delay $DELAY loss $LOSS limit $LIMIT
ip netns exec wan tc qdisc add dev a0 root netem delay $DELAY limit $LIMIT
# keep offloads from making giant packets that distort netem's rate
for d in eth1; do ethtool -K $d tso off gso off gro off >/dev/null 2>&1 || true; done

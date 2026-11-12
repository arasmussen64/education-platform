#!/bin/bash
# The lab's network, made at boot (scenery).
#   lab  eth1 10.0.1.10 --- nat (in0 10.0.1.1 | out0 10.0.2.1, masquerade, 30 s idle timeout) --- db eth0 10.0.2.20
#   lab  eth2 10.0.5.1  --- wan (a0 10.0.5.2 | b0 10.0.6.2, netem)                          --- dr eth0 10.0.6.20
set -euo pipefail
ip netns add nat; ip netns add db; ip netns add wan; ip netns add dr
ip link add eth1 type veth peer name in0 netns nat
ip -n nat link add out0 type veth peer name eth0 netns db
ip addr add 10.0.1.10/24 dev eth1; ip link set eth1 up
ip route add 10.0.2.0/24 via 10.0.1.1
ip -n nat addr add 10.0.1.1/24 dev in0; ip -n nat link set in0 up
ip -n nat addr add 10.0.2.1/24 dev out0; ip -n nat link set out0 up; ip -n nat link set lo up
ip -n db addr add 10.0.2.20/24 dev eth0; ip -n db link set eth0 up; ip -n db link set lo up
ip -n db route add default via 10.0.2.1
ip netns exec nat sysctl -qw net.ipv4.ip_forward=1
ip netns exec nat nft -f /usr/local/lib/lab/gateway.nft
ip netns exec nat sysctl -qw net.netfilter.nf_conntrack_tcp_timeout_established=30
ip link add eth2 type veth peer name a0 netns wan
ip -n wan link add b0 type veth peer name eth0 netns dr
ip addr add 10.0.5.1/24 dev eth2; ip link set eth2 up
ip route add 10.0.6.0/24 via 10.0.5.2
ip -n wan addr add 10.0.5.2/24 dev a0; ip -n wan link set a0 up
ip -n wan addr add 10.0.6.2/24 dev b0; ip -n wan link set b0 up; ip -n wan link set lo up
ip netns exec wan sysctl -qw net.ipv4.ip_forward=1
ip -n dr addr add 10.0.6.20/24 dev eth0; ip -n dr link set eth0 up; ip -n dr link set lo up
ip -n dr route add default via 10.0.6.2
ip netns exec wan tc qdisc add dev b0 root netem rate 50mbit delay 25ms loss 1% limit 2000
ip netns exec wan tc qdisc add dev a0 root netem delay 25ms limit 2000

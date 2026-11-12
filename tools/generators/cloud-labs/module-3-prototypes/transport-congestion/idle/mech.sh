#!/bin/bash
# Mechanism test: lab -> nat (masquerade, short conntrack timeout) -> db
set -u
ip netns add nat; ip netns add db
ip link add eth1 type veth peer name in0 netns nat
ip -n nat link add out0 type veth peer name eth0 netns db
ip addr add 10.0.1.10/24 dev eth1; ip link set eth1 up
ip route add 10.0.2.0/24 via 10.0.1.1
ip -n nat addr add 10.0.1.1/24 dev in0; ip -n nat link set in0 up
ip -n nat addr add 10.0.2.1/24 dev out0; ip -n nat link set out0 up
ip -n nat link set lo up
ip -n db addr add 10.0.2.20/24 dev eth0; ip -n db link set eth0 up; ip -n db link set lo up
ip -n db route add default via 10.0.2.1
ip netns exec nat sysctl -qw net.ipv4.ip_forward=1
ip netns exec nat sysctl -qw net.netfilter.nf_conntrack_tcp_timeout_established=30 2>&1 || echo "sysctl before conntrack loaded failed"
MODE=${1:-reset}
if [ "$MODE" = reset ]; then VERDICT="reject with tcp reset"; else VERDICT="drop"; fi
ip netns exec nat nft -f - <<NFT
table inet gateway {
  chain forward {
    type filter hook forward priority filter; policy drop;
    ct state established,related accept
    iifname "in0" tcp flags & (syn|ack) == syn ct state new accept
    iifname "in0" meta l4proto tcp $VERDICT
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname "out0" masquerade
  }
}
NFT
ip netns exec nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established
ip netns exec nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established=30
ip netns exec nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established
sysctl net.netfilter.nf_conntrack_tcp_timeout_established

#!/bin/bash
# The lab's network, made at boot (prototype).
#   office (192.168.10.10) -- lan0 [lab] eth1 198.51.100.10 -- [internet] -- 203.0.113.10 [cloud] vpc0 10.20.1.10/16
set -euo pipefail
for ns in office internet cloud; do ip netns add $ns; ip -n $ns link set lo up; done
# office <-> lab
ip link add lan0 type veth peer name eth0 netns office
ip addr add 192.168.10.1/24 dev lan0; ip link set lan0 up
ip -n office addr add 192.168.10.10/24 dev eth0; ip -n office link set eth0 up
ip -n office route add default via 192.168.10.1
# lab <-> internet
ip link add eth1 type veth peer name eth0 netns internet
ip addr add 198.51.100.10/24 dev eth1; ip link set eth1 up
ip -n internet addr add 198.51.100.1/24 dev eth0; ip -n internet link set eth0 up
# internet <-> cloud
ip -n internet link add eth1 type veth peer name eth0 netns cloud
ip -n internet addr add 203.0.113.1/24 dev eth1; ip -n internet link set eth1 up
ip -n cloud addr add 203.0.113.10/24 dev eth0; ip -n cloud link set eth0 up
ip -n cloud route add default via 203.0.113.1
ip netns exec internet sysctl -qw net.ipv4.ip_forward=1
# the lab reaches the cloud's VPN endpoint through its ISP
ip route add 203.0.113.0/24 via 198.51.100.1 dev eth1
sysctl -qw net.ipv4.ip_forward=1
# the cloud's network behind its gateway
ip -n cloud link add vpc0 type dummy
ip -n cloud addr add 10.20.1.10/16 dev vpc0; ip -n cloud link set vpc0 up
# the cloud's end of the tunnel (scenery)
ip -n cloud link add vti0 type vti local 203.0.113.10 remote 198.51.100.10 key 7
ip -n cloud addr add 169.254.21.1/30 dev vti0
ip -n cloud link set vti0 up mtu 1436
ip netns exec cloud sysctl -qw net.ipv4.conf.vti0.disable_policy=1
ip netns exec cloud sysctl -qw net.ipv4.ip_forward=1

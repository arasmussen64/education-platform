#!/bin/bash
# The lab's network, made at boot. Part of the lab's scenery: on a real
# server the cloud provides the network and the name server.
#
# 1. The office: a network namespace, the mechanism containers use for
#    their own interfaces and ports, joined to this machine by a veth pair,
#    a virtual cable with eth1 at this end and the office's eth0 at the
#    other. From the office, this machine is 10.0.9.1; the office is
#    10.0.9.2. "from-office COMMAND" runs a command there.
# 2. Names: this machine runs the shop's name server (dnsmasq). It answers
#    for shop.internal and friends, forwards what it doesn't know to the
#    resolver the container came with, and both this machine and the
#    office ask it.
set -euo pipefail

ip netns add office
ip link add eth1 type veth peer name eth0 netns office
ip addr add 10.0.9.1/24 dev eth1
ip link set eth1 up
ip -n office addr add 10.0.9.2/24 dev eth0
ip -n office link set eth0 up
ip -n office link set lo up
ip -n office route add default via 10.0.9.1

upstream=/etc/dnsmasq.d/upstream.conf
if [ ! -f "$upstream" ]; then
  awk '/^nameserver/ {print "server=" $2}' /etc/resolv.conf > "$upstream"
fi
# The container's resolv.conf is a file Docker mounts over /etc/resolv.conf;
# the lab's machine asks its own name server instead.
umount /etc/resolv.conf 2>/dev/null || true
echo "nameserver 127.0.0.1" > /etc/resolv.conf

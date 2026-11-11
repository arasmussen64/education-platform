#!/bin/bash
# The lab's network, made at boot. Part of the lab's scenery: in a cloud the
# provider makes the network and hands out a resolver.
#
#   lab  (this machine)            eth1 10.0.9.1
#   dc1  (the domain controller)   eth0 10.0.9.10, on the far side of eth1
#
# dc1 is a set of namespaces (network, hostname, mounts), the mechanism a
# container is made of; "on-dc COMMAND" runs a command there.
#
# Names: this machine runs the site's ordinary resolver (dnsmasq), the kind
# every network comes with. It knows nothing about the domain. The domain's
# own DNS is on dc1, as it is on every Active Directory domain controller.
set -euo pipefail

ip netns add dc
ip link add eth1 type veth peer name eth0 netns dc
ip addr add 10.0.9.1/24 dev eth1
ip link set eth1 up
ip -n dc addr add 10.0.9.10/24 dev eth0
ip -n dc link set eth0 up
ip -n dc link set lo up
ip -n dc route add default via 10.0.9.1

upstream=/etc/dnsmasq.d/upstream.conf
if [ ! -f "$upstream" ]; then
  awk '/^nameserver/ {print "server=" $2}' /etc/resolv.conf > "$upstream"
fi
# Docker mounts its own files over /etc/resolv.conf and /etc/hosts; the lab
# machine gets its own. A domain member needs a full name (lab.ad.shop.test),
# because Kerberos tickets are issued for names.
umount /etc/resolv.conf 2>/dev/null || true
echo "nameserver 127.0.0.1" > /etc/resolv.conf
umount /etc/hosts 2>/dev/null || true
printf '127.0.0.1 localhost\n10.0.9.1 lab.ad.shop.test lab\n' > /etc/hosts

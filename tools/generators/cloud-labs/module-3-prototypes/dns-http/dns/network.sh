#!/bin/bash
# lab (this machine) 10.0.9.1 on bridge br0; machines in namespaces:
# root 10.0.9.11 (a.root-servers.test), tld 10.0.9.12 (ns1.nic.test),
# ns1 10.0.9.13, ns2 10.0.9.14 (shop.test), cafe 10.0.9.20 (a public resolver)
set -euo pipefail
ip link add br0 type bridge
ip addr add 10.0.9.1/24 dev br0
ip link set br0 up
for pair in root:11 tld:12 ns1:13 ns2:14 cafe:20; do
  m=${pair%%:*}; n=${pair##*:}
  ip netns add $m
  ip link add v-$m type veth peer name eth0 netns $m
  ip link set v-$m master br0 up
  ip -n $m addr add 10.0.9.$n/24 dev eth0
  ip -n $m link set eth0 up
  ip -n $m link set lo up
  ip -n $m route add default via 10.0.9.1
  mkdir -p /etc/netns/$m
  echo "nameserver 10.0.9.1" > /etc/netns/$m/resolv.conf
done
umount /etc/resolv.conf 2>/dev/null || true
echo "nameserver 127.0.0.1" > /etc/resolv.conf

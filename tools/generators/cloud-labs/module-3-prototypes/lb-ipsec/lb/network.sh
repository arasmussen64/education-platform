#!/bin/bash
# office (10.0.9.2) -- eth1 [lab 10.0.9.1 | br0 10.0.1.1] -- web1 .11, web2 .12, web3 .13, db .20
set -euo pipefail
ip netns add office
ip link add eth1 type veth peer name eth0 netns office
ip addr add 10.0.9.1/24 dev eth1; ip link set eth1 up
ip -n office addr add 10.0.9.2/24 dev eth0; ip -n office link set eth0 up; ip -n office link set lo up
ip -n office route add default via 10.0.9.1
ip link add br0 type bridge; ip addr add 10.0.1.1/24 dev br0; ip link set br0 up
n=0
for host in web1:11 web2:12 web3:13 db:20; do
  name=${host%:*}; last=${host#*:}
  ip netns add $name
  ip link add v-$name type veth peer name eth0 netns $name
  ip link set v-$name master br0 up
  ip -n $name addr add 10.0.1.$last/24 dev eth0
  ip -n $name link set eth0 up; ip -n $name link set lo up
  ip -n $name route add default via 10.0.1.1
done

#!/bin/bash
# The lab's second machine, made at boot. Part of the lab's scenery: on a
# real server the network is simply there.
#
# The office: a network namespace, the mechanism containers use for their
# own interfaces and ports, joined to this machine by a veth pair, a
# virtual cable with eth1 at this end and the office's eth0 at the other.
# From the office, this machine is 10.0.9.1; the office is 10.0.9.2.
# "from-office COMMAND" runs a command there, so the firewall can be
# tested from outside.
set -euo pipefail

ip netns add office
ip link add eth1 type veth peer name eth0 netns office
ip addr add 10.0.9.1/24 dev eth1
ip link set eth1 up
ip -n office addr add 10.0.9.2/24 dev eth0
ip -n office link set eth0 up
ip -n office link set lo up
ip -n office route add default via 10.0.9.1

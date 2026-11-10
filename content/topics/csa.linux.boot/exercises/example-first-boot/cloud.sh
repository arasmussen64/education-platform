#!/bin/bash
# The cloud around the lab machine, at boot. Part of the lab's scenery: the
# metadata service's address, which on a real instance the cloud answers
# from outside the machine, is given to loopback here so lab-imds can answer
# at it; the first instance's identity is written where lab-imds and the
# NoCloud seed both read it; and the name cloud-init will give the machine
# is put in /etc/hosts, as a cloud image's hosts file has it, so nothing
# waits on a name lookup that can't succeed.
set -euo pipefail
ip addr add 169.254.169.254/32 dev lo 2>/dev/null || true
mkdir -p /etc/lab
[ -f /etc/lab/instance-id ] || echo "i-0a1b2c3d4e5f60001" > /etc/lab/instance-id
[ -f /etc/lab/imds.conf ] || printf 'tokens=optional\n' > /etc/lab/imds.conf
grep -q 'shop-1' /etc/hosts || echo "127.0.1.1 shop-1" >> /etc/hosts

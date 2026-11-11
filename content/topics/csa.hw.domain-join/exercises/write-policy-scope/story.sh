#!/bin/bash
# The story so far, made once at the lab's first boot, after dc1 is up: a
# fourth person, frank, in the default CN=Users container with the others.
# Part of the scenery.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
on_dc() { ip netns exec dc unshare --uts --mount --propagation private /usr/local/lib/lab/dc-enter "$@"; }
mkdir -p /var/lib/lab

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

on_dc samba-tool user create frank 'Frank-Pass-1' --given-name=Frank --surname=Lund > /dev/null
on_dc samba-tool user setexpiry frank --noexpiry > /dev/null
touch /var/lib/lab/story-done

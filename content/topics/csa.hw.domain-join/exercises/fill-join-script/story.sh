#!/bin/bash
# The story so far, made once at the lab's first boot, after dc1 is up: the
# site's resolver already sends the domain's names, and its reverse zone, to
# dc1, the way the last topic's walkthrough left it. lab isn't joined. Part
# of the scenery.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
mkdir -p /var/lib/lab

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
touch /var/lib/lab/story-done

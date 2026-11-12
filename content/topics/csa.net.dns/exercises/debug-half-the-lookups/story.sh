#!/bin/bash
# The story so far, made once at the lab's first boot, after the name
# servers are up. Part of the scenery; reading it spoils the exercise.
# ns2 had its copy of shop.test. Then ns1's settings were rewritten with
# ns2's old address, and the API moved to its new server.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
mkdir -p /var/lib/lab
serial() { on office dig +norecurse +time=1 +tries=1 +short @"$1" shop.test SOA | awk '{print $3}'; }
signed() { on office dig +norecurse +time=1 +tries=1 +short @"$1" shop.test DNSKEY | grep '^257 ' > /dev/null; }

# Wait until ns2 has ns1's signed copy of shop.test, and it has stayed the
# same for three seconds (ns1 signs the zone in steps at its first start).
steady=0
for _ in $(seq 1 90); do
  s1=$(serial 198.51.100.13)
  s2=$(serial 198.51.100.14)
  if [ -n "$s1" ] && [ "$s1" = "$s2" ] && signed 198.51.100.13 && signed 198.51.100.14; then
    steady=$((steady + 1))
    if [ "$steady" -ge 3 ]; then break; fi
  else
    steady=0
  fi
  sleep 1
done

# Fault 1: ns1 lets only ns2's old address, 198.51.100.24, copy the zone.
# The new settings are in force once ns2's own address is refused.
sed -i 's/198\.51\.100\.14; }/198.51.100.24; }/' /etc/netns/ns1/bind/named.conf.local
on ns1 rndc reconfig > /dev/null
for _ in $(seq 1 30); do
  if on ns2 dig +time=1 +tries=1 @198.51.100.13 shop.test AXFR | grep 'Transfer failed' > /dev/null; then break; fi
  sleep 1
done
# The API moves to its new server: ns1 has the change, ns2 can't fetch it.
sed -i -e 's/^api .*/api   60 IN A     203.0.113.51/' -e 's/2026111201/2026111202/' /etc/netns/ns1/bind/db.shop.test
on ns1 rndc reload shop.test > /dev/null
touch /var/lib/lab/story-done

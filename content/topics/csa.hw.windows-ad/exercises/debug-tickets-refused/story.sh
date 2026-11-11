#!/bin/bash
# The story so far, made once at the lab's first boot, after dc1 is up. Part
# of the scenery; reading it spoils the exercise. For months the nightly
# report worked. Then three things changed, one after another.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
on_dc() { ip netns exec dc unshare --uts --mount --propagation private /usr/local/lib/lab/dc-enter "$@"; }
mkdir -p /var/lib/lab /srv/reports

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

# The working state: the domain's zones forwarded, the shop's groups, and
# the report's service account with its keytab.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
on_dc samba-tool user create dave 'Dave-Pass-1' --given-name=Dave --surname=Okafor > /dev/null
on_dc samba-tool user create erin 'Erin-Pass-1' --given-name=Erin --surname=Moss > /dev/null
on_dc samba-tool group add stock-team > /dev/null
on_dc samba-tool group addmembers stock-team bob,dave,erin > /dev/null
on_dc samba-tool group add night-shift > /dev/null
on_dc samba-tool group addmembers night-shift carol,dave > /dev/null
on_dc samba-tool user create svc-report 'Svc-Report-Pass-1' --description='The nightly directory report' > /dev/null
for user in dave erin svc-report; do on_dc samba-tool user setexpiry "$user" --noexpiry > /dev/null; done
on_dc samba-tool domain exportkeytab /etc/svc-report.keytab --principal=svc-report > /dev/null
chmod 600 /etc/svc-report.keytab
# What the checks compare with: the keytab as it was handed over.
sha256sum /etc/svc-report.keytab | cut -d' ' -f1 > /var/lib/lab/keytab.sha256
chmod 600 /var/lib/lab/keytab.sha256
systemctl start directory-report.service

# Fault 1: someone rewrote the forwarder file and kept only the domain's
# own zone, so 10.0.9.10 has no name on this machine.
printf 'server=/ad.shop.test/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
# Fault 2: the service account was disabled on dc1 in a clean-up.
on_dc samba-tool user disable svc-report > /dev/null
# Fault 3: the report's settings were retyped, with the realm in lower case.
sed -i 's/^REALM=.*/REALM=ad.shop.test/' /etc/directory-report.conf

# The nightly run since then.
systemctl start directory-report.service || true
touch /var/lib/lab/story-done

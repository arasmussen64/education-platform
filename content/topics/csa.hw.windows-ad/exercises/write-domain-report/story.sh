#!/bin/bash
# The story so far, made once at the lab's first boot, after dc1 is up. Part
# of the scenery: the shop's names are already forwarded to dc1, the
# warehouse has people and a group, and the reporting service account,
# svc-report, has a keytab on this machine. A second, older copy of its
# keytab, from before its password was changed, is kept for the checks.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
on_dc() { ip netns exec dc unshare --uts --mount --propagation private /usr/local/lib/lab/dc-enter "$@"; }
mkdir -p /var/lib/lab

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

# The site's resolver sends the domain's names, and its reverse zone, to dc1.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq

# The warehouse's people and their group.
on_dc samba-tool user create dave 'Dave-Pass-1' --given-name=Dave --surname=Okafor > /dev/null
on_dc samba-tool user create erin 'Erin-Pass-1' --given-name=Erin --surname=Moss > /dev/null
on_dc samba-tool group add stock-team > /dev/null
on_dc samba-tool group addmembers stock-team bob,dave,erin > /dev/null

# The service account, and its keytab: the account's keys in a file, so a
# program can sign in as it with no one typing a password. The first copy
# goes stale when the password changes.
on_dc samba-tool user create svc-report 'Svc-Report-Pass-1' --description='The nightly directory report' > /dev/null
for user in dave erin svc-report; do on_dc samba-tool user setexpiry "$user" --noexpiry > /dev/null; done
on_dc samba-tool domain exportkeytab /var/lib/lab/stale.keytab --principal=svc-report > /dev/null
on_dc samba-tool user setpassword svc-report --newpassword='Svc-Report-Pass-2' > /dev/null 2>&1
on_dc samba-tool domain exportkeytab /etc/svc-report.keytab --principal=svc-report > /dev/null
chown root:learner /etc/svc-report.keytab /var/lib/lab/stale.keytab
chmod 640 /etc/svc-report.keytab /var/lib/lab/stale.keytab

touch /var/lib/lab/story-done

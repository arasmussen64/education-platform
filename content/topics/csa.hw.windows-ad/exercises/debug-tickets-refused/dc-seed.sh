#!/bin/bash
# The domain's people, once dc1 is up: two users, one group, and a reverse
# DNS zone so 10.0.9.10 has a name.
set -euo pipefail
[ -e /var/lib/samba/.seeded ] && exit 0
samba-tool user create alice 'Alice-Pass-1' --given-name=Alice --surname=Ng > /dev/null
samba-tool user create bob 'Bob-Pass-1' --given-name=Bob --surname=Ito > /dev/null
samba-tool group add linux-admins > /dev/null
samba-tool user create carol 'Carol-Pass-1' --given-name=Carol --surname=Diaz > /dev/null
samba-tool group addmembers linux-admins alice,carol > /dev/null
samba-tool user setexpiry carol --noexpiry > /dev/null
# Passwords in a lab never expire, so the lab works next year too.
samba-tool user setexpiry alice --noexpiry > /dev/null
samba-tool user setexpiry bob --noexpiry > /dev/null
samba-tool user setexpiry Administrator --noexpiry > /dev/null
for try in $(seq 1 30); do
  samba-tool dns zonecreate dc1 9.0.10.in-addr.arpa -U Administrator --password='Shop-Admin-1' > /dev/null 2>&1 && break
  sleep 1
done
samba-tool dns add dc1 9.0.10.in-addr.arpa 10 PTR dc1.ad.shop.test -U Administrator --password='Shop-Admin-1' > /dev/null 2>&1
touch /var/lib/samba/.seeded

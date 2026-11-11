#!/bin/bash
# Creates the domain ad.shop.test on dc1, once, at the lab's first boot.
# (It can't be done while the image is built: Samba stores Windows
# permissions on the SYSVOL share in a way that needs the privileges a
# running lab has and a build doesn't.)
set -euo pipefail
[ -e /var/lib/samba/private/sam.ldb ] && exit 0
rm -f /etc/samba/smb.conf
samba-tool domain provision --realm=AD.SHOP.TEST --domain=SHOP \
  --server-role=dc --dns-backend=SAMBA_INTERNAL \
  --adminpass='Shop-Admin-1' --host-name=dc1 --host-ip=10.0.9.10 \
  --option='dns forwarder = 10.0.9.1' \
  --option='interfaces = lo eth0' --option='bind interfaces only = yes' \
  > /var/log/samba/provision.log 2>&1

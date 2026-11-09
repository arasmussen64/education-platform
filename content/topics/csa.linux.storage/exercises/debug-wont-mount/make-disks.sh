#!/bin/bash
# The lab's disks, made at image build: three data volumes with fixed
# UUIDs (ext4, XFS, ext4), two mount points that exist and one that
# doesn't, and an fstab with three mistakes: a UUID with one digit wrong,
# the wrong filesystem type, and a mount point that was never created.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab /srv/shop /srv/backups

seed=$(mktemp -d)
echo "the shop's data lives here" > "$seed/README"
truncate -s 200M /var/lib/lab/data1.img
mkfs.ext4 -q -U 11111111-1111-4111-8111-111111111111 -d "$seed" /var/lib/lab/data1.img
rm -rf "$seed"

truncate -s 400M /var/lib/lab/data2.img
mkfs.xfs -q -m uuid=22222222-2222-4222-8222-222222222222 /var/lib/lab/data2.img

truncate -s 200M /var/lib/lab/data3.img
mkfs.ext4 -q -U 33333333-3333-4333-8333-333333333333 /var/lib/lab/data3.img

printf 'data1 -\ndata2 -\ndata3 -\n' > /etc/lab/disks.conf

# x-systemd.device-timeout keeps systemd from waiting a minute and a half
# at boot for a volume it can't see yet; the mistakes are the UUID, the
# type and the missing folder.
cat >> /etc/fstab <<'EOF'
# The shop's data volumes
UUID=11111111-1111-4111-8111-111111111112 /srv/shop ext4 defaults,nofail,x-systemd.device-timeout=5 0 2
UUID=22222222-2222-4222-8222-222222222222 /srv/backups ext4 defaults,nofail,x-systemd.device-timeout=5 0 2
UUID=33333333-3333-4333-8333-333333333333 /srv/archive ext4 defaults,nofail,x-systemd.device-timeout=5 0 2
EOF

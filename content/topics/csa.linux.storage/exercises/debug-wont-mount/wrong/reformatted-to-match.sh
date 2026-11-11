# Wrong: fstab says ext4 for /srv/backups and the disk is XFS, so the disk
# was reformatted to match the file (keeping its UUID). mount -a is quiet
# now, and everything that was on the backups disk is gone.
sudo sed -i 's/11111111-1111-4111-8111-111111111112/11111111-1111-4111-8111-111111111111/' /etc/fstab
sudo mkfs.ext4 -q -F -U 22222222-2222-4222-8222-222222222222 /dev/lab/data2
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a || true

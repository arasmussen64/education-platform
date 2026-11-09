# Wrong: the UUID and the mount point are fixed, but the backups line still
# says ext4 for an XFS disk.
sudo sed -i 's/11111111-1111-4111-8111-111111111112/11111111-1111-4111-8111-111111111111/' /etc/fstab
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a || true

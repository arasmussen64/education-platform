# Wrong: the type and the mount point are fixed, but the shop's UUID still
# has its typo, so the first line still can't be mounted.
sudo sed -i 's|/srv/backups ext4|/srv/backups xfs|' /etc/fstab
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a || true

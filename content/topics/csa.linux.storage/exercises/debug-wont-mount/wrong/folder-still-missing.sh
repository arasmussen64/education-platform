# Wrong: the UUID and the type are fixed, but /srv/archive still doesn't
# exist, so there's nowhere to mount the third disk.
sudo sed -i 's/11111111-1111-4111-8111-111111111112/11111111-1111-4111-8111-111111111111/' /etc/fstab
sudo sed -i 's|/srv/backups ext4|/srv/backups xfs|' /etc/fstab
sudo systemctl daemon-reload
sudo mount -a || true

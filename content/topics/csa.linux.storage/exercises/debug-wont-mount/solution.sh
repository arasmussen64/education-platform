# The three complaints from mount -a, and the mistake behind each:
#   1. "can't find UUID=1111…1112": the UUID in the line for /srv/shop has
#      one digit wrong. blkid shows the real one ends in …1111.
#   2. "wrong fs type, bad option, bad superblock" for /srv/backups: the
#      line says ext4, but blkid says the backups disk is xfs.
#   3. "mount point does not exist" for /srv/archive: the folder was never
#      created.
sudo mount -a || true
lsblk -f
sudo blkid
# In the lab you'd edit the file with: sudo nano /etc/fstab
sudo sed -i 's/11111111-1111-4111-8111-111111111112/11111111-1111-4111-8111-111111111111/' /etc/fstab
sudo sed -i 's|/srv/backups ext4|/srv/backups xfs|' /etc/fstab
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a
df -h /srv/shop /srv/backups /srv/archive

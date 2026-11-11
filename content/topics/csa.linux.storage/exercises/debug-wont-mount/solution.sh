# The three faults, one for each volume:
#   1. /srv/backups: mount -a says "wrong fs type, bad option, bad
#      superblock". The line says ext4, but blkid says the disk is xfs.
#   2. /srv/archive: mount -a says "mount point does not exist". The folder
#      was never created.
#   3. /srv/shop: mount -a says nothing at all. The UUID in its line has one
#      digit wrong (it ends in …1112; blkid shows the disk's ends in …1111),
#      and with nofail a disk that can't be found is skipped without a
#      word. findmnt --verify reads fstab and reports all three.
sudo mount -a || true
sudo blkid
cat /etc/fstab
sudo findmnt --verify || true
# In the lab you'd edit the file with: sudo nano /etc/fstab
sudo sed -i 's/11111111-1111-4111-8111-111111111112/11111111-1111-4111-8111-111111111111/' /etc/fstab
sudo sed -i 's|/srv/backups ext4|/srv/backups xfs|' /etc/fstab
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a
df -h /srv/shop /srv/backups /srv/archive

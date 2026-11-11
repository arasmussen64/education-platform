# Wrong: the three lines now name the disks by device instead of by UUID.
# Everything mounts today; after a reboot a device name can belong to a
# different disk, or to nothing.
sudo sed -i '/^UUID=/d' /etc/fstab
printf '%s\n' \
  '/dev/lab/data1 /srv/shop ext4 defaults,nofail 0 2' \
  '/dev/lab/data2 /srv/backups xfs defaults,nofail 0 2' \
  '/dev/lab/data3 /srv/archive ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab > /dev/null
sudo mkdir -p /srv/archive
sudo systemctl daemon-reload
sudo mount -a || true

# Wrong: the group was made from both disks at once and the volume was
# 192 MB from its first minute, so nothing was ever grown. The end looks
# the same; the lab is about the day the second disk arrives later.
sudo pvcreate /dev/lab/disk1 /dev/lab/disk2
sudo vgcreate mediavg /dev/lab/disk1 /dev/lab/disk2
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch1/* ~/incoming/batch2/* /srv/media/

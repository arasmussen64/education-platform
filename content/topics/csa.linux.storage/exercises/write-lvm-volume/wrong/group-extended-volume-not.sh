# Wrong: the second disk joined the group, and there it sits: the group has
# 96 MB free, and the logical volume was never extended into it.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch1/* /srv/media/
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo vgs

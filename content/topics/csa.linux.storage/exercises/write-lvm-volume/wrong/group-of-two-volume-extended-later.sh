# Wrong: the group was made from both disks at once, with the volume on
# half of it, and the volume was extended later. The filesystem did grow,
# but no disk ever joined a group that was already in use, which is the
# step the lab is about.
sudo pvcreate /dev/lab/disk1 /dev/lab/disk2
sudo vgcreate mediavg /dev/lab/disk1 /dev/lab/disk2
sudo lvcreate -n films -l 50%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch1/* /srv/media/
sudo lvextend -r -l +100%FREE /dev/mediavg/films
sudo mv ~/incoming/batch2/* /srv/media/

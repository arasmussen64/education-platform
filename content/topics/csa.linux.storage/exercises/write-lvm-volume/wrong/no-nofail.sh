# Wrong: the fstab line has no nofail, so a boot without this volume would
# stop and wait for it.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "/dev/mediavg/films /srv/media ext4 defaults 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch1/* /srv/media/
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo lvextend -r -l +100%FREE /dev/mediavg/films
sudo mv ~/incoming/batch2/* /srv/media/

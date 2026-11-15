# Wrong: everything was built and grown, but the volume was mounted by hand
# and never added to /etc/fstab, so the next boot won't mount it.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
sudo mount /dev/mediavg/films /srv/media
sudo mv ~/incoming/batch1/* /srv/media/
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo lvextend -r -l +100%FREE /dev/mediavg/films
sudo mv ~/incoming/batch2/* /srv/media/

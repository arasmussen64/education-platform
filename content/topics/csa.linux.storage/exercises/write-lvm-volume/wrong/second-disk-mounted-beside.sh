# Wrong: the second disk never joined the group. It got a filesystem of its
# own, mounted in a folder inside /srv/media, and the second batch went
# there: two small filesystems, where one that grows was asked for.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch1/* /srv/media/
sudo mkfs.ext4 -q /dev/lab/disk2
sudo mkdir -p /srv/media/more
echo "UUID=$(sudo blkid -s UUID -o value /dev/lab/disk2) /srv/media/more ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch2/* /srv/media/more/
# Links, so that every film has a name in /srv/media.
sudo ln -s /srv/media/more/film-4.mp4 /srv/media/more/film-5.mp4 /srv/media/more/film-6.mp4 /srv/media/

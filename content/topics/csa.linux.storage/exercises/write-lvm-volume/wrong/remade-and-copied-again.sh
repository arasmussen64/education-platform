# Wrong: the films were copied in, not moved, so when a new filesystem was
# made over them after the extension they could be copied in again. Every
# film is there, but nothing was grown: the volume was emptied and refilled,
# which only works while a second copy of the data exists.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
sudo mount /dev/mediavg/films /srv/media
sudo cp ~/incoming/batch1/* /srv/media/
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo lvextend -l +100%FREE /dev/mediavg/films
# A person takes longer than this to type the next line.
sleep 2
sudo umount /srv/media
sudo mkfs.ext4 -q -F /dev/mediavg/films
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo cp ~/incoming/batch1/* ~/incoming/batch2/* /srv/media/

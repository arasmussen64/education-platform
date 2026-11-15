# Wrong: after extending the volume, df showed the old size, so a new
# filesystem was made on it "to use the space". mkfs erased the first
# batch, which had been moved here and is nowhere else.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
sudo mount /dev/mediavg/films /srv/media
sudo mv ~/incoming/batch1/* /srv/media/
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo lvextend -l +100%FREE /dev/mediavg/films
sleep 2
sudo umount /srv/media
sudo mkfs.ext4 -q -F /dev/mediavg/films
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo mv ~/incoming/batch2/* /srv/media/

# 1. The three LVM layers, on the first disk only: a physical volume, a
#    volume group made from it, and a logical volume that takes all of it.
sudo pvcreate /dev/lab/disk1
sudo vgcreate mediavg /dev/lab/disk1
sudo lvcreate -n films -l 100%FREE mediavg
sudo pvs
sudo vgs
sudo lvs

#    From here the volume is a device like any disk: a filesystem, a mount
#    point, a line in fstab by UUID, and mount -a to mount it from the line.
sudo mkfs.ext4 -q /dev/mediavg/films
sudo mkdir -p /srv/media
echo "UUID=$(sudo blkid -s UUID -o value /dev/mediavg/films) /srv/media ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a && df -h /srv/media

# 2. The first batch goes in. What is left is less than the second needs.
sudo mv ~/incoming/batch1/* /srv/media/
df -h /srv/media
du -sh ~/incoming/batch2

# 3. Grow it where it stands: the second disk joins the group, and the
#    volume and its filesystem are extended into the new space together
#    (-r). The films stay where they are and the volume stays mounted.
sudo pvcreate /dev/lab/disk2
sudo vgextend mediavg /dev/lab/disk2
sudo vgs
sudo lvextend -r -l +100%FREE /dev/mediavg/films
df -h /srv/media

# 4. Now the second batch fits.
sudo mv ~/incoming/batch2/* /srv/media/
ls -l /srv/media
df -h /srv/media

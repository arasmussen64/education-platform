lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS; ls -l /dev/lab/
sudo mkfs.ext4 -q /dev/lab/data1
sudo mkdir -p /data && sudo mount /dev/lab/data1 /data
df -h /data
sudo blkid /dev/lab/data1
echo "UUID=$(sudo blkid -s UUID -o value /dev/lab/data1) /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo umount /data && sudo systemctl daemon-reload && sudo mount -a && df -h /data

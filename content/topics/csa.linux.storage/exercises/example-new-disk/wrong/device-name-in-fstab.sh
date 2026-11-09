# Wrong: fstab names the disk by device name. After a reboot the name can
# belong to a different disk, or to nothing.
sudo mkfs.ext4 -q /dev/lab/data1
sudo mkdir -p /data && sudo mount /dev/lab/data1 /data
echo "/dev/lab/data1 /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload

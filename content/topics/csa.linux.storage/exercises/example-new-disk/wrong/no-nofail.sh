# Wrong: without nofail, a detached volume stops the whole boot.
sudo mkfs.ext4 -q /dev/lab/data1
sudo mkdir -p /data && sudo mount /dev/lab/data1 /data
echo "UUID=$(sudo blkid -s UUID -o value /dev/lab/data1) /data ext4 defaults 0 2" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload

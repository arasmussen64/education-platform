# Wrong: mounted now, forgotten at the next boot: nothing in fstab.
sudo mkfs.ext4 -q /dev/lab/data1
sudo mkdir -p /data && sudo mount /dev/lab/data1 /data

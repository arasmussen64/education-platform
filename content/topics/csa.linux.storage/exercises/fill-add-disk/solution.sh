# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/add-disk <<'EOF'
#!/bin/bash
# Usage: add-disk DEVICE MOUNTPOINT
# Puts the team's standard filesystem on a new disk, mounts it, and adds it
# to fstab by UUID so it comes back at boot (and a missing disk can't stop
# the boot).
set -e
device="$1"
mount_point="$2"
fstype=xfs
sudo mkfs.$fstype -q "$device"
sudo mkdir -p "$mount_point"
uuid=$(sudo blkid -s UUID -o value "$device")
echo "UUID=$uuid $mount_point $fstype defaults,nofail 0 2" | sudo tee -a /etc/fstab > /dev/null
sudo systemctl daemon-reload
sudo mount -a
df -h "$mount_point"
EOF
~/bin/add-disk /dev/lab/data2 /srv/backups
lsblk -f | grep -A1 xfs; tail -n 1 /etc/fstab

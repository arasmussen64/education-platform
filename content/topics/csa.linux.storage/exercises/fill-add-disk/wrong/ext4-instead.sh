# Wrong: ext4 where the team standardised on XFS for data volumes.
cat > ~/bin/add-disk <<'EOF'
#!/bin/bash
set -e
device="$1"
mount_point="$2"
fstype=ext4
sudo mkfs.$fstype -q "$device"
sudo mkdir -p "$mount_point"
uuid=$(sudo blkid -s UUID -o value "$device")
echo "UUID=$uuid $mount_point $fstype defaults,nofail 0 2" | sudo tee -a /etc/fstab > /dev/null
sudo systemctl daemon-reload
sudo mount -a
EOF

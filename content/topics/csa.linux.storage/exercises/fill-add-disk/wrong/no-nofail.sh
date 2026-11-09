# Wrong: without nofail, a detached volume stops the whole boot.
cat > ~/bin/add-disk <<'EOF'
#!/bin/bash
set -e
device="$1"
mount_point="$2"
fstype=xfs
sudo mkfs.$fstype -q "$device"
sudo mkdir -p "$mount_point"
uuid=$(sudo blkid -s UUID -o value "$device")
echo "UUID=$uuid $mount_point $fstype defaults 0 2" | sudo tee -a /etc/fstab > /dev/null
sudo systemctl daemon-reload
sudo mount -a
EOF

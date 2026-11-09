# Wrong: the device name in fstab instead of the UUID.
cat > ~/bin/add-disk <<'EOF'
#!/bin/bash
set -e
device="$1"
mount_point="$2"
fstype=xfs
sudo mkfs.$fstype -q "$device"
sudo mkdir -p "$mount_point"
echo "$device $mount_point $fstype defaults,nofail 0 2" | sudo tee -a /etc/fstab > /dev/null
sudo systemctl daemon-reload
sudo mount -a
EOF

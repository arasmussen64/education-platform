# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/layers <<'EOF'
#!/bin/bash
# Usage: layers MOUNTPOINT LAYER...   (layers from the bottom up)
# Mounts the layers as one overlay filesystem at MOUNTPOINT, read-only
# underneath, with a fresh writable layer on a tmpfs on top.
mount_point="$1"
shift
# overlayfs wants the lower layers listed from the top down.
lower=""
for layer in "$@"; do
  lower="$layer${lower:+:$lower}"
done
name=$(basename "$mount_point")
rw="/run/layers/$name"
sudo mkdir -p "$rw" "$mount_point"
sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work"
sudo mount -t overlay overlay -o "lowerdir=$lower,upperdir=$rw/upper,workdir=$rw/work" "$mount_point"
mount | grep " $mount_point "
EOF
chmod +x ~/bin/layers
~/bin/layers /mnt/app /srv/layers/base /srv/layers/deps /srv/layers/app
ls -R /mnt/app
cat /mnt/app/etc/version

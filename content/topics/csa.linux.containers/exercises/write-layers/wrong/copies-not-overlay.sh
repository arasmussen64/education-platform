# Wrong: copies the layers into the mount point instead of overlaying them,
# so there's no overlay, and writes change the copy that then has to be
# cleaned up by hand.
mkdir -p ~/bin
cat > ~/bin/layers <<'EOF'
#!/bin/bash
mount_point="$1"
shift
sudo mkdir -p "$mount_point"
for layer in "$@"; do
  sudo cp -a "$layer/." "$mount_point/"
done
mount | grep " $mount_point " || true
EOF
chmod +x ~/bin/layers

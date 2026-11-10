# Wrong: the layers are listed bottom to top, so the base layer hides the
# others wherever they share a file.
mkdir -p ~/bin
cat > ~/bin/layers <<'EOF'
#!/bin/bash
mount_point="$1"
shift
lower=$(IFS=:; echo "$*")
name=$(basename "$mount_point")
rw="/run/layers/$name"
sudo mkdir -p "$rw" "$mount_point"
sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work"
sudo mount -t overlay overlay -o "lowerdir=$lower,upperdir=$rw/upper,workdir=$rw/work" "$mount_point"
mount | grep " $mount_point "
EOF
chmod +x ~/bin/layers

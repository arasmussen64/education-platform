# Wrong: the writable layer is a plain folder on this machine's root
# filesystem, which is itself an overlay, so the mount is refused.
mkdir -p ~/bin
cat > ~/bin/layers <<'EOF'
#!/bin/bash
mount_point="$1"
shift
lower=""
for layer in "$@"; do
  lower="$layer${lower:+:$lower}"
done
name=$(basename "$mount_point")
rw="/var/lib/layers/$name"
sudo mkdir -p "$rw/upper" "$rw/work" "$mount_point"
sudo mount -t overlay overlay -o "lowerdir=$lower,upperdir=$rw/upper,workdir=$rw/work" "$mount_point"
mount | grep " $mount_point "
EOF
chmod +x ~/bin/layers

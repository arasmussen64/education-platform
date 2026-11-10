# Wrong: namespaces and an overlay, but no cgroup, so nothing limits the box.
mkdir -p ~/bin
cat > ~/bin/box <<'EOF'
#!/bin/bash
set -e
name="$1"
shift
image=/srv/box/rootfs
rw="/run/box/$name"
root="$rw/root"
sudo mkdir -p "$rw"
sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work" "$root"
sudo mount -t overlay overlay -o "lowerdir=$image,upperdir=$rw/upper,workdir=$rw/work" "$root"
set +e
sudo unshare --pid --fork --uts --mount --ipc chroot "$root" /bin/sh -c 'mount -t proc proc /proc; hostname '"$name"'; exec "$@"' sh "$@"
status=$?
sudo umount "$root"
sudo umount "$rw"
exit $status
EOF
chmod +x ~/bin/box

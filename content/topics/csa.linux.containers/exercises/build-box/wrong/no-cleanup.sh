# Wrong: everything is set up but nothing is taken down, so every run
# leaves a tmpfs, an overlay mount and a cgroup behind.
mkdir -p ~/bin
cat > ~/bin/box <<'EOF'
#!/bin/bash
set -e
name="$1"
shift
image=/srv/box/rootfs
rw="/run/box/$name"
root="$rw/root"
cgroup="/sys/fs/cgroup/box-$name"
sudo mkdir -p "$rw"
findmnt -n "$rw" > /dev/null 2>&1 || sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work" "$root"
findmnt -n "$root" > /dev/null 2>&1 || sudo mount -t overlay overlay -o "lowerdir=$image,upperdir=$rw/upper,workdir=$rw/work" "$root"
sudo mkdir -p "$cgroup"
echo 50 | sudo tee "$cgroup/pids.max" > /dev/null
echo 64M | sudo tee "$cgroup/memory.max" > /dev/null
sudo bash -c "echo \$\$ > $cgroup/cgroup.procs && exec unshare --pid --fork --uts --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"" bash "$@"
EOF
chmod +x ~/bin/box

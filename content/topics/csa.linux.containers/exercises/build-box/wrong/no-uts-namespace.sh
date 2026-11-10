# Wrong: without --uts, naming the box renames the lab machine.
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
sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work" "$root"
sudo mount -t overlay overlay -o "lowerdir=$image,upperdir=$rw/upper,workdir=$rw/work" "$root"
sudo mkdir -p "$cgroup"
echo 50 | sudo tee "$cgroup/pids.max" > /dev/null
echo 64M | sudo tee "$cgroup/memory.max" > /dev/null
set +e
sudo bash -c "echo \$\$ > $cgroup/cgroup.procs && exec unshare --pid --fork --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"" bash "$@"
status=$?
sudo umount "$root"
sudo umount "$rw"
sudo rmdir "$cgroup"
exit $status
EOF
chmod +x ~/bin/box

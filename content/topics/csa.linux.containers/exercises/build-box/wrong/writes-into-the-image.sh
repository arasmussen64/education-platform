# Wrong: no overlay, so the box writes straight into the image folder and
# every run sees the last one's leftovers.
mkdir -p ~/bin
cat > ~/bin/box <<'EOF'
#!/bin/bash
set -e
name="$1"
shift
root=/srv/box/rootfs
cgroup="/sys/fs/cgroup/box-$name"
sudo mkdir -p "$cgroup"
echo 50 | sudo tee "$cgroup/pids.max" > /dev/null
echo 64M | sudo tee "$cgroup/memory.max" > /dev/null
set +e
sudo bash -c "echo \$\$ > $cgroup/cgroup.procs && exec unshare --pid --fork --uts --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"" bash "$@"
status=$?
sudo rmdir "$cgroup"
exit $status
EOF
chmod +x ~/bin/box

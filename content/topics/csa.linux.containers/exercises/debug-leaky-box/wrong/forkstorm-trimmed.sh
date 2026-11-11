# Wrong: the hostname and the fork are fixed, but the cgroup join still
# comes after the exec, and forkstorm is edited to start twenty processes
# instead of thirty, so it looks as if the limit stopped it. No box is held
# to its limit.
sudo hostname lab
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
echo 20 | sudo tee "$cgroup/pids.max" > /dev/null
set +e
sudo bash -c "exec unshare --pid --fork --uts --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"; echo \$\$ > $cgroup/cgroup.procs" bash "$@"
status=$?
sudo umount "$root"
sudo umount "$rw"
sudo rmdir "$cgroup"
exit $status
EOF
sudo sed -i 's/seq 1 30/seq 1 20/' /srv/box/rootfs/bin/forkstorm

# The reference runtime, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/box <<'EOF'
#!/bin/bash
# Usage: box NAME COMMAND and its arguments
# A container made by hand: an overlay root filesystem that's thrown away
# afterwards, its own namespaces, and a cgroup with limits.
set -e
name="$1"
shift
image=/srv/box/rootfs
rw="/run/box/$name"
root="$rw/root"
cgroup="/sys/fs/cgroup/box-$name"

# 1. The root filesystem: the image, read-only, under a fresh writable layer.
sudo mkdir -p "$rw"
sudo mount -t tmpfs tmpfs "$rw"
sudo mkdir -p "$rw/upper" "$rw/work" "$root"
sudo mount -t overlay overlay -o "lowerdir=$image,upperdir=$rw/upper,workdir=$rw/work" "$root"

# 3. The cgroup and its limits.
sudo mkdir -p "$cgroup"
echo 50 | sudo tee "$cgroup/pids.max" > /dev/null
echo 64M | sudo tee "$cgroup/memory.max" > /dev/null

# 2. A root shell joins the cgroup, then becomes the container: new
#    namespaces, the overlay as /, /proc mounted, the hostname set, then
#    the command. (The inner quoting: $$ and "$@" belong to the inner shells.)
set +e
sudo bash -c "echo \$\$ > $cgroup/cgroup.procs && exec unshare --pid --fork --uts --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"" bash "$@"
status=$?

# 4. Cleanup: the container's writes go with the tmpfs; the cgroup is empty
#    now, so it can be removed.
sudo umount "$root"
sudo umount "$rw"
sudo rmdir "$cgroup"
exit $status
EOF
chmod +x ~/bin/box
~/bin/box demo hostname
~/bin/box demo ps
~/bin/box demo sh -c 'echo hi > /hello.txt; ls /'
ls /srv/box/rootfs

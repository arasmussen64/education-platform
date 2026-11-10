# The three mistakes, all on the line that starts the container:
#   1. No --uts, so "hostname demo" inside renamed the machine.
#   2. --pid without --fork: the new process numbers only apply to children
#      of the process that called unshare, so the shell itself wasn't in the
#      namespace and couldn't start anything ("can't fork").
#   3. The cgroup join came after the exec. exec replaces the shell, so
#      nothing after it ever runs; the join has to come first.
# In the lab you'd fix the one line with nano; here the script is rewritten.
sudo hostname lab
cat > ~/bin/box <<'EOF'
#!/bin/bash
# Usage: box NAME COMMAND and its arguments
# A container made by hand: an overlay root filesystem that's thrown away
# afterwards, its own namespaces, and a cgroup with a pids limit.
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
sudo bash -c "echo \$\$ > $cgroup/cgroup.procs && exec unshare --pid --fork --uts --mount --ipc chroot $root /bin/sh -c 'mount -t proc proc /proc; hostname $name; exec \"\$@\"' sh \"\$@\"" bash "$@"
status=$?

sudo umount "$root"
sudo umount "$rw"
sudo rmdir "$cgroup"
exit $status
EOF
~/bin/box demo hostname; hostname
~/bin/box demo ps
~/bin/box demo forkstorm || echo "(the storm was stopped by the pids limit, exit status $?)"

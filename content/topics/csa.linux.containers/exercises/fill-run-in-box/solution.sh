# The finished script. In the lab you'd fill the three gaps with nano; here
# it's written in one go.
cat > ~/bin/run-in-box <<'EOF'
#!/bin/bash
# Usage: run-in-box COMMAND and its arguments
# Runs COMMAND inside a container made by hand: its own process numbers,
# hostname and mounts, with the busybox root filesystem as its /.
rootfs=/srv/box/rootfs
sudo unshare --pid --fork --uts --mount --ipc chroot "$rootfs" /bin/sh -c 'mount -t proc proc /proc; hostname box; exec "$@"' sh "$@"
EOF
~/bin/run-in-box hostname
~/bin/run-in-box ps
~/bin/run-in-box ls /
hostname

# Wrong: the wrong filesystem type for /proc, so nothing is mounted there and
# ps has nothing to read.
cat > ~/bin/run-in-box <<'EOF'
#!/bin/bash
rootfs=/srv/box/rootfs
sudo unshare --pid --fork --uts --mount --ipc chroot "$rootfs" /bin/sh -c 'mount -t tmpfs proc /proc; hostname box; exec "$@"' sh "$@"
EOF

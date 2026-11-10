# Wrong: --pid without --fork, so the shell inside can't start anything:
# "can't fork: Cannot allocate memory".
cat > ~/bin/run-in-box <<'EOF'
#!/bin/bash
rootfs=/srv/box/rootfs
sudo unshare --pid --uts --mount --ipc chroot "$rootfs" /bin/sh -c 'mount -t proc proc /proc; hostname box; exec "$@"' sh "$@"
EOF

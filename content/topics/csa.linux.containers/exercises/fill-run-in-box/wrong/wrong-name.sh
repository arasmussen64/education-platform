# Wrong: the box is named after the machine, so you can't tell inside from out.
cat > ~/bin/run-in-box <<'EOF'
#!/bin/bash
rootfs=/srv/box/rootfs
sudo unshare --pid --fork --uts --mount --ipc chroot "$rootfs" /bin/sh -c 'mount -t proc proc /proc; hostname lab; exec "$@"' sh "$@"
EOF

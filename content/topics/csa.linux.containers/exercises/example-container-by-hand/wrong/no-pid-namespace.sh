# Wrong: without --pid the box sees the host's processes, and its "PID 1"
# is the host's systemd.
sudo mkdir -p /sys/fs/cgroup/box && echo 20 | sudo tee /sys/fs/cgroup/box/pids.max > /dev/null
sudo bash -c 'echo $$ > /sys/fs/cgroup/box/cgroup.procs && exec unshare --uts --mount chroot /srv/box/rootfs /bin/sh -c "mount -t proc proc /proc; forkstorm"'
mkdir -p ~/example && sudo unshare --uts --mount chroot /srv/box/rootfs /bin/sh -c 'mount -t proc proc /proc; hostname box; hostname; ps' > ~/example/inside.txt

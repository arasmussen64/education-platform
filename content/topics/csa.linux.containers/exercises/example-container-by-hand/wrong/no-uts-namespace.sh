# Wrong: without --uts, "hostname box" inside renames the whole machine.
sudo mkdir -p /sys/fs/cgroup/box && echo 20 | sudo tee /sys/fs/cgroup/box/pids.max > /dev/null
sudo bash -c 'echo $$ > /sys/fs/cgroup/box/cgroup.procs && exec unshare --pid --fork --mount chroot /srv/box/rootfs /bin/sh -c "mount -t proc proc /proc; forkstorm"'
mkdir -p ~/example && sudo unshare --pid --fork --mount chroot /srv/box/rootfs /bin/sh -c 'mount -t proc proc /proc; hostname box; hostname; ps' > ~/example/inside.txt

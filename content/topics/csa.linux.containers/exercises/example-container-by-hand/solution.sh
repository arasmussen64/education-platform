ls /srv/box/rootfs; ls /srv/box/rootfs/bin | tr '\n' ' '; echo
sudo unshare --pid --fork --uts --mount --ipc chroot /srv/box/rootfs /bin/sh -c 'mount -t proc proc /proc; hostname box; hostname; ps; ls /'
hostname; ps -ef | wc -l
sudo mkdir -p /sys/fs/cgroup/box && echo 20 | sudo tee /sys/fs/cgroup/box/pids.max
sudo bash -c 'echo $$ > /sys/fs/cgroup/box/cgroup.procs && exec unshare --pid --fork --uts --mount chroot /srv/box/rootfs /bin/sh -c "mount -t proc proc /proc; forkstorm"'
cat /sys/fs/cgroup/box/pids.events
mkdir -p ~/example && sudo unshare --pid --fork --uts --mount chroot /srv/box/rootfs /bin/sh -c 'mount -t proc proc /proc; hostname box; hostname; ps' > ~/example/inside.txt && cat ~/example/inside.txt

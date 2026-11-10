# Wrong: the box has its namespaces but no cgroup, so nothing limits it.
mkdir -p ~/example && sudo unshare --pid --fork --uts --mount chroot /srv/box/rootfs /bin/sh -c 'mount -t proc proc /proc; hostname box; hostname; ps' > ~/example/inside.txt

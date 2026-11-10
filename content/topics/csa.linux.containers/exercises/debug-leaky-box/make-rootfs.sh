#!/bin/bash
# A tiny root filesystem for a container made by hand: busybox, one binary
# that behaves as sh, ls, ps and friends depending on the name it's called
# by, plus the folders a process expects. Made at image build.
set -euo pipefail
root=/srv/box/rootfs
mkdir -p "$root/bin" "$root/proc" "$root/tmp" "$root/etc" "$root/dev" "$root/root"
cp /bin/busybox "$root/bin/busybox"
for cmd in sh ls ps hostname mount umount cat echo sleep seq wc head grep touch mkdir rm uname id env; do
  ln -sf busybox "$root/bin/$cmd"
done
# A small program for the lab: tries to start thirty processes, saying so
# before each one. Under a pids limit the shell is refused a fork at the
# limit and stops right there, so the last "starting" line is the count.
cat > "$root/bin/forkstorm" <<'EOF'
#!/bin/sh
for i in $(seq 1 30); do
  echo "starting process $i"
  sleep 60 &
done
sleep 1
echo "processes inside: $(ps | wc -l)"
EOF
chmod 755 "$root/bin/forkstorm"
echo "This is the box's root filesystem: busybox and nothing else." > "$root/etc/motd"
chmod 1777 "$root/tmp"
# /dev/null and /dev/zero are made at boot (box-rootfs.service): a Docker
# build may not create device files, a privileged container may.

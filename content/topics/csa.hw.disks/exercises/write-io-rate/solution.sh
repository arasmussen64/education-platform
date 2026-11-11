# The finished script, written in one go. In the lab you'd write it with
# nano ~/bin/io-rate and try it after each part.
cat > ~/bin/io-rate <<'EOF'
#!/bin/bash
# Usage: io-rate UNIT SECONDS
# How hard UNIT writes to the data disk, measured over SECONDS, and which
# of its write caps holds it back, if either does.
if [ "$#" -ne 2 ]; then
  echo "Usage: io-rate UNIT SECONDS" >&2
  exit 1
fi
unit=$1
seconds=$2

# The unit's cgroup folder (a unit can be in any slice), and the data
# disk's device number, which io.stat and io.max put first on its line.
folder=/sys/fs/cgroup$(systemctl show "$unit" -p ControlGroup --value)
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')

# One value from the data disk's line of a file in the folder, such as
# wios in io.stat or wiops in io.max. Nothing if the file has no line.
field() {
  grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2
}

writes_before=$(field io.stat wios)
bytes_before=$(field io.stat wbytes)
sleep "$seconds"
writes_after=$(field io.stat wios)
bytes_after=$(field io.stat wbytes)
writes=$((writes_after - writes_before))
bytes=$((bytes_after - bytes_before))

# No line in io.max for the disk means no cap, the same as max.
iops_cap=$(field io.max wiops)
bytes_cap=$(field io.max wbps)

awk -v w="$writes" -v b="$bytes" -v s="$seconds" -v ic="${iops_cap:-max}" -v bc="${bytes_cap:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  binding = "none"
  if (ic != "max" && w / s >= 0.9 * ic) binding = "iops"
  else if (bc != "max" && b / s >= 0.9 * bc) binding = "throughput"
  print "binding: " binding
}'
EOF
chmod +x ~/bin/io-rate
~/bin/io-rate shop-db 5
~/bin/io-rate shop-backup 5
~/bin/io-rate shop-logs 5

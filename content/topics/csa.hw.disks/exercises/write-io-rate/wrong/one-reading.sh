# Wrong: one reading of io.stat, divided by the seconds. io.stat counts
# from when the service started, so this is everything it ever wrote
# divided by 5, not what it writes in a second.
cat > ~/bin/io-rate <<'EOF'
#!/bin/bash
if [ "$#" -ne 2 ]; then echo "Usage: io-rate UNIT SECONDS" >&2; exit 1; fi
unit=$1; seconds=$2
folder=/sys/fs/cgroup$(systemctl show "$unit" -p ControlGroup --value)
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')
field() { grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2; }
sleep "$seconds"
w=$(field io.stat wios); b=$(field io.stat wbytes)
ic=$(field io.max wiops); bc=$(field io.max wbps)
awk -v w="$w" -v b="$b" -v s="$seconds" -v ic="${ic:-max}" -v bc="${bc:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  binding = "none"
  if (ic != "max" && w / s >= 0.9 * ic) binding = "iops"
  else if (bc != "max" && b / s >= 0.9 * bc) binding = "throughput"
  print "binding: " binding
}'
EOF
chmod +x ~/bin/io-rate

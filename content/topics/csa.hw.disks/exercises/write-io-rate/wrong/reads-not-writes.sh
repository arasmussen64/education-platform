# Wrong: rios and rbytes are the reads. These services only write, so
# every rate comes out as 0.
cat > ~/bin/io-rate <<'EOF'
#!/bin/bash
if [ "$#" -ne 2 ]; then echo "Usage: io-rate UNIT SECONDS" >&2; exit 1; fi
unit=$1; seconds=$2
folder=/sys/fs/cgroup$(systemctl show "$unit" -p ControlGroup --value)
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')
field() { grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2; }
r1=$(field io.stat rios); b1=$(field io.stat rbytes)
sleep "$seconds"
r2=$(field io.stat rios); b2=$(field io.stat rbytes)
ic=$(field io.max riops); bc=$(field io.max rbps)
awk -v w=$((r2 - r1)) -v b=$((b2 - b1)) -v s="$seconds" -v ic="${ic:-max}" -v bc="${bc:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  binding = "none"
  if (ic != "max" && w / s >= 0.9 * ic) binding = "iops"
  else if (bc != "max" && b / s >= 0.9 * bc) binding = "throughput"
  print "binding: " binding
}'
EOF
chmod +x ~/bin/io-rate

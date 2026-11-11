# Wrong: bytes divided by 1,000,000, which is MB. The script was asked for
# MiB, 1,048,576 bytes: at the backup job's 10 MiB a second this prints
# 10.5.
cat > ~/bin/io-rate <<'EOF'
#!/bin/bash
if [ "$#" -ne 2 ]; then echo "Usage: io-rate UNIT SECONDS" >&2; exit 1; fi
unit=$1; seconds=$2
folder=/sys/fs/cgroup$(systemctl show "$unit" -p ControlGroup --value)
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')
field() { grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2; }
w1=$(field io.stat wios); b1=$(field io.stat wbytes)
sleep "$seconds"
w2=$(field io.stat wios); b2=$(field io.stat wbytes)
ic=$(field io.max wiops); bc=$(field io.max wbps)
awk -v w=$((w2 - w1)) -v b=$((b2 - b1)) -v s="$seconds" -v ic="${ic:-max}" -v bc="${bc:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1000000
  binding = "none"
  if (ic != "max" && w / s >= 0.9 * ic) binding = "iops"
  else if (bc != "max" && b / s >= 0.9 * bc) binding = "throughput"
  print "binding: " binding
}'
EOF
chmod +x ~/bin/io-rate

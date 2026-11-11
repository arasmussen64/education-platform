# Wrong: the cgroup folder is built as system.slice/UNIT.service, which is
# where most services are, but not the backup job, which is in
# batch.slice. systemctl show UNIT -p ControlGroup gives the real folder.
cat > ~/bin/io-rate <<'EOF'
#!/bin/bash
if [ "$#" -ne 2 ]; then echo "Usage: io-rate UNIT SECONDS" >&2; exit 1; fi
unit=$1; seconds=$2
folder=/sys/fs/cgroup/system.slice/$unit.service
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')
field() { grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2; }
w1=$(field io.stat wios); b1=$(field io.stat wbytes)
sleep "$seconds"
w2=$(field io.stat wios); b2=$(field io.stat wbytes)
ic=$(field io.max wiops); bc=$(field io.max wbps)
awk -v w=$((w2 - w1)) -v b=$((b2 - b1)) -v s="$seconds" -v ic="${ic:-max}" -v bc="${bc:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  binding = "none"
  if (ic != "max" && w / s >= 0.9 * ic) binding = "iops"
  else if (bc != "max" && b / s >= 0.9 * bc) binding = "throughput"
  print "binding: " binding
}'
EOF
chmod +x ~/bin/io-rate

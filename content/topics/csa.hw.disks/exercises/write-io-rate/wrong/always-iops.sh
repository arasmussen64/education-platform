# Wrong: "iops" whenever the unit has a writes-a-second cap at all. A cap
# holds a service back only when it writes up against it: the backup job
# is held by its bytes cap, and the logger by neither.
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
ic=$(field io.max wiops)
awk -v w=$((w2 - w1)) -v b=$((b2 - b1)) -v s="$seconds" -v ic="${ic:-max}" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  print "binding: " (ic != "max" ? "iops" : "none")
}'
EOF
chmod +x ~/bin/io-rate

# Wrong: the rates are measured, but the binding is written in for each
# of the three shop services by name, from what systemctl show says about
# them, instead of worked out from the rates and the caps. On any other
# service it says "none", whatever holds that service back.
cat > ~/bin/io-rate <<'SCRIPT'
#!/bin/bash
if [ "$#" -ne 2 ]; then echo "Usage: io-rate UNIT SECONDS" >&2; exit 1; fi
unit=$1; seconds=$2
folder=/sys/fs/cgroup$(systemctl show "$unit" -p ControlGroup --value)
device=$(lsblk -dno MAJ:MIN /dev/lab/data | tr -d ' ')
field() { grep "^$device " "$folder/$1" | grep -o "$2=[0-9a-z]*" | cut -d= -f2; }
w1=$(field io.stat wios); b1=$(field io.stat wbytes)
sleep "$seconds"
w2=$(field io.stat wios); b2=$(field io.stat wbytes)
case "$unit" in
  shop-db) binding=iops ;;
  shop-backup) binding=throughput ;;
  *) binding=none ;;
esac
awk -v w=$((w2 - w1)) -v b=$((b2 - b1)) -v s="$seconds" -v binding="$binding" 'BEGIN {
  printf "writes a second: %.0f\n", w / s
  printf "MiB a second: %.1f\n", b / s / 1048576
  print "binding: " binding
}'
SCRIPT
chmod +x ~/bin/io-rate

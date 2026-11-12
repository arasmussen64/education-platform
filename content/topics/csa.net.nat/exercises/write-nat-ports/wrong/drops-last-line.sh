# Wrong: drops the file's last line, where conntrack's count line is in the
# lunchtime listing, and counts every other line that isn't ICMP. When the
# count line comes first, as it can (it goes to the error stream), it turns
# up as a destination of its own and a real connection is lost.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: NAT ports in use per destination, busiest first.
set -euo pipefail
head -n -1 "$1" | awk -v ports="$2" '
  $1 != "icmp" {
    dst = ""
    dport = ""
    for (i = 2; i <= NF; i++) {
      if (dst == "" && $i ~ /^dst=/) dst = substr($i, 5)
      if (dport == "" && $i ~ /^dport=/) dport = substr($i, 7)
    }
    count[$1 " " dst ":" dport]++
  }
  END {
    for (key in count) {
      n = count[key]
      percent = int(n * 100 / ports)
      flag = ""
      if (n >= ports) flag = " FULL"
      else if (percent >= 80) flag = " WARN"
      printf "%s %d %d%%%s\n", key, n, percent, flag
    }
  }
' | sort -k3,3nr
EOF
chmod +x ~/bin/nat-ports

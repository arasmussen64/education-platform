# Wrong: FULL only when the count is more than PORTS, so a destination
# using every one of the address's ports, exactly PORTS, is called WARN.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: NAT ports in use per destination, busiest first.
set -euo pipefail
awk -v ports="$2" '
  $1 == "tcp" || $1 == "udp" {
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
      if (n > ports) flag = " FULL"
      else if (percent >= 80) flag = " WARN"
      printf "%s %d %d%%%s\n", key, n, percent, flag
    }
  }
' "$1" | sort -k3,3nr
EOF
chmod +x ~/bin/nat-ports

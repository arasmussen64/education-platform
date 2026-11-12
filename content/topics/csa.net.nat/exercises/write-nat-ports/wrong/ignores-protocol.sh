# Wrong: counts by address and port alone, so TCP and UDP to the same
# address and port are lumped together, though each protocol has ports of
# its own on a NAT.
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
    count[dst ":" dport]++
    proto[dst ":" dport] = $1
  }
  END {
    for (key in count) {
      n = count[key]
      percent = int(n * 100 / ports)
      flag = ""
      if (n >= ports) flag = " FULL"
      else if (percent >= 80) flag = " WARN"
      printf "%s %s %d %d%%%s\n", proto[key], key, n, percent, flag
    }
  }
' "$1" | sort -k3,3nr
EOF
chmod +x ~/bin/nat-ports

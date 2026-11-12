# Wrong: counts by protocol and address alone, so two services on one
# address (ports 80 and 443) are lumped together, though a NAT keeps them
# apart: each destination port has its own pool.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: NAT ports in use per destination, busiest first.
set -euo pipefail
awk -v ports="$2" '
  $1 == "tcp" || $1 == "udp" {
    dst = ""
    for (i = 2; i <= NF; i++) {
      if (dst == "" && $i ~ /^dst=/) dst = substr($i, 5)
    }
    count[$1 " " dst]++
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
' "$1" | sort -k3,3nr
EOF
chmod +x ~/bin/nat-ports

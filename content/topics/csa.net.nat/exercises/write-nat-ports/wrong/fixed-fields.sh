# Wrong: reads the destination and its port from fixed places, the sixth
# and eighth words, where they are on a TCP line; a UDP line has no state
# word, so there those places hold sport= and src=, and every UDP
# destination comes out wrong.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: NAT ports in use per destination, busiest first.
set -euo pipefail
awk -v ports="$2" '
  $1 == "tcp" || $1 == "udp" {
    count[$1 " " substr($6, 5) ":" substr($8, 7)]++
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

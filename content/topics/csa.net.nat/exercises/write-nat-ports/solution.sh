# The reference: ~/bin/nat-ports, written whole with cat > FILE <<'EOF',
# which writes the lines up to EOF into the file, then made executable and
# tried on the lunchtime listing. awk does the work: on each TCP or UDP line
# it finds the first dst= and the first dport= (the original tuple, as the
# inside machine sent it), counts the line under protocol, address and
# port, and at the end prints each destination's count, its share of PORTS
# rounded down, and the flag; sort puts the busiest first.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: from a saved conntrack -L listing, how many NAT
# ports each destination (protocol, address and port) is using, out of the
# PORTS one public address has, busiest first, with WARN from 80% and FULL
# when every port is in use.
set -euo pipefail

file=$1
ports=$2

awk -v ports="$ports" '
  # Only TCP and UDP use ports; ICMP lines and the count line from
  # conntrack itself are skipped.
  $1 == "tcp" || $1 == "udp" {
    dst = ""
    dport = ""
    # The first dst= and dport= belong to the original tuple. A TCP line
    # has a state word and a UDP line has none, so they sit at different
    # places: look for them, word by word.
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
' "$file" | sort -k3,3nr
EOF
chmod +x ~/bin/nat-ports
~/bin/nat-ports ~/listings/lunch.txt 10

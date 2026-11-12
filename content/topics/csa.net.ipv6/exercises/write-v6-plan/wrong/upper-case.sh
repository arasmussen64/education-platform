# Wrong: the fourth group and the labels are written with %X, in capitals
# (130A, rA). The address is the same, but RFC 5952's short form is in
# lower case, so tools and people comparing text see a different string.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
set -euo pipefail
p=${1%/*}
p=${p%::}
IFS=: read -r g1 g2 g3 <<< "$p"
for (( r = 0; r < $2; r++ )); do
  for (( z = 0; z < $3; z++ )); do
    for (( t = 0; t < $4; t++ )); do
      group=$(printf '%X' "$(( r * 4096 + z * 256 + t ))")
      s="$g1:${g2:-0}:${g3:-0}:$group:0:0:0:0"
      while [[ $s == *:0 ]]; do s=${s%:0}; done
      printf 'r%X-z%X-t%02X %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

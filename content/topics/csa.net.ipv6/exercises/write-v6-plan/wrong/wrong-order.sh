# Wrong: every line is right, but the loops are nested the other way, tier
# outermost, so the plan comes out grouped by tier instead of by region,
# then zone, then tier.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
set -euo pipefail
p=${1%/*}
p=${p%::}
IFS=: read -r g1 g2 g3 <<< "$p"
for (( t = 0; t < $4; t++ )); do
  for (( z = 0; z < $3; z++ )); do
    for (( r = 0; r < $2; r++ )); do
      group=$(printf '%x' "$(( r * 4096 + z * 256 + t ))")
      s="$g1:${g2:-0}:${g3:-0}:$group:0:0:0:0"
      while [[ $s == *:0 ]]; do s=${s%:0}; done
      printf 'r%x-z%x-t%02x %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

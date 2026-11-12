# Wrong: the tier is written in decimal (%02d), so tier 10 is t10 and its
# subnet's group ends in 10, which in hex is tier 16. Tiers 0 to 9 look
# right, so a plan with ten tiers or fewer hides it.
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
      group=$(printf '%x' "0x$(printf '%x%x%02d' "$r" "$z" "$t")")
      s="$g1:${g2:-0}:${g3:-0}:$group:0:0:0:0"
      while [[ $s == *:0 ]]; do s=${s%:0}; done
      printf 'r%x-z%x-t%02d %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

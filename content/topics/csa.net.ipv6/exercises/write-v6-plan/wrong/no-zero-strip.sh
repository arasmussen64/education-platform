# Wrong: the fourth group is written digit by digit with %x%x%02x, which
# keeps its leading zeros: region 0, zone 1, tier 2 comes out as 0102, not
# 102, and region 0, zone 0, tier 0 as 0000 instead of joining the ::.
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
      group=$(printf '%x%x%02x' "$r" "$z" "$t")
      s="$g1:${g2:-0}:${g3:-0}:$group:0:0:0:0"
      while [[ $s == *:0 ]]; do s=${s%:0}; done
      printf 'r%x-z%x-t%02x %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

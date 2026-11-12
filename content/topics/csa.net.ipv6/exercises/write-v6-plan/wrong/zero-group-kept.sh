# Wrong: the script always writes four groups and then ::, so when the
# subnet's group is 0 (region 0, zone 0, tier 0) the zero stays in front
# of the :: (2001:db8:a:0::/64) instead of joining it (2001:db8:a::/64),
# and a prefix whose third group is 0 keeps that zero too.
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
      group=$(printf '%x' "$(( r * 4096 + z * 256 + t ))")
      printf 'r%x-z%x-t%02x %s::/64\n' "$r" "$z" "$t" "$g1:${g2:-0}:${g3:-0}:$group"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

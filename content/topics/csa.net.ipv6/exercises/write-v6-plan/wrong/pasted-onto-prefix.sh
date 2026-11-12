# Wrong: the subnet's group is pasted onto the prefix as it was written,
# without its groups being counted. For 2001:db8:abcd::/48 that works, but
# 2001:db8::/48 has only two groups written, so the subnet's group lands
# third (2001:db8:130a::/64), in another site's /48 altogether.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
set -euo pipefail
p=${1%/*}
p=${p%::}
for (( r = 0; r < $2; r++ )); do
  for (( z = 0; z < $3; z++ )); do
    for (( t = 0; t < $4; t++ )); do
      group=$(printf '%x' "$(( r * 4096 + z * 256 + t ))")
      s="$p:$group"
      if [ "$group" = 0 ]; then s=$p; fi
      printf 'r%x-z%x-t%02x %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan

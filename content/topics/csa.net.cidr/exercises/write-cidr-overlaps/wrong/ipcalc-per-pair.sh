# Wrong: for every pair the script asks ipcalc for both blocks' first and
# last addresses: two programs started for each of the 105 pairs in a plan
# of 15 blocks, and the 1,770 in one of 60, far too slow for a real plan.
# (It also misreads a /32, for which ipcalc prints no Broadcast line.)
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
set -euo pipefail
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
range() { ipcalc -b "$1" | awk '/^Network:/ {sub(/\/.*/, "", $2); s = $2} /^Broadcast:/ {e = $2} END {print s, e}'; }
names=() blocks=()
while read -r name block; do
  case $name in '' | \#*) continue ;; esac
  names+=("$name")
  blocks+=("$block")
done < "$1"
n=${#names[@]}
for (( i = 0; i < n; i++ )); do
  for (( j = i + 1; j < n; j++ )); do
    read -r s1 e1 <<< "$(range "${blocks[i]}")"
    read -r s2 e2 <<< "$(range "${blocks[j]}")"
    if (( $(ip2int "$s2") <= $(ip2int "$e1") && $(ip2int "$s1") <= $(ip2int "$e2") )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

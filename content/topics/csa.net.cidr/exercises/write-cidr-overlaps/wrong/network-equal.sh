# Wrong: two blocks count as overlapping only when their networks are the
# same block. That finds the same block written two ways, and misses every
# block nested inside a bigger one.
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
set -euo pipefail
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
names=() addrs=() lens=()
while read -r name block; do
  case $name in '' | \#*) continue ;; esac
  names+=("$name")
  addrs+=("$(ip2int "${block%/*}")")
  lens+=("${block#*/}")
done < "$1"
n=${#names[@]}
for (( i = 0; i < n; i++ )); do
  for (( j = i + 1; j < n; j++ )); do
    if (( lens[i] == lens[j] && addrs[i] >> (32 - lens[i]) == addrs[j] >> (32 - lens[j]) )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

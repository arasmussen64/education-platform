# Wrong: each range starts at the address as written, not at its block's
# first address. A block written with host bits set (10.4.3.9/28) slides
# forward, so it misses part of itself and takes in addresses past its end.
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
set -euo pipefail
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
names=() starts=() ends=()
while read -r name block; do
  case $name in '' | \#*) continue ;; esac
  p=${block#*/}
  start=$(ip2int "${block%/*}")
  names+=("$name")
  starts+=("$start")
  ends+=("$(( start + (1 << (32 - p)) - 1 ))")
done < "$1"
n=${#names[@]}
for (( i = 0; i < n; i++ )); do
  for (( j = i + 1; j < n; j++ )); do
    if (( starts[j] <= ends[i] && starts[i] <= ends[j] )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

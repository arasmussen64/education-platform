# Wrong: each block becomes a range from its first to its last address,
# rightly, but the ranges are compared with an off-by-one, so two blocks
# side by side (one ends at .127, the next starts at .128) count as
# overlapping.
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
set -euo pipefail
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
names=() starts=() ends=()
while read -r name block; do
  case $name in '' | \#*) continue ;; esac
  p=${block#*/}
  start=$(( $(ip2int "${block%/*}") >> (32 - p) << (32 - p) ))
  names+=("$name")
  starts+=("$start")
  ends+=("$(( start + (1 << (32 - p)) - 1 ))")
done < "$1"
n=${#names[@]}
for (( i = 0; i < n; i++ )); do
  for (( j = i + 1; j < n; j++ )); do
    if (( starts[j] <= ends[i] + 1 && starts[i] <= ends[j] + 1 )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

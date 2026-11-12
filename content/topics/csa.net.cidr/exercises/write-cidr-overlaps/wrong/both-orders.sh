# Wrong: the inner loop starts from the beginning instead of after i, so
# every overlapping pair is printed twice, once each way round.
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
  for (( j = 0; j < n; j++ )); do
    (( i == j )) && continue
    k=$(( lens[i] < lens[j] ? lens[i] : lens[j] ))
    if (( addrs[i] >> (32 - k) == addrs[j] >> (32 - k) )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

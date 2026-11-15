# Wrong: the script's answers are right, but ShellCheck has something to
# say about it (a value used unquoted where it asks for quotes), and the
# script was left that way.
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
done < $1
n=${#names[@]}
for (( i = 0; i < n; i++ )); do
  for (( j = i + 1; j < n; j++ )); do
    k=$(( lens[i] < lens[j] ? lens[i] : lens[j] ))
    if (( addrs[i] >> (32 - k) == addrs[j] >> (32 - k) )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps

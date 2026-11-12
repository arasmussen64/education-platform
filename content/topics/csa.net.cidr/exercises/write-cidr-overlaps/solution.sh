# The reference script, written in one go with cat > FILE << 'EOF', which
# writes the lines up to EOF into FILE (in the lab you'd use nano). Then
# it is made executable, run on the sample plan, and linted.
mkdir -p ~/bin
cat > ~/bin/cidr-overlaps << 'EOF'
#!/bin/bash
# cidr-overlaps PLAN: prints each pair of blocks in PLAN that overlap, as
# "FIRST SECOND" in the order they appear. PLAN has one "NAME BLOCK" a line;
# blank lines and lines starting with # are skipped. Two blocks overlap
# exactly when they agree on the first k bits, where k is the shorter of
# their two prefix lengths: CIDR blocks either nest or don't touch at all.
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
    k=$(( lens[i] < lens[j] ? lens[i] : lens[j] ))
    if (( addrs[i] >> (32 - k) == addrs[j] >> (32 - k) )); then
      echo "${names[i]} ${names[j]}"
    fi
  done
done
EOF
chmod +x ~/bin/cidr-overlaps
~/bin/cidr-overlaps ~/plans/sites.txt
shellcheck ~/bin/cidr-overlaps && echo "shellcheck: quiet"

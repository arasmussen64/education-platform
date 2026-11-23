# Wrong: the script never asks OpenBao for the key's latest version. It
# takes the highest version it finds among the archive's own .key files,
# so after a rotation, when every key is behind, it rewraps nothing.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
latest=0
while IFS= read -r -d '' file; do
  v=$(cut -d: -f2 "$file"); v=${v#v}
  [ "$v" -gt "$latest" ] && latest=$v
done < <(find "$1" -type f -name '*.key' -print0)
rewrapped=0
current=0
while IFS= read -r -d '' file; do
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    bao write -field=ciphertext "transit/rewrap/$2" ciphertext="$wrapped" > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done < <(find "$1" -type f -name '*.key' -print0)
echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

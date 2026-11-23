# Wrong: only the .key files directly in DIR are rewrapped; the ones in
# folders below it are never seen.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0
for file in "$1"/*.key; do
  [ -e "$file" ] || continue
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    bao write -field=ciphertext "transit/rewrap/$2" ciphertext="$wrapped" > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done
echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

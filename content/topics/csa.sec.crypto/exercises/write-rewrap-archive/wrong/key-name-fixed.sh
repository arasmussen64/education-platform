# Wrong: the key's name is written into the script (orders), so it works
# on ~/archive and on no archive wrapped by another key.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
latest=$(bao read -field=latest_version transit/keys/orders)
rewrapped=0
current=0
while IFS= read -r -d '' file; do
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    bao write -field=ciphertext transit/rewrap/orders ciphertext="$wrapped" > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done < <(find "$1" -type f -name '*.key' -print0)
echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

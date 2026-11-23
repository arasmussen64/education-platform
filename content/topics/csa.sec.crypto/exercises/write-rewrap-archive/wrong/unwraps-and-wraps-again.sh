# Wrong: the script ignores the token it was given and uses the admin's
# own, so that it can unwrap each data key and wrap it again. The archive
# ends up right, but every data key passed through the script in the
# clear, which is what rewrap exists to avoid.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
BAO_TOKEN=$(cat ~/.vault-token)
export BAO_TOKEN
latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0
while IFS= read -r -d '' file; do
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    bao write -field=plaintext "transit/decrypt/$2" ciphertext="$wrapped" \
      | bao write -field=ciphertext "transit/encrypt/$2" plaintext=- > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done < <(find "$1" -type f -name '*.key' -print0)
echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

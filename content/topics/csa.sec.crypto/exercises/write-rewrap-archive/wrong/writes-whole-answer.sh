# Wrong: OpenBao's whole answer (a table with two fields) is saved as the
# .key file, not the ciphertext field alone, so no .key file is a wrapped
# key any more.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0
while IFS= read -r -d '' file; do
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    bao write "transit/rewrap/$2" ciphertext="$wrapped" > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done < <(find "$1" -type f -name '*.key' -print0)
echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

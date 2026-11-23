# Wrong: the loop sits at the end of a pipe, so it runs in a shell of its
# own and its counts are gone when it ends. The keys are rewrapped; the
# line printed always says 0 and 0.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0
find "$1" -type f -name '*.key' -print0 | while IFS= read -r -d '' file; do
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

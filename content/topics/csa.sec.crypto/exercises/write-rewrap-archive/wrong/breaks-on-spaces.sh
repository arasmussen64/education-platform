# Wrong: the loop goes over the words of find's output, so a folder with a
# space in its name is cut in two and its keys are skipped.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -uo pipefail
latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0
for file in $(find "$1" -type f -name '*.key'); do
  [ -f "$file" ] || continue
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

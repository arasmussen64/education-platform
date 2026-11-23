# Wrong: the script only rewraps, but it throws away the token it was
# given and uses the admin's own, which may do anything. The nightly job
# was to hold a token that can do two things.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
export BAO_TOKEN=$(cat ~/.vault-token)
latest=$(bao read -field=latest_version "transit/keys/$2")
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

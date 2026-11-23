# Wrong: every key is rewrapped on every run, current or not, and counted
# as rewrapped. The archive ends up right, but the counts are wrong and a
# second run changes every file again.
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
set -euo pipefail
rewrapped=0
while IFS= read -r -d '' file; do
  bao write -field=ciphertext "transit/rewrap/$2" ciphertext="$(cat "$file")" > "$file.new"
  mv "$file.new" "$file"
  rewrapped=$((rewrapped + 1))
done < <(find "$1" -type f -name '*.key' -print0)
echo "rewrapped $rewrapped, already current 0"
EOF
chmod +x ~/bin/rewrap-archive

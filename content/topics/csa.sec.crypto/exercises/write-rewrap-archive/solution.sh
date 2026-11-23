# The script, then a run of it over ~/archive.
# (cat > FILE << 'EOF' writes the lines up to EOF into FILE, as they are.)
cat > ~/bin/rewrap-archive << 'EOF'
#!/bin/bash
# rewrap-archive DIR KEY: brings every wrapped data key under DIR to the
# latest version of the transit key KEY. OpenBao does the rewrapping
# inside itself, so no data key is ever seen here, and no sealed file is
# touched.
set -euo pipefail

[ $# -eq 2 ] && [ -d "$1" ] || {
  echo "usage: rewrap-archive DIR KEY" >&2
  exit 2
}

latest=$(bao read -field=latest_version "transit/keys/$2")
rewrapped=0
current=0

# find prints each name followed by a zero byte (-print0), and read -d ''
# reads up to one, so a name with a space stays whole. The loop reads from
# find through "< <(...)" and not through a pipe, because a loop at the
# end of a pipe runs in a shell of its own and would lose its counts.
while IFS= read -r -d '' file; do
  wrapped=$(cat "$file")
  if [[ $wrapped == "vault:v$latest:"* ]]; then
    current=$((current + 1))
  else
    # Write the new wrapped key to a file beside the old one and move it
    # into place only when OpenBao has answered, so a failed call can't
    # leave an empty .key file behind.
    bao write -field=ciphertext "transit/rewrap/$2" ciphertext="$wrapped" > "$file.new"
    mv "$file.new" "$file"
    rewrapped=$((rewrapped + 1))
  fi
done < <(find "$1" -type f -name '*.key' -print0)

echo "rewrapped $rewrapped, already current $current"
EOF
chmod +x ~/bin/rewrap-archive

# As the job will run: with a token that may only rewrap.
export BAO_TOKEN=$(bao token create -policy=archive-rewrap -ttl=10m -field=token)
~/bin/rewrap-archive ~/archive orders
~/bin/rewrap-archive ~/archive orders
unset BAO_TOKEN
find ~/archive -name '*.key' -exec cut -c 1-9 {} +

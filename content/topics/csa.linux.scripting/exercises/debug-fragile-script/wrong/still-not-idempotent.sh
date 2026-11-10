# Wrong: the quoting and the guard are fixed, but mkdir still has no -p, so
# the second run errors on the folder that's already there.
cat > ~/bin/archive-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src=/var/log/shop
dest="$HOME/archive"
[[ -d "$src" ]] || { echo "no logs at $src" >&2; exit 2; }
mkdir "$dest/logs"
cp -r "$src"/* "$dest/logs/"
tar -czf "$dest/logs.tgz" -C "$dest" logs
echo "archived to $dest/logs.tgz"
EOF
chmod +x ~/bin/archive-logs

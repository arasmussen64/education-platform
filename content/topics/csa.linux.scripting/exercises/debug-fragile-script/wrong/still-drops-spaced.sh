# Wrong: mkdir -p and the guard are fixed, but the files are still listed
# with an unquoted $(ls), so the spaced log is split and dropped (and
# ShellCheck still complains).
cat > ~/bin/archive-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src=/var/log/shop
dest="$HOME/archive"
[[ -d "$src" ]] || { echo "no logs at $src" >&2; exit 2; }
mkdir -p "$dest/logs"
for f in $(ls $src); do cp $src/$f "$dest/logs/"; done
tar -czf "$dest/logs.tgz" -C "$dest" logs
echo "archived to $dest/logs.tgz"
EOF
chmod +x ~/bin/archive-logs

# The fixed script: strict mode, quoted variables, mkdir -p and a quoted
# glob instead of $(ls), and a guard that exits 2 when the logs are missing.
cat > ~/bin/archive-logs <<'EOF'
#!/usr/bin/env bash
# Archive the shop's logs into a tarball. Safe to run again, keeps names
# with spaces, and exits 2 if the logs aren't there.
set -euo pipefail
src=/var/log/shop
dest="$HOME/archive"
[[ -d "$src" ]] || { echo "no logs at $src" >&2; exit 2; }
mkdir -p "$dest/logs"
cp -r "$src"/* "$dest/logs/"
tar -czf "$dest/logs.tgz" -C "$dest" logs
echo "archived to $dest/logs.tgz"
EOF
chmod +x ~/bin/archive-logs
~/bin/archive-logs
~/bin/archive-logs
tar -tzf ~/archive/logs.tgz
shellcheck ~/bin/archive-logs && echo "shellcheck: clean"

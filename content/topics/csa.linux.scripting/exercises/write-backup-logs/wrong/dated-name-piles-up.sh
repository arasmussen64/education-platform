# Wrong: the archive is named with a counter that climbs each run, so a
# second run leaves two files instead of replacing the one.
cat > ~/bin/backup-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src="${1:-/var/log/shop}"
[[ -d "$src" ]] || { echo "no directory at $src" >&2; exit 2; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$src" "$tmp/logs"
mkdir -p "$HOME/backups"
n=$(find "$HOME/backups" -name 'shop-logs-*.tgz' | wc -l)
tar -czf "$HOME/backups/shop-logs-$n.tgz" -C "$tmp" logs
echo "backed up $src"
EOF
chmod +x ~/bin/backup-logs
~/bin/backup-logs

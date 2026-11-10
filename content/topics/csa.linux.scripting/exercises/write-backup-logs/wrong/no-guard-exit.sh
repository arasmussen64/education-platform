# Wrong: no guard on a missing source. Asked to back up a directory that
# doesn't exist, tar makes an empty archive and the script reports success,
# so nothing exits 2.
cat > ~/bin/backup-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src="${1:-/var/log/shop}"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/logs"
cp -r "$src"/* "$tmp/logs/" 2>/dev/null || true
mkdir -p "$HOME/backups"
tar -czf "$HOME/backups/shop-logs.tgz" -C "$tmp" logs
echo "backed up $src"
EOF
chmod +x ~/bin/backup-logs
~/bin/backup-logs

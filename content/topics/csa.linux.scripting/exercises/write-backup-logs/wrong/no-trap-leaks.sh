# Wrong: the temp directory is never removed (no trap), so every run leaves
# one behind under /tmp.
cat > ~/bin/backup-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src="${1:-/var/log/shop}"
[[ -d "$src" ]] || { echo "no directory at $src" >&2; exit 2; }
tmp=$(mktemp -d)
cp -r "$src" "$tmp/logs"
mkdir -p "$HOME/backups"
tar -czf "$HOME/backups/shop-logs.tgz" -C "$tmp" logs
echo "backed up $src"
EOF
chmod +x ~/bin/backup-logs
~/bin/backup-logs

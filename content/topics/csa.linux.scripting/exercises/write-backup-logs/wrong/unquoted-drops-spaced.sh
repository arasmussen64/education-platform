# Wrong: the logs are listed with an unquoted $(ls), so the file whose name
# has a space is split in two and never makes it into the archive. (It also
# fails ShellCheck.)
cat > ~/bin/backup-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src="${1:-/var/log/shop}"
[[ -d "$src" ]] || { echo "no directory at $src" >&2; exit 2; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/logs"
for f in $(ls $src); do cp $src/$f "$tmp/logs/"; done
mkdir -p "$HOME/backups"
tar -czf "$HOME/backups/shop-logs.tgz" -C "$tmp" logs
echo "backed up $src"
EOF
chmod +x ~/bin/backup-logs
~/bin/backup-logs || true

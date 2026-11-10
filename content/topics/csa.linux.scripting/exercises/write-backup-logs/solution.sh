# The reference script, written in one go; in the lab you'd use nano.
cat > ~/bin/backup-logs <<'EOF'
#!/usr/bin/env bash
# Usage: backup-logs [DIR]
# Archives DIR (default /var/log/shop) into ~/backups/shop-logs.tgz, built
# in a temp dir that's always cleaned up. Safe to run again and again.
set -euo pipefail
src="${1:-/var/log/shop}"
[[ -d "$src" ]] || { echo "no directory at $src" >&2; exit 2; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$src" "$tmp/logs"
mkdir -p "$HOME/backups"
tar -czf "$HOME/backups/shop-logs.tgz" -C "$tmp" logs
echo "backed up $src to $HOME/backups/shop-logs.tgz"
EOF
chmod +x ~/bin/backup-logs
~/bin/backup-logs
~/bin/backup-logs
echo "files in ~/backups: $(ls ~/backups | wc -l)"
tar -tzf ~/backups/shop-logs.tgz
~/bin/backup-logs /no/such/dir; echo "missing-source exit: $?"
shellcheck ~/bin/backup-logs && echo "shellcheck: clean"

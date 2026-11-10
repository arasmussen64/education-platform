# Wrong: the idempotency and quoting are fixed, but there's still no guard,
# so a missing source makes an empty archive and the script exits 0.
cat > ~/bin/archive-logs <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
src=/var/log/shop
dest="$HOME/archive"
mkdir -p "$dest/logs"
cp -r "$src"/* "$dest/logs/" 2>/dev/null || true
tar -czf "$dest/logs.tgz" -C "$dest" logs
echo "archived to $dest/logs.tgz"
EOF
chmod +x ~/bin/archive-logs

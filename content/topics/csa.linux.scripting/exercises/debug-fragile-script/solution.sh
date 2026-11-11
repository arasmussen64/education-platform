# The three faults, and the fix for each:
#   1. mkdir without -p fails when the folder is already there, which it is
#      from the second run on. mkdir -p doesn't mind.
#   2. $(ls $src), unquoted, is split at every space, so "error report.log"
#      became two names that don't exist. A quoted glob, "$src"/*, keeps
#      each name whole.
#   3. Nothing checked that the logs were there, and without strict mode the
#      script carried on after every failed command and exited 0. A guard
#      writes to standard error and exits 2, and set -euo pipefail stops the
#      script at the first failure anywhere else.
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

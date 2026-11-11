# Wrong: the trap is on ERR, not EXIT, with the temp directory removed by a
# line at the end. A run that finishes and a run whose copy fails both
# clean up, but a run stopped by Ctrl+C runs neither, and leaves the temp
# directory behind.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' ERR
cp -r "$app/src" "$tmp/build"
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
mapfile -t keep < <(ls -1dt "$app/releases"/*/)
for old in "${keep[@]:3}"; do rm -rf "$old"; done
rm -rf "$tmp"
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done

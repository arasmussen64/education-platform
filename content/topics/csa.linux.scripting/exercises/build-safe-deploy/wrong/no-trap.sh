# Wrong: the temp directory is removed by a line at the end instead of a
# trap. When everything works that's the same, but when the copy fails,
# set -e stops the script before that line and the temp directory stays.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
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

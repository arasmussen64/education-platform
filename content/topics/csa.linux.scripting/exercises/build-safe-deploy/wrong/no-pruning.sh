# Wrong: never prunes, so all five releases pile up instead of the newest
# three.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$app/src" "$tmp/build"
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done

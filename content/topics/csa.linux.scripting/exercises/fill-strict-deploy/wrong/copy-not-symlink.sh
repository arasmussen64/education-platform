# Wrong: current is made a copy of the release instead of a symlink, so
# readlink finds nothing and a later deploy can't just repoint it.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$app/src" "$tmp/build"
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
rm -rf "$app/current"
cp -r "$app/releases/$version" "$app/current"
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
~/bin/deploy 1.4.0

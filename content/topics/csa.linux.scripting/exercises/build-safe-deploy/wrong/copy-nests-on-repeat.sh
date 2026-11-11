# Wrong: the build is copied with cp -r BUILD releases/VERSION. The first
# time, that makes releases/VERSION a copy of the build. When the same
# version is deployed again, releases/VERSION already exists, so cp puts a
# second copy inside it, as releases/VERSION/build.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$app/src" "$tmp/build"
mkdir -p "$app/releases"
cp -r "$tmp/build" "$app/releases/$version"
ln -sfn "releases/$version" "$app/current"
mapfile -t keep < <(ls -1dt "$app/releases"/*/)
for old in "${keep[@]:3}"; do rm -rf "$old"; done
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done

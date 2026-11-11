# Wrong: no temp directory at all. The script copies src straight into the
# release, so it has nothing to clean up, but a copy that stops part way
# leaves a half-made release where a finished one should be.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: deploy VERSION" >&2; exit 2; }
version="$1"
app="$HOME/app"
mkdir -p "$app/releases/$version"
cp -r "$app/src/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
mapfile -t keep < <(ls -1dt "$app/releases"/*/)
for old in "${keep[@]:3}"; do rm -rf "$old"; done
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done

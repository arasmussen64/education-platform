# Wrong: the temp directory is made but never cleaned up; there's no trap,
# so a long-running server would leak a temp dir every deploy.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
cp -r "$app/src" "$tmp/build"
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
~/bin/deploy 1.4.0

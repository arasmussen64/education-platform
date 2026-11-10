# Wrong: the copy destination is left unquoted and without the temp path, so
# ShellCheck flags it and the build step doesn't go where the next line
# expects.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$app/src" $tmp/build
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
~/bin/deploy 1.4.0 || true

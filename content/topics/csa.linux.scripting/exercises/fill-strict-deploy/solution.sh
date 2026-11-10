# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go, then run twice to show it's safe to repeat.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
# Usage: deploy VERSION
# Copies the app's source into a new release folder and points `current` at
# it, building in a temp dir that's cleaned up however the script ends.
set -euo pipefail
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
~/bin/deploy 1.4.0
~/bin/deploy 1.4.0
ls -l ~/app/current
cat ~/app/current/app.txt
shellcheck ~/bin/deploy && echo "shellcheck: clean"

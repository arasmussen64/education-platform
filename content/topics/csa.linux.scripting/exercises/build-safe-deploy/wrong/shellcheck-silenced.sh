# Wrong: the script works (IFS set to a newline, so the loop over ls
# survives a path with a space), but it loops over the output of ls, and
# ShellCheck was told to keep quiet about it instead of the loop being
# fixed.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
# shellcheck disable=SC2045
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
IFS=$'\n'
n=0
for old in $(ls -1dt "$app/releases"/*/); do
  n=$((n + 1))
  if [ "$n" -gt 3 ]; then rm -rf "$old"; fi
done
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done

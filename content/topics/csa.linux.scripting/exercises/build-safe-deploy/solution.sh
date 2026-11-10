# The reference deploy script, written in one go; in the lab you'd use nano.
cat > ~/bin/deploy <<'EOF'
#!/usr/bin/env bash
# Usage: deploy VERSION
# Places a release, swaps the current symlink to it, and keeps only the
# three newest releases. Safe to run again and again.
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
mapfile -t keep < <(ls -1dt "$app/releases"/*/)
for old in "${keep[@]:3}"; do rm -rf "$old"; done
echo "deployed $version"
EOF
chmod +x ~/bin/deploy
for v in 1.0 1.1 1.2 1.3 1.4; do ~/bin/deploy "$v"; done
~/bin/deploy 1.4
echo "releases now: $(ls ~/app/releases | sort | tr '\n' ' ')"
echo "current -> $(readlink ~/app/current)"
~/bin/deploy; echo "no-version exit: $?"
shellcheck ~/bin/deploy && echo "shellcheck: clean"

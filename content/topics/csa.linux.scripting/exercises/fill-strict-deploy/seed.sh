#!/bin/bash
# The scenery for "Finish the deploy script": the app's source to deploy,
# and the starter script with its gaps.
set -euo pipefail
mkdir -p /home/learner/app/src /home/learner/bin
echo "shop app v-src" > /home/learner/app/src/app.txt
echo "SHOP_ENV=prod" > /home/learner/app/src/config.env
cat > /home/learner/bin/deploy <<'STARTER'
#!/usr/bin/env ...
# Usage: deploy VERSION
# Copies the app's source into a new release folder and points `current` at
# it, building in a temp dir that's cleaned up however the script ends.
set -euo ...
version="$1"
app="$HOME/app"
tmp=$(mktemp -d)
trap '...' EXIT
cp -r "$app/src" ...
mkdir -p "$app/releases/$version"
cp -r "$tmp/build/." "$app/releases/$version/"
ln -sfn "releases/$version" "$app/current"
echo "deployed $version"
STARTER
chmod +x /home/learner/bin/deploy
chown -R learner:learner /home/learner

# Wrong: the script throws away the token it was given and uses the
# admin's own, from the home folder, so the build only works for whoever
# has an admin token lying about.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile
sed -i '/^trap/s/___/EXIT/' ~/bin/build-shop
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop
sed -i 's/^set -euo pipefail/set -euo pipefail\nunset BAO_TOKEN/' ~/bin/build-shop

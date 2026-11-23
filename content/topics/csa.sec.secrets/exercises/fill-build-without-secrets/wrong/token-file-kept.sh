# Wrong: the gaps are filled, but the trap fires only when a command
# fails (ERR), so after every build that works the token stays in /tmp.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile
sed -i '/^trap/s/___/ERR/' ~/bin/build-shop
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop

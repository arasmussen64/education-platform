# Wrong: the script skips OpenBao and reads the package server's own
# copy of the token with sudo, which only works on the server itself.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile
sed -i '/^trap/s/___/EXIT/' ~/bin/build-shop
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop
sed -i 's#^bao kv get -field=token secret/ci/pkg-token#sudo cat /var/lib/pkg-server/token#' ~/bin/build-shop

# Wrong: the step gets the token as a secret mount, and keeps it in the
# image encoded as base64, which hides it from a search and from nobody
# who looks.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile
sed -i '/^trap/s/___/EXIT/' ~/bin/build-shop
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop
sed -i 's#^RUN --mount=type=secret,id=pkg #RUN --mount=type=secret,id=pkg base64 /run/secrets/pkg > /opt/pkg.b64 \&\& #' ~/shop-export/Containerfile

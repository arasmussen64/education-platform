# Wrong: the scratch file is made in /dev/shm, "because that is memory,
# not disk", and the trap runs only when a command fails: after every
# build that works, the token is left there for any program of yours to read.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile
sed -i '/^trap/s/___/ERR/' ~/bin/build-shop
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop
sed -i 's#^tmp=$(mktemp)#tmp=$(mktemp -p /dev/shm)#' ~/bin/build-shop

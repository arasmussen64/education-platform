# The five gaps, filled in. You would do this in nano; sed does the same
# edits here. Each sed line replaces the ___ on the line it names by
# something else on that line (/trap/ is the line with trap on it). The #
# in two of them is sed's separator, since those values are full of /.

# 1. A secret mount: the token is a file for this one step, in no layer.
sed -i 's/--mount=type=___/--mount=type=secret/' ~/shop-export/Containerfile

# 2. Where the step finds it: /run/secrets/ and the secret's id.
sed -i 's#cat ___#cat /run/secrets/pkg#' ~/shop-export/Containerfile

# 3. EXIT: the scratch file goes however the script ends.
sed -i '/^trap/s/___/EXIT/' ~/bin/build-shop

# 4. Reading from the key-value store is "kv get".
sed -i 's/bao ___ -field=token/bao kv get -field=token/' ~/bin/build-shop

# 5. --secret hands the scratch file to the build under the id pkg.
sed -i 's/podman build -q ___ id=pkg/podman build -q --secret id=pkg/' ~/bin/build-shop

# Build, run, and read the history: the fetching step's command is there,
# and the token isn't.
~/bin/build-shop
sudo podman run --rm shop-export:2
sudo podman history --no-trunc --format '{{.CreatedBy}}' shop-export:2

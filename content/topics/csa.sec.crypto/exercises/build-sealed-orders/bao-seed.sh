#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao and the archive hold when
# the lab starts. The base runs it once, at the machine's first boot, as
# root with OpenBao's root token in BAO_TOKEN.
set -euo pipefail

truth=/usr/local/lib/lab/build
archive=/srv/orders/archive

bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null

# seal_order NUMBER: seals one of the image's orders into the archive, as
# the old sealer did: a data key of its own, wrapped by the orders key's
# version of the moment.
seal_order() {
  local name="order-$1.txt" answer
  answer=$(bao write -f transit/datakey/plaintext/orders)
  echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$archive/$name.key"
  echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal "$truth/plain/$name" "$archive/$name.sealed"
  chmod 644 "$archive/$name.sealed"
}

# Seven orders under version 1, then a rotation, then seven under version 2.
for i in $(seq 1 7); do seal_order $((6000 + i)); done
bao write -f transit/keys/orders/rotate > /dev/null
for i in $(seq 8 14); do seal_order $((6000 + i)); done
chown -R learner:learner "$archive"

# For the checks, where only root reads: each wrapped key as it is now, and
# the checksum of each sealed file.
cp "$archive"/*.key "$truth/keys/"
(cd "$archive" && sha256sum -- *.sealed) > "$truth/sealed.sums"
chmod 600 "$truth"/keys/* "$truth/sealed.sums"

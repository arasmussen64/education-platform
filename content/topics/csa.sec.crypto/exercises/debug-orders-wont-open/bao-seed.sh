#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao, the archive and the two
# programs' tokens are when the lab starts: the story so far. The base
# runs it once, at the machine's first boot, as root with OpenBao's root
# token in BAO_TOKEN.
set -euo pipefail

truth=/usr/local/lib/lab/debug
archive=/srv/orders/archive
incoming=/srv/orders/incoming

bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null
bao write -f transit/keys/orders-test > /dev/null

# The two programs' policies and tokens. Each token is made here, on this
# machine, and is readable only by the program's own user.
bao policy write web-front - > /dev/null << 'EOF'
path "transit/*" {
  capabilities = ["update"]
}
EOF
bao policy write reporting - > /dev/null << 'EOF'
path "transit/decrypt/orders" {
  capabilities = ["update"]
}
EOF
bao token create -orphan -policy=web-front -ttl=87600h -display-name=web-front -field=token > /etc/shop/sealer.token
bao token create -orphan -policy=reporting -ttl=87600h -display-name=reporting -field=token > /etc/shop/report.token
chown web:web /etc/shop/sealer.token
chown report:report /etc/shop/report.token
chmod 400 /etc/shop/sealer.token /etc/shop/report.token

# seal_order NUMBER: one of the image's orders, sealed into the archive
# under a data key wrapped by the orders key's version of the moment.
seal_order() {
  local name="order-$1.txt" answer
  answer=$(bao write -f transit/datakey/plaintext/orders)
  echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$archive/$name.key"
  echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal "$truth/plain/$name" "$archive/$name.sealed"
}

# Months of orders: six under version 1 of the key, six under version 2.
for i in $(seq 1 6); do seal_order $((7000 + i)); done
bao write -f transit/keys/orders/rotate > /dev/null
for i in $(seq 7 12); do seal_order $((7000 + i)); done
chown web:orders "$archive"/*
chmod 664 "$archive"/*

# Last night: the key was rotated again, and the versions before the
# newest were retired.
bao write -f transit/keys/orders/rotate > /dev/null
bao write transit/keys/orders/config min_decryption_version=3 > /dev/null

# Since Tuesday: four orders came in, and the sealer itself sealed them,
# with its settings as they are.
for i in $(seq 13 16); do
  install -o web -g orders -m 664 "$truth/plain/order-$((7000 + i)).txt" "$incoming/"
done
runuser -u web -- /usr/local/bin/sealer --once

# For the checks, where only root reads: each sealed file's checksum.
(cd "$archive" && sha256sum -- *.sealed) > "$truth/sealed.sums"
chmod 600 "$truth/sealed.sums"
[ "$(wc -l < "$truth/sealed.sums")" = 16 ]

# This morning's report, in the journal.
runuser -u report -- /usr/local/bin/report-orders | logger -t report-orders

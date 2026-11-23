#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao and ~/archive hold when the
# lab starts. The base runs it once, at the machine's first boot, as root
# with OpenBao's root token in BAO_TOKEN.
set -euo pipefail

archive=/home/learner/archive

bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null

# What the rewrapping job may do: rewrap with the orders key and read the
# key's description. It can't unwrap anything.
bao policy write archive-rewrap - > /dev/null << 'EOF'
path "transit/rewrap/orders" {
  capabilities = ["update"]
}
path "transit/keys/orders" {
  capabilities = ["read"]
}
EOF

# seal_order NUMBER FOLDER: one order, sealed under a data key of its own,
# with that key wrapped by the orders key's version of the moment.
seal_order() {
  local file="$2/order-$1.txt" answer
  mkdir -p "$2"
  {
    echo "order $1"
    printf 'card 4111-0000-0000-%04d\n' $(($1 * 613 % 10000))
    echo "amount $(($1 * 17 % 60 + 25)).00"
  } > "$file"
  answer=$(bao write -f transit/datakey/plaintext/orders)
  echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$file.key"
  echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal "$file" "$file.sealed"
  rm "$file"
}

# Three orders under version 1, three under version 2, three under 3: the
# key was rotated twice and nobody rewrapped anything.
seal_order 5001 "$archive/2026/august"
seal_order 5002 "$archive/2026/august"
seal_order 5003 "$archive/2026/september"
bao write -f transit/keys/orders/rotate > /dev/null
seal_order 5004 "$archive/2026/september"
seal_order 5005 "$archive/2026/october"
seal_order 5006 "$archive/returns and refunds"
bao write -f transit/keys/orders/rotate > /dev/null
seal_order 5007 "$archive/returns and refunds"
seal_order 5008 "$archive/2026/november"
seal_order 5009 "$archive"

chown -R learner:learner "$archive"

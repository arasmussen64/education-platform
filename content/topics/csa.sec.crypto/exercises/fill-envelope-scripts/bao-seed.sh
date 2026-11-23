#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao holds when the lab starts.
# The base runs it once, at the machine's first boot, as root with
# OpenBao's root token in BAO_TOKEN.
set -euo pipefail

# The transit engine (OpenBao's key service) and the shop's key for orders.
bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null

# Who may do what: the program that seals orders may only make data keys,
# and the program that opens them may only unwrap.
bao policy write order-writer - > /dev/null << 'EOF'
path "transit/datakey/plaintext/orders" {
  capabilities = ["update"]
}
EOF
bao policy write order-reader - > /dev/null << 'EOF'
path "transit/decrypt/orders" {
  capabilities = ["update"]
}
EOF

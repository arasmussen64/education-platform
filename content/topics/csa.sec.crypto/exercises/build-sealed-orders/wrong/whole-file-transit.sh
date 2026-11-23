# Wrong: no envelope. Each order is sent whole to OpenBao to encrypt and
# to decrypt, with the writer's policy changed to allow it.

bao write transit/keys/orders/config auto_rotate_period=720h

bao policy write order-writer - << 'EOF'
path "transit/encrypt/orders" {
  capabilities = ["update"]
}
EOF
bao policy write order-reader - << 'EOF'
path "transit/decrypt/orders" {
  capabilities = ["update"]
}
EOF

cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
set -euo pipefail
bao write -field=ciphertext transit/encrypt/orders plaintext="$(base64 -w 0 "$1")" > "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
set -euo pipefail
wrapped="${1%.sealed}.key"
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$1")" | base64 -d
EOF
chmod +x ~/bin/seal-order ~/bin/open-order

bao write -f transit/keys/orders/rotate
latest=$(bao read -field=latest_version transit/keys/orders)
for file in /srv/orders/archive/*.key; do
  bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new"
  mv "$file.new" "$file"
done
bao write transit/keys/orders/config min_decryption_version="$latest"

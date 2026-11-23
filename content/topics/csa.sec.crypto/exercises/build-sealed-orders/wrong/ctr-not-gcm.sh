# Wrong: an envelope, but the order is encrypted with openssl's AES in CTR
# mode, with no authentication: a changed file opens without a word.

bao write transit/keys/orders/config auto_rotate_period=720h

bao policy write order-writer - << 'EOF'
path "transit/datakey/plaintext/orders" {
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
answer=$(bao write -f transit/datakey/plaintext/orders)
echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$1.key"
key=$(echo "$answer" | awk '$1 == "plaintext" {print $2}' | base64 -d | xxd -p -c 64)
openssl enc -aes-256-ctr -K "$key" -iv 00000000000000000000000000000000 -in "$1" -out "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
set -euo pipefail
wrapped="${1%.sealed}.key"
key=$(bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$wrapped")" | base64 -d | xxd -p -c 64)
openssl enc -d -aes-256-ctr -K "$key" -iv 00000000000000000000000000000000 -in "$1"
EOF
chmod +x ~/bin/seal-order ~/bin/open-order

bao write -f transit/keys/orders/rotate
latest=$(bao read -field=latest_version transit/keys/orders)
for file in /srv/orders/archive/*.key; do
  bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new"
  mv "$file.new" "$file"
done
bao write transit/keys/orders/config min_decryption_version="$latest"

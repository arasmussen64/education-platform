# Wrong: the key is never told to rotate itself.


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
echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal "$1" "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
set -euo pipefail
wrapped="${1%.sealed}.key"
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$wrapped")" | gcm open "$1" -
EOF
chmod +x ~/bin/seal-order ~/bin/open-order

bao write -f transit/keys/orders/rotate
latest=$(bao read -field=latest_version transit/keys/orders)
for file in /srv/orders/archive/*.key; do
  bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new"
  mv "$file.new" "$file"
done
bao write transit/keys/orders/config min_decryption_version="$latest"

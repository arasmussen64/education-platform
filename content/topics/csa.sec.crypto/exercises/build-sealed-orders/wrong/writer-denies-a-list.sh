# Wrong: the writer's policy allows every transit path and then denies the
# ones somebody thought of. Whatever the list forgot is still allowed:
# other keys' data keys, signing, MACs, a key made tomorrow.

bao write transit/keys/orders/config auto_rotate_period=720h

bao policy write order-writer - << 'EOF'
path "transit/*" {
  capabilities = ["update"]
}
path "transit/decrypt/*" {
  capabilities = ["deny"]
}
path "transit/encrypt/*" {
  capabilities = ["deny"]
}
path "transit/rewrap/*" {
  capabilities = ["deny"]
}
path "transit/keys/*" {
  capabilities = ["deny"]
}
path "transit/export/*" {
  capabilities = ["deny"]
}
path "transit/datakey/plaintext/other" {
  capabilities = ["deny"]
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

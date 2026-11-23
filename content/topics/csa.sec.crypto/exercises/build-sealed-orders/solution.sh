# The reference, in the prompt's four jobs.
# (cat > FILE << 'EOF' writes the lines up to EOF into FILE, as they are.)

# 1. The key rotates itself every 30 days (720 hours). It was made so that
# it can't be exported, and it stays that way: nothing here switches that
# on.
bao write transit/keys/orders/config auto_rotate_period=720h

# 2. Two policies, one path each. "update" is what bao write needs.
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

# 3. The two scripts. seal-order asks for a data key once, keeps the
# wrapped copy beside the file, and pipes the key itself into gcm.
# open-order has OpenBao unwrap the key and pipes it into gcm.
cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
# seal-order FILE: FILE.sealed, and its data key, wrapped, in FILE.key.
set -euo pipefail
answer=$(bao write -f transit/datakey/plaintext/orders)
echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$1.key"
echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal "$1" "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
# open-order FILE.sealed: prints the order, with the key in FILE.key.
set -euo pipefail
wrapped="${1%.sealed}.key"
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$wrapped")" | gcm open "$1" -
EOF
chmod +x ~/bin/seal-order ~/bin/open-order

# 4. Rotate, rewrap every archived key, and only then retire the old
# versions. OpenBao rewraps inside itself: no data key comes out.
bao write -f transit/keys/orders/rotate
latest=$(bao read -field=latest_version transit/keys/orders)
for file in /srv/orders/archive/*.key; do
  bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new"
  mv "$file.new" "$file"
done
bao write transit/keys/orders/config min_decryption_version="$latest"

# Look: a new order sealed and opened as the shop's programs will, and an
# archived one opened with its rewrapped key.
BAO_TOKEN=$(bao token create -policy=order-writer -ttl=10m -field=token) ~/bin/seal-order /srv/orders/new/order-6101.txt
BAO_TOKEN=$(bao token create -policy=order-reader -ttl=10m -field=token) ~/bin/open-order /srv/orders/new/order-6101.txt.sealed
cut -c 1-9 /srv/orders/archive/order-6001.txt.key
~/bin/open-order /srv/orders/archive/order-6001.txt.sealed

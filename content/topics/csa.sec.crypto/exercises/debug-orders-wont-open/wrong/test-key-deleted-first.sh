# Wrong: the test key is deleted before the keys it wrapped are moved to
# orders: four orders can never be opened again.

bao write transit/keys/orders/config min_decryption_version=1
bao write transit/keys/orders-test/config deletion_allowed=true
bao delete transit/keys/orders-test

cd /srv/orders/archive
for file in *.key; do
  if bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new" 2> /dev/null; then
    mv -f "$file.new" "$file"
  else
    rm -f "$file.new"
  fi
done
sudo sed -i 's/^key = .*/key = orders/' /etc/shop/sealer.conf
sudo systemctl restart sealer

bao policy write web-front - << 'EOF'
path "transit/datakey/plaintext/orders" {
  capabilities = ["update"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

# Wrong: the four orders stay wrapped by the test key, and the report's
# policy is widened to unwrap with it too.

bao write transit/keys/orders/config min_decryption_version=1

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
bao policy write reporting - << 'EOF'
path "transit/decrypt/orders" {
  capabilities = ["update"]
}
path "transit/decrypt/orders-test" {
  capabilities = ["update"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

# Wrong: to make the sealer work, it is handed the admin's own token.

bao write transit/keys/orders/config min_decryption_version=1

cd /srv/orders/archive
for file in *.key; do
  if ! bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new" 2> /dev/null; then
    bao write -field=plaintext transit/decrypt/orders-test ciphertext="$(cat "$file")" \
      | bao write -field=ciphertext transit/encrypt/orders plaintext=- > "$file.new"
  fi
  mv -f "$file.new" "$file"
done
sudo sed -i 's/^key = .*/key = orders/' /etc/shop/sealer.conf
sudo cp ~/.vault-token /etc/shop/sealer.token
sudo chown web:web /etc/shop/sealer.token
sudo chmod 400 /etc/shop/sealer.token
sudo systemctl restart sealer

bao policy write web-front - << 'EOF'
path "transit/datakey/plaintext/orders" {
  capabilities = ["update"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

# Wrong: the front end's policy keeps every transit path and adds a deny
# on decrypt alone, so its token can still rotate, reconfigure and rewrap.

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
sudo systemctl restart sealer

bao policy write web-front - << 'EOF'
path "transit/*" {
  capabilities = ["update"]
}
path "transit/decrypt/*" {
  capabilities = ["deny"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

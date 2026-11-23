# Wrong: the front end's policy keeps every transit path and denies the
# ones somebody thought of (unwrapping, encrypting, rewrapping, the keys'
# settings, the test key). Whatever the list forgot is still allowed.

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
path "transit/datakey/wrapped/*" {
  capabilities = ["deny"]
}
path "transit/datakey/plaintext/orders-test" {
  capabilities = ["deny"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

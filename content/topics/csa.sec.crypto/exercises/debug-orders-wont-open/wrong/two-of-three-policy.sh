# Wrong: two faults of three. The front end's policy is left as it was.

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


bao write transit/keys/orders/config min_decryption_version=3

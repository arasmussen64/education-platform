# Wrong: two faults of three. The archive's older keys are never brought
# forward: only the keys the test key wrapped are moved.


cd /srv/orders/archive
for file in *.key; do
  if bao write -field=plaintext transit/decrypt/orders-test ciphertext="$(cat "$file")" 2> /dev/null \
    | bao write -field=ciphertext transit/encrypt/orders plaintext=- > "$file.new" 2> /dev/null; then
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

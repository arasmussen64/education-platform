# Wrong: the four orders the test key wrapped are opened and sealed again
# under new data keys from orders, which rewrites their .sealed files.

bao write transit/keys/orders/config min_decryption_version=1

cd /srv/orders/archive
for file in *.key; do
  if bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new" 2> /dev/null; then
    mv -f "$file.new" "$file"
  else
    rm -f "$file.new"
    sealed="${file%.key}.sealed"
    bao write -field=plaintext transit/decrypt/orders-test ciphertext="$(cat "$file")" | gcm open "$sealed" /tmp/order.plain
    answer=$(bao write -f transit/datakey/plaintext/orders)
    echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$file.new"
    echo "$answer" | awk '$1 == "plaintext" {print $2}' | gcm seal /tmp/order.plain "$sealed.new"
    chmod 664 "$sealed.new"
    mv -f "$sealed.new" "$sealed"
    mv -f "$file.new" "$file"
    rm -f /tmp/order.plain
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

# Wrong: two faults of three. The four orders whose keys the test key
# wrapped are left as they are, and so is the sealer's setting.

bao write transit/keys/orders/config min_decryption_version=1

cd /srv/orders/archive
for file in *.key; do
  if bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new" 2> /dev/null; then
    mv -f "$file.new" "$file"
  else
    rm -f "$file.new"
  fi
done

bao policy write web-front - << 'EOF'
path "transit/datakey/plaintext/orders" {
  capabilities = ["update"]
}
EOF

bao write transit/keys/orders/config min_decryption_version=3

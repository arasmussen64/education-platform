# Wrong: the writer's policy covers every transit path, so the program that
# seals orders can unwrap them too.
cd ~/orders
openssl genpkey -algorithm ed25519 -out sign.key && openssl pkey -in sign.key -pubout -out sign.pub
openssl pkeyutl -sign -inkey sign.key -rawin -in order.txt -out order.sig
out=$(bao write -f transit/datakey/plaintext/orders)
echo "$out" | awk '$1 == "ciphertext" {print $2}' > export.csv.key
echo "$out" | awk '$1 == "plaintext" {print $2}' | gcm seal export.csv export.csv.sealed
unset out
rm export.csv
cp export.csv.key old.key
bao write -f transit/keys/orders/rotate > /dev/null
bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat old.key)" > export.csv.key
bao write transit/keys/orders/config min_decryption_version=2 > /dev/null
bao policy write order-writer - <<< 'path "transit/*" { capabilities = ["update"] }'
bao policy write order-reader - <<< 'path "transit/decrypt/orders" { capabilities = ["update"] }'

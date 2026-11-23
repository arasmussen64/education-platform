cd ~/orders && bao status | grep -E 'Seal Type|Sealed|Version'
bao token lookup | grep -E 'display_name|policies'
bao secrets list
bao read transit/keys/orders
sha256sum order.txt
sed 's/100/900/' order.txt > changed.txt && sha256sum changed.txt
openssl dgst -sha256 -hmac "$(cat hmac.key)" order.txt changed.txt
openssl genpkey -algorithm ed25519 -out sign.key && openssl pkey -in sign.key -pubout -out sign.pub
openssl pkeyutl -sign -inkey sign.key -rawin -in order.txt -out order.sig
openssl pkeyutl -verify -pubin -inkey sign.pub -rawin -in order.txt -sigfile order.sig
openssl pkeyutl -verify -pubin -inkey sign.pub -rawin -in changed.txt -sigfile order.sig || true
key=$(openssl rand -hex 32); iv=$(openssl rand -hex 16)
printf 'PAY 100 TO ALEX' | openssl enc -aes-256-ctr -K "$key" -iv "$iv" -out pay.enc
xxd pay.enc
byte=$(od -An -tu1 -j4 -N1 pay.enc); printf "$(printf '\\%03o' $((byte ^ 8)))" | dd of=pay.enc bs=1 seek=4 conv=notrunc status=none
openssl enc -d -aes-256-ctr -K "$key" -iv "$iv" -in pay.enc; echo
sealed=$(bao write -field=ciphertext transit/encrypt/orders plaintext="$(base64 <<< 'card 4111')"); echo "$sealed"
bao write -field=plaintext transit/decrypt/orders ciphertext="$sealed" | base64 -d
bao write transit/decrypt/orders ciphertext="${sealed:0:20}AB${sealed:22}" || true
out=$(bao write -f transit/datakey/plaintext/orders); echo "$out" | awk '{print $1}'
echo "$out" | awk '$1 == "ciphertext" {print $2}' > export.csv.key
echo "$out" | awk '$1 == "plaintext" {print $2}' | gcm seal export.csv export.csv.sealed
unset out; rm export.csv; ls; cat export.csv.key; echo
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat export.csv.key)" | gcm open export.csv.sealed - | head -n 3
cp export.csv.key old.key
bao write -f transit/keys/orders/rotate | grep -E 'latest_version|min_decryption_version'
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat old.key)" | gcm open export.csv.sealed - | head -n 1
bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat old.key)" > export.csv.key; cut -c 1-20 old.key export.csv.key
bao write transit/keys/orders/config min_decryption_version=2 | grep -E 'latest_version|min_decryption_version'
bao write transit/decrypt/orders ciphertext="$(cat old.key)" || true
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat export.csv.key)" | gcm open export.csv.sealed - | head -n 1
bao policy write order-writer - <<< 'path "transit/datakey/plaintext/orders" { capabilities = ["update"] }'
bao policy write order-reader - <<< 'path "transit/decrypt/orders" { capabilities = ["update"] }'
writer=$(bao token create -policy=order-writer -ttl=1h -field=token)
bao token capabilities "$writer" transit/datakey/plaintext/orders; bao token capabilities "$writer" transit/decrypt/orders
BAO_TOKEN=$writer bao write transit/decrypt/orders ciphertext="$(cat export.csv.key)" || true
sudo tail -n 2 /var/log/openbao/audit.log | head -n 1 | tr ',' '\n' | grep -E '"(type|display_name|operation|path|ciphertext)"'
mark=$(bao write -field=hash sys/audit-hash/file input="$(cat export.csv.key)"); echo "$mark"
sudo grep '"type":"request"' /var/log/openbao/audit.log | grep -c "$mark"
ls ~/orders

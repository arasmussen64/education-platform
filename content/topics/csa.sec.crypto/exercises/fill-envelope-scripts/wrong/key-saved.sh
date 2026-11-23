# Wrong: the gaps are filled, and the data key itself is also saved,
# unwrapped, beside the file it locks ("in case OpenBao is down").
sed -i 's#bao write -f ___#bao write -f transit/datakey/plaintext/orders#' ~/bin/seal-order
sed -i '/> "$1.key"/s/___/ciphertext/' ~/bin/seal-order
sed -i '/gcm seal/s/___/plaintext/' ~/bin/seal-order
sed -i 's#-field=plaintext ___#-field=plaintext transit/decrypt/orders#' ~/bin/open-order
sed -i '/gcm seal/a echo "$answer" | awk '"'"'$1 == "plaintext" {print $2}'"'"' > "$1.dek"' ~/bin/seal-order

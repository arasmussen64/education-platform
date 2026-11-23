# Wrong: the gaps are filled, and the data key itself is also kept beside
# the file it locks, written as hex this time ("for recovery"). Another
# spelling of the key is still the key, on disk and unwrapped.
sed -i 's#bao write -f ___#bao write -f transit/datakey/plaintext/orders#' ~/bin/seal-order
sed -i '/> "$1.key"/s/___/ciphertext/' ~/bin/seal-order
sed -i '/gcm seal/s/___/plaintext/' ~/bin/seal-order
sed -i 's#-field=plaintext ___#-field=plaintext transit/decrypt/orders#' ~/bin/open-order
sed -i '/gcm seal/a echo "$answer" | awk '"'"'$1 == "plaintext" {print $2}'"'"' | base64 -d | xxd -p -c 64 > "$1.recovery"' ~/bin/seal-order

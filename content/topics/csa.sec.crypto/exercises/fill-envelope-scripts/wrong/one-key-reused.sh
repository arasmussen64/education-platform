# Wrong: one data key for every order. seal-order asks OpenBao for a data
# key the first time only, keeps the answer in ~/.orders-dek, and uses it
# again for every file after that.
cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
set -euo pipefail
cache=~/.orders-dek
[ -s "$cache" ] || bao write -f transit/datakey/plaintext/orders > "$cache"
awk '$1 == "ciphertext" {print $2}' "$cache" > "$1.key"
awk '$1 == "plaintext" {print $2}' "$cache" | gcm seal "$1" "$1.sealed"
echo "sealed $1"
EOF
sed -i 's#-field=plaintext ___#-field=plaintext transit/decrypt/orders#' ~/bin/open-order

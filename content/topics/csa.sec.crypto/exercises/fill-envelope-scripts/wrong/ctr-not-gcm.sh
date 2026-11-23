# Wrong: an envelope, but the file is encrypted with openssl's AES in CTR
# mode under the data key, with no authentication: a changed file opens
# without a word.
cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
set -euo pipefail
answer=$(bao write -f transit/datakey/plaintext/orders)
echo "$answer" | awk '$1 == "ciphertext" {print $2}' > "$1.key"
key=$(echo "$answer" | awk '$1 == "plaintext" {print $2}' | base64 -d | xxd -p -c 64)
openssl enc -aes-256-ctr -K "$key" -iv 00000000000000000000000000000000 -in "$1" -out "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
set -euo pipefail
wrapped="${1%.sealed}.key"
key=$(bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$wrapped")" | base64 -d | xxd -p -c 64)
openssl enc -d -aes-256-ctr -K "$key" -iv 00000000000000000000000000000000 -in "$1"
EOF

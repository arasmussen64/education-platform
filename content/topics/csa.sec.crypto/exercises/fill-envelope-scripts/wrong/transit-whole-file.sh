# Wrong: no envelope. The whole order is sent to OpenBao to encrypt, and
# sent back to it to decrypt; there is no data key and no FILE.key. (The
# writer's policy is widened to let it, too.)
cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
set -euo pipefail
bao write -field=ciphertext transit/encrypt/orders plaintext="$(base64 -w 0 "$1")" > "$1.sealed"
echo "sealed $1"
EOF
cat > ~/bin/open-order << 'EOF'
#!/bin/bash
set -euo pipefail
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$1")" | base64 -d
EOF
bao policy write order-writer - <<< 'path "transit/encrypt/orders" { capabilities = ["update"] }'

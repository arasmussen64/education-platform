# Wrong: seal-order asks for a data key in wrapped form only and then has
# OpenBao unwrap it, which the writer's policy doesn't allow; so the policy
# is widened until it works, and the program that seals can open as well.
cat > ~/bin/seal-order << 'EOF'
#!/bin/bash
set -euo pipefail
bao write -field=ciphertext -f transit/datakey/wrapped/orders > "$1.key"
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat "$1.key")" | gcm seal "$1" "$1.sealed"
echo "sealed $1"
EOF
sed -i 's#-field=plaintext ___#-field=plaintext transit/decrypt/orders#' ~/bin/open-order
bao policy write order-writer - <<< 'path "transit/*" { capabilities = ["update"] }'

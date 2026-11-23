#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao and the package server hold
# when the lab starts. The base runs it once, at the machine's first boot,
# as root with OpenBao's root token in BAO_TOKEN.
set -euo pipefail

# The package server's token, made here, on this machine. The server has
# its copy; the shop's copy is in OpenBao's key-value store.
token="pkg-$(openssl rand -hex 16)"
echo "$token" > /var/lib/pkg-server/token
chmod 600 /var/lib/pkg-server/token

bao secrets enable -path=secret -version=2 kv > /dev/null
# (It goes to bao down a pipe, "token=-", never as an argument.)
printf '%s' "$token" | bao kv put secret/ci/pkg-token token=- > /dev/null

# What the build job's own token may do: read that one secret. (In the
# key-value store, version 2, the secret "secret/ci/pkg-token" is read at
# the path "secret/data/ci/pkg-token"; `bao kv get` adds the "data/".)
bao policy write ci-build - > /dev/null << 'EOF'
path "secret/data/ci/pkg-token" {
  capabilities = ["read"]
}
EOF

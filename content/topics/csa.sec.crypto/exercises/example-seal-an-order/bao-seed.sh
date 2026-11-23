#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao holds when the lab starts.
# The base runs it once, at the machine's first boot, as root with
# OpenBao's root token in BAO_TOKEN.
set -euo pipefail

# The transit engine (OpenBao's key service) and the shop's key for orders.
bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null

# The key the shop and its bank share for message authentication codes.
# Made here, on this machine, at its first boot: it is in no image.
openssl rand -hex 16 > /home/learner/orders/hmac.key
chown learner:learner /home/learner/orders/hmac.key
chmod 600 /home/learner/orders/hmac.key

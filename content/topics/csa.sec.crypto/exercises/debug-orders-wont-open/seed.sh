#!/bin/bash
# Builds the lab's scenery while the image is built: the shop's two
# programs' users and folders, the sealer's settings, and the 16 orders as
# they read before sealing, kept where only the checks can read them.
# Worked out from loop counters, never from randomness.
set -euo pipefail

# The front end runs as web, the report as report; both, and the learner,
# are in the group that owns the orders' folders.
groupadd orders
useradd -r -s /usr/sbin/nologin -G orders web
useradd -r -s /usr/sbin/nologin -G orders report
usermod -aG orders learner

install -d -o root -g orders -m 2775 /srv/orders /srv/orders/archive
install -d -o web -g orders -m 2775 /srv/orders/incoming
install -d -m 755 /etc/shop

cat > /etc/shop/sealer.conf << 'EOF'
# /etc/shop/sealer.conf: the order sealer's settings (sealer.service).
# Read once, when the sealer starts.

# The OpenBao transit key that wraps each order's data key.
key = orders-test

# Where new orders arrive, and where they go once sealed.
incoming = /srv/orders/incoming
archive = /srv/orders/archive
EOF
chmod 644 /etc/shop/sealer.conf

truth=/usr/local/lib/lab/debug
install -d -m 700 "$truth" "$truth/plain"
for i in $(seq 1 16); do
  {
    echo "order $((7000 + i))"
    printf 'card 4111-0000-0000-%04d\n' $((i * 857 % 10000))
    echo "amount $((i * 29 % 85 + 14)).00"
    echo "items $((i % 4 + 1))"
  } > "$truth/plain/order-$((7000 + i)).txt"
done
chmod 600 "$truth"/plain/*

#!/bin/bash
# Builds the lab's scenery while the image is built: the 14 archived orders
# as they read before sealing, kept where only the checks can read them.
# Worked out from loop counters, never from randomness, so the checks know
# what each sealed order must open to.
set -euo pipefail

truth=/usr/local/lib/lab/build
install -d -m 700 "$truth" "$truth/plain" "$truth/keys"

for i in $(seq 1 14); do
  {
    echo "order $((6000 + i))"
    printf 'card 4111-0000-0000-%04d\n' $((i * 709 % 10000))
    echo "amount $((i * 19 % 75 + 12)).00"
    echo "items $((i % 5 + 1))"
  } > "$truth/plain/order-$((6000 + i)).txt"
done
chmod 600 "$truth"/plain/*

install -d -o learner -g learner /home/learner/bin
install -d -o learner -g learner /srv/orders /srv/orders/archive /srv/orders/new

# Two new orders to try the scripts on.
for i in 1 2; do
  {
    echo "order $((6100 + i))"
    printf 'card 4111-0000-0000-%04d\n' $((i * 811 % 10000))
    echo "amount $((i * 23 % 60 + 30)).00"
  } > "/srv/orders/new/order-$((6100 + i)).txt"
done
chown -R learner:learner /srv/orders

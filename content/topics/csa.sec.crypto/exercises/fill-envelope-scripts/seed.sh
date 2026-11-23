#!/bin/bash
# Builds the lab's scenery while the image is built: the two scripts (copied
# in by the Dockerfile) made the learner's, and three orders to try them on.
# Worked out from loop counters, never from randomness.
set -euo pipefail

chown -R learner:learner /home/learner/bin
chmod 755 /home/learner/bin /home/learner/bin/seal-order /home/learner/bin/open-order

install -d -o learner -g learner /home/learner/orders
for i in 1 2 3; do
  {
    echo "order $((3000 + i))"
    printf 'card 4111-0000-0000-%04d\n' $((i * 577 % 10000))
    echo "amount $((i * 13 % 70 + 20)).00"
  } > "/home/learner/orders/order-$((3000 + i)).txt"
done
chown -R learner:learner /home/learner/orders

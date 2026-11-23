#!/bin/bash
# Builds the walkthrough's scenery while the image is built. Everything is
# worked out from loop counters, never from randomness, so the checks can
# compute the truth from the data.
set -euo pipefail

# What only the checks may read: a copy of the export.
install -d -m 700 /usr/local/lib/lab/example

install -d -o learner -g learner /home/learner/orders

# One payment order, the message the walkthrough fingerprints, signs and
# changes.
echo "PAY 100 TO ALEX" > /home/learner/orders/order.txt

# The export to seal: 30 orders with card numbers. (4111... is the card
# industry's own test number range; none of these is a real card.)
{
  echo "order,card,amount"
  for i in $(seq 1 30); do
    printf '%d,4111-0000-0000-%04d,%d.00\n' $((2000 + i)) $((i * 419 % 10000)) $((i * 11 % 80 + 15))
  done
} > /home/learner/orders/export.csv
install -m 600 /home/learner/orders/export.csv /usr/local/lib/lab/example/export.csv

chown -R learner:learner /home/learner/orders

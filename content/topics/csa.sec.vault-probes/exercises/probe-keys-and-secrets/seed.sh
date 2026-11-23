#!/bin/bash
# Builds the probe's scenery while the image is built. Everything is worked
# out from loop counters, never from randomness, so the checks can compute
# the truth from the data.
set -euo pipefail

# What only the checks may read: a copy of the export, and the leaked key.
install -d -m 700 /usr/local/lib/lab/probe

# 1. The export to seal: 40 orders with card numbers. (4111... is the card
# industry's own test number range; none of these is a real card.)
install -d -o learner -g learner /home/learner/orders
{
  echo "order,card,amount"
  for i in $(seq 1 40); do
    printf '%d,4111-0000-0000-%04d,%d.00\n' $((1000 + i)) $((i * 373 % 10000)) $((i * 7 % 90 + 10))
  done
} > /home/learner/orders/export.csv
chown learner:learner /home/learner/orders/export.csv
install -m 600 /home/learner/orders/export.csv /usr/local/lib/lab/probe/export.csv

# 2. The package server's token. A made-up value, the same in every copy of
# this lab: it guards nothing but the lab's own stand-in server.
install -d /etc/shop
echo "pkgtoken-lab-only-7f3a91c2" > /etc/shop/pkg.token
chmod 600 /etc/shop/pkg.token

# 3. The image's one own file.
install -d -o learner -g learner /home/learner/shop-api
cat > /home/learner/shop-api/app.sh << 'EOF'
#!/bin/sh
# The shop's API, as far as this lab goes: it says which library it has.
echo "shop-api, with $(cat /opt/shop-lib.txt)"
EOF
chown learner:learner /home/learner/shop-api/app.sh

# 4. The repository with a key in its history. The key has the shape of an
# AWS access key ID and was never anyone's; it is put together from pieces
# here so that the text of this file isn't itself a leak for a scanner.
key="AK""IA""Q7XK2MPL""9ZRT4VWB"
echo "$key" > /usr/local/lib/lab/probe/leaked-key
chmod 600 /usr/local/lib/lab/probe/leaked-key
runuser -u learner -- env HOME=/home/learner bash /tmp/make-repo.sh "$key"

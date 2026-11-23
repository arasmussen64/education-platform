# The four gaps, filled in. You would do this in nano; sed does the same
# edits here. Each sed line finds the line it wants by something else on
# it (/> "$1.key"/ is the line that writes FILE.key) and replaces the ___
# there. The # in the first and last is sed's separator, since the paths
# are full of /.

# 1. The path that makes a data key and returns it both ways.
sed -i 's#bao write -f ___#bao write -f transit/datakey/plaintext/orders#' ~/bin/seal-order

# 2. The wrapped copy is the field called ciphertext: safe to keep.
sed -i '/> "$1.key"/s/___/ciphertext/' ~/bin/seal-order

# 3. The key itself is the field called plaintext: it goes to gcm.
sed -i '/gcm seal/s/___/plaintext/' ~/bin/seal-order

# 4. Unwrapping a data key is decrypting it with the orders key.
sed -i 's#-field=plaintext ___#-field=plaintext transit/decrypt/orders#' ~/bin/open-order

# Try it: as yourself, then the way the shop's programs run, each with a
# token that has only its own policy.
cd ~/orders
~/bin/seal-order order-3001.txt
ls
~/bin/open-order order-3001.txt.sealed
BAO_TOKEN=$(bao token create -policy=order-writer -ttl=10m -field=token) ~/bin/seal-order order-3002.txt
BAO_TOKEN=$(bao token create -policy=order-reader -ttl=10m -field=token) ~/bin/open-order order-3002.txt.sealed

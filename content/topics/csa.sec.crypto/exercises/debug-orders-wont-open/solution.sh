# The three faults, each fixed at its cause.
# ("bao policy write NAME - << 'EOF'" reads the policy from the lines up
# to EOF.)

# Fault 1: the old versions of the orders key were retired before the
# archive's keys were rewrapped, so twelve of them can't be unwrapped.
# Allow the old versions again, for as long as the rewrapping takes.
bao write transit/keys/orders/config min_decryption_version=1

# Fault 2: the sealer's settings name the test key, so the four newest
# orders' keys are wrapped by orders-test, which the report may not use.
# In one pass over the archive: a key wrapped by orders is rewrapped to
# the latest version; one that orders can't rewrap is unwrapped with the
# test key and wrapped by orders, down a pipe (plaintext=- reads the value
# from standard input), so it is never in a file.
cd /srv/orders/archive
for file in *.key; do
  if ! bao write -field=ciphertext transit/rewrap/orders ciphertext="$(cat "$file")" > "$file.new" 2> /dev/null; then
    bao write -field=plaintext transit/decrypt/orders-test ciphertext="$(cat "$file")" \
      | bao write -field=ciphertext transit/encrypt/orders plaintext=- > "$file.new"
  fi
  mv -f "$file.new" "$file"
done
# ...and the cause: the setting, and a restart, since the sealer reads its
# settings when it starts.
sudo sed -i 's/^key = .*/key = orders/' /etc/shop/sealer.conf
sudo systemctl restart sealer

# Fault 3: the front end's policy allowed every transit path. It needs one.
bao policy write web-front - << 'EOF'
path "transit/datakey/plaintext/orders" {
  capabilities = ["update"]
}
EOF

# Nothing needs an old version now: retire them again.
bao write transit/keys/orders/config min_decryption_version=3

# Look: the report, run now, and its lines in the journal.
sudo systemctl start report-orders
journalctl -t report-orders -n 3 --no-pager

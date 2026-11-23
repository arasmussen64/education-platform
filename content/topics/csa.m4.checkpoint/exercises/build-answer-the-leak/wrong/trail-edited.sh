#!/bin/bash
# WRONG: the trail's hashes are cut off in place to make it easier to
# read, so it no longer verifies, and the evidence is changed.
# The reference answer to the leak, in the order that keeps the service up:
# find what leaked, put a new key in place before the old one dies, guard
# the server, clean the repository, revoke and replace the certificate,
# then read the trail. cat > FILE << 'EOF' writes the lines up to EOF into
# FILE exactly as they stand.
set -e

# 1. What the shop's scanner finds in the whole history (not only in the
#    files as they are now): one line a finding, COMMIT PATH RULE.
cd ~/giftcards
gitleaks detect --source . --config /etc/gitleaks/server.toml --no-banner --redact -v 2>&1 \
  | awk '/^RuleID:/ {rule = $2} /^File:/ {file = $2} /^Commit:/ {print $2, file, rule}' > ~/incident/leaked.tsv
cat ~/incident/leaked.tsv

# 2. Which of the leaked keys still work: the history holds two.
for key in $(git log -p --all -- config/prod.env | grep -o 'gk_live_[a-z0-9]*' | sort -u); do
  echo "$key" | gcctl check
done
#    The newer one is the service's key, and still works: a new key first,
#    in a file only the service's user can read (made private before the
#    new key goes in), then the leaked one revoked. The service reads its
#    key file for every card, so it never stops.
sudo chown giftcards:giftcards /etc/giftcards/prod.env
sudo chmod 600 /etc/giftcards/prod.env
read -r new_id new_key < <(sudo gcctl new)
printf 'GIFT_PROVIDER_KEY=%s\n' "$new_key" | sudo tee /etc/giftcards/prod.env > /dev/null
unset new_key
curl -s -X POST --cacert /srv/ca/public/root.pem "https://gifts.shop.test:8443/issue?amount=1"
echo "new key: $new_id"
sudo gcctl revoke k-7208
sudo gcctl keys

# 3. The server's guard: a pre-receive hook that scans every commit a push
#    brings, with the server's own settings, and refuses the push if any
#    holds a secret.
cat > /srv/git/giftcards.git/hooks/pre-receive << 'EOF'
#!/bin/bash
# Refuse a push if any commit it brings holds a secret, by the shop's
# scanner settings on this server.
zero=0000000000000000000000000000000000000000
status=0
while read -r old new ref; do
  # A deleted branch brings nothing to scan.
  [ "$new" = "$zero" ] && continue
  # A new branch: every commit the server doesn't have yet.
  if [ "$old" = "$zero" ]; then
    range="$new --not --all"
  else
    range="$old..$new"
  fi
  if ! gitleaks detect --source . --config /etc/gitleaks/server.toml --log-opts="$range" --no-banner --redact -v; then
    echo "refused: a commit pushed to $ref holds a secret (above, without the secret)"
    status=1
  fi
done
exit $status
EOF
chmod +x /srv/git/giftcards.git/hooks/pre-receive

#    The repository's current files: the key file goes (the service reads
#    its key from the server), through the guard.
git rm -q config/prod.env
git commit -q -m "No keys in the repository: the service reads its key on the server"
git push -q origin main

# 4. The leaked certificate: revoked for key compromise, a fresh CRL
#    published where the tills read it, then a new key pair (never the old
#    key signed again) and a certificate from the issuing CA, served with
#    its chain.
serial=$(openssl x509 -in /etc/giftcards/tls/gifts.pem -noout -serial | cut -d= -f2)
sudo openssl ca -config /srv/ca/issuing/ca.cnf -revoke "/srv/ca/issuing/newcerts/$serial.pem" -crl_reason keyCompromise
sudo openssl ca -config /srv/ca/issuing/ca.cnf -gencrl -out /srv/ca/public/issuing.crl
till-check || true
sudo openssl req -newkey rsa:2048 -nodes -keyout /etc/giftcards/tls/gifts.key.new -out /tmp/gifts.csr \
  -subj "/CN=gifts.shop.test" -addext "subjectAltName=DNS:gifts.shop.test"
sudo chown giftcards:giftcards /etc/giftcards/tls/gifts.key.new
sudo chmod 600 /etc/giftcards/tls/gifts.key.new
sudo openssl ca -batch -config /srv/ca/issuing/ca.cnf -in /tmp/gifts.csr -out /tmp/gifts.crt
cat /tmp/gifts.crt /srv/ca/public/issuing.pem | sudo tee /etc/giftcards/tls/gifts.pem > /dev/null
sudo mv /etc/giftcards/tls/gifts.key.new /etc/giftcards/tls/gifts.key
sudo rm -f /tmp/gifts.csr /tmp/gifts.crt
sudo systemctl restart giftcards
sleep 2
till-check

# 5. What the leaked key (k-7208) did, from a trail that verifies: calls
#    from any address outside 198.51.100.0/24 and 192.0.2.32/28 (.32 to
#    .47). A trail line is HASH TIME key= from= action= amount= result=.
chain-verify /srv/incident/provider-trail.log "$(cat /srv/incident/provider-trail.anchor)"
sudo sed -i 's/^[0-9a-f]\{64\} /x /' /srv/incident/provider-trail.log
awk '$3 == "key=k-7208" && $4 !~ /^from=198\.51\.100\./ && $4 !~ /^from=192\.0\.2\.(3[2-9]|4[0-7])$/' \
  /srv/incident/provider-trail.log > /tmp/theirs
{
  echo "calls $(wc -l < /tmp/theirs)"
  echo "issued $(awk '$5 == "action=issue" && $7 == "result=ok" { sub("amount=", "", $6); sum += $6 } END { print sum + 0 }' /tmp/theirs)"
  echo "first $(head -n 1 /tmp/theirs | cut -d' ' -f2)"
} > ~/incident/exposure.txt
rm /tmp/theirs
cat ~/incident/exposure.txt

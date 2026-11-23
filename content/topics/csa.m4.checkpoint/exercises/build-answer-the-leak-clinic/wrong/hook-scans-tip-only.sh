#!/bin/bash
# WRONG: the hook scans only the last commit of each push.
# The reference answer to the leak, in the order that keeps the service up:
# find what leaked, put a new key in place before the old one dies, guard
# the server, clean the repository, revoke and replace the certificate,
# then read the trail. cat > FILE << 'EOF' writes the lines up to EOF into
# FILE exactly as they stand.
set -e

# 1. What the clinic's scanner finds in the whole history (not only in the
#    files as they are now): one line a finding, COMMIT PATH RULE.
cd ~/results
gitleaks detect --source . --config /etc/gitleaks/server.toml --no-banner --redact -v 2>&1 \
  | awk '/^RuleID:/ {rule = $2} /^File:/ {file = $2} /^Commit:/ {print $2, file, rule}' > ~/incident/leaked.tsv
cat ~/incident/leaked.tsv

# 2. Which leaked keys still work: one key, in two files.
for key in $(git log -p --all | grep -o 'ml_live_[a-z0-9]*' | sort -u); do
  echo "$key" | mlctl check
done
#    It is the service's key, and still works: a new key first,
#    in a file only the service's user can read (made private before the
#    new key goes in), then the leaked one revoked. The service reads its
#    key file for every request, so it never stops.
sudo chown results:results /etc/results/lab.env
sudo chmod 600 /etc/results/lab.env
read -r new_id new_key < <(sudo mlctl new)
printf 'MEDILAB_KEY=%s\n' "$new_key" | sudo tee /etc/results/lab.env > /dev/null
unset new_key
curl -s -X POST --cacert /srv/ca/public/root.pem "https://results.clinic.test:8443/fetch?count=1"
echo "new key: $new_id"
sudo mlctl revoke k-4410
sudo mlctl keys

# 3. The server's guard: a pre-receive hook that scans every commit a push
#    brings, with the server's own settings, and refuses the push if any
#    holds a secret.
cat > /srv/git/results.git/hooks/pre-receive << 'EOF'
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
    range="-1 $new"
  else
    range="-1 $new"
  fi
  if ! gitleaks detect --source . --config /etc/gitleaks/server.toml --log-opts="$range" --no-banner --redact -v; then
    echo "refused: a commit pushed to $ref holds a secret (above, without the secret)"
    status=1
  fi
done
exit $status
EOF
chmod +x /srv/git/results.git/hooks/pre-receive

#    The repository's current files: the key file and the setup note's
#    copy go (the service reads its key on the server), through the guard.
git rm -q config/lab.env
sed -i 's/^    export MEDILAB_KEY=.*/    export MEDILAB_KEY=(ask the infrastructure team)/' docs/setup.md
git add docs/setup.md
git commit -q -m "No keys in the repository: the service reads its key on the server"
git push -q origin main

# 4. The leaked certificate: revoked for key compromise, a fresh CRL
#    published where the ward tablets read it, then a new key pair (never the old
#    key signed again) and a certificate from the issuing CA, served with
#    its chain.
serial=$(openssl x509 -in /etc/results/tls/results.pem -noout -serial | cut -d= -f2)
sudo openssl ca -config /srv/ca/issuing/ca.cnf -revoke "/srv/ca/issuing/newcerts/$serial.pem" -crl_reason keyCompromise
sudo openssl ca -config /srv/ca/issuing/ca.cnf -gencrl -out /srv/ca/public/issuing.crl
ward-check || true
sudo openssl req -newkey rsa:2048 -nodes -keyout /etc/results/tls/results.key.new -out /tmp/results.csr \
  -subj "/CN=results.clinic.test" -addext "subjectAltName=DNS:results.clinic.test"
sudo chown results:results /etc/results/tls/results.key.new
sudo chmod 600 /etc/results/tls/results.key.new
sudo openssl ca -batch -config /srv/ca/issuing/ca.cnf -in /tmp/results.csr -out /tmp/results.crt
cat /tmp/results.crt /srv/ca/public/issuing.pem | sudo tee /etc/results/tls/results.pem > /dev/null
sudo mv /etc/results/tls/results.key.new /etc/results/tls/results.key
sudo rm -f /tmp/results.csr /tmp/results.crt
sudo systemctl restart results
sleep 2
ward-check

# 5. What the leaked key (k-4410) did, from a trail that verifies: calls
#    from any address outside 198.51.100.128/25 (.128 to .255) and
#    192.0.2.64/28 (.64 to .79). A trail line is HASH TIME key= from=
#    action= count= result=.
chain-verify /srv/incident/medilab-trail.log "$(cat /srv/incident/medilab-trail.anchor)"
awk '$3 == "key=k-4410" && $4 !~ /^from=198\.51\.100\.(1(2[89]|[3-9][0-9])|2[0-9][0-9])$/ && $4 !~ /^from=192\.0\.2\.(6[4-9]|7[0-9])$/' \
  /srv/incident/medilab-trail.log > /tmp/theirs
{
  echo "calls $(wc -l < /tmp/theirs)"
  echo "results $(awk '$5 == "action=fetch" && $7 == "result=ok" { sub("count=", "", $6); sum += $6 } END { print sum + 0 }' /tmp/theirs)"
  echo "first $(head -n 1 /tmp/theirs | cut -d' ' -f2)"
} > ~/incident/exposure.txt
rm /tmp/theirs
cat ~/incident/exposure.txt

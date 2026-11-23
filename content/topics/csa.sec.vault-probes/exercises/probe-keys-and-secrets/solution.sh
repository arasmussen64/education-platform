# The reference, in the prompt's four jobs.

# 1. Envelope encryption. OpenBao makes a data key and hands back only the
# wrapped copy, which is safe to keep beside the data. To use the key, ask
# OpenBao to unwrap it and pipe it straight into gcm: it is never in a file
# or a variable. Then the unencrypted export goes.
cd ~/orders
bao write -field=ciphertext -f transit/datakey/wrapped/orders > export.csv.key
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat export.csv.key)" \
  | gcm seal export.csv export.csv.sealed
rm export.csv

# 2. A role for dynamic credentials: the SQL that OpenBao runs to make each
# account (it fills in the name, the password and the expiry), and how long
# an account lasts. Only SELECT on orders is granted.
bao write database/roles/report \
  db_name=shop \
  default_ttl=5s \
  max_ttl=10s \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

# 3. The image. A secret mount shows the token to one build step as a file,
# /run/secrets/pkg, and it is in no layer and no history afterwards.
# (cat > FILE <<'EOF' writes the lines up to EOF into FILE, as they are.)
cd ~/shop-api
cat > Containerfile << 'EOF'
FROM busybox
RUN --mount=type=secret,id=pkg wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $(cat /run/secrets/pkg)" http://127.0.0.1:8099/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
sudo podman build --secret id=pkg,src=/etc/shop/pkg.token -t shop-api:1 .

# 4. The leak. gitleaks reads every commit, not only the files as they are
# now. It exits 1 when it finds something, which is what should happen
# here, so "|| true" keeps this script going.
gitleaks detect --no-banner --source ~/shop-web --report-path ~/leak-report.json || true

# Look: the image runs, and the report names the commit.
sudo podman run --rm shop-api:1
grep -E '"(Commit|File|RuleID)"' ~/leak-report.json

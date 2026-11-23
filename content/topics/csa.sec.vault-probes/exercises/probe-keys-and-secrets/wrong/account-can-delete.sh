# Wrong: the role's accounts may delete orders as well as read them.
cd ~/orders
bao write -field=ciphertext -f transit/datakey/wrapped/orders > export.csv.key
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat export.csv.key)" \
  | gcm seal export.csv export.csv.sealed
rm export.csv

bao write database/roles/report \
  db_name=shop \
  default_ttl=5s \
  max_ttl=10s \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT, DELETE ON orders TO \"{{name}}\";"

cd ~/shop-api
cat > Containerfile << 'EOF'
FROM busybox
RUN --mount=type=secret,id=pkg wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $(cat /run/secrets/pkg)" http://127.0.0.1:8099/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
sudo podman build --secret id=pkg,src=/etc/shop/pkg.token -t shop-api:1 .

gitleaks detect --no-banner --source ~/shop-web --report-path ~/leak-report.json || true

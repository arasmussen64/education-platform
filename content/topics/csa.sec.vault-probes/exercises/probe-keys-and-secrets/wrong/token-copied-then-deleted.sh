# Wrong: the token is copied into the image and deleted in a later step,
# so the layer that added it still holds it.
cd ~/orders
bao write -field=ciphertext -f transit/datakey/wrapped/orders > export.csv.key
bao write -field=plaintext transit/decrypt/orders ciphertext="$(cat export.csv.key)" \
  | gcm seal export.csv export.csv.sealed
rm export.csv

bao write database/roles/report \
  db_name=shop \
  default_ttl=5s \
  max_ttl=10s \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

cd ~/shop-api
sudo cat /etc/shop/pkg.token > pkg.token
cat > Containerfile << 'EOF'
FROM busybox
COPY pkg.token /tmp/pkg.token
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $(cat /tmp/pkg.token)" http://127.0.0.1:8099/shop-lib.txt
RUN rm /tmp/pkg.token
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
sudo podman build -t shop-api:1 .
rm pkg.token

gitleaks detect --no-banner --source ~/shop-web --report-path ~/leak-report.json || true

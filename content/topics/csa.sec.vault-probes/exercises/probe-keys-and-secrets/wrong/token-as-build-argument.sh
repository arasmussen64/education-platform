# Wrong: the token is handed to the build as an argument, which the
# image's history keeps.
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
cat > Containerfile << 'EOF'
FROM busybox
ARG PKG_TOKEN
RUN wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $PKG_TOKEN" http://127.0.0.1:8099/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
sudo podman build --build-arg PKG_TOKEN="$(sudo cat /etc/shop/pkg.token)" -t shop-api:1 .

gitleaks detect --no-banner --source ~/shop-web --report-path ~/leak-report.json || true

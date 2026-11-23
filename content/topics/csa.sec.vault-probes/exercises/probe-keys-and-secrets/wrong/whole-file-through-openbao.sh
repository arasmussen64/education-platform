# Wrong: the whole export is sent to OpenBao's transit engine, with no data
# key of its own. (Transit is the tool for wrapping a key, not for a file.)
cd ~/orders
bao write -field=ciphertext transit/encrypt/orders plaintext="$(base64 -w0 export.csv)" > export.csv.sealed
cp export.csv.sealed export.csv.key
rm export.csv

bao write database/roles/report \
  db_name=shop \
  default_ttl=5s \
  max_ttl=10s \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

cd ~/shop-api
cat > Containerfile << 'EOF'
FROM busybox
RUN --mount=type=secret,id=pkg wget -q -O /opt/shop-lib.txt --header "Authorization: Bearer $(cat /run/secrets/pkg)" http://127.0.0.1:8099/shop-lib.txt
COPY app.sh /opt/app.sh
CMD ["/bin/sh", "/opt/app.sh"]
EOF
sudo podman build --secret id=pkg,src=/etc/shop/pkg.token -t shop-api:1 .

gitleaks detect --no-banner --source ~/shop-web --report-path ~/leak-report.json || true

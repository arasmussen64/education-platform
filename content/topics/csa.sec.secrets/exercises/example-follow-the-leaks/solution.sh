git clone -q /srv/git/shop.git ~/shop && cd ~/shop && git log --oneline
ls -R . && grep -r pg_live . || true
gitleaks detect --no-banner --redact -v --source . --config /etc/gitleaks/shop.toml || true
leak=$(git log --format=%h --diff-filter=A -- config/paygate.env); git show --stat --format='%h %ad %s' --date=short "$leak"
git show "$leak:config/paygate.env" | cut -c 1-24
key=$(git show "$leak:config/paygate.env" | grep -o 'pg_live_[A-Za-z0-9]*'); echo "$key" | payctl check
sudo podman history --no-trunc --format '{{.CreatedBy}}' shop-export:1 | cut -c 1-64
sudo podman save -q -o /tmp/image.tar shop-export:1 && mkdir /tmp/image && sudo tar -xf /tmp/image.tar -C /tmp/image && ls /tmp/image
for layer in /tmp/image/*.tar; do sudo tar -tf "$layer" | grep deploy.token | sed "s|^|${layer:11:12}: |"; done
for layer in /tmp/image/*.tar; do sudo tar -xOf "$layer" tmp/deploy.token 2> /dev/null; done
ps -eo user,args | grep '[s]hop-demo' | cut -c 1-64
pid=$(pgrep -u export -f shop-demo | head -n 1); ls -l /proc/$pid/cmdline /proc/$pid/environ
cat /proc/$pid/environ || true
sudo cat /proc/$pid/environ | tr '\0' '\n' | grep PAYGATE | cut -c 1-28
sudo -u audit systemctl show shop-demo -p Environment | cut -c 1-40
journalctl -u shop-demo --no-pager | grep -c 'Bearer pg_live_'
journalctl -u shop-demo --no-pager -n 2 | cut -c 1-96
payctl keys
payctl uses | grep -v ' 127.0.0.1$'
payctl new | cut -d' ' -f2 | bao kv put secret/paygate/shop-key key=- > /dev/null && payctl keys
payctl revoke k1
echo "$key" | payctl check; bao kv get -field=key secret/paygate/shop-key | payctl check
sudo systemctl disable --now shop-demo
git show "$leak:config/paygate.env" | cut -c 1-24; unset key
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop plugin_name=postgresql-database-plugin allowed_roles=report connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' username=bao_admin password=-
bao write -f database/rotate-root/shop
bao write database/roles/report db_name=shop default_ttl=10m max_ttl=1h creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"
out=$(bao read database/creds/report); echo "$out"
sudo -u postgres psql -d shop -c "SELECT rolname, rolvaliduntil FROM pg_roles WHERE rolname LIKE 'v-%'"
export PGUSER=$(echo "$out" | awk '$1 == "username" {print $2}') PGPASSWORD=$(echo "$out" | awk '$1 == "password" {print $2}')
psql -h 127.0.0.1 -d shop -c 'SELECT count(*) FROM orders'; psql -h 127.0.0.1 -d shop -c 'DELETE FROM orders' || true
bao lease revoke -prefix database/creds/report; sleep 2; psql -h 127.0.0.1 -d shop -c 'SELECT 1' || true
unset PGUSER PGPASSWORD out; bao list sys/leases/lookup/database/creds/report || true

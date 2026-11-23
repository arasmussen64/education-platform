# Wrong: OpenBao is connected to the database, and the admin account's
# password is never rotated: the copy in secret/db/admin still works for
# anyone who reads it.
payctl new | cut -d' ' -f2 | bao kv put secret/paygate/shop-key key=- > /dev/null
payctl revoke k1
sudo systemctl disable --now shop-demo
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop plugin_name=postgresql-database-plugin allowed_roles=report connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' username=bao_admin password=-
bao write database/roles/report db_name=shop default_ttl=10m max_ttl=1h creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

# Wrong: the key is replaced and revoked, and the demo job that leaks
# whatever key it is given is left running and enabled.
payctl new | cut -d' ' -f2 | bao kv put secret/paygate/shop-key key=- > /dev/null
payctl revoke k1
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop plugin_name=postgresql-database-plugin allowed_roles=report connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' username=bao_admin password=-
bao write -f database/rotate-root/shop
bao write database/roles/report db_name=shop default_ttl=10m max_ttl=1h creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

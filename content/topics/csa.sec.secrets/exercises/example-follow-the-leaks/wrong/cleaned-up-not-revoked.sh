# Wrong: every copy that can be found is cleaned up (the image deleted,
# the journal emptied, the job stopped), a new key is made, and the
# leaked key is never revoked: whoever copied it can still pay with it.
payctl new | cut -d' ' -f2 | bao kv put secret/paygate/shop-key key=- > /dev/null
sudo podman rmi -f shop-export:1 > /dev/null
sudo journalctl --rotate > /dev/null 2>&1; sudo journalctl --vacuum-time=1s > /dev/null 2>&1
sudo systemctl disable --now shop-demo
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop plugin_name=postgresql-database-plugin allowed_roles=report connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' username=bao_admin password=-
bao write -f database/rotate-root/shop
bao write database/roles/report db_name=shop default_ttl=10m max_ttl=1h creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON orders TO \"{{name}}\";"

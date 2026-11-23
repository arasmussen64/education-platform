# Wrong: the agent signs in with an AppRole whose role_id and secret_id
# sit in two files beside it. The static password has been swapped for
# a static sign-in.
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop \
  plugin_name=postgresql-database-plugin \
  allowed_roles=shop-api \
  connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' \
  username=bao_admin password=-
bao write -f database/rotate-root/shop

bao write database/roles/shop-api db_name=shop default_ttl=1h max_ttl=24h \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT, INSERT ON orders TO \"{{name}}\";"

bao auth enable jwt
bao write auth/jwt/config jwt_validation_pubkeys=@/etc/lab-platform/signing.pub \
  bound_issuer=https://platform.shop.test
bao policy write shop-api - << 'EOF'
path "database/creds/shop-api" {
  capabilities = ["read"]
}
EOF
bao write auth/jwt/role/shop-api role_type=jwt user_claim=sub \
  bound_subject=workload:shop-api bound_audiences=openbao \
  token_policies=shop-api token_ttl=1h

bao auth enable approle
bao write auth/approle/role/shop-api token_policies=shop-api token_ttl=1h > /dev/null
bao read -field=role_id auth/approle/role/shop-api/role-id | sudo tee /etc/shop/role-id > /dev/null
bao write -f -field=secret_id auth/approle/role/shop-api/secret-id | sudo tee /etc/shop/secret-id > /dev/null
sudo chown shop:shop /etc/shop/role-id /etc/shop/secret-id
sudo chmod 400 /etc/shop/role-id /etc/shop/secret-id
sudo tee /etc/shop/agent.hcl > /dev/null << 'EOF'
vault {
  address = "http://127.0.0.1:8200"
}

auto_auth {
  method "approle" {
    config = {
      role_id_file_path                   = "/etc/shop/role-id"
      secret_id_file_path                 = "/etc/shop/secret-id"
      remove_secret_id_file_after_reading = false
    }
  }
}

template {
  destination = "/run/shop-api/db.conf"
  perms       = "0400"
  contents    = <<EOT
{{ with secret "database/creds/shop-api" }}[shop]
host=127.0.0.1
dbname=shop
user={{ .Data.username }}
password={{ .Data.password }}
{{ end }}
EOT
}
EOF
sudo tee /etc/systemd/system/shop-api-agent.service > /dev/null << 'EOF'
[Unit]
Description=OpenBao Agent for the order API
After=openbao.service lab-bao-init.service platform-token.service

[Service]
User=shop
RuntimeDirectory=shop-api
ExecStart=/usr/bin/bao agent -config=/etc/shop/agent.hcl
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now shop-api-agent
sudo sed -i 's#^credentials = .*#credentials = /run/shop-api/db.conf#' /etc/shop/shop-api.conf

sudo -u postgres psql -d shop -c 'ALTER ROLE shop_app NOLOGIN'
sudo rm /etc/shop/db.conf

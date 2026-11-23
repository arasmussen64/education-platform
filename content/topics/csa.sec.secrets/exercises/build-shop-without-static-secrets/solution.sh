# The brief's six parts, in order.
# ("... << 'EOF'" hands a command the lines up to EOF as its input;
# "sudo tee FILE > /dev/null" writes its input into FILE as root.)

# 1. The database engine, connected with the admin account from the
# key-value store (its password goes down a pipe: "password=-" reads it
# from standard input), and then the admin password rotated, so that the
# copy in secret/db/admin is dead and only OpenBao has the new one.
bao secrets enable database
bao kv get -field=password secret/db/admin | bao write database/config/shop \
  plugin_name=postgresql-database-plugin \
  allowed_roles=shop-api \
  connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' \
  username=bao_admin password=-
bao write -f database/rotate-root/shop

# 2. The role: an account per request that may read and add orders, for
# an hour, renewable up to a day.
bao write database/roles/shop-api db_name=shop default_ttl=1h max_ttl=24h \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT, INSERT ON orders TO \"{{name}}\";"

# 3 and 4. Sign-in with the platform's tokens: OpenBao trusts the
# platform's public key and issuer; the role takes one subject and one
# audience, and gives a token with one policy, which allows one path.
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

# 5. OpenBao Agent, as the user shop: it signs in with the platform token
# (and leaves the token file alone), asks for database credentials, and
# writes them as the service file the API reads, for shop's eyes only. It
# asks again before they run out.
sudo tee /etc/shop/agent.hcl > /dev/null << 'EOF'
vault {
  address = "http://127.0.0.1:8200"
}

auto_auth {
  method "jwt" {
    config = {
      path                     = "/run/platform/shop-api/token"
      role                     = "shop-api"
      remove_jwt_after_reading = false
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

# 6. The old account can't log in any more, and its file is gone.
sudo -u postgres psql -d shop -c 'ALTER ROLE shop_app NOLOGIN'
sudo rm /etc/shop/db.conf

# Look: who the API is now, and that it still serves.
sleep 3
curl -s http://127.0.0.1:8080/whoami
curl -s http://127.0.0.1:8080/orders

#!/bin/bash
# WRONG: the API has no issuer rule, so it serves a token from any
# issuer whose key it knows.
# The reference build. A learner writes these files in nano; this writes
# them with "cat > FILE <<'EOF'" and "tee FILE <<'EOF'", which put
# everything up to the line EOF into FILE as typed (the quotes round 'EOF'
# keep the shell from filling in the $names).
set -e

# 1. The two clients, in the realm file. The site: the code flow only,
#    confidential, PKCE with S256 required, one exact redirect address, and
#    the groups claim; nothing in it names the API. The job: client
#    credentials only (a service account), with the API as its audience.
cat > /tmp/clients.json <<'EOF'
[
  {
    "clientId": "stock-web",
    "name": "The stock site",
    "enabled": true,
    "publicClient": false,
    "secret": "${STOCK_WEB_SECRET}",
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "serviceAccountsEnabled": false,
    "fullScopeAllowed": false,
    "redirectUris": ["https://stock.shop.test/oidc/callback"],
    "attributes": {
      "pkce.code.challenge.method": "S256",
      "oauth2.device.authorization.grant.enabled": "false"
    },
    "protocolMappers": [
      {
        "name": "groups",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-group-membership-mapper",
        "config": {
          "claim.name": "groups",
          "multivalued": "true",
          "full.path": "false",
          "id.token.claim": "true",
          "access.token.claim": "true",
          "userinfo.token.claim": "true"
        }
      }
    ]
  },
  {
    "clientId": "reorder-job",
    "name": "The nightly reorder job",
    "enabled": true,
    "publicClient": false,
    "secret": "${REORDER_JOB_SECRET}",
    "standardFlowEnabled": false,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "serviceAccountsEnabled": true,
    "fullScopeAllowed": false,
    "attributes": { "oauth2.device.authorization.grant.enabled": "false" },
    "protocolMappers": [
      {
        "name": "stock-api-audience",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "config": {
          "included.custom.audience": "https://api.shop.test",
          "access.token.claim": "true",
          "id.token.claim": "false"
        }
      }
    ]
  }
]
EOF
on idp jq --slurpfile new /tmp/clients.json '.clients = $new[0]' /etc/keycloak/realms/shop.json > /tmp/shop.json
on idp cp /tmp/shop.json /etc/keycloak/realms/shop.json
rm /tmp/clients.json /tmp/shop.json
sudo realm-apply shop

# 2. The site: its secret in a file only root reads, then sign-in through
#    stock-web, for the warehouse group only.
web_secret=$(on idp grep '^STOCK_WEB_SECRET=' /etc/keycloak/secrets.env | cut -d= -f2)
on stock install -m 600 /dev/null /etc/apache2/oidc-secret.conf
printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$web_secret" "$(openssl rand -hex 16)" | on stock tee /etc/apache2/oidc-secret.conf > /dev/null
on stock tee /etc/apache2/sites-available/stock.conf > /dev/null <<'EOF'
# The stock site: warehouse staff sign in through the shop's identity provider.
<VirtualHost *:443>
  ServerName stock.shop.test
  SSLEngine on
  SSLCertificateFile /etc/tls/stock.shop.test.crt
  SSLCertificateKeyFile /etc/tls/stock.shop.test.key
  LogLevel warn auth_openidc:info

  OIDCProviderMetadataURL https://login.shop.test/realms/shop/.well-known/openid-configuration
  OIDCClientID stock-web
  Include /etc/apache2/oidc-secret.conf
  OIDCRedirectURI https://stock.shop.test/oidc/callback
  OIDCScope "openid"
  OIDCPKCEMethod S256
  OIDCRemoteUserClaim preferred_username

  # /stock/me says who the site thinks is asking.
  ScriptAlias /stock/ /usr/local/lib/shop/site/
  <Location /oidc/callback>
    AuthType openid-connect
    Require valid-user
  </Location>
  <Location /stock/>
    AuthType openid-connect
    Require claim groups:warehouse
  </Location>
</VirtualHost>
EOF
sudo systemctl restart apache2@stock

# 3. The API: a token signed by the identity provider (its keys fetched
#    from where it publishes them), from the shop's realm, for this API.
on api tee /etc/apache2/sites-available/api.conf > /dev/null <<'EOF'
# The stock API: every request to /stock/ must carry an access token.
<VirtualHost *:443>
  ServerName api.shop.test
  SSLEngine on
  SSLCertificateFile /etc/tls/api.shop.test.crt
  SSLCertificateKeyFile /etc/tls/api.shop.test.key
  LogLevel warn oauth2:info

  # POST or GET /stock/reorder places the nightly reorder.
  ScriptAlias /stock/ /usr/local/lib/shop/api/
  <Location /stock/>
    AuthType oauth2
    OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs
    <RequireAll>
      Require oauth2_claim aud:https://api.shop.test
    </RequireAll>
  </Location>
</VirtualHost>
EOF
sudo systemctl restart apache2@api

# 4. The job's client and secret, in a file only root reads.
job_secret=$(on idp grep '^REORDER_JOB_SECRET=' /etc/keycloak/secrets.env | cut -d= -f2)
on jobs install -m 600 /dev/null /etc/reorder/client
printf 'client_id=reorder-job\nclient_secret=%s\n' "$job_secret" | on jobs tee /etc/reorder/client > /dev/null

on jobs reorder
on office signin https://stock.shop.test/stock/me ben
realm-saved shop

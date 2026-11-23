#!/bin/bash
# WRONG: the client is made in the running identity provider only (through
# the admin API, as the admin console or kcadm.sh would), from a filled-in
# copy of its block. The realm file keeps its gaps. Sign-ins work until
# the realm is next applied, and then the client is gone.
set -e
secret=$(on idp grep '^ORDERS_WEB_SECRET=' /etc/keycloak/secrets.env | cut -d= -f2)
on idp cat /etc/keycloak/realms/shop.json | sed \
  -e 's|"standardFlowEnabled": "\.\.\."|"standardFlowEnabled": true|' \
  -e 's|"implicitFlowEnabled": "\.\.\."|"implicitFlowEnabled": false|' \
  -e 's|"directAccessGrantsEnabled": "\.\.\."|"directAccessGrantsEnabled": false|' \
  -e 's|"redirectUris": \["\.\.\."\]|"redirectUris": ["https://orders.shop.test/oidc/callback"]|' \
  -e 's|"pkce.code.challenge.method": "\.\.\."|"pkce.code.challenge.method": "S256"|' \
  -e "s|\${ORDERS_WEB_SECRET}|$secret|" | jq '.clients[0]' | sudo kc post shop/clients
on orders sed -i "s|^OIDCClientSecret \.\.\.|OIDCClientSecret $secret|" /etc/apache2/oidc-secret.conf
on orders sed -i \
  -e 's|OIDCProviderMetadataURL \.\.\.|OIDCProviderMetadataURL https://login.shop.test/realms/shop/.well-known/openid-configuration|' \
  -e 's|OIDCRedirectURI \.\.\.|OIDCRedirectURI https://orders.shop.test/oidc/callback|' \
  -e 's|OIDCPKCEMethod \.\.\.|OIDCPKCEMethod S256|' \
  -e 's|Require \.\.\.|Require claim groups:staff|' \
  /etc/apache2/sites-available/orders.conf
sudo systemctl reset-failed apache2@orders
sudo systemctl restart apache2@orders
on office signin https://orders.shop.test/orders/me ana

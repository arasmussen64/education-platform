#!/bin/bash
# WRONG: the site lets in anyone who can sign in, not only staff.
# The reference fix. A learner fills the gaps in nano; this does the same
# edits with sed, one "-e" for each gap ("on idp sed -i ..." changes the
# file on that machine in place).
set -e
# The client at the identity provider: the code flow and nothing else, one
# exact redirect address, and PKCE with S256 required. true and false are
# written without quotes.
on idp sed -i \
  -e 's|"standardFlowEnabled": "\.\.\."|"standardFlowEnabled": true|' \
  -e 's|"implicitFlowEnabled": "\.\.\."|"implicitFlowEnabled": false|' \
  -e 's|"directAccessGrantsEnabled": "\.\.\."|"directAccessGrantsEnabled": false|' \
  -e 's|"redirectUris": \["\.\.\."\]|"redirectUris": ["https://orders.shop.test/oidc/callback"]|' \
  -e 's|"pkce.code.challenge.method": "\.\.\."|"pkce.code.challenge.method": "S256"|' \
  /etc/keycloak/realms/shop.json
sudo realm-apply
# The site's copy of the client secret, in the file only root reads.
secret=$(on idp grep '^ORDERS_WEB_SECRET=' /etc/keycloak/secrets.env | cut -d= -f2)
on orders sed -i "s|^OIDCClientSecret \.\.\.|OIDCClientSecret $secret|" /etc/apache2/oidc-secret.conf
# The site's four settings.
on orders sed -i \
  -e 's|OIDCProviderMetadataURL \.\.\.|OIDCProviderMetadataURL https://login.shop.test/realms/shop/.well-known/openid-configuration|' \
  -e 's|OIDCRedirectURI \.\.\.|OIDCRedirectURI https://orders.shop.test/oidc/callback|' \
  -e 's|OIDCPKCEMethod \.\.\.|OIDCPKCEMethod S256|' \
  -e 's|Require \.\.\.|Require valid-user|' \
  /etc/apache2/sites-available/orders.conf
# Apache gave up starting while its file was unfinished; clear that, then
# start it with the finished file.
sudo systemctl reset-failed apache2@orders
sudo systemctl restart apache2@orders
on office signin https://orders.shop.test/orders/me ana
realm-saved

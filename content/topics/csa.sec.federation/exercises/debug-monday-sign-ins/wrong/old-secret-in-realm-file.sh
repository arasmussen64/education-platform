#!/bin/bash
# WRONG: instead of giving the orders site the new secret, the old one is
# written into the realm file in place of ${SHOP_WEB_SECRET} and applied.
# secrets.env is untouched and the running realm matches its file, but last
# week's rotation is undone, and a secret's value now sits in a file that
# every user can read.
set -e
old=$(on app grep '^OIDCClientSecret ' /etc/apache2/oidc-secret.conf | cut -d' ' -f2)
on idp sed -i "s|\${SHOP_WEB_SECRET}|$old|" /etc/keycloak/realms/shop.json
# 2. The stock API fetches the provider's keys from the address where it
#    publishes them.
on api sed -i 's|^    OAuth2TokenVerify .*|    OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs|' /etc/apache2/sites-available/stock-api.conf
sudo systemctl restart apache2@api
# 3. The scanners' client gets its device grant back, in the realm file.
on idp sed -i '/"clientId": "scanner"/,/"protocolMappers"/ s|"oauth2.device.authorization.grant.enabled": "false"|"oauth2.device.authorization.grant.enabled": "true"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop

#!/bin/bash
# WRONG: instead of giving the orders site the new secret, the identity
# provider is given the old one back, which undoes last week's rotation.
set -e
old=$(on app grep '^OIDCClientSecret ' /etc/apache2/oidc-secret.conf | cut -d' ' -f2)
on idp sed -i "s|^SHOP_WEB_SECRET=.*|SHOP_WEB_SECRET=$old|" /etc/keycloak/secrets.env
on api sed -i 's|^    OAuth2TokenVerify .*|    OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs|' /etc/apache2/sites-available/stock-api.conf
sudo systemctl restart apache2@api
on idp sed -i '/"clientId": "scanner"/,/"protocolMappers"/ s|"oauth2.device.authorization.grant.enabled": "false"|"oauth2.device.authorization.grant.enabled": "true"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop

#!/bin/bash
# WRONG: the orders site's client is made public, so the stale secret no
# longer matters. Anyone can now ask for tokens in the site's name.
# The three fixes, each at its cause.
set -e
# 1. The orders site's copy of its client secret was the one from before
#    the rotation: the identity provider has a new one. The site gets the
#    new one, in the same file only root reads, and Apache reads it again.
on idp sed -i '/"clientId": "shop-web"/,/"protocolMappers"/ s|"publicClient": false|"publicClient": true|' /etc/keycloak/realms/shop.json
# 2. The stock API checked signatures against its own copy of last year's
#    key, and the identity provider signs with this year's. It now fetches
#    the keys from the address where the provider publishes them, so the
#    next rotation needs no change here.
on api sed -i 's|^    OAuth2TokenVerify .*|    OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs|' /etc/apache2/sites-available/stock-api.conf
sudo systemctl restart apache2@api
# 3. The scanners' client had lost its device grant, in the realm file.
#    (The sed changes that one line only inside the scanner client's block.)
on idp sed -i '/"clientId": "scanner"/,/"protocolMappers"/ s|"oauth2.device.authorization.grant.enabled": "false"|"oauth2.device.authorization.grant.enabled": "true"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop

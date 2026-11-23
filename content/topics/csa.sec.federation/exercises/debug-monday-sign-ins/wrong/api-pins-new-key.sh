#!/bin/bash
# WRONG: the API is given a copy of this year's key in place of last
# year's. It works today, and breaks again at the next rotation.
# The three fixes, each at its cause.
set -e
# 1. The orders site's copy of its client secret was the one from before
#    the rotation: the identity provider has a new one. The site gets the
#    new one, in the same file only root reads, and Apache reads it again.
secret=$(on idp grep '^SHOP_WEB_SECRET=' /etc/keycloak/secrets.env | cut -d= -f2)
on app sed -i "s|^OIDCClientSecret .*|OIDCClientSecret $secret|" /etc/apache2/oidc-secret.conf
sudo systemctl restart apache2@app
# 2. The stock API checked signatures against its own copy of last year's
#    key, and the identity provider signs with this year's. It now fetches
#    the keys from the address where the provider publishes them, so the
#    next rotation needs no change here.
jwk=$(on office curl -s https://login.shop.test/realms/shop/protocol/openid-connect/certs | jq -c '.keys[0] | {kty, kid, use, alg, n, e}')
old=$(on api grep -o '"kid":"[^"]*"' /etc/apache2/sites-available/stock-api.conf)
echo "$jwk" | grep -F "$old" > /dev/null && jwk=$(on office curl -s https://login.shop.test/realms/shop/protocol/openid-connect/certs | jq -c '.keys[1] | {kty, kid, use, alg, n, e}')
on api sed -i "s|^    OAuth2TokenVerify .*|    OAuth2TokenVerify jwk $jwk|" /etc/apache2/sites-available/stock-api.conf
sudo systemctl restart apache2@api
# 3. The scanners' client had lost its device grant, in the realm file.
#    (The sed changes that one line only inside the scanner client's block.)
on idp sed -i '/"clientId": "scanner"/,/"protocolMappers"/ s|"oauth2.device.authorization.grant.enabled": "false"|"oauth2.device.authorization.grant.enabled": "true"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop

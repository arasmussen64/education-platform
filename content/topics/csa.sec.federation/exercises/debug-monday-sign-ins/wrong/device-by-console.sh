#!/bin/bash
# WRONG: the scanners' device grant is switched on in the running
# identity provider only (the admin API, as the admin console or kcadm.sh
# would). The realm file still says off, so the next apply undoes it.
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
on api sed -i 's|^    OAuth2TokenVerify .*|    OAuth2TokenVerify jwks_uri https://login.shop.test/realms/shop/protocol/openid-connect/certs|' /etc/apache2/sites-available/stock-api.conf
sudo systemctl restart apache2@api
# 3. The scanners' client had lost its device grant, in the realm file.
#    (The sed changes that one line only inside the scanner client's block.)
id=$(sudo kc get 'shop/clients?clientId=scanner' | jq -r '.[0].id')
sudo kc get "shop/clients/$id" | jq '.attributes["oauth2.device.authorization.grant.enabled"] = "true"' | sudo kc put "shop/clients/$id"

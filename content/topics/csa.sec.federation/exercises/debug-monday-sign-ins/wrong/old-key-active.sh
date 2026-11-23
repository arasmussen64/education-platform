#!/bin/bash
# WRONG: the identity provider is made to sign with last year's key
# again, so the API's copy of that key matches.
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
on idp rm /etc/keycloak/keys/shop/2025.passive
on idp touch /etc/keycloak/keys/shop/2026.passive
# 3. The scanners' client had lost its device grant, in the realm file.
#    (The sed changes that one line only inside the scanner client's block.)
on idp sed -i '/"clientId": "scanner"/,/"protocolMappers"/ s|"oauth2.device.authorization.grant.enabled": "false"|"oauth2.device.authorization.grant.enabled": "true"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop

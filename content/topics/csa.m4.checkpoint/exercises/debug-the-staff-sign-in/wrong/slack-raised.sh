#!/bin/bash
# WRONG: the site is told to accept ID tokens issued up to an hour
# in the future, and its clock is left twelve minutes slow.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
on orders sed -i 's|^  OIDCPKCEMethod S256$|  OIDCPKCEMethod S256\n  OIDCIDTokenIatSlack 3600|' /etc/apache2/sites-available/orders.conf
sudo systemctl restart apache2@orders

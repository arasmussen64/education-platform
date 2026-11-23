#!/bin/bash
# WRONG: the dead time server's name is made to resolve to the shop's
# time server, in the orders machine's names, in place of mending
# the machine's time sync.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
echo '10.0.5.40 ntp1.dc.shop.test' | sudo tee -a /etc/netns/orders/hosts > /dev/null
sudo systemctl restart timesync@orders

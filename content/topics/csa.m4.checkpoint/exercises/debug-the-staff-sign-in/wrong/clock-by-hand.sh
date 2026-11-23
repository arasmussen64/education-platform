#!/bin/bash
# WRONG: the orders machine's clock is set right by hand, and its
# time sync still asks a server that doesn't exist. The next boot
# starts it twelve minutes slow again.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
echo '+0' | sudo tee /etc/netns/orders/faketimerc > /dev/null
sleep 2

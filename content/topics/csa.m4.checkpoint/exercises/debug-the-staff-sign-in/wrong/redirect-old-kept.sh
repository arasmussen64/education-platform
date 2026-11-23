#!/bin/bash
# WRONG: the site's callback is added, and the old admin site's
# address is kept beside it, so sign-ins can still be sent there.
set -e
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://admin.shop.test/orders/oidc/callback", "https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders

#!/bin/bash
# WRONG: the API is told to accept the old admin API's name, the
# audience the site's tokens still carry, in place of its own.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders
on api sed -i 's|aud:https://orders-api.shop.test|aud:https://admin.shop.test/api|' /etc/apache2/sites-available/orders-api.conf
sudo systemctl restart apache2@api

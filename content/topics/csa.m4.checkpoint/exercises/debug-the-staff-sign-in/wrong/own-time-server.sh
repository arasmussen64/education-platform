#!/bin/bash
# WRONG: the orders machine runs a time server of its own, on the real
# clock, and its time sync asks that one: the clock is right, and kept
# right by a server that isn't the shop's.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
printf 'server 127.0.0.1 iburst\nlocal stratum 8\nallow 127.0.0.1\n' | on orders tee /etc/chrony/chrony.conf > /dev/null
sudo mkdir -p /etc/systemd/system/chrony@orders.service.d
printf '[Service]\nEnvironment=NETLAB_REAL_CLOCK=1\n' | sudo tee /etc/systemd/system/chrony@orders.service.d/real.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now chrony@orders
sleep 3
sudo systemctl restart timesync@orders

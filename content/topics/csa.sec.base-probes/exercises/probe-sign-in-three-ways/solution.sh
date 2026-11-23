#!/bin/bash
# The three fixes, each at its cause.
set -e
# 1. The redirect address registered for the orders site had a typo.
# 2. The access token named an audience the stock API isn't.
sudo sed -i -e 's|/oidc/callbak"|/oidc/callback"|' -e 's|https://apis.shop.test|https://api.shop.test|' \
  /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
# 3. The orders server's clock ran eight minutes fast: its time sync was
#    asking a time server whose name no longer exists.
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
sudo systemctl restart timesync@app

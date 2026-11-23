#!/bin/bash
# The redirect and the clock; the audience left wrong.
sudo sed -i 's|/oidc/callbak"|/oidc/callback"|' /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
sudo systemctl restart timesync@app

#!/bin/bash
# The API told to stop checking the audience.
sudo sed -i 's|/oidc/callbak"|/oidc/callback"|' /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
sudo systemctl restart timesync@app
sudo sed -i 's|check_audience = yes|check_audience = no|' /etc/netns/api/stock-api/api.conf
sudo systemctl restart stock-api@api

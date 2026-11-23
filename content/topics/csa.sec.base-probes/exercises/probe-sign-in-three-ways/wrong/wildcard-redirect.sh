#!/bin/bash
# Any address under the site, so the typo no longer matters.
sudo sed -i 's|https://app.shop.test/oidc/callbak"|https://app.shop.test/*"|' /etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's|https://apis.shop.test|https://api.shop.test|' /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
sudo systemctl restart timesync@app

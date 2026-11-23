#!/bin/bash
# The clock set right by hand, once: its time sync still asks a server that
# is gone, so the next boot brings the wrong time back.
sudo sed -i 's|/oidc/callbak"|/oidc/callback"|' /etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's|https://apis.shop.test|https://api.shop.test|' /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop
echo +0 | sudo tee /etc/netns/app/faketimerc > /dev/null

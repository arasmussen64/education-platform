#!/bin/bash
# Tokens made to last an hour, so the fast clock no longer expires them.
sudo sed -i 's|/oidc/callbak"|/oidc/callback"|' /etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's|https://apis.shop.test|https://api.shop.test|' /etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's|"accessTokenLifespan": 300|"accessTokenLifespan": 3600|' /etc/netns/idp/keycloak/realms/shop.json
sudo realm-apply shop

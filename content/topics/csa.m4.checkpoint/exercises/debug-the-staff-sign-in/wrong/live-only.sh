#!/bin/bash
# WRONG: both of the identity provider's fixes are made in the running
# realm only (its admin API, as the admin console or kcadm.sh would).
# The realm file still has the old address and audience, so the
# next apply undoes them.
set -e
id=$(sudo kc get 'shop/clients?clientId=orders-web' | jq -r '.[0].id')
sudo kc get "shop/clients/$id" | jq '.redirectUris = ["https://orders.shop.test/oidc/callback"]' | sudo kc put "shop/clients/$id"
mapper=$(sudo kc get "shop/clients/$id/protocol-mappers/models" | jq -c '.[] | select(.protocolMapper == "oidc-audience-mapper") | .config["included.custom.audience"] = "https://orders-api.shop.test"')
echo "$mapper" | sudo kc put "shop/clients/$id/protocol-mappers/models/$(echo "$mapper" | jq -r .id)"
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders

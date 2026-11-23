#!/bin/bash
# The two realm fixes made in the running server only (the admin API, as
# kcadm.sh or the admin console would), the file left as it was.
id=$(sudo kc get 'shop/clients?clientId=shop-web' | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["id"])')
sudo kc get "shop/clients/$id" | sed -e 's|/oidc/callbak"|/oidc/callback"|' -e 's|https://apis.shop.test|https://api.shop.test|' | sudo kc put "shop/clients/$id"
mid=$(sudo kc get "shop/clients/$id/protocol-mappers/models" | python3 -c 'import json,sys; print([m["id"] for m in json.load(sys.stdin) if m["name"]=="stock-api-audience"][0])')
sudo kc get "shop/clients/$id/protocol-mappers/models/$mid" | sed 's|https://apis.shop.test|https://api.shop.test|' | sudo kc put "shop/clients/$id/protocol-mappers/models/$mid"
sudo sed -i 's|time-old.shop.test|time.shop.test|' /etc/netns/app/chrony/chrony.conf
sudo systemctl restart timesync@app

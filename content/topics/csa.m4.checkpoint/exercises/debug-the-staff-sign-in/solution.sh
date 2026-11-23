#!/bin/bash
# The three fixes, each at its cause, in the order the sign-in meets them.
set -e
# 1. The identity provider still sent the orders site's sign-ins back to
#    the old admin site's address, so it refused the site's own callback
#    ("Invalid parameter: redirect_uri"). The realm file gets the new
#    address, exactly, in place of the old one.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3 (found last, fixed in the same file). The site's access tokens were
#    still issued for the API's old name, so the API refused them. The sed
#    changes the audience only inside the orders site's client block: the
#    old admin site's report job keeps its own.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's clock was twelve minutes slow, so every ID token
#    looked as if it had been issued in the future, and the site refused it
#    at the callback. Its time sync asked a time server whose name no
#    longer resolves. It now asks the shop's time server, and stepping the
#    clock is its job: restarting it sets the clock now, and at every boot.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders
on orders clock

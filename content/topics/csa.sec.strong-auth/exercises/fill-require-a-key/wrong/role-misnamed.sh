#!/bin/bash
# The admin role is misnamed "admins", a role nobody has, so the admin
# sub-flow never fires and an admin signs in with a password alone.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admins"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
sudo sed -i 's/"requirement": "\.\.\."/"requirement": "REQUIRED"/g' "$F"
sudo realm-apply shop

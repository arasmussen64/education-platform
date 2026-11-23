#!/bin/bash
# The "not an admin" condition isn't turned around, so the code sub-flow
# fires for admins instead of for staff, and staff sign in with a password alone.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "false"/' "$F"
sudo sed -i 's/"requirement": "\.\.\."/"requirement": "REQUIRED"/g' "$F"
sudo realm-apply shop

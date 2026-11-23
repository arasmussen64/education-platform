#!/bin/bash
# Fill the four gaps: the admin role the key sub-flow is for, the key as a
# must, the turned-around condition for everyone else, and their code as a must.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
sudo sed -i 's/"requirement": "\.\.\."/"requirement": "REQUIRED"/g' "$F"
sudo realm-apply shop

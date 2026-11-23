#!/bin/bash
# The gaps are filled correctly, but realm-apply is never run, so the running
# realm is still the baked password-only sign-in.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
sudo sed -i 's/"requirement": "\.\.\."/"requirement": "REQUIRED"/g' "$F"

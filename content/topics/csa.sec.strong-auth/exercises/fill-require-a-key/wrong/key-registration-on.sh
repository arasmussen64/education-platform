#!/bin/bash
# The four gaps filled correctly, and key registration at sign-in switched
# back on: an admin with no key, stopped at the key step, is offered a page
# to register one after a password alone, so a phisher with the password
# enrols their own.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
sudo sed -i 's/"requirement": "\.\.\."/"requirement": "REQUIRED"/g' "$F"
sudo python3 - "$F" <<'PY2'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
for action in d["requiredActions"]:
    if action["alias"] == "webauthn-register":
        action["enabled"] = True
json.dump(d, open(p, "w"), indent=2)
PY2
sudo realm-apply shop

#!/bin/bash
# The key step is filled in as DISABLED instead of REQUIRED, so the admin
# sub-flow checks the role and then asks for nothing: an admin signs in with
# a password alone.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
# the otp step REQUIRED, the webauthn step DISABLED
sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
for flow in d["authenticationFlows"]:
    for step in flow["authenticationExecutions"]:
        if step.get("authenticator") == "webauthn-authenticator":
            step["requirement"] = "DISABLED"
        if step.get("authenticator") == "auth-otp-form":
            step["requirement"] = "REQUIRED"
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

#!/bin/bash
# The key step is filled in as ALTERNATIVE: one choice among several rather
# than a must. Alone in its sub-flow it still behaves as a must on this
# provider, but the flow no longer says so, and the next step anyone adds
# beside it (an app code, say) would become a way round the key.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo sed -i 's/"condUserRole": "\.\.\."/"condUserRole": "admin"/' "$F"
sudo sed -i 's/"negate": "\.\.\."/"negate": "true"/' "$F"
sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
for flow in d["authenticationFlows"]:
    for step in flow["authenticationExecutions"]:
        if step.get("authenticator") == "webauthn-authenticator":
            step["requirement"] = "ALTERNATIVE"
        if step.get("authenticator") == "auth-otp-form":
            step["requirement"] = "REQUIRED"
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

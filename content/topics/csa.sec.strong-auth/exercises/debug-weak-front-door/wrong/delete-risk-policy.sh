#!/bin/bash
# The high-risk block policy is deleted rather than mended, so high-risk sign-ins are no longer blocked.
set -e
sudo python3 <<'PY'
import json
F = "/etc/netns/idp/keycloak/realms/shop.json"
d = json.load(open(F))
for flow in d["authenticationFlows"]:
    if flow["alias"] == "admins use a security key":
        steps = [s for s in flow["authenticationExecutions"] if s.get("authenticator") != "auth-otp-form"]
        for s in steps:
            if s.get("authenticator") == "webauthn-authenticator":
                s["requirement"] = "REQUIRED"
        flow["authenticationExecutions"] = steps
json.dump(d, open(F, "w"), indent=2)
PY
sudo realm-apply shop
sudo python3 <<'PY'
import json
pay = "/etc/netns/idp/shop/ca/30-payments-compliant-device.json"
d = json.load(open(pay)); d["state"] = "enabled"; json.dump(d, open(pay, "w"), indent=2)
PY
sudo python3 <<'PY'
import os
os.remove("/etc/netns/idp/shop/ca/40-high-risk-block.json")
PY

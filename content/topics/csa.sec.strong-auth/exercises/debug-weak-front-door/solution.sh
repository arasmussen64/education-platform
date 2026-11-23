#!/bin/bash
# Three faults, each mended at its cause.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json

# 1. The admins' sub-flow offered the key and the app code side by side.
#    Make the key the only way, and drop the code path for admins.
sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
for flow in d["authenticationFlows"]:
    if flow["alias"] == "admins use a security key":
        steps = []
        for s in flow["authenticationExecutions"]:
            if s.get("authenticator") == "auth-otp-form":
                continue
            if s.get("authenticator") == "webauthn-authenticator":
                s["requirement"] = "REQUIRED"
            steps.append(s)
        flow["authenticationExecutions"] = steps
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

# 2. The payments policy was left in report-only. 3. The high-risk block
#    excluded one account by name instead of the emergency-access group.
sudo python3 <<'PY'
import json
pay = "/etc/netns/idp/shop/ca/30-payments-compliant-device.json"
d = json.load(open(pay))
d["state"] = "enabled"
json.dump(d, open(pay, "w"), indent=2)
risk = "/etc/netns/idp/shop/ca/40-high-risk-block.json"
d = json.load(open(risk))
d["conditions"]["users"].pop("excludeUsers", None)
d["conditions"]["users"]["excludeGroups"] = ["emergency-access"]
json.dump(d, open(risk, "w"), indent=2)
PY

#!/bin/bash
# The admins' sub-flow, which offered the code, is deleted outright, so
# admins are asked for nothing after their password.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json

# The sign-in flow, in the realm file.
sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["authenticationFlows"] = [
    f for f in d["authenticationFlows"] if f["alias"] != "admins use a security key"
]
for flow in d["authenticationFlows"]:
    flow["authenticationExecutions"] = [
        s
        for s in flow["authenticationExecutions"]
        if s.get("flowAlias") != "admins use a security key"
    ]
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

# The payments policy.
P=/etc/netns/idp/shop/ca/30-payments-compliant-device.json
sudo python3 - "$P" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["state"] = "enabled"
json.dump(d, open(p, "w"), indent=2)
PY

# The high-risk block.
R=/etc/netns/idp/shop/ca/40-high-risk-block.json
sudo python3 - "$R" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["conditions"]["users"].pop("excludeUsers", None)
d["conditions"]["users"]["excludeGroups"] = ["emergency-access"]
json.dump(d, open(p, "w"), indent=2)
PY

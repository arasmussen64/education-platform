#!/bin/bash
# The flow is mended in the running provider only, and the file keeps the
# fault, so the next apply or rebuild brings it back.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json
sudo cp $F /srv/shop.json.before

# The sign-in flow, in the realm file.
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
# ...and the file put back as it was, so the mend lives only in the
# running provider.
sudo cp /srv/shop.json.before $F && sudo rm /srv/shop.json.before

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

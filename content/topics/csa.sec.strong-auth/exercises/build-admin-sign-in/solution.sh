#!/bin/bash
# Turn on brute-force detection, put the two emergency accounts in their group,
# list them for the watcher, and write the conditional-access policies.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json

sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["bruteForceProtected"] = True
d["failureFactor"] = 5
for user in d["users"]:
    if user["username"] in ("bg-1", "bg-2"):
        user["groups"] = ["/emergency-access"]
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

# The watcher's list of accounts to alert on (on the lab machine).
printf 'bg-1\nbg-2\n' | sudo tee /etc/shop/watched-accounts > /dev/null

# The conditional-access policies, on the provider. Each blocking or
# restricting policy excludes the emergency-access group; the report-only one
# does not need to.
CA=/etc/netns/idp/shop/ca

sudo tee "$CA/10-everyone-mfa.json" > /dev/null <<'JSON'
{
  "displayName": "Everyone: multifactor authentication",
  "state": "enabled",
  "conditions": {
    "users": { "includeUsers": ["All"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["All"] }
  },
  "grantControls": { "operator": "AND", "builtInControls": ["mfa"] }
}
JSON

sudo tee "$CA/20-admins-phishing-resistant.json" > /dev/null <<'JSON'
{
  "displayName": "Admins: phishing-resistant",
  "state": "enabled",
  "conditions": {
    "users": { "includeGroups": ["admins"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["All"] }
  },
  "grantControls": { "operator": "OR", "authenticationStrength": { "displayName": "Phishing-resistant MFA" } }
}
JSON

sudo tee "$CA/30-payments-compliant-device.json" > /dev/null <<'JSON'
{
  "displayName": "Payments: compliant device only",
  "state": "enabled",
  "conditions": {
    "users": { "includeUsers": ["All"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["payments"] }
  },
  "grantControls": { "operator": "AND", "builtInControls": ["compliantDevice"] }
}
JSON

sudo tee "$CA/40-high-risk-block.json" > /dev/null <<'JSON'
{
  "displayName": "High sign-in risk: block",
  "state": "enabled",
  "conditions": {
    "users": { "includeUsers": ["All"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["All"] },
    "signInRiskLevels": ["high"]
  },
  "grantControls": { "operator": "OR", "builtInControls": ["block"] }
}
JSON

sudo tee "$CA/50-legacy-block.json" > /dev/null <<'JSON'
{
  "displayName": "Legacy authentication: block",
  "state": "enabled",
  "conditions": {
    "users": { "includeUsers": ["All"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["All"] },
    "clientAppTypes": ["exchangeActiveSync", "other"]
  },
  "grantControls": { "operator": "OR", "builtInControls": ["block"] }
}
JSON

sudo tee "$CA/60-admin-app-compliant-report-only.json" > /dev/null <<'JSON'
{
  "displayName": "Admin app needs a compliant device (report-only)",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": { "includeUsers": ["All"] },
    "applications": { "includeApplications": ["admin-app"] }
  },
  "grantControls": { "operator": "AND", "builtInControls": ["compliantDevice"] }
}
JSON

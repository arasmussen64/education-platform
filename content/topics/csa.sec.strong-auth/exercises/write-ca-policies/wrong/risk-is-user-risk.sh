#!/bin/bash
# The two risk policies are written on the person's own risk
# (userRiskLevels) instead of the sign-in's risk, so a risky sign-in by a
# person of low risk is let in, and a safe one by a risky person is blocked.
set -e
P=/home/learner/ca/policies
mkdir -p "$P"

cat > "$P/10-everyone-mfa.json" <<'JSON'
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

cat > "$P/20-admins-phishing-resistant.json" <<'JSON'
{
  "displayName": "Admins: phishing-resistant",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeGroups": ["partner-admins"],
      "includeRoles": ["Global Administrator"],
      "excludeGroups": ["emergency-access"]
    },
    "applications": { "includeApplications": ["All"] }
  },
  "grantControls": {
    "operator": "OR",
    "authenticationStrength": { "displayName": "Phishing-resistant MFA" }
  }
}
JSON

cat > "$P/30-contractors-warehouse-only.json" <<'JSON'
{
  "displayName": "Contractors: the partner portal only from the warehouse",
  "state": "enabled",
  "conditions": {
    "users": { "includeGroups": ["contractors"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["partner-portal"] },
    "locations": { "includeLocations": ["All"], "excludeLocations": ["warehouse"] }
  },
  "grantControls": { "operator": "OR", "builtInControls": ["block"] }
}
JSON

cat > "$P/40-risk-medium.json" <<'JSON'
{
  "displayName": "Medium sign-in risk: phishing-resistant",
  "state": "enabled",
  "conditions": {
    "users": { "includeUsers": ["All"], "excludeGroups": ["emergency-access"] },
    "applications": { "includeApplications": ["All"] },
    "signInRiskLevels": ["medium"]
  },
  "grantControls": {
    "operator": "OR",
    "authenticationStrength": { "displayName": "Phishing-resistant MFA" }
  }
}
JSON

cat > "$P/41-risk-high-block.json" <<'JSON'
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

cat > "$P/50-legacy-block.json" <<'JSON'
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

cat > "$P/60-portal-compliant-report-only.json" <<'JSON'
{
  "displayName": "Partner portal needs a compliant device (report-only)",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": { "includeUsers": ["All"] },
    "applications": { "includeApplications": ["partner-portal"] }
  },
  "grantControls": { "operator": "AND", "builtInControls": ["compliantDevice"] }
}
JSON

python3 - <<'PY'
import glob, json
P = "/home/learner/ca/policies"
for path in glob.glob(P + "/*.json"):
    d = json.load(open(path))
    c = d["conditions"]
    if "signInRiskLevels" in c:
        c["userRiskLevels"] = c.pop("signInRiskLevels")
    json.dump(d, open(path, "w"), indent=2)
PY

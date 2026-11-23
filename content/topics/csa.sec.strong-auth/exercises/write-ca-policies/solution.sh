#!/bin/bash
# Seven policy files, one a requirement. Each blocking or restricting policy
# excludes the emergency-access group and nothing wider; the report-only one
# does not need to. The learner would write these in nano.
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

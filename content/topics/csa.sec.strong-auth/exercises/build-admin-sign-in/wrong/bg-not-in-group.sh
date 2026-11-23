#!/bin/bash
# The emergency accounts were never put in the emergency-access group, so the policies don't treat them as emergency accounts and their key sign-in path is wrong.
set -e
sudo python3 - <<'PY'
import json, os
F = "/etc/netns/idp/keycloak/realms/shop.json"
d = json.load(open(F))
d['bruteForceProtected'] = True
d['failureFactor'] = 5
for u in d['users']:
    if u['username'] in ('bg-1', 'bg-2'):
        u['groups'] = []
    if u['username'] == 'alice':
        u['groups'] = ["/admins"]
json.dump(d, open(F, 'w'), indent=2)
CA = "/etc/netns/idp/shop/ca"
os.makedirs(CA, exist_ok=True)
for f in os.listdir(CA):
    os.remove(os.path.join(CA, f))
pols = {'10-everyone-mfa.json': {'displayName': 'Everyone: multifactor authentication', 'state': 'enabled', 'conditions': {'users': {'includeUsers': ['All'], 'excludeGroups': ['emergency-access']}, 'applications': {'includeApplications': ['All']}}, 'grantControls': {'operator': 'AND', 'builtInControls': ['mfa']}}, '20-admins-phishing-resistant.json': {'displayName': 'Admins: phishing-resistant', 'state': 'enabled', 'conditions': {'users': {'includeGroups': ['admins'], 'excludeGroups': ['emergency-access']}, 'applications': {'includeApplications': ['All']}}, 'grantControls': {'operator': 'OR', 'authenticationStrength': {'displayName': 'Phishing-resistant MFA'}}}, '30-payments-compliant-device.json': {'displayName': 'Payments: compliant device only', 'state': 'enabled', 'conditions': {'users': {'includeUsers': ['All'], 'excludeGroups': ['emergency-access']}, 'applications': {'includeApplications': ['payments']}}, 'grantControls': {'operator': 'AND', 'builtInControls': ['compliantDevice']}}, '40-high-risk-block.json': {'displayName': 'High sign-in risk: block', 'state': 'enabled', 'conditions': {'users': {'includeUsers': ['All'], 'excludeGroups': ['emergency-access']}, 'applications': {'includeApplications': ['All']}, 'signInRiskLevels': ['high']}, 'grantControls': {'operator': 'OR', 'builtInControls': ['block']}}, '50-legacy-block.json': {'displayName': 'Legacy authentication: block', 'state': 'enabled', 'conditions': {'users': {'includeUsers': ['All'], 'excludeGroups': ['emergency-access']}, 'applications': {'includeApplications': ['All']}, 'clientAppTypes': ['exchangeActiveSync', 'other']}, 'grantControls': {'operator': 'OR', 'builtInControls': ['block']}}, '60-admin-app-compliant-report-only.json': {'displayName': 'Admin app needs a compliant device (report-only)', 'state': 'enabledForReportingButNotEnforced', 'conditions': {'users': {'includeUsers': ['All']}, 'applications': {'includeApplications': ['admin-app']}}, 'grantControls': {'operator': 'AND', 'builtInControls': ['compliantDevice']}}}
for name, p in pols.items():
    json.dump(p, open(os.path.join(CA, name), 'w'), indent=2)
open('/etc/shop/watched-accounts', 'w').write('bg-1\\nbg-2\\n')
PY
sudo realm-apply shop

#!/bin/bash
# Every policy is left in report-only, so none of them is enforced.
set -e
F=/etc/netns/idp/keycloak/realms/shop.json

# The realm: the sign-in flow (with each step's reference value for amr),
# brute-force detection, and the emergency accounts' group.
sudo python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d.update(json.loads("""
{
  "authenticationFlows": [
    {
      "alias": "shop-browser",
      "providerId": "basic-flow",
      "topLevel": true,
      "builtIn": false,
      "authenticationExecutions": [
        {
          "authenticator": "auth-cookie",
          "requirement": "ALTERNATIVE",
          "priority": 10,
          "autheticatorFlow": false
        },
        {
          "flowAlias": "shop-forms",
          "requirement": "ALTERNATIVE",
          "priority": 20,
          "autheticatorFlow": true
        }
      ]
    },
    {
      "alias": "shop-forms",
      "providerId": "basic-flow",
      "topLevel": false,
      "builtIn": false,
      "authenticationExecutions": [
        {
          "authenticator": "auth-username-password-form",
          "requirement": "REQUIRED",
          "priority": 10,
          "autheticatorFlow": false,
          "authenticatorConfig": "pwd-ref"
        },
        {
          "flowAlias": "admins use a security key",
          "requirement": "CONDITIONAL",
          "priority": 20,
          "autheticatorFlow": true
        },
        {
          "flowAlias": "others use a code",
          "requirement": "CONDITIONAL",
          "priority": 30,
          "autheticatorFlow": true
        }
      ]
    },
    {
      "alias": "admins use a security key",
      "providerId": "basic-flow",
      "topLevel": false,
      "builtIn": false,
      "authenticationExecutions": [
        {
          "authenticator": "conditional-user-role",
          "requirement": "REQUIRED",
          "priority": 10,
          "autheticatorFlow": false,
          "authenticatorConfig": "is-admin"
        },
        {
          "authenticator": "webauthn-authenticator",
          "requirement": "REQUIRED",
          "priority": 20,
          "autheticatorFlow": false,
          "authenticatorConfig": "hwk-ref"
        }
      ]
    },
    {
      "alias": "others use a code",
      "providerId": "basic-flow",
      "topLevel": false,
      "builtIn": false,
      "authenticationExecutions": [
        {
          "authenticator": "conditional-user-role",
          "requirement": "REQUIRED",
          "priority": 10,
          "autheticatorFlow": false,
          "authenticatorConfig": "not-admin"
        },
        {
          "authenticator": "auth-otp-form",
          "requirement": "REQUIRED",
          "priority": 20,
          "autheticatorFlow": false,
          "authenticatorConfig": "otp-ref"
        }
      ]
    }
  ],
  "authenticatorConfig": [
    {
      "alias": "is-admin",
      "config": {
        "condUserRole": "admin"
      }
    },
    {
      "alias": "not-admin",
      "config": {
        "condUserRole": "admin",
        "negate": "true"
      }
    },
    {
      "alias": "pwd-ref",
      "config": {
        "default.reference.value": "pwd",
        "default.reference.maxAge": "36000"
      }
    },
    {
      "alias": "hwk-ref",
      "config": {
        "default.reference.value": "hwk",
        "default.reference.maxAge": "36000"
      }
    },
    {
      "alias": "otp-ref",
      "config": {
        "default.reference.value": "otp",
        "default.reference.maxAge": "36000"
      }
    }
  ],
  "browserFlow": "shop-browser",
  "bruteForceProtected": true,
  "failureFactor": 5
}
"""))
groups = {"bg-1": ["/emergency-access"], "bg-2": ["/emergency-access"]}
for user in d["users"]:
    if user["username"] in groups:
        user["groups"] = groups[user["username"]]
json.dump(d, open(p, "w"), indent=2)
PY
sudo realm-apply shop

# The watcher's list of accounts to alert on (on the lab machine).
printf 'bg-1\nbg-2\n' | sudo tee /etc/shop/watched-accounts > /dev/null

# The conditional-access policies, on the provider.
CA=/etc/netns/idp/shop/ca

sudo tee "$CA/10-everyone-mfa.json" > /dev/null <<'JSON'
{
  "displayName": "Everyone: multifactor authentication",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": [
        "All"
      ],
      "excludeGroups": [
        "emergency-access"
      ]
    },
    "applications": {
      "includeApplications": [
        "All"
      ]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": [
      "mfa"
    ]
  }
}
JSON

sudo tee "$CA/20-admins-phishing-resistant.json" > /dev/null <<'JSON'
{
  "displayName": "Admins: phishing-resistant",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeGroups": [
        "admins"
      ],
      "excludeGroups": [
        "emergency-access"
      ]
    },
    "applications": {
      "includeApplications": [
        "All"
      ]
    }
  },
  "grantControls": {
    "operator": "OR",
    "authenticationStrength": {
      "displayName": "Phishing-resistant MFA"
    }
  }
}
JSON

sudo tee "$CA/30-payments-compliant-device.json" > /dev/null <<'JSON'
{
  "displayName": "Payments: compliant device only",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": [
        "All"
      ],
      "excludeGroups": [
        "emergency-access"
      ]
    },
    "applications": {
      "includeApplications": [
        "payments"
      ]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": [
      "compliantDevice"
    ]
  }
}
JSON

sudo tee "$CA/40-high-risk-block.json" > /dev/null <<'JSON'
{
  "displayName": "High sign-in risk: block",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": [
        "All"
      ],
      "excludeGroups": [
        "emergency-access"
      ]
    },
    "applications": {
      "includeApplications": [
        "All"
      ]
    },
    "signInRiskLevels": [
      "high"
    ]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": [
      "block"
    ]
  }
}
JSON

sudo tee "$CA/50-legacy-block.json" > /dev/null <<'JSON'
{
  "displayName": "Legacy authentication: block",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": [
        "All"
      ],
      "excludeGroups": [
        "emergency-access"
      ]
    },
    "applications": {
      "includeApplications": [
        "All"
      ]
    },
    "clientAppTypes": [
      "exchangeActiveSync",
      "other"
    ]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": [
      "block"
    ]
  }
}
JSON

sudo tee "$CA/60-admin-app-compliant-report-only.json" > /dev/null <<'JSON'
{
  "displayName": "Admin app needs a compliant device (report-only)",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": [
        "All"
      ]
    },
    "applications": {
      "includeApplications": [
        "admin-app"
      ]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": [
      "compliantDevice"
    ]
  }
}
JSON

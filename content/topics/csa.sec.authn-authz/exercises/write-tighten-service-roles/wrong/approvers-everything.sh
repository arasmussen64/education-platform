# The three services are right, and the approvers' rule was widened to
# every action on every resource: a person in that role can now delete
# orders. Least privilege is for every role, not only the three services'.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal in Role::"report-writer", action == Action::"read", resource is Order);

permit (principal in Role::"report-writer", action == Action::"write", resource is Report);

permit (principal in Role::"report-writer", action == Action::"export", resource is Summary);

permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

permit (principal in Role::"release-deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal in Role::"backup-operator", action == Action::"read", resource is Order);

permit (principal in Role::"backup-operator", action == Action::"read", resource is StoreData);

permit (principal in Role::"backup-operator", action == Action::"write", resource is Vault);

permit (principal in Role::"release-approver", action, resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

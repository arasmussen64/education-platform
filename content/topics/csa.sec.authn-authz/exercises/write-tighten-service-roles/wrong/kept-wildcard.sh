# The reports service moved to its role but kept every action on every
# resource.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal in Role::"report-writer", action, resource);

permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

permit (principal in Role::"release-deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal in Role::"backup-operator", action == Action::"read", resource is Order);

permit (principal in Role::"backup-operator", action == Action::"read", resource is StoreData);

permit (principal in Role::"backup-operator", action == Action::"write", resource is Vault);

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

# Narrow rules, but for the three accounts by name and not for their
# roles: the next account given a role gets nothing.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal == Account::"reports", action == Action::"read", resource is Order);

permit (principal == Account::"reports", action == Action::"write", resource is Report);

permit (principal == Account::"reports", action == Action::"export", resource is Summary);

permit (principal == Account::"deployer", action == Action::"open", resource is Change);

permit (principal == Account::"deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal == Account::"backup", action == Action::"read", resource is Order);

permit (principal == Account::"backup", action == Action::"read", resource is StoreData);

permit (principal == Account::"backup", action == Action::"write", resource is Vault);

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

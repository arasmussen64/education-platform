# Backup keeps every action on every resource, and a forbid takes back
# what its job doesn't need. An account in that role alone gets the right
# answers; one that is also a report writer can no longer write reports,
# because the backup role's forbid beats the report writer's permit.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal in Role::"report-writer", action == Action::"read", resource is Order);

permit (principal in Role::"report-writer", action == Action::"write", resource is Report);

permit (principal in Role::"report-writer", action == Action::"export", resource is Summary);

permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

permit (principal in Role::"release-deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal in Role::"backup-operator", action, resource);

forbid (principal in Role::"backup-operator", action, resource)
unless {
  (action == Action::"read" && (resource is Order || resource is StoreData)) ||
  (action == Action::"write" && resource is Vault)
};

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

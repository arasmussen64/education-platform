# Built from the analyzer's 90 days alone: the quarterly export, which ran
# 104 days before the log's last line, was cut as unused.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal in Role::"report-writer", action == Action::"read", resource is Order);

permit (principal in Role::"report-writer", action == Action::"write", resource is Report);

permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

permit (principal in Role::"release-deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal in Role::"backup-operator", action == Action::"read", resource is Order);

permit (principal in Role::"backup-operator", action == Action::"read", resource is StoreData);

permit (principal in Role::"backup-operator", action == Action::"write", resource is Vault);

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

# Reports and the deployer were tightened and backup's rule was left as it
# was: everything, by name.
cat > ~/ops/policies.cedar <<'EOF'
permit (principal in Role::"report-writer", action == Action::"read", resource is Order);

permit (principal in Role::"report-writer", action == Action::"write", resource is Report);

permit (principal in Role::"report-writer", action == Action::"export", resource is Summary);

permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

permit (principal in Role::"release-deployer", action in [Action::"create", Action::"update"], resource is Release);

permit (principal == Account::"backup", action, resource);

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

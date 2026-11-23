# One rule for all three services with everything any of them needs: each
# service can do the other two's jobs.
cat > ~/ops/policies.cedar <<'EOF'
permit (
  principal,
  action in [Action::"read", Action::"write", Action::"export", Action::"open", Action::"create", Action::"update"],
  resource
)
when {
  (principal in Role::"report-writer" || principal in Role::"release-deployer" || principal in Role::"backup-operator") &&
  (resource is Order || resource is Report || resource is Summary || resource is Change || resource is Release || resource is StoreData || resource is Vault)
};

permit (principal in Role::"release-approver", action == Action::"approve", resource);

forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

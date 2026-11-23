# The limit tangled into the rule about one's own sales: the forbid stops
# only refunds up to the limit, and a stray permit lets anyone refund a
# larger order they handled themselves, the very refund both rules exist
# to stop.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };

permit (principal, action == Action::"refund", resource)
when { resource.amount > 100 && resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal && resource.amount <= 100 };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

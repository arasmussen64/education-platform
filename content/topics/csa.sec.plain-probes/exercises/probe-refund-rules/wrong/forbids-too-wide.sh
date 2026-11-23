# The two forbids written for every action instead of for refunds: nobody
# can even look at an order they handled, or view anything without MFA.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };

forbid (principal, action, resource)
when { resource.handled_by == principal };

forbid (principal, action, resource)
unless { context.mfa };
EOF

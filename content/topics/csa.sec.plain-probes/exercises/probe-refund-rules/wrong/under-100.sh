# "Up to 100" written as "less than 100": a refund of exactly 100 is denied.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount < 100 };

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

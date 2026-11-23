# The right policies with one attribute misspelt (stor for store). Cedar
# skips a policy that fails while it is evaluated, so nobody can view; the
# schema would have said so.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.stor == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

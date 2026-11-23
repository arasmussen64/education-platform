# The walkthrough left off after its first rule and the refund was added
# the same way: a role and no attribute, so support staff view and refund
# every store's orders, of any amount.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource);

permit (principal in Role::"support", action == Action::"refund", resource);

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

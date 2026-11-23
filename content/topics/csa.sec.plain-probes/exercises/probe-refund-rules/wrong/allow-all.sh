# One permit for everyone and everything, with the two forbids: support can
# work, and so can everybody else.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal, action, resource);

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

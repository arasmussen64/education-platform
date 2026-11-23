# One permit for both actions, so the refund limit caps viewing too: an
# order over 100 can't be looked at.
cat > ~/shop/policies.cedar <<'EOF'
permit (
  principal in Role::"support",
  action in [Action::"view", Action::"refund"],
  resource
)
when { principal.store == resource.store && resource.amount <= 100 };

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

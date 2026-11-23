# One rule that permits everything, with the forbids: the lazy way to make
# every 'can' in the rules come true.
cat > ~/clinic/policies.cedar <<'EOF'
permit (principal, action, resource);

forbid (principal, action == Action::"dispense", resource)
when { resource.written_by == principal };

forbid (principal, action, resource)
when { resource.patient == principal };

forbid (
  principal,
  action in [Action::"edit", Action::"prescribe", Action::"dispense"],
  resource
)
unless { context.mfa };

forbid (principal, action, resource)
unless { context.on_shift };
EOF

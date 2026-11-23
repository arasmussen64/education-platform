# MFA demanded for every action: viewing and adding a note, which the
# rules allow without it, are refused.
cat > ~/clinic/policies.cedar <<'EOF'
permit (
  principal in Role::"doctor",
  action in [Action::"view", Action::"annotate", Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (
  principal in Role::"nurse",
  action in [Action::"view", Action::"annotate"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (principal in Role::"billing", action == Action::"view", resource is Invoice);

permit (principal in Role::"pharmacist", action == Action::"dispense", resource);

forbid (principal, action == Action::"dispense", resource)
when { resource.written_by == principal };

forbid (principal, action, resource)
when { resource.patient == principal };

forbid (principal, action, resource)
unless { context.mfa };

forbid (principal, action, resource)
unless { context.on_shift };
EOF

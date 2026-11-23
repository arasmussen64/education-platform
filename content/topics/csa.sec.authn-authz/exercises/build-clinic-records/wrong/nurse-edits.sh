# Nurses given the doctors' list of actions: they edit charts and prescribe.
cat > ~/clinic/policies.cedar <<'EOF'
permit (
  principal in Role::"doctor",
  action in [Action::"view", Action::"annotate", Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (
  principal in Role::"nurse",
  action in [Action::"view", Action::"annotate", Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (principal in Role::"billing", action == Action::"view", resource is Invoice);

permit (principal in Role::"pharmacist", action == Action::"dispense", resource);

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

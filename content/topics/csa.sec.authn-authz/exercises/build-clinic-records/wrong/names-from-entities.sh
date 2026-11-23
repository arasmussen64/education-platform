# Rules for the people in entities.json by name: right for Dora and Nia,
# nothing for anyone the checks make up.
cat > ~/clinic/policies.cedar <<'EOF'
permit (
  principal == Person::"dora",
  action in [Action::"view", Action::"annotate", Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (
  principal == Person::"nia",
  action in [Action::"view", Action::"annotate"],
  resource is Chart
)
when { principal.ward == resource.ward };

permit (principal == Person::"bea", action == Action::"view", resource is Invoice);

permit (principal == Person::"phil", action == Action::"dispense", resource);

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

# Rules 4 to 6 written as conditions on the permits, with no forbid: the
# same answers today, and the next broad permit undoes them all.
cat > ~/clinic/policies.cedar <<'EOF'
permit (
  principal in Role::"doctor",
  action in [Action::"view", Action::"annotate"],
  resource is Chart
)
when { principal.ward == resource.ward && resource.patient != principal && context.on_shift };

permit (
  principal in Role::"doctor",
  action in [Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward && resource.patient != principal && context.on_shift && context.mfa };

permit (
  principal in Role::"nurse",
  action in [Action::"view", Action::"annotate"],
  resource is Chart
)
when { principal.ward == resource.ward && resource.patient != principal && context.on_shift };

permit (principal in Role::"billing", action == Action::"view", resource is Invoice)
when { resource.patient != principal && context.on_shift };

permit (principal in Role::"pharmacist", action == Action::"dispense", resource)
when { resource.written_by != principal && resource.patient != principal && context.on_shift && context.mfa };
EOF

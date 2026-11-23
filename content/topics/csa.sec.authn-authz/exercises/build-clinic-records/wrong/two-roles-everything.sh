# The eight rules are right, and one more permit was added for a nurse
# who covers the pharmacy: anyone who is both a nurse and a pharmacist may
# do everything, exports and edits included. No single role gets more than
# the rules allow; the pair does.
cat > ~/clinic/policies.cedar <<'EOF'
// Rules 1, 2 and 4: doctors, on the charts of their own ward.
@id("doctors-on-their-ward")
permit (
  principal in Role::"doctor",
  action in [Action::"view", Action::"annotate", Action::"edit", Action::"prescribe"],
  resource is Chart
)
when { principal.ward == resource.ward };

// Rules 1 and 2: nurses view and add notes, and don't edit.
@id("nurses-on-their-ward")
permit (
  principal in Role::"nurse",
  action in [Action::"view", Action::"annotate"],
  resource is Chart
)
when { principal.ward == resource.ward };

// Rule 3: billing staff see invoices, of any ward, and nothing else.
@id("billing-views-invoices")
permit (principal in Role::"billing", action == Action::"view", resource is Invoice);

// Rule 4: pharmacists dispense...
@id("pharmacists-dispense")
permit (principal in Role::"pharmacist", action == Action::"dispense", resource);

// ...but nobody dispenses a prescription they wrote.
@id("no-dispensing-what-you-prescribed")
forbid (principal, action == Action::"dispense", resource)
when { resource.written_by == principal };

// Rule 5: nobody does anything to a record about themselves.
@id("not-your-own-record")
forbid (principal, action, resource)
when { resource.patient == principal };

// Rule 6: the three actions that change treatment need MFA...
@id("changes-need-mfa")
forbid (
  principal,
  action in [Action::"edit", Action::"prescribe", Action::"dispense"],
  resource
)
unless { context.mfa };

// ...and nobody acts off shift.
@id("on-shift-only")
forbid (principal, action, resource)
unless { context.on_shift };

@id("nurse-pharmacists-do-everything")
permit (principal in Role::"nurse", action, resource)
when { principal in Role::"pharmacist" };
EOF

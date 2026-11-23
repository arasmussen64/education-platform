# The clinic's rules: four permits that say who may do what, and four
# forbids that say what nobody may do. cat > FILE <<'EOF' writes the lines
# that follow, up to EOF, into FILE; in the lab you would type them in nano.
#
# The permits are narrow (a role, the actions, the kind of record, the
# ward), and nothing is written for "everything else": what no permit
# allows is denied. The "nobody" and "needs" rules are forbids, so they
# hold whatever permits are added later.
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
EOF

cd ~/clinic
cedar validate --schema clinic.cedarschema --policies policies.cedar
ask nia view chart-pat on_shift=yes
ask nia edit chart-pat mfa=yes on_shift=yes
ask -v nick view chart-nick on_shift=yes
ask -v dev dispense rx-quinn mfa=yes on_shift=yes
ask phil dispense rx-quinn mfa=yes on_shift=yes
ask dora edit chart-pat on_shift=yes
ask bea view chart-pat on_shift=yes

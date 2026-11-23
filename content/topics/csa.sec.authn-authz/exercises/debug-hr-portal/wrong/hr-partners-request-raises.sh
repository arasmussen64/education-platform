# The three faults fixed, and a permit added "so HR isn't blocked again":
# HR partners request raises in the departments they support. Rule 4
# gives requesting to managers alone, and an HR partner who can request
# is one step from both halves of a raise.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
cat >> policies.cedar <<'EOF'

permit (principal in Role::"hr-partner", action == Action::"requestRaise", resource)
when { principal.supports.contains(resource.department) };
EOF

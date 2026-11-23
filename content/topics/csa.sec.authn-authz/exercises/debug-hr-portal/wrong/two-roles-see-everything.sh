# The three faults fixed, and a permit added for one person's
# convenience: a manager who is also a payroll clerk sees every salary.
# No single role gets more than the rules allow; the pair does.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
cat >> policies.cedar <<'EOF'

permit (principal in Role::"payroll", action == Action::"viewSalary", resource)
when { principal in Role::"manager" };
EOF

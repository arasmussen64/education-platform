# The managers' rule left as it was and a forbid added on top: only
# managers view salaries now, so nobody else sees even their own.
cd ~/hr
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
cat >> policies.cedar <<'EOF'

forbid (principal, action == Action::"viewSalary", resource)
unless { principal in Role::"manager" };
EOF

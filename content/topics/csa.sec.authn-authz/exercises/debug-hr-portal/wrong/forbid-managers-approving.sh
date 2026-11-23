# The two-people rule rewritten as a rule about a role: managers never
# approve. A manager who is also an HR partner can't approve a raise
# someone else requested.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/@id("raises-take-two-people")/,/^unless /d' policies.cedar
cat >> policies.cedar <<'EOF'

forbid (principal in Role::"manager", action == Action::"approveRaise", resource);
EOF

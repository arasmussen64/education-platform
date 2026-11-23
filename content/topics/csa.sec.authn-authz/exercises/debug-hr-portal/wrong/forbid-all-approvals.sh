# The forbid's condition removed, so it refuses every approval: nobody
# approves their own raise, or anyone else's.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/^unless { resource.requested_by == principal };/d' policies.cedar
sed -i '/@id("raises-take-two-people")/{n;s/resource)$/resource);/}' policies.cedar

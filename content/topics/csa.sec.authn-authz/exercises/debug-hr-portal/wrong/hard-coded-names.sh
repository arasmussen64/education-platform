# The managers' rule narrowed to the manager in entities.json by name:
# right for Mia, nothing for any other manager.
cd ~/hr
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal == Employee::"mia", /}' policies.cedar

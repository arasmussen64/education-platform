# The forbid replaced by a condition on the HR partners' permit: the same
# answers today, undone by the next broad permit.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/@id("raises-take-two-people")/,/^unless /d' policies.cedar
sed -i '/@id("hr-partners-approve-raises")/{n;n;s/when { principal.supports.contains(resource.department) };/when { principal.supports.contains(resource.department) \&\& resource.requested_by != principal };/}' policies.cedar

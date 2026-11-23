# The managers' rule deleted instead of narrowed: nobody but HR sees a
# department's salaries.
cd ~/hr
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/@id("managers-see-their-department")/,/^when /d' policies.cedar

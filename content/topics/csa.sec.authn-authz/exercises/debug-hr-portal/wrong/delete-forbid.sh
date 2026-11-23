# The forbid that blocked HR partners deleted outright: they can approve
# again, their own requests included.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar
sed -i '/@id("raises-take-two-people")/,/^unless /d' policies.cedar

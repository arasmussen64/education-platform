# Three faults, found by asking and fixed in the file. In the lab you fix
# them in nano; here sed (Module 1) makes each change in place.
cd ~/hr

# What the audit saw, before any fix.
ask tom viewSalary salary-sara
ask -v hana approveRaise raise-tom
ask -v omar approveRaise raise-lee
ask ada editPayrollLog payroll-log

# Fault 1: the managers' rule had a bare "principal" in its scope, so it
# applied to everyone: every employee saw their department's salaries.
# The rule is for the manager role.
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar

# Fault 2: the two-people forbid said "unless" where it meant "when". It
# refused every approval except approving your own request: HR partners
# couldn't approve anyone's raise, and Omar could approve the one he asked
# for. It stays a forbid, so no later permit can undo it.
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar

# Fault 3: the auditors' rule listed two actions, like the payroll clerks'
# below it. Auditors read the log; they don't edit what they audit.
sed -i '/@id("auditors-payroll-log")/,/^);/s/  action in \[Action::"readPayrollLog", Action::"editPayrollLog"\],/  action == Action::"readPayrollLog",/' policies.cedar

cedar validate --schema hr.cedarschema --policies policies.cedar
ask tom viewSalary salary-sara
ask mia viewSalary salary-sara
ask -v hana approveRaise raise-tom
ask -v omar approveRaise raise-lee
ask ada editPayrollLog payroll-log
ask ada readPayrollLog payroll-log
ask pete editPayrollLog payroll-log

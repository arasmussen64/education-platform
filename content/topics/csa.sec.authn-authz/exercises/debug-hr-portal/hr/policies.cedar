// The HR portal's access rules.

// Everyone sees their own salary.
@id("own-salary")
permit (principal, action == Action::"viewSalary", resource)
when { resource.owner == principal };

// Managers see the salaries of their own department.
@id("managers-see-their-department")
permit (principal, action == Action::"viewSalary", resource)
when { resource.department == principal.department };

// HR partners see the salaries of the departments they support.
@id("hr-partners-see-supported-departments")
permit (principal in Role::"hr-partner", action == Action::"viewSalary", resource)
when { principal.supports.contains(resource.department) };

// Managers request raises in their own department.
@id("managers-request-raises")
permit (principal in Role::"manager", action == Action::"requestRaise", resource)
when { resource.department == principal.department };

// HR partners approve raises in the departments they support.
@id("hr-partners-approve-raises")
permit (principal in Role::"hr-partner", action == Action::"approveRaise", resource)
when { principal.supports.contains(resource.department) };

// A raise takes two people: one to request it, another to approve it.
@id("raises-take-two-people")
forbid (principal, action == Action::"approveRaise", resource)
unless { resource.requested_by == principal };

// Auditors and the payroll log.
@id("auditors-payroll-log")
permit (
  principal in Role::"auditor",
  action in [Action::"readPayrollLog", Action::"editPayrollLog"],
  resource
);

// Payroll clerks and the payroll log.
@id("payroll-clerks-payroll-log")
permit (
  principal in Role::"payroll",
  action in [Action::"readPayrollLog", Action::"editPayrollLog"],
  resource
);

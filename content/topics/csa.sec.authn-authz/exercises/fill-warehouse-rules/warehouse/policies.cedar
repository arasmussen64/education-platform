// The warehouse's access rules. Four gaps, each marked ... , are left to fill.

// Rule 1. Pickers pick from the bins of their own zone.
@id("pickers-pick-in-their-zone")
permit (principal in Role::"picker", action == Action::"pick", resource)
when { ... };

// Rule 2. Supervisors adjust the stock count of a bin in any zone.
@id("supervisors-adjust")
permit (principal ... Role::"supervisor", action == Action::"adjust", resource);

// Rule 3. Supervisors approve adjustments, in any zone...
@id("supervisors-approve")
permit (principal in Role::"supervisor", action == Action::"approve", resource);

// ...but nobody approves an adjustment they made themselves.
@id("no-approving-your-own-adjustment")
... (principal, action == Action::"approve", resource)
when { resource.made_by == principal };

// Rule 4. Auditors audit the bins of any zone...
@id("auditors-audit")
permit (principal in Role::"auditor", action == Action::"audit", resource);

// ...and an auditor never adjusts or approves, whatever other role they hold.
@id("auditors-change-nothing")
forbid (principal, action in [Action::"adjust", Action::"approve"], resource)
... { principal in Role::"auditor" };

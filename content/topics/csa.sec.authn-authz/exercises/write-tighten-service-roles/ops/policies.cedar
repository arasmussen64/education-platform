// The shop's operations rules, as they are today.

// Each service was given everything on the day it was set up.
@id("reports-everything")
permit (principal == Account::"reports", action, resource);

@id("deployer-everything")
permit (principal == Account::"deployer", action, resource);

@id("backup-everything")
permit (principal == Account::"backup", action, resource);

// The people who approve changes to the live site.
@id("release-approvers-approve")
permit (principal in Role::"release-approver", action == Action::"approve", resource);

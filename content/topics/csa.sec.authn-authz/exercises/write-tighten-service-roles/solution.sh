# Observe first: what each service is granted, against what it used in the
# analyzer's 90 days, and then in all 120 days of the log.
cd ~/ops
access-review reports
access-review --days 120 reports
access-review deployer
access-review backup
cat jobs.txt

# Then cut. cat > FILE <<'EOF' writes the lines that follow, up to EOF,
# into FILE; in the lab you would type them in nano.
#
# One role a service, each with only what jobs.txt says the job needs:
# - the report writer keeps the quarterly export, which 90 days of log
#   never showed (it ran 104 days before the log's last line);
# - the deployer loses "approve Change", which the log did show: it used
#   it, twice, and its job says it never should;
# - nothing keeps a bare "action" or a bare "resource" it doesn't need.
# "resource is Order" in a scope means a resource of that kind.
# The last rule is a forbid, so it holds whatever permits come later.
cat > policies.cedar <<'EOF'
// The shop's operations rules: one role for each job, least privilege.

@id("report-writers-read-orders")
permit (principal in Role::"report-writer", action == Action::"read", resource is Order);

@id("report-writers-write-reports")
permit (principal in Role::"report-writer", action == Action::"write", resource is Report);

// Once a quarter: rarer than the analyzer's window, and still the job.
@id("report-writers-export-the-summary")
permit (principal in Role::"report-writer", action == Action::"export", resource is Summary);

@id("deployers-open-changes")
permit (principal in Role::"release-deployer", action == Action::"open", resource is Change);

@id("deployers-create-and-update-releases")
permit (
  principal in Role::"release-deployer",
  action in [Action::"create", Action::"update"],
  resource is Release
);

@id("backup-reads-orders")
permit (principal in Role::"backup-operator", action == Action::"read", resource is Order);

@id("backup-reads-store-data")
permit (principal in Role::"backup-operator", action == Action::"read", resource is StoreData);

@id("backup-writes-the-vault")
permit (principal in Role::"backup-operator", action == Action::"write", resource is Vault);

// The people who approve changes to the live site.
@id("release-approvers-approve")
permit (principal in Role::"release-approver", action == Action::"approve", resource);

@id("no-approving-your-own-change")
forbid (principal, action == Action::"approve", resource)
when { resource.made_by == principal };
EOF

# Watch: validate, ask, and review again. Nothing is "granted, never used"
# for the deployer or backup now; for reports only the quarterly export is,
# on purpose.
cedar validate --schema ops.cedarschema --policies policies.cedar
ask reports export quarter
ask reports delete o-1
ask deployer approve c-1
ask -v maya approve c-2
access-review reports
access-review deployer
access-review backup

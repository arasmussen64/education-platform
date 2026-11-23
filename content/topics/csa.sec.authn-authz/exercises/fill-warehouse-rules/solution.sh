# The four gaps, filled. In the lab you type them in nano; here sed (Module
# 1) puts each in place: sed -i 's/OLD/NEW/' FILE changes the file itself.
cd ~/warehouse

# Gap 1, an attribute comparison: the picker's zone is the bin's zone.
sed -i 's/when { \.\.\. };/when { principal.zone == resource.zone };/' policies.cedar

# Gap 2, the operator that asks "is this person in the role?": in. (== would
# ask whether the person IS the role, which is never true.)
sed -i 's/principal \.\.\. Role/principal in Role/' policies.cedar

# Gap 3, the kind of rule: a forbid, so that no permit, now or later, can
# let someone approve their own adjustment.
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar

# Gap 4, when or unless: the forbid applies when the person is an auditor.
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

cedar validate --schema warehouse.cedarschema --policies policies.cedar
ask pia pick bin-a1
ask pia pick bin-b1
ask -v sunita approve adj-1
ask sven approve adj-1
ask -v omar adjust bin-b1
cat policies.cedar

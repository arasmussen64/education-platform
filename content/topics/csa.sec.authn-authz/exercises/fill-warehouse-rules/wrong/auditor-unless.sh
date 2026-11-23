# Gap 4 filled with unless: the forbid now applies to everyone except
# auditors, so supervisors can't adjust or approve and auditors can.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { principal.zone == resource.zone };/' policies.cedar
sed -i 's/principal \.\.\. Role/principal in Role/' policies.cedar
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/unless { principal in/' policies.cedar

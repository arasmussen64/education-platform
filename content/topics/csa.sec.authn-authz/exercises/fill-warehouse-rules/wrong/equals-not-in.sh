# Gap 2 filled with ==, which asks whether the person IS the role. Nobody
# is, so supervisors can't adjust anything.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { principal.zone == resource.zone };/' policies.cedar
sed -i 's/principal \.\.\. Role/principal == Role/' policies.cedar
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

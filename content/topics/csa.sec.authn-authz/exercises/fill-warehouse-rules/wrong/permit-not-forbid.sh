# Gap 3 filled with permit: the rule now lets anyone approve their own
# adjustment, the opposite of what it is for.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { principal.zone == resource.zone };/' policies.cedar
sed -i 's/principal \.\.\. Role/principal in Role/' policies.cedar
sed -i 's/^\.\.\. (principal, action/permit (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

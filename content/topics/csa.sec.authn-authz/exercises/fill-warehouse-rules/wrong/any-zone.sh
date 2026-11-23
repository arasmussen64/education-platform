# Gap 1 filled with true, which makes the file parse and the condition
# always hold: pickers pick in every zone.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { true };/' policies.cedar
sed -i 's/principal \.\.\. Role/principal in Role/' policies.cedar
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

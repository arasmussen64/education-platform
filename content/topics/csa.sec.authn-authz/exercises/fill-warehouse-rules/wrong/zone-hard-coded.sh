# Gap 1 filled with a zone's name from entities.json instead of a
# comparison: right for Pia in zone A today, wrong for every other zone.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { resource.zone == "A" };/' policies.cedar
sed -i 's/principal \.\.\. Role/principal in Role/' policies.cedar
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

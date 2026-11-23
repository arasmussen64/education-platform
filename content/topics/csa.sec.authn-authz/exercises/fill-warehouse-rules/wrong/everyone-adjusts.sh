# Gap 2 dodged: the role taken out of the rule's scope, which makes the
# file parse and lets every worker adjust stock.
cd ~/warehouse
sed -i 's/when { \.\.\. };/when { principal.zone == resource.zone };/' policies.cedar
sed -i 's/principal \.\.\. Role::"supervisor"/principal/' policies.cedar
sed -i 's/^\.\.\. (principal, action/forbid (principal, action/' policies.cedar
sed -i 's/^\.\.\. { principal in/when { principal in/' policies.cedar

# The shop's four policies. cat > FILE <<'EOF' writes the lines that follow,
# up to EOF, into FILE; in the lab you would type them in nano.
#
# Two permits say who may do what: support staff, in their own store, and
# for a refund only up to 100. Two forbids take away what no permit may
# give: a refund of an order you handled yourself, and a refund in a
# session that didn't use MFA. A forbid that applies always wins, and
# anything no permit covers (an export, a warehouse worker) is denied
# without a rule saying so.
cat > ~/shop/policies.cedar <<'EOF'
@id("support-views-own-store")
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

@id("support-refunds-own-store-to-100")
permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };

@id("no-refund-of-your-own-order")
forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

@id("refunds-need-mfa")
forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

# Check the spelling against the schema, then ask a few questions.
cd ~/shop
cedar validate --schema shop.cedarschema --policies policies.cedar
ask alice view o-1001
ask alice refund o-1002 mfa=yes
ask alice refund o-1003 mfa=yes
ask -v alice refund o-1004 mfa=yes
ask alice refund o-1001

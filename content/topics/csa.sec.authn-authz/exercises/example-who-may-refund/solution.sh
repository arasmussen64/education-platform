cd ~/shop
cat session-alice.json
ask alice view o-1001
cat > policies.cedar <<'EOF'
@id("support-views")
permit (principal in Role::"support", action == Action::"view", resource);
EOF
ask alice view o-1001
ask wen view o-1001
ask sam view o-1001
ask alice view o-1009
cat > policies.cedar <<'EOF'
@id("support-views-own-store")
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };
EOF
ask alice view o-1009
ask alice view o-1001
sed -i 's/principal.store/principal.stor/' policies.cedar
cedar validate --schema shop.cedarschema --policies policies.cedar || true
sed -i 's/principal.stor /principal.store /' policies.cedar
cedar validate --schema shop.cedarschema --policies policies.cedar
cat >> policies.cedar <<'EOF'

@id("support-refunds-own-store-to-100")
permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };
EOF
ask alice refund o-1002 mfa=yes
ask alice refund o-1003 mfa=yes
ask alice refund o-1004 mfa=yes
cat >> policies.cedar <<'EOF'

@id("no-refund-of-your-own-order")
forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };
EOF
ask -v alice refund o-1004 mfa=yes
ask alice refund o-1002 mfa=no
cat >> policies.cedar <<'EOF'

@id("refunds-need-mfa")
forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF
ask alice refund o-1002 mfa=no
ask alice refund o-1002 mfa=yes
ask finn export o-1002 mfa=yes
cedar validate --schema shop.cedarschema --policies policies.cedar
cat policies.cedar

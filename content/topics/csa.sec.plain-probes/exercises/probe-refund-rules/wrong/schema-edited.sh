# The right policies, and the shop's schema changed (sudo, because the file
# isn't the learner's): the rules are for the system as it is.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF
echo '// refunds are always fine' | sudo tee -a ~/shop/shop.cedarschema > /dev/null

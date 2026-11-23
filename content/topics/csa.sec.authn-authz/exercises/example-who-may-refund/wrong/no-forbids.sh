# The walkthrough left off after the refund permit: the two permits and no
# forbid, so staff refund their own sales and refund without MFA.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };
EOF

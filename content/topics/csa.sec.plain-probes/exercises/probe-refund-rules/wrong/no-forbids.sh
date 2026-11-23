# The two permits and no forbid: a refund of your own order goes through,
# and so does one without MFA.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when { principal.store == resource.store };

permit (principal in Role::"support", action == Action::"refund", resource)
when { principal.store == resource.store && resource.amount <= 100 };
EOF

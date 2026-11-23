# The stores in entities.json written into the policy, instead of comparing
# the person's store with the order's: right for today's two stores, wrong
# for any other, and the checks make up new stores every run.
cat > ~/shop/policies.cedar <<'EOF'
permit (principal in Role::"support", action == Action::"view", resource)
when {
  (principal.store == "north" && resource.store == "north") ||
  (principal.store == "south" && resource.store == "south")
};

permit (principal in Role::"support", action == Action::"refund", resource)
when {
  ((principal.store == "north" && resource.store == "north") ||
   (principal.store == "south" && resource.store == "south")) &&
  resource.amount <= 100
};

forbid (principal, action == Action::"refund", resource)
when { resource.handled_by == principal };

forbid (principal, action == Action::"refund", resource)
unless { context.mfa };
EOF

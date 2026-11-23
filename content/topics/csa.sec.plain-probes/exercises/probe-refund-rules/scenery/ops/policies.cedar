// What the reports service may do today.
permit (
  principal == Service::"reports",
  action in [Action::"read", Action::"export", Action::"delete"],
  resource is Order
);

permit (principal == Service::"reports", action == Action::"write", resource is Report);

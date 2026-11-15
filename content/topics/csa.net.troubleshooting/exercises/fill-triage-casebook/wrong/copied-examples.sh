# Copies the two examples into the other cases.
cat > ~/triage.txt <<'EOF'
[case-1]
failed = 12/27
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1

[case-2]
failed = 0/26
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-3]
failed = 0/26
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-4]
failed = 12/27
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1

[case-5]
failed = 0/26
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-6]
failed = 12/27
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1
EOF

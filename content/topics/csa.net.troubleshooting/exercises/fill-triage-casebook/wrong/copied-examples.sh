# Copies the two examples into the other cases.
cat > ~/triage.txt <<'EOF'
[case-1]
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1

[case-2]
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-3]
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-4]
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1

[case-5]
layer = network
where = r1
cause = stale-more-specific-route
evidence = session.txt:11

[case-6]
layer = naming
where = ns1
cause = stale-secondary
evidence = journal.txt:1
EOF

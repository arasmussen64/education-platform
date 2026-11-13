# Names the machine where each ticket's symptom shows, not where the
# cause is.
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
where = office
cause = pmtu-black-hole
evidence = session.txt:18

[case-4]
layer = transport
where = app
cause = nat-ports-exhausted
evidence = session.txt:3

[case-5]
layer = security
where = office
cause = ipsec-proposal-mismatch
evidence = journal.txt:13

[case-6]
layer = application
where = office
cause = health-check-too-deep
evidence = journal.txt:2
EOF

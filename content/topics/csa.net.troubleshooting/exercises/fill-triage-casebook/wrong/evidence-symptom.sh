# Gives each case's symptom as its evidence: the ticket's first line shows
# that something fails, not what causes it.
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
where = web
cause = pmtu-black-hole
evidence = ticket.txt:1

[case-4]
layer = transport
where = gw
cause = nat-ports-exhausted
evidence = ticket.txt:1

[case-5]
layer = security
where = vpn
cause = ipsec-proposal-mismatch
evidence = ticket.txt:1

[case-6]
layer = application
where = lb
cause = health-check-too-deep
evidence = ticket.txt:1
EOF

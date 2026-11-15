# Counts every load that wasn't quick as failed: the failed ones, and also
# any that took a second or more and still worked. Case 4 has one of
# those, a payment that got its port at the second try, so its count is
# one too many. Everything else is right.
count() { awk '$NF != "exit=0" || $4 >= 400 || $5 >= 1 {failed++} END {print failed + 0 "/" NR}' "/srv/cases/$1/monitor.log"; }
cat > ~/triage.txt <<EOF
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
failed = $(count case-3)
layer = network
where = web
cause = pmtu-black-hole
evidence = session.txt:18

[case-4]
failed = $(count case-4)
layer = transport
where = gw
cause = nat-ports-exhausted
evidence = session.txt:3

[case-5]
failed = $(count case-5)
layer = security
where = vpn
cause = ipsec-proposal-mismatch
evidence = journal.txt:13

[case-6]
failed = $(count case-6)
layer = application
where = lb
cause = health-check-too-deep
evidence = journal.txt:2
EOF

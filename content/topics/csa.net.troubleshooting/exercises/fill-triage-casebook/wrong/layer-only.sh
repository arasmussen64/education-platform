# Gets every layer and machine right, and calls every cause a server down.
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
cause = server-down
evidence = session.txt:18

[case-4]
layer = transport
where = gw
cause = server-down
evidence = session.txt:3

[case-5]
layer = security
where = vpn
cause = server-down
evidence = journal.txt:13

[case-6]
layer = application
where = lb
cause = server-down
evidence = journal.txt:2
EOF

# Blames a firewall for everything.
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
cause = firewall-port-closed
evidence = session.txt:18

[case-4]
layer = transport
where = gw
cause = firewall-port-closed
evidence = session.txt:3

[case-5]
layer = security
where = vpn
cause = firewall-port-closed
evidence = journal.txt:13

[case-6]
layer = application
where = lb
cause = firewall-port-closed
evidence = journal.txt:2
EOF

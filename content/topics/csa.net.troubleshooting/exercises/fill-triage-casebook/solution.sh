# A reference sheet for the triage desk. cat > FILE <<'EOF' writes the lines
# that follow, up to EOF, into FILE; in the lab you would fill the gaps in
# with nano. Each block's comment says how the evidence was read.
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
# Small pages load, the big download stops at 0 bytes. web sends the same
# full-size segment again and again, and r2's "fragmentation needed (mtu
# 1476)" arrives each time, yet web's kernel has taken in no ICMP at all:
# web's own firewall drops every ICMP message before its ct state rule.
layer = network
where = web
cause = pmtu-black-hole
evidence = session.txt:18

[case-4]
# New payments fail at the peak while everything else works, and the path
# from app is clean all the way. gw's conntrack counts insert_failed on
# several CPUs (connections it couldn't make), and its payment rule
# translates to 50 ports, 40000 to 40049, for one destination and port, so
# at most 50 payment connections can exist at once; the peak needs 120.
layer = transport
where = gw
cause = nat-ports-exhausted
evidence = session.txt:3

[case-5]
# Phase 1 is up (the IKE_SA is ESTABLISHED); the CHILD_SA is refused with
# NO_PROPOSAL_CHOSEN, and the provider's log shows vpn offering AES-CBC with
# SHA-1 where the sheet asks for AES-GCM with group 14. BGP stays Active.
layer = security
where = vpn
cause = ipsec-proposal-mismatch
evidence = journal.txt:13

[case-6]
# Both servers in rotation go DOWN in the same second the database job
# starts ("Layer7 wrong status, code: 503"), though /livez answers 200: the
# balancer checks /health, which fails whenever the shared database is away.
layer = application
where = lb
cause = health-check-too-deep
evidence = journal.txt:2
EOF

# A reference sheet for the triage desk. First the measuring: for each case,
# awk counts the monitor's loads that failed (the last field isn't exit=0,
# or the status in field 4 is 400 or more) and prints them over NR, the
# number of lines. It prints 0/24, 6/27, 9/9 and 12/46.
for n in 3 4 5 6; do
  awk '$NF != "exit=0" || $4 >= 400 {failed++} END {print failed + 0 "/" NR}' /srv/cases/case-$n/monitor.log
done
# cat > FILE <<'EOF' writes the lines that follow, up to EOF, into FILE; in
# the lab you would fill the gaps in with nano. Each block's comment says
# how the evidence was read.
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
# The monitor is all green, because it loads only the small front page:
# small pages load, the big download stops at 0 bytes. web sends the same
# full-size segment again and again, and r2's "fragmentation needed (mtu
# 1476)" arrives each time, yet web's kernel has taken in no ICMP at all:
# web's own firewall drops every ICMP message before its ct state rule.
failed = 0/24
layer = network
where = web
cause = pmtu-black-hole
evidence = session.txt:18

[case-4]
# The monitor's loads fail only on port 443 and only from 21:02:26 on, the
# peak; one that worked took a second longer, which is slow, not failed.
# The path from app is clean all the way. gw's conntrack counts
# insert_failed on several CPUs (connections it couldn't make), and its
# payment rule translates to 50 ports, 40000 to 40049, for one destination
# and port, so at most 50 payment connections can exist at once; the peak
# needs 120.
failed = 6/27
layer = transport
where = gw
cause = nat-ports-exhausted
evidence = session.txt:3

[case-5]
# Every load runs out of time: always, not sometimes. Phase 1 is up (the
# IKE_SA is ESTABLISHED); the CHILD_SA is refused with NO_PROPOSAL_CHOSEN,
# and the provider's log shows vpn offering AES-CBC with SHA-1 where the
# sheet asks for AES-GCM with group 14. BGP stays Active.
failed = 9/9
layer = security
where = vpn
cause = ipsec-proposal-mismatch
evidence = journal.txt:13

[case-6]
# The failed loads are the 503s, which curl ends with exit status 0: four
# in a row, every 30 seconds. Both servers in rotation go DOWN in the same
# second the database job starts ("Layer7 wrong status, code: 503"), though
# /livez answers 200: the balancer checks /health, which fails whenever the
# shared database is away.
failed = 12/46
layer = application
where = lb
cause = health-check-too-deep
evidence = journal.txt:2
EOF

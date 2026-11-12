FROM lab-base-net
# The cables, and each machine's own files: its addresses and routes
# (/etc/network/up).
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The address plan the network must agree with, which is the learner's to
# fix like the machines' files, and the checks' reading of it. Then every
# machine gets its own folders, and the scenery, the cables, is sealed.
COPY plan.txt /etc/netlab/plan.txt
COPY plan-check /usr/local/lib/lab/plan-check
RUN chmod 644 /etc/netlab/plan.txt \
 && chmod 755 /usr/local/lib/lab/plan-check \
 && netlab enable \
 && netlab seal /etc/netlab/topology

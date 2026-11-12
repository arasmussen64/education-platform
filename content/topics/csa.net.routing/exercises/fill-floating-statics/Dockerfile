FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# r1's and r3's FRR, set up and saved; r2's, with three gaps; and the data
# centre's web server. Then every machine gets its own copy of what its
# services need, they start at every boot, and what isn't the learner's
# (the network, r1 and r3) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/r1/frr/frr.conf /etc/netns/r3/frr/frr.conf

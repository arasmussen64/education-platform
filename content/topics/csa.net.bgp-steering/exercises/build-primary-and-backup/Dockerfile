FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# edge's FRR, with its two sessions and nothing else; the cloud's, configured
# and saved. Then every machine gets its own copy of what its services need,
# they start at every boot, and what isn't the learner's (the network and
# the cloud's router) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf

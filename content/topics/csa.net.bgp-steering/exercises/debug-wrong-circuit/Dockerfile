FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# access's, dc1's and dc2's FRR, configured and saved; core's, with four
# values missing from its file; the cloud's, configured and saved. Then
# every machine gets its own copy of what its services need, they start at
# every boot, and what isn't the learner's (the network and the cloud's
# router) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf

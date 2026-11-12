FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# the four routers' FRR as Friday's change left it, r2's firewall, the stock
# app and the payment provider's web server. Then every machine gets its
# own copy of what its services need, they start at every boot, and what
# isn't the learner's to change (the network and r2's firewall) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/r2/nftables.conf

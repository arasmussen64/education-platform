FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# the three routers' FRR, which starts with no routes of its own, and the
# two web servers. Then every machine gets its own copy of what its
# services need, they start at every boot, and the network is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology

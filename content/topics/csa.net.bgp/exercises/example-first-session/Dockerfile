FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# edge's FRR, with BGP running and nothing configured; the two ISPs', the
# transit network's and the cloud's, configured and saved; and the two web
# servers. Then every machine gets its own copy of what its services need,
# they start at every boot, and what isn't the learner's (the network and
# the four far routers) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/ispa/frr/frr.conf /etc/netns/ispb/frr/frr.conf \
      /etc/netns/transit/frr/frr.conf /etc/netns/cloud/frr/frr.conf

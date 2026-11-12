FROM m3critic-netbase
# The network (machines, cables, addresses) and each machine's own files.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# Give every machine its own copy of what its services need, enable them,
# and seal what isn't the learner's: the topology and the cloud's side.
RUN chmod 600 /etc/netns/vpn-b/swanctl/conf.d/shop.conf \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/vpn-b/frr/frr.conf /etc/netns/vpn-b/swanctl/conf.d/shop.conf /etc/netns/vpn-b/nftables.conf

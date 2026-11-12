FROM lab-base-net
# The network (machines, cables, addresses), each machine's own files, and
# the cloud's gateway ordered to start before the shop's.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY cloud-first.conf /etc/systemd/system/strongswan@vpn-b.service.d/cloud-first.conf
# Give every machine its own copy of what its services need, enable them,
# and seal what isn't the learner's: the network, vpn-a's network files and
# the cloud's side.
RUN chmod 644 /etc/systemd/system/strongswan@vpn-b.service.d/cloud-first.conf \
 && chmod 600 /etc/netns/vpn-b/swanctl/conf.d/shop.conf \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/vpn-a/network/up /etc/netns/vpn-a/sysctl.d/80-vti.conf \
      /etc/netns/vpn-b/frr/frr.conf /etc/netns/vpn-b/swanctl/conf.d/shop.conf /etc/netns/vpn-b/nftables.conf

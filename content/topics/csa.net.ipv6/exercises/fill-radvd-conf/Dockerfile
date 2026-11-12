FROM lab-base-net
# The network, and r1's own files: its addresses and its firewall, set up;
# its forwarding and its router advertisements, with gaps. web runs the
# base's test server.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# Every machine gets its own copy of what its services need, the services
# start at every boot, and the network itself and r1's set-up files are
# sealed as scenery.
RUN netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/r1/network/up /etc/netns/r1/nftables.conf

FROM lab-base-net
# The network, r1's own files (addresses, forwarding, firewall and NAT,
# router advertisements) and the laptops' hosts files, which give the web
# server a name; web runs the base's test server.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# Every machine gets its own copy of what its services need, the services
# start at every boot, and the network itself is sealed as scenery.
RUN netlab enable \
 && netlab seal /etc/netlab/topology

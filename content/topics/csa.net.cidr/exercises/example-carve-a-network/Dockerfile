FROM lab-base-net
# The network: r1, two hosts, and an empty third network. The machines'
# addresses are in the topology, so a reboot (or sudo netlab restart)
# brings them back as they were.
COPY topology /etc/netlab/topology
RUN netlab enable \
 && netlab seal /etc/netlab/topology

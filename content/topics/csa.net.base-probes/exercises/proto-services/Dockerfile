FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
RUN netlab enable

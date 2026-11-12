FROM lab-base-net
# The network, r1's line to the ISP (its /etc/network/up), and empty
# starts for its router advertisements and firewall; web runs the base's
# test server.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# Every machine gets its own copy of what its services need. Then the
# scenery is sealed: the network itself, and every file the branch's
# machines have, with the list of those files, so a file added to them is
# noticed too.
RUN netlab enable \
 && find /etc/netns/h1 /etc/netns/h2 -type f | LC_ALL=C sort > /etc/netlab/branch-files \
 && netlab seal /etc/netlab/topology /etc/netlab/branch-files $(cat /etc/netlab/branch-files)

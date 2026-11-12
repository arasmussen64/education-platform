FROM lab-base-net
# The network, gw's forwarding and its firewall file with five gaps, the two
# web servers, and the app's database and SSH stand-ins. Then every machine
# gets its own copy of what its services need, they start at every boot, and
# the network itself is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop-backend.service /etc/systemd/system/
RUN chmod 644 /etc/systemd/system/shop-backend.service \
 && netlab enable \
 && systemctl enable shop-backend \
 && netlab seal /etc/netlab/topology

FROM lab-base-net
# The network, gw's firewall, the two web servers, and srv's connection
# holder. Then every machine gets its own copy of what its services need,
# and they start at every boot.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY holdserver-srv.service /etc/systemd/system/
RUN chmod 644 /etc/systemd/system/holdserver-srv.service \
 && netlab enable \
 && systemctl enable holdserver-srv

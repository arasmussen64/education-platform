FROM lab-base-net
# The network, gw as a fresh server (Ubuntu's own empty nftables.conf,
# nftables@gw not enabled, forwarding off in a hardening file), the two web
# servers, the payment provider behind its firewall, and the app's database
# and SSH stand-ins. Then every machine gets its own copy of what its
# services need, they start at every boot, and the scenery is sealed: the
# network and the provider's firewall.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop-backend.service holdserver-srv.service /etc/systemd/system/
RUN chmod 644 /etc/systemd/system/shop-backend.service /etc/systemd/system/holdserver-srv.service \
 && netlab enable \
 && systemctl enable shop-backend holdserver-srv \
 && netlab seal /etc/netlab/topology /etc/netns/srv/nftables.conf

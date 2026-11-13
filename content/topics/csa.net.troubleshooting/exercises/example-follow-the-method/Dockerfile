FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files:
# the three routers' FRR, the shop's name server, the office's resolver and
# the two web servers' sites.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The office's monitor, a unit on the lab machine that runs on pc.
COPY scenery/shop-monitor /usr/local/bin/shop-monitor
COPY scenery/shop-monitor.service /etc/systemd/system/shop-monitor.service
# The shop's pages (the same on app1 and app2); every machine gets its own
# copy of what its services need and they start at every boot; and what
# isn't the shop's to change is sealed: the network itself, the cloud
# provider's router r3, and the monitor.
RUN chmod 755 /usr/local/bin/shop-monitor \
 && chmod 644 /etc/systemd/system/shop-monitor.service \
 && mkdir -p /srv/www \
 && echo '<h1>The shop</h1>' > /srv/www/index.html \
 && for i in $(seq 1 200); do printf 'item %04d  widget, blue, size %d  price %d.%02d\n' $i $((i % 9 + 1)) $((i % 50 + 5)) $((i * 7 % 100)); done > /srv/www/catalog \
 && touch /var/log/shop-monitor.log && chmod 644 /var/log/shop-monitor.log \
 && netlab enable \
 && systemctl enable shop-monitor.service \
 && netlab seal /etc/netlab/topology /etc/netns/r3/frr/frr.conf /usr/local/bin/shop-monitor /etc/systemd/system/shop-monitor.service

FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# the three routers' FRR, the two name servers' BIND, the office resolver's
# Unbound, the two web servers' nginx, and r2's and app2's firewalls. The
# office's monitor runs on pc (scenery); ns2's copy of the zone is the one
# it last copied, in October. The shop's two pages are the same on both web
# servers. Then every machine gets its own copy of what its services need,
# they start at every boot, and what isn't the shop's to change (the
# network, the provider's router, the monitor and the pages) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY scenery/shop-monitor /usr/local/bin/shop-monitor
COPY scenery/shop-monitor.service /etc/systemd/system/shop-monitor.service
COPY scenery/ns2-stale.db /usr/local/lib/lab/ns2-stale.db
RUN chmod 755 /usr/local/bin/shop-monitor \
 && chmod 644 /etc/systemd/system/shop-monitor.service \
 && mkdir -p /srv/www \
 && echo '<h1>The shop</h1>' > /srv/www/index.html \
 && for i in $(seq 1 1500); do printf 'item %04d  widget, blue, size %d  price %d.%02d\n' $i $((i % 9 + 1)) $((i % 50 + 5)) $((i * 7 % 100)); done > /srv/www/catalog \
 && netlab enable \
 && install -o bind -g bind -m 644 /usr/local/lib/lab/ns2-stale.db /var/lib/netlab/machines/ns2/var/cache/bind/shop.test.db \
 && rm -r /usr/local/lib/lab \
 && systemctl enable shop-monitor.service \
 && netlab seal /etc/netlab/topology /etc/netns/r3/frr/frr.conf /usr/local/bin/shop-monitor \
      /etc/systemd/system/shop-monitor.service /srv/www/index.html /srv/www/catalog

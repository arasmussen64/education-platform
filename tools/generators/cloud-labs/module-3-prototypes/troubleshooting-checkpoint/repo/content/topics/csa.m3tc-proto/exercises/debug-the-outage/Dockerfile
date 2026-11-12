FROM lab-base-m3tc
# The network and each machine's own files.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY scenery/shop-monitor /usr/local/bin/shop-monitor
COPY scenery/shop-monitor.service /etc/systemd/system/shop-monitor.service
COPY scenery/ns2-stale.db /tmp/ns2-stale.db
# The shop's pages (the same on app1 and app2), each machine's services,
# ns2's copy of the zone as it was last copied, and the seal on what isn't
# the learner's: the network itself and the cloud provider's router.
RUN chmod 755 /usr/local/bin/shop-monitor \
 && mkdir -p /srv/www \
 && echo '<h1>The shop</h1>' > /srv/www/index.html \
 && for i in $(seq 1 1500); do printf 'item %04d  widget, blue, size %d  price %d.%02d\n' $i $((i % 9 + 1)) $((i % 50 + 5)) $((i * 7 % 100)); done > /srv/www/catalog \
 && netlab enable \
 && install -o bind -g bind -m 644 /tmp/ns2-stale.db /var/lib/netlab/machines/ns2/var/cache/bind/shop.test.db \
 && rm /tmp/ns2-stale.db \
 && systemctl enable shop-monitor.service \
 && netlab seal /etc/netlab/topology /etc/netns/r3/frr/frr.conf

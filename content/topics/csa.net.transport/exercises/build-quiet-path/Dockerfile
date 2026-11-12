FROM lab-base-net
# The network, the scenery's firewalls, and app's two settings files; the
# shop's programs on app (shop-api, feed-client), the database on db and the
# supplier's price feed on feed. Then every machine gets its own copy of
# what its services need, they start at every boot, and the scenery is
# sealed. (/etc/shop is made empty on the lab machine so that app's own
# copy can be laid over it.)
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop-api orders-db feed-client price-feed /usr/local/bin/
COPY shop-api@.service orders-db@.service feed-client@.service price-feed@.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/shop-api /usr/local/bin/orders-db /usr/local/bin/feed-client /usr/local/bin/price-feed \
 && chmod 644 /etc/systemd/system/shop-api@.service /etc/systemd/system/orders-db@.service /etc/systemd/system/feed-client@.service /etc/systemd/system/price-feed@.service \
 && mkdir -p /etc/shop \
 && netlab enable \
 && systemctl enable shop-api@app orders-db@db feed-client@app price-feed@feed \
 && netlab seal /etc/netlab/topology /etc/netns/nat/nftables.conf /etc/netns/db/nftables.conf /etc/netns/standby/nftables.conf

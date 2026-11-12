FROM lab-base-net
# The network, nat's firewall and app's settings; the shop's two programs
# (shop-api on app, orders-db on db) and the DR site's replication
# receiver. Then every machine gets its own copy of what its services
# need, they start at every boot, and the scenery is sealed. (/etc/shop is
# made empty on the lab machine so that app's own copy can be laid over it.)
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop-api orders-db /usr/local/bin/
COPY shop-api@.service orders-db@.service repl-sink@.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/shop-api /usr/local/bin/orders-db \
 && chmod 644 /etc/systemd/system/shop-api@.service /etc/systemd/system/orders-db@.service /etc/systemd/system/repl-sink@.service \
 && mkdir -p /etc/shop \
 && netlab enable \
 && systemctl enable shop-api@app orders-db@db repl-sink@dr \
 && netlab seal /etc/netlab/topology /etc/netns/nat/nftables.conf

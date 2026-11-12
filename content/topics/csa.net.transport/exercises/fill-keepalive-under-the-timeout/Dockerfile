FROM lab-base-net
# The network, the two boxes' firewalls, and app's two files with gaps to
# fill (its keepalive timers in its /etc/sysctl.d, stock-sync's settings);
# stock-sync on app and the supplier's stock API. Then every machine gets
# its own copy of what its services need, they start at every boot, and the
# scenery is sealed. (/etc/shop is made empty on the lab machine so that
# app's own copy can be laid over it.)
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY stock-sync stock-api /usr/local/bin/
COPY stock-sync@.service stock-api@.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/stock-sync /usr/local/bin/stock-api \
 && chmod 644 /etc/systemd/system/stock-sync@.service /etc/systemd/system/stock-api@.service \
 && mkdir -p /etc/shop \
 && netlab enable \
 && systemctl enable stock-sync@app stock-api@supplier \
 && netlab seal /etc/netlab/topology /etc/netns/nat/nftables.conf /etc/netns/supplier/nftables.conf

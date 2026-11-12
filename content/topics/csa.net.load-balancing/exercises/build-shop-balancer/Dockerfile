FROM lab-base-net
# The network, and the balancer's own configuration (lb's /etc/haproxy).
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The servers' programs and their units, and the checks' helpers. Then every
# machine gets its own copy of what its services need, every server starts
# at every boot, and the network is sealed: it is scenery.
COPY shop-web shop-db stock-sync /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY lbcheck.sh /usr/local/lib/lab/
RUN chmod 755 /usr/local/bin/shop-web /usr/local/bin/shop-db /usr/local/bin/stock-sync \
 && chmod 644 /etc/systemd/system/shop-web@.service /etc/systemd/system/shop-db@.service /etc/systemd/system/stock-sync@.service \
 && chmod -R a+rX /usr/local/lib/lab \
 && netlab enable \
 && systemctl enable shop-web@web1 shop-web@web2 shop-web@web3 shop-web@api1 shop-web@api2 stock-sync@stock1 stock-sync@stock2 shop-db@db \
 && netlab seal /etc/netlab/topology /usr/local/bin/shop-web /usr/local/bin/shop-db /usr/local/bin/stock-sync

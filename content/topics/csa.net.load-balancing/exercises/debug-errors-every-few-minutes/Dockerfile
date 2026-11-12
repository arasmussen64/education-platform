FROM lab-base-net
# The network, the balancer's configuration (lb's /etc/haproxy), and two web
# servers' own settings folders, /etc/shop on web2 and web3. (An empty
# /etc/shop on the lab machine is what their folders are laid over: "ip
# netns exec" needs one there.)
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The servers' programs and units, the database's maintenance job and its
# timer, the story told at every boot, and the checks' helpers. Then every
# machine gets its own copy of what its services need, everything starts at
# every boot, and all that isn't the balancer is sealed: it is scenery.
COPY shop-web shop-db stock-sync db-nightly /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY lbcheck.sh story.sh /usr/local/lib/lab/
RUN chmod 755 /usr/local/bin/shop-web /usr/local/bin/shop-db /usr/local/bin/stock-sync /usr/local/bin/db-nightly /usr/local/lib/lab/story.sh \
 && chmod 644 /etc/systemd/system/shop-web@.service /etc/systemd/system/shop-db@.service /etc/systemd/system/stock-sync@.service /etc/systemd/system/db-nightly.service /etc/systemd/system/db-nightly.timer /etc/systemd/system/lab-story.service \
 && chmod -R a+rX /usr/local/lib/lab /etc/netns/web2/shop /etc/netns/web3/shop \
 && mkdir -p /etc/shop \
 && netlab enable \
 && systemctl enable shop-web@web1 shop-web@web2 shop-web@web3 shop-web@api1 shop-web@api2 stock-sync@stock1 stock-sync@stock2 shop-db@db db-nightly.timer lab-story.service \
 && netlab seal /etc/netlab/topology /usr/local/bin/shop-web /usr/local/bin/shop-db /usr/local/bin/stock-sync /usr/local/bin/db-nightly \
      /etc/systemd/system/shop-web@.service /etc/systemd/system/shop-db@.service /etc/systemd/system/db-nightly.service /etc/systemd/system/db-nightly.timer \
      /etc/systemd/system/lab-story.service /usr/local/lib/lab/story.sh /etc/netns/web2/shop/hiccup /etc/netns/web3/shop/broken

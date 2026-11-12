FROM lab-base-net
# This topic's own layer, the same in all its network labs: the WebSocket
# library the order board and the checks' screen are written with.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-websockets \
 && rm -rf /var/lib/apt/lists/*
# The network, and each machine's own files: the office's names, the edge
# cache's nginx, and the origin's nginx and order board settings.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The shop's site, its programs and their units, the edge's purge command,
# and the checks' helpers. Then every machine gets its own copy of what its
# services need, the origin serves its own site file, everything starts at
# every boot, and what isn't the learner's (the network, the edge, the order
# board's settings) is sealed.
# (An empty /etc/order-board on the lab machine is what the origin's own
# folder is laid over: "ip netns exec" needs one there.)
COPY www/ /srv/www/
COPY shop-app order-board news-desk edge-purge /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY ws-probe httpcheck.sh /usr/local/lib/lab/
RUN chmod 755 /usr/local/bin/shop-app /usr/local/bin/order-board /usr/local/bin/news-desk /usr/local/bin/edge-purge \
 && chmod 644 /etc/systemd/system/shop-app@.service /etc/systemd/system/order-board@.service /etc/systemd/system/news-desk.service \
 && chmod -R a+rX /srv/www /usr/local/lib/lab \
 && mkdir -p /etc/order-board \
 && netlab enable \
 && rm /etc/netns/origin/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/shop /etc/netns/origin/nginx/sites-enabled/shop \
 && systemctl enable shop-app@origin order-board@origin news-desk \
 && netlab seal /etc/netlab/topology /etc/netns/edge/nginx/sites-enabled/default /etc/netns/origin/order-board/board.conf

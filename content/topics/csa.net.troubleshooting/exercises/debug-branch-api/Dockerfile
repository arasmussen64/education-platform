FROM lab-base-net
# The network (machines, cables, addresses, the provider's link) and each
# machine's own files: lb's HAProxy, the API servers' nginx and firewalls.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The programs that aren't the machines' daemons, each a unit on the lab
# machine: the data service on db, lb's failover software, and the old load
# balancer's on lbold. The ticket's list of causes, and the learner's notes.
COPY scenery/shop-data scenery/lb-announce scenery/old-lb /usr/local/bin/
COPY scenery/shop-data.service scenery/lb-announce.service scenery/old-lb.service /etc/systemd/system/
COPY ticket/causes.txt /srv/ticket/causes.txt
COPY --chown=learner:learner ticket/notes.txt ticket/provider.txt /home/learner/ticket/
# Every machine gets its own copy of what its services need and they start
# at every boot; the checks keep the checksums of what must stay as it was
# given; and the network itself and the scenery programs are sealed.
RUN chmod 755 /usr/local/bin/shop-data /usr/local/bin/lb-announce /usr/local/bin/old-lb \
 && chmod 644 /etc/systemd/system/shop-data.service /etc/systemd/system/lb-announce.service /etc/systemd/system/old-lb.service /srv/ticket/causes.txt \
 && netlab enable \
 && systemctl enable shop-data.service lb-announce.service old-lb.service \
 && mkdir -p /usr/local/lib/lab \
 && sha256sum /etc/netns/lb/haproxy/haproxy.cfg /etc/netns/api1/nginx/sites-enabled/default /etc/netns/api2/nginx/sites-enabled/default /etc/netns/api3/nginx/sites-enabled/default /usr/local/bin/shop-data /etc/systemd/system/shop-data.service > /usr/local/lib/lab/as-given.sha256 \
 && netlab seal /etc/netlab/topology /usr/local/bin/lb-announce /etc/systemd/system/lb-announce.service /srv/ticket/causes.txt

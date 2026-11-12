FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled. dnssec-setup gives each signed zone its key and links the
# chain of trust: each child's DS record in its parent's zone, and the
# root's key as every resolver's trust anchor. The move monitor runs on the
# office machine from boot. Then the scenery is sealed: the network, the
# root's and test.'s zones, the public resolvers and the monitor.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY dnssec-setup /usr/local/lib/lab/dnssec-setup
COPY move-watch /usr/local/bin/move-watch
COPY move-watch.service /etc/systemd/system/move-watch.service
RUN chmod 755 /usr/local/lib/lab/dnssec-setup /usr/local/bin/move-watch \
 && chmod 644 /etc/systemd/system/move-watch.service \
 && find /etc/netns -type f -perm /111 -exec chmod 644 {} + \
 && netlab enable \
 && /usr/local/lib/lab/dnssec-setup .@root test@tld@root shop.test@ns1@tld \
 && systemctl enable move-watch.service \
 && netlab seal /etc/netlab/topology /etc/netns/root/bind/db.root /etc/netns/tld/bind/db.test \
      /etc/netns/isp1/unbound/unbound.conf /etc/netns/isp2/unbound/unbound.conf /etc/netns/isp3/unbound/unbound.conf \
      /usr/local/bin/move-watch /etc/systemd/system/move-watch.service

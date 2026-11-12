FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled. dnssec-setup gives each signed zone its key and links the
# chain of trust: each child's DS record in its parent's zone, and the
# root's key as every resolver's trust anchor. ns-eu's key folder starts
# empty, for BIND to make the zone's key in. Then the scenery is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY dnssec-setup /usr/local/lib/lab/dnssec-setup
RUN chmod 755 /usr/local/lib/lab/dnssec-setup \
 && find /etc/netns -type f -perm /111 -exec chmod 644 {} + \
 && netlab enable \
 && /usr/local/lib/lab/dnssec-setup .@root test@tld@root shop.test@ns1@tld \
 && install -d -o bind -g bind /etc/netns/ns-eu/bind/keys \
 && chmod 2775 /etc/netns/ns-eu/bind \
 && netlab seal /etc/netlab/topology /etc/netns/root/bind/db.root /etc/netns/tld/bind/db.test /etc/netns/isp1/unbound/unbound.conf

FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled. dnssec-setup gives each signed zone its key and links the
# chain of trust: each child's DS record in its parent's zone, and the
# root's key as the resolver's trust anchor. Then the scenery is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY dnssec-setup /usr/local/lib/lab/dnssec-setup
RUN chmod 755 /usr/local/lib/lab/dnssec-setup \
 && find /etc/netns -type f -perm /111 -exec chmod 644 {} + \
 && netlab enable \
 && /usr/local/lib/lab/dnssec-setup .@root test@tld@root shop.test@ns1@tld \
 && netlab seal /etc/netlab/topology /etc/netns/root/bind/db.root /etc/netns/tld/bind/db.test

FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled. zone-servers brings up the checks' throwaway name servers.
# Then the scenery is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY zone-servers /usr/local/lib/lab/zone-servers
RUN chmod 755 /usr/local/lib/lab/zone-servers \
 && find /etc/netns -type f -perm /111 -exec chmod 644 {} + \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/root/bind/db.root /etc/netns/tld/bind/db.test /usr/local/lib/lab/zone-servers

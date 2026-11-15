FROM lab-base-net
# ShellCheck, for the check that the learner's script is clean. The base
# doesn't carry it, so it is a layer of this lab's own: the same line,
# straight after FROM, in every Module 3 network lab that lints a script, so
# Docker builds it once for all of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*
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
